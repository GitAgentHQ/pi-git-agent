# Repository Guidelines

## Project Structure & Module Organization

Pi coding-agent package that exposes git-agent workflows as a native `/git-agent` menu. `index.ts` re-exports `src/index.ts`, which composes the package extensions. `extensions/` holds the three implementation entry points: `menu.ts` (command menu), `session-context.ts` (the `session_context` tool feeding commit intents), and `validate-commit.ts` (the post-tool guard blocking raw `git commit`, embedding bounded local session context; `git add` remains allowed). Shared extraction lives in `extensions/lib/session-context-core.ts`. `procedures/*.md` are inline workflow documents embedded verbatim into follow-up messages; `references/` are appendix docs linked from procedures via `{{PKG_DIR}}`. `features/git-agent-menu.feature` holds the Gherkin behavior specs; `tests/test_git_agent_extension.py` asserts source-level contracts. The extension uses the shared `@fradser/pi-kit` runtime for monitor-style lifecycle rows. `@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`, and `typebox` remain peer dependencies.

## Build/Test/Development Commands

```bash
pnpm install                              # package.json has no scripts; pnpm-lock.yaml is the lockfile
./node_modules/.bin/tsc --noEmit        # typecheck (strict, noEmit; package.json has no scripts)
python3 -m pytest tests/ -q             # full test suite
pi install /path/to/pi-git-agent        # load into pi (or: npm:pi-git-agent)
```

The `git-agent` CLI must be on PATH (built from the sibling `git-agent-cli/` repo).

## Coding Style & Naming Conventions

TypeScript ES2022 modules, strict mode, 2-space indent, no emojis. Extensions export `default function (pi: ExtensionAPI)` and register through `pi.registerCommand` / `registerTool` / `pi.on`. Procedures use imperative CRITICAL-style directives with fenced bash blocks.

## Testing Guidelines

BDD order is mandatory: change `features/git-agent-menu.feature` scenarios first, then make assertions in `tests/test_git_agent_extension.py` fail (RED) — they read source files as text and assert contract strings, so wording changes must stay synchronized between source and tests — then implement to GREEN.

## Agent-Specific Instructions

The installed guard blocks bash tool calls whose text matches command-position `git commit`, including snippets inside heredocs or `node -e` strings. It does not block `git add`. When blocking, it locally extracts bounded session context and tells the agent to run bare `git-agent --intent` directly, avoiding a separate `session_context` round. Commits never use raw Git plumbing.

## Commit & Pull Request Guidelines

Conventional commits: lowercase `type(scope): description`, title ≤50 characters; observed types include `feat`, `fix`, `docs`, `test`, `chore`, `ci`; scopes mirror component directories (`extensions`, `features`, `procedures`, `references`, `tests`). npm publishing runs only on `v*` release tags (`.github/workflows/publish.yml`, OIDC trusted publishing); cut releases with a `chore: release version X.Y.Z` commit.
