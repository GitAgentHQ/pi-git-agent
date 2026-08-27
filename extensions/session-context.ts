import { keyHint, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Container, Text, truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";
import { eventToolLifecycle, renderToolLifecycle, safeDisplayText } from "@fradser/pi-kit";
import { Type } from "typebox";
import {
  collapseSkillInvocations,
  extractSessionContext,
  type SessionEntry,
} from "./lib/session-context-core";

export { collapseSkillInvocations, extractSessionContext } from "./lib/session-context-core";

export const SessionContextParams = Type.Object({
  maxMessages: Type.Optional(
    Type.Integer({
      minimum: 1,
      maximum: 50,
      description: "Max recent user messages to include (default: 15)",
    }),
  ),
  tailChars: Type.Optional(
    Type.Integer({
      minimum: 50,
      maximum: 4000,
      description: "Per-message character cap (default: 600)",
    }),
  ),
  sinceLastCall: Type.Optional(
    Type.Boolean({
      description:
        "Only include user messages since the last session_context call or commit (default: true)",
    }),
  ),
});

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "session_context",
    label: "Session Context",
    description: [
      "Extract recent user requests and decisions from the current session.",
      "Primary value: after context compaction, earlier requests are no longer in the model window - this recovers them.",
      "Each call also marks the commit boundary; later calls only return messages since the last commit or call.",
      "Use before committing: build the commit intent from this context instead of a one-line summary,",
      "so the commit message reflects what the user asked for and why.",
    ].join(" "),
    promptSnippet: "Extract recent user requests from the session to build a commit intent",
    promptGuidelines: [
      "Use session_context before committing to ground the commit intent in what the user actually asked for, not a one-line summary.",
    ],
    parameters: SessionContextParams,
    renderShell: "self",
    renderCall: () => new Container(),
    renderResult(result, { expanded }, theme, context) {
      const text = result.content.find((part) => part.type === "text")?.text ?? "";
      if (context.isError) {
        return new Text(theme.fg("error", firstNonEmptyLine(text)), 0, 0);
      }

      const details = result.details as { count?: number; deduplicated?: boolean } | undefined;
      const subject = contextSubject(details?.count ?? 0, details?.deduplicated ?? false);
      const bodyLines = safeDisplayText(text).split("\n").filter((line) => line.trim()).slice(0, 50);
      const spec = eventToolLifecycle("context", subject, { label: "gathered", details: bodyLines });
      return {
        invalidate: () => {},
        render: (width: number) =>
          renderToolLifecycle(spec, {
            width,
            expanded,
            expandHint: keyHint("app.tools.expand", "to expand"),
            theme,
            fit: truncateToWidth,
            visibleWidth,
          }),
      };
    },

    async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
      const entries = (ctx.sessionManager.getEntries() as SessionEntry[]) ?? [];
      const result = extractSessionContext(entries, params);
      return {
        content: [{ type: "text", text: result.text }],
        details: { count: result.count, deduplicated: result.deduplicated },
      };
    },
  });
}

function firstNonEmptyLine(text: string): string {
  return safeDisplayText(text).split("\n").find((line) => line.trim())?.trim() || "Tool failed.";
}

function contextSubject(count: number, deduplicated: boolean): string {
  if (count === 0) return "no user requests";
  const requests = `${count} request${count === 1 ? "" : "s"}`;
  return deduplicated ? `${requests} since last commit` : `${requests} in session`;
}
