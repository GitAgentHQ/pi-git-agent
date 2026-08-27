"""Tests for the pi-git-agent pi package.

Covers the native /git-agent command menu (no skill surface — same pattern as
@fradser/memory), the commit guard extension (extensions/validate-commit.ts),
and the session_context tool (extensions/session-context.ts).
"""
from __future__ import annotations

import json
import os
import unittest

GA_PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tokens that must never reappear outside tests. Built by concatenation so this
# file itself does not contain the forbidden literals.
HOOK_SCRIPT_NAME = "validate-commit-" + "pretool"
HOOK_EVENT = "Pre" + "ToolUse"


class TestGitAgentManifest(unittest.TestCase):
    def test_package_json_validity(self):
        """package.json is a valid Pi package manifest — extensions only, no skills."""
        with open(os.path.join(GA_PKG_DIR, "package.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["name"], "pi-git-agent")
        self.assertIn("pi-package", data.get("keywords", []))
        self.assertEqual(data.get("repository", {}).get("url"), "https://github.com/GitAgentHQ/pi-git-agent.git")
        self.assertNotIn("skills", data["pi"], "git-agent uses the /git-agent menu, not skills")
        self.assertIn("extensions", data["pi"])
        self.assertEqual(data["pi"]["extensions"], ["./index.ts"])
        self.assertIn("index.ts", data.get("files", []))
        self.assertIn("procedures", data.get("files", []))
        self.assertIn("@earendil-works/pi-coding-agent", data.get("peerDependencies", {}))
        self.assertIn("typebox", data.get("peerDependencies", {}))
        self.assertEqual(data.get("dependencies", {}).get("@fradser/pi-kit"), "^0.4.1")
        self.assertNotIn("hooks", data.get("files", []))
        self.assertNotIn("pretool-hook", data.get("keywords", []))


class TestGitAgentMenu(unittest.TestCase):
    def test_root_index_delegates_to_src_entrypoint(self):
        """The package root re-exports a src entrypoint, like pi-packages."""
        index_path = os.path.join(GA_PKG_DIR, "index.ts")
        self.assertTrue(os.path.exists(index_path), "index.ts is missing")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content.strip(), 'export { default } from "./src/index.ts";')

        src_path = os.path.join(GA_PKG_DIR, "src", "index.ts")
        self.assertTrue(os.path.exists(src_path), "src/index.ts is missing")
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('from "../extensions/menu.ts"', content)
        self.assertIn('from "../extensions/session-context.ts"', content)
        self.assertIn('from "../extensions/validate-commit.ts"', content)
        self.assertIn("export default", content)
        self.assertIn("registerMenu(pi)", content)
        self.assertIn("registerSessionContext(pi)", content)
        self.assertIn("registerValidateCommit(pi)", content)

    def test_skills_directory_removed(self):
        """The skill surface is gone — workflows live in procedures/ behind the /git-agent menu."""
        self.assertFalse(os.path.exists(os.path.join(GA_PKG_DIR, "skills")), "skills/ must be removed")

    def test_menu_extension_registers_command(self):
        """extensions/menu.ts registers the /git-agent command with a select menu."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "menu.ts")
        self.assertTrue(os.path.exists(ext_path), "extensions/menu.ts is missing")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('registerCommand("git-agent"', content)
        self.assertIn("ctx.ui.select", content)
        self.assertIn("sendUserMessage", content)
        self.assertIn("deliverAs", content)
        self.assertIn("{{PKG_DIR}}", content)

    def test_menu_covers_all_procedures(self):
        """Every menu item has a matching procedure file under procedures/."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "menu.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        proc_dir = os.path.join(GA_PKG_DIR, "procedures")
        for name in ("commit.md", "commit-and-push.md", "init.md", "related.md"):
            self.assertIn(name, content, f"menu must reference {name}")
            self.assertTrue(os.path.exists(os.path.join(proc_dir, name)), f"{name} missing")

    def test_procedures_use_pkg_dir_placeholder(self):
        """Procedures resolve reference paths through the {{PKG_DIR}} placeholder."""
        for name in ("commit.md", "commit-and-push.md", "init.md", "related.md"):
            with open(os.path.join(GA_PKG_DIR, "procedures", name), "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("{{PKG_DIR}}", content, f"{name} must use {{{{PKG_DIR}}}}")
            self.assertIn("references/cli.md", content, f"{name} must point at the CLI reference")

    def test_no_skill_invocations_in_procedures(self):
        """Procedures never invoke themselves as /skill:... — the menu delivers them inline."""
        for name in ("commit.md", "commit-and-push.md", "init.md", "related.md"):
            with open(os.path.join(GA_PKG_DIR, "procedures", name), "r", encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("/skill:", content, f"{name} must not reference /skill:")


class TestNoClaudeHookRegression(unittest.TestCase):
    def test_hooks_directory_removed(self):
        """The Claude Code pre-tool hook sidecar must be gone."""
        self.assertFalse(
            os.path.exists(os.path.join(GA_PKG_DIR, "hooks")),
            "hooks/ must be removed — pi has no hook system; the extension covers the guard",
        )

    def test_no_pretool_references(self):
        """Nothing outside tests may reference the removed hook."""
        forbidden = (HOOK_SCRIPT_NAME, HOOK_EVENT)
        for root, _, files in os.walk(GA_PKG_DIR):
            if "__pycache__" in root or "node_modules" in root or "tests" in root:
                continue
            for file in files:
                if not file.endswith((".md", ".json", ".ts", ".py", ".sh")):
                    continue
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for token in forbidden:
                    self.assertNotIn(token, content, f"Forbidden reference '{token}' in {filepath}")


class TestValidateCommitExtension(unittest.TestCase):
    def test_extension_registers_native_guard(self):
        """extensions/validate-commit.ts intercepts bash tool calls natively."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "validate-commit.ts")
        self.assertTrue(os.path.exists(ext_path))
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('pi.on("tool_call"', content)
        self.assertIn('isToolCallEventType("bash", event)', content)
        # Denies raw git commit, but allows raw git add
        self.assertIn("git\\\\s+commit", content)
        self.assertNotIn("git\\\\s+add", content)
        self.assertIn("block: true", content)

    def test_guard_reason_requires_bare_git_agent_intent(self):
        """The guard must point straight at bare git-agent --intent, not the menu."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "validate-commit.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("git-agent --intent", content)
        self.assertIn("session context", content)
        self.assertIn("extractSessionContext", content)
        self.assertIn("MAX_CONTEXT_CHARS", content)
        self.assertNotIn("session_context tool", content)
        self.assertNotIn("/git-agent menu", content)
        self.assertNotIn("Use the /commit skill", content)
        self.assertNotIn("git add", content)


    def test_guard_uses_bounded_shared_context_extractor(self):
        """The post-tool guard embeds the same bounded local context as the tool."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "validate-commit.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('from "./lib/session-context-core"', content)
        self.assertIn("extractSessionContext", content)
        self.assertIn("MAX_CONTEXT_CHARS", content)
        self.assertIn("getEntries", content)
        self.assertIn("getEntries() as SessionEntry[]", content)


class TestSessionContextExtension(unittest.TestCase):
    def test_extension_exists_and_registers_tool(self):
        """extensions/session-context.ts registers a session_context tool that reads session entries."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "session-context.ts")
        self.assertTrue(os.path.exists(ext_path), "extensions/session-context.ts is missing")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("session_context", content)
        self.assertIn("registerTool", content)
        self.assertIn("getEntries", content)
        core_path = os.path.join(GA_PKG_DIR, "extensions", "lib", "session-context-core.ts")
        with open(core_path, "r", encoding="utf-8") as f:
            core_content = f.read()
        self.assertIn('"message"', core_content)
        self.assertIn("sinceLastCall", content)
        self.assertIn("isContextOrCommitEntry", core_content)
        self.assertIn("isInjectedProcedureMessage", core_content)
        self.assertIn("promptSnippet", content)
        self.assertIn("promptGuidelines", content)
        self.assertIn("session-context-core", content)

    def test_session_context_excludes_injected_menu_procedures(self):
        """session_context must skip menu-injected procedure messages (Run the "..." workflow.),
        which are git-agent's own commands, not user requests."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "lib", "session-context-core.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("isInjectedProcedureMessage", content)
        self.assertIn("extractSessionContext", content)
        self.assertIn('Run the "', content)
        self.assertIn("workflow", content)

    def test_commit_boundary_recognizes_bare_invocation(self):
        """The commit-boundary check must match bare `git-agent --intent ...` as well as
        the legacy `git-agent commit` subcommand form."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "lib", "session-context-core.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("isGitAgentCommit", content)
        self.assertIn('--intent', content)

    def test_session_context_uses_monitor_style_rendering(self):
        """session_context owns one compact pi-kit lifecycle row and expands details."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "session-context.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('renderShell: "self"', content)
        self.assertIn("renderCall: () => new Container()", content)
        self.assertIn("renderResult(result, { expanded }, theme, context)", content)
        # Shared band channel, not a hand-rolled box or the retired label fn.
        self.assertIn("eventToolLifecycle(", content)
        self.assertIn("renderToolLifecycle(spec,", content)
        self.assertIn('label: "gathered"', content)
        self.assertIn('keyHint("app.tools.expand", "to expand")', content)
        self.assertIn("expanded", content)
        self.assertIn('"no user requests"', content)
        self.assertNotIn("formatToolEventLabel", content)
        self.assertNotIn("new Box", content)
        self.assertNotIn('renderShell: "default"', content)
        self.assertNotIn('renderShell: "default"', content)

    def test_session_context_collapses_skill_invocations(self):
        """session_context must collapse expanded skill prompt blocks into concise [Invoked skill: ...]
        indicators, preserving user arguments while stripping massive skill prompt bodies."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "session-context.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        core_path = os.path.join(GA_PKG_DIR, "extensions", "lib", "session-context-core.ts")
        with open(core_path, "r", encoding="utf-8") as f:
            core_content = f.read()
        self.assertIn("<skill", core_content)
        self.assertIn("[Invoked skill:", core_content)

    def test_collapse_skill_invocations_execution(self):
        """Test collapseSkillInvocations logic against various skill invocation inputs."""
        import subprocess

        js_code = """
        const { collapseSkillInvocations } = require('./extensions/session-context.ts');
        """
        # We can test with tsx or node with a small script that tests the collapse function
        test_script = """
        const fs = require('fs');
        const content = fs.readFileSync('./extensions/lib/session-context-core.ts', 'utf-8');
        // Extract the collapseSkillInvocations function body or compile on the fly
        const funcMatch = content.match(/export function collapseSkillInvocations[\\s\\S]*?\\n}/);
        if (!funcMatch) {
            console.error('collapseSkillInvocations not found');
            process.exit(1);
        }
        const fn = new Function('text', funcMatch[0].replace('export function collapseSkillInvocations(text: string): string', '').replace(/^[^{]*{/, '').slice(0, -1));

        // Test 1: Expanded skill with arguments
        const input1 = '<skill name="web-perf" location="/path/SKILL.md">\\n# Prompt\\nLots of instructions...\\n</skill>\\n\\naudit the site';
        const res1 = fn(input1);
        if (res1 !== '[Invoked skill: web-perf]\\n\\naudit the site') {
            console.error('Test 1 failed:', JSON.stringify(res1));
            process.exit(1);
        }

        // Test 2: Expanded skill without arguments
        const input2 = '<skill name="commit" location="/path/SKILL.md">\\n# Prompt\\nCommit instructions...\\n</skill>';
        const res2 = fn(input2);
        if (res2 !== '[Invoked skill: commit]') {
            console.error('Test 2 failed:', JSON.stringify(res2));
            process.exit(1);
        }

        // Test 3: Raw /skill: command
        const input3 = '/skill:patent-architect foo bar';
        const res3 = fn(input3);
        if (res3 !== '[Invoked skill: patent-architect] foo bar') {
            console.error('Test 3 failed:', JSON.stringify(res3));
            process.exit(1);
        }

        // Test 4: Normal message untouched
        const input4 = 'Please optimize session_context for skills';
        const res4 = fn(input4);
        if (res4 !== 'Please optimize session_context for skills') {
            console.error('Test 4 failed:', JSON.stringify(res4));
            process.exit(1);
        }

        console.log('OK');
        """
        proc = subprocess.run(
            ["node", "-e", test_script],
            cwd=GA_PKG_DIR,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Node script failed: {proc.stderr}\n{proc.stdout}")

    def test_commit_procedure_prioritizes_session_context(self):
        """commit procedure must instruct building the intent from session context, not a one-liner."""
        proc = os.path.join(GA_PKG_DIR, "procedures", "commit.md")
        with open(proc, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("session_context", content)
        self.assertIn("intent", content)
        self.assertIn("session", content)

    def test_commit_and_push_procedure_prioritizes_session_context(self):
        """commit-and-push procedure must also build the intent from session context."""
        proc = os.path.join(GA_PKG_DIR, "procedures", "commit-and-push.md")
        with open(proc, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("session_context", content)
        self.assertIn("intent", content)

    def test_commit_procedure_no_longer_asks_for_one_sentence(self):
        """The one-sentence-intent instruction must be gone in favor of session-driven context."""
        proc = os.path.join(GA_PKG_DIR, "procedures", "commit.md")
        with open(proc, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("one-sentence", content)
        self.assertNotIn("concise one-sentence", content)

    def test_procedures_delegate_fully_to_git_agent(self):
        """commit procedures must explicitly instruct full delegation to git-agent."""
        for name in ("commit.md", "commit-and-push.md"):
            proc = os.path.join(GA_PKG_DIR, "procedures", name)
            with open(proc, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("CRITICAL:", content)
            self.assertIn("delegate", content.lower())
            self.assertIn("git-agent --intent", content)
            self.assertNotIn("git-agent commit", content)

    def test_related_procedure_covers_agent_loop(self):
        """related procedure must document the coding agent loop and --tests."""
        proc = os.path.join(GA_PKG_DIR, "procedures", "related.md")
        with open(proc, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("--tests", content)
        self.assertIn("Loop", content)

    def test_menu_does_not_inject_before_agent_start_guidance(self):
        """Git guidance is provided by the post-tool harness, not before_agent_start."""
        ext_path = os.path.join(GA_PKG_DIR, "extensions", "menu.ts")
        with open(ext_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn('pi.on("before_agent_start"', content)
        self.assertNotIn("Git Intelligence & Co-Change Analysis", content)
        self.assertNotIn("git-agent related", content)

    def test_cli_reference_config_precedence(self):
        """references/cli.md must reflect correct config precedence and session attribution distinction."""
        ref = os.path.join(GA_PKG_DIR, "references", "cli.md")
        with open(ref, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Configuration Precedence", content)
        self.assertIn("Local Git Config", content)
        self.assertIn("set the inference", content.lower())
        self.assertIn("Co-Authored-By", content)


if __name__ == "__main__":
    unittest.main()
