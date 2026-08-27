# Git Agent for Pi ![](https://img.shields.io/badge/runtime-Pi-blue)

[![Version](https://img.shields.io/npm/v/pi-git-agent)](https://www.npmjs.com/package/pi-git-agent) [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**English** | [简体中文](README.zh-CN.md)

A Pi coding-agent package that turns `git-agent` into a native `/git-agent` command menu: atomic AI commits, co-change relations, and a guard that blocks raw `git commit` in favor of the atomic-commit workflow. No skill surface.

## Overview

- **Atomic Commits**: splits staged changes into up to 5 logically distinct commits with AI-generated conventional messages (`git-agent commit`).
- **Co-change Relations**: mined from git history to reveal files and test suites that change together (`git-agent related`).
- **Native Extension Guard**: `extensions/validate-commit.ts` intercepts raw `git commit` tool calls, locally embeds bounded session context in the block reason, and points the agent directly at `git-agent --intent`. Normal `git add` calls remain allowed.
- **Session-Grounded Commits**: `extensions/session-context.ts` exposes the `session_context` tool, which reads the live session entries so commit intents are built from what the user actually asked for, not a compressed one-liner.
- **Automatic Model Identity Resolution**: `git-agent` auto-detects agent environment variables (`PI_MODEL`, `CLAUDE_CODE_MODEL`, `CODEX_MODEL`, `MODEL`), so no manual co-author flags are needed.

## Usage

Type `/git-agent` to open the native menu:

```
git-agent workflows:
❯ 1. Commit changes        (procedures/commit.md)
  2. Commit and push       (procedures/commit-and-push.md)
  3. Init / optimize       (procedures/init.md)
  4. Related files & tests (procedures/related.md)
```

Or pass a workflow keyword to skip the menu:

```bash
/git-agent commit                # commit with intent built from session context
/git-agent commit --co-author "Alice <a@example.com>"
/git-agent related src/foo.ts    # co-change for specific files
/git-agent related --tests src/
/git-agent init                  # regenerate scopes + .gitignore
```

Each selection embeds the full procedure (`procedures/*.md`) into a follow-up message via `pi.sendUserMessage`. Commit enforcement stays in the post-tool harness guard rather than a system-prompt guidance injection. When raw `git commit` is blocked, the guard locally extracts bounded session context so the agent can invoke `git-agent --intent` without a separate `session_context` round.

## Installation

```bash
# published
pi install npm:pi-git-agent
# or from this repo: pi install /path/to/git-agent/pi-git-agent
```

Requires the `git-agent` CLI on PATH (built from the sibling `git-agent-cli/` directory in this repo).

## Files

```
pi-git-agent/
├── extensions/
│   ├── menu.ts               # /git-agent command menu
│   ├── session-context.ts    # session_context tool (intent source for commits)
│   ├── validate-commit.ts    # blocks raw git commit and embeds session context
│   └── lib/session-context-core.ts # shared local context extraction
├── procedures/
│   ├── commit.md             # atomic AI commit workflow
│   ├── commit-and-push.md    # commit + push workflow
│   ├── init.md               # scope/.gitignore regeneration
│   └── related.md            # co-change queries
└── references/
    ├── cli.md                # git-agent CLI reference
    └── coauthor-attribution.md
```

## License

[MIT](LICENSE)
