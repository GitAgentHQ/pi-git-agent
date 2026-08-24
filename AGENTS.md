# Repository Guidelines

## Project Structure & Module Organization

Pi coding-agent package that exposes git-agent workflows as a native `/git-agent` menu. `extensions/` holds the three entry points: `menu.ts` (command menu plus system-prompt guidance injection), `session-context.ts` (the `session_context` tool feeding commit intents), and `validate-commit.ts` (the tool-call guard blocking raw `git add`/`git commit`). `procedures/*.md` are inline workflow documents embedded verbatim into follow-up messages; `references/` are appendix docs linked from procedures via `{{PKG_DIR}}`. `features/git-agent-menu.feature` holds the Gherkin behavior specs; `tests/test_git_agent_extension.py` asserts source-level contracts. There is no shared pi-kit runtime dependency here — peer deps are `@earendil-works/pi-coding-agent` and `typebox`.

## Build/Test/Development Commands

```bash
CI=true pnpm install                    # non-TTY shells skip the modules-purge prompt
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

The installed guard blocks any bash tool call whose text matches command-position `git add` / `git commit` — including snippets inside heredocs or `node -e` strings. When simulating guard regexes, compose those literals by concatenation (`"git " + "add"`). Commits go through bare `git-agent --intent "<intent built via session_context>"`, never raw git plumbing.

## Commit & Pull Request Guidelines

Conventional commits: lowercase `type(scope): description`, title ≤50 characters; observed types include `feat`, `fix`, `docs`, `test`, `chore`, `ci`; scopes mirror component directories (`extensions`, `features`, `procedures`, `references`, `tests`). npm publishing runs only on `v*` release tags (`.github/workflows/publish.yml`, OIDC trusted publishing); cut releases with a `chore: release version X.Y.Z` commit.
