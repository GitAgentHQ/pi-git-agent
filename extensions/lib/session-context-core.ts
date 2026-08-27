export const MAX_CONTEXT_CHARS = 6000;

export type SessionEntry = {
  type?: string;
  message?: { role?: string; content?: unknown };
};

type ExtractedUserMessage = { index: number; text: string };

export interface SessionContextOptions {
  maxMessages?: number;
  tailChars?: number;
  sinceLastCall?: boolean;
}

export interface SessionContextResult {
  text: string;
  count: number;
  deduplicated: boolean;
}

function extractText(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .filter(
        (part): part is { type: string; text: string } =>
          !!part &&
          typeof part === "object" &&
          (part as { type?: unknown }).type === "text" &&
          typeof (part as { text?: unknown }).text === "string",
      )
      .map((part) => part.text)
      .join("\n");
  }
  return "";
}

function isInjectedProcedureMessage(text: string): boolean {
  return /^Run the "[^"]+" workflow\./.test(text);
}

export function collapseSkillInvocations(text: string): string {
  let result = text.replace(
    /<skill\b([^>]*)>[\s\S]*?<\/skill>/gi,
    (_match, attrs) => {
      const nameMatch = attrs.match(/\bname=["']([^"']+)["']/i);
      const name = nameMatch ? nameMatch[1] : undefined;
      return name ? `[Invoked skill: ${name}]` : "[Invoked skill]";
    },
  );
  result = result.replace(/^\/skill:([^\s]+)/gm, "[Invoked skill: $1]");
  return result.replace(/\n{3,}/g, "\n\n").trim();
}

function isGitAgentCommit(command: unknown): boolean {
  if (typeof command !== "string") return false;
  return command.includes("git-agent commit") || /\bgit-agent(?:\s+-\S+)*\s+--intent\b/.test(command);
}

export function isContextOrCommitEntry(entry: SessionEntry): boolean {
  if (!entry) return false;

  if (entry.type === "tool_call" || entry.type === "tool_result") {
    const name = (entry as { name?: string }).name;
    if (name === "session_context") return true;
    if (name === "bash") {
      const args =
        (entry as { args?: { command?: string }; input?: { command?: string } }).args ||
        (entry as { input?: { command?: string } }).input;
      if (args?.command && typeof args.command === "string" && isGitAgentCommit(args.command)) return true;
    }
  }

  if (entry.type === "message" && entry.message) {
    const msg = entry.message as { role?: string; content?: unknown; toolCalls?: unknown[] };
    if (Array.isArray(msg.toolCalls)) {
      for (const call of msg.toolCalls) {
        if (call && typeof call === "object") {
          const name = (call as { name?: string }).name;
          if (name === "session_context") return true;
          if (name === "bash") {
            const args =
              (call as { args?: { command?: string }; input?: { command?: string } }).args ||
              (call as { input?: { command?: string } }).input;
            if (args?.command && typeof args.command === "string" && isGitAgentCommit(args.command)) return true;
          }
        }
      }
    }

    if (Array.isArray(msg.content)) {
      for (const part of msg.content) {
        if (part && typeof part === "object") {
          const type = (part as { type?: string }).type;
          const name = (part as { name?: string }).name;
          if (type === "toolCall" || type === "tool_use" || type === "tool_result") {
            if (name === "session_context") return true;
            if (name === "bash") {
              const args =
                (part as { args?: { command?: string }; input?: { command?: string } }).args ||
                (part as { input?: { command?: string } }).input;
              if (args?.command && typeof args.command === "string" && isGitAgentCommit(args.command)) return true;
            }
          }
        }
      }
    }
  }
  return false;
}

function collectUserMessages(entries: readonly SessionEntry[]): ExtractedUserMessage[] {
  const messages: ExtractedUserMessage[] = [];
  for (let i = 0; i < entries.length; i += 1) {
    const entry = entries[i];
    if (entry.type !== "message" || entry.message?.role !== "user") continue;
    let text = extractText(entry.message.content).trim();
    if (!text || isInjectedProcedureMessage(text)) continue;
    text = collapseSkillInvocations(text);
    if (text) messages.push({ index: i, text });
  }
  return messages;
}

function limitContext(text: string): string {
  if (text.length <= MAX_CONTEXT_CHARS) return text;
  const suffix = "\n\n... (session context truncated)";
  return `${text.slice(0, MAX_CONTEXT_CHARS - suffix.length)}${suffix}`;
}

export function extractSessionContext(
  entries: readonly SessionEntry[],
  options: SessionContextOptions = {},
): SessionContextResult {
  const maxMessages = options.maxMessages ?? 15;
  const tailChars = options.tailChars ?? 600;
  const sinceLastCall = options.sinceLastCall ?? true;
  const allUserMessages = collectUserMessages(entries);

  if (allUserMessages.length === 0) {
    return { text: "No user messages found in the current session.", count: 0, deduplicated: false };
  }

  let selectedUserMessages = allUserMessages;
  let deduplicated = false;
  if (sinceLastCall) {
    const lastUserIndex = allUserMessages[allUserMessages.length - 1].index;
    let maxPreviousCutoffIndex = -1;
    for (let i = 0; i < lastUserIndex; i += 1) {
      if (isContextOrCommitEntry(entries[i])) maxPreviousCutoffIndex = i;
    }
    if (maxPreviousCutoffIndex >= 0) {
      const newMessages = allUserMessages.filter((message) => message.index > maxPreviousCutoffIndex);
      if (newMessages.length > 0) {
        selectedUserMessages = newMessages;
        deduplicated = true;
      }
    }
  }

  const recent = selectedUserMessages.slice(-maxMessages).map((message) => message.text);
  const lines: string[] = [
    "## Recent user requests (session context)",
    deduplicated
      ? `Showing ${recent.length} new user message(s) since last commit/context call — use these to build a detailed commit intent (what + why + verification):`
      : `Last ${recent.length} user message(s) — use these to build a detailed commit intent (what + why + verification):`,
    "",
  ];
  recent.forEach((message, index) => {
    const body = message.length > tailChars ? `${message.slice(0, tailChars)}... (truncated)` : message;
    lines.push(`### Request ${index + 1}`, body, "");
  });
  return { text: limitContext(lines.join("\n")), count: recent.length, deduplicated };
}
