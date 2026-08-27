import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import registerMenu from "../extensions/menu.ts";
import registerSessionContext from "../extensions/session-context.ts";
import registerValidateCommit from "../extensions/validate-commit.ts";

export default function gitAgentExtension(pi: ExtensionAPI): void {
  registerMenu(pi);
  registerSessionContext(pi);
  registerValidateCommit(pi);
}
