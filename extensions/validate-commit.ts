import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { isToolCallEventType } from "@earendil-works/pi-coding-agent";
import { extractSessionContext, MAX_CONTEXT_CHARS, type SessionEntry } from "./lib/session-context-core";

function rawGitCommit(command: string): boolean {
  const pos = "(?:^|[;&|\\n])\\s*(?:[A-Za-z_][A-Za-z_0-9]*=[^\\s]*\\s+)*";
  const end = "(?:[;&|\\s]|$)";
  return new RegExp(`${pos}git\\s+commit${end}`).test(command);
}

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (!isToolCallEventType("bash", event)) return;
    const command = event.input.command || "";
    if (!rawGitCommit(command)) return;

    const context = extractSessionContext(ctx.sessionManager.getEntries() as SessionEntry[]).text;
    return {
      block: true,
      reason: [
        "Raw git commit is blocked.",
        "Use the locally prepared session context below to build the intent, then run git-agent --intent \"<intent>\" directly.",
        "The command will stage changes, split atomic commits, generate messages, and validate hooks.",
        `\n${context.slice(0, MAX_CONTEXT_CHARS)}`,
      ].join(" "),
    };
  });
}
