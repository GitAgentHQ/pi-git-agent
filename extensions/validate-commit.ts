import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { isToolCallEventType } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, _ctx) => {
    if (isToolCallEventType("bash", event)) {
      const cmd = event.input.command || "";
      if (!cmd.includes("git")) return;

      // Command-position anchors
      const pos = "(?:^|[;&|\\n])\\s*(?:[A-Za-z_][A-Za-z_0-9]*=[^\\s]*\\s+)*";
      const end = "(?:[;&|\\s]|$)";

      const reCommit = new RegExp(`${pos}git\\s+commit${end}`);
      const reAdd = new RegExp(`${pos}git\\s+add${end}`);
      const reAgent = new RegExp(`${pos}git-agent(?:\\s|$)`);

      if (reCommit.test(cmd)) {
        return {
          block: true,
          reason:
            'Raw git commit is blocked. Commit with git-agent instead: gather session context (session_context tool), then run git-agent --intent "<intent assembled from that context>". It stages, splits into atomic commits, and validates.',
        };
      }

      if (reAdd.test(cmd) && !reAgent.test(cmd)) {
        return {
          block: true,
          reason:
            'Raw git add is blocked. For folder-scoped staging, chain it with git-agent: git add <path> && git-agent --no-stage --intent "<intent>"',
        };
      }
    }
  });
}
