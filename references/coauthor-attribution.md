# Co-Author Attribution & Execution Ladder in git-agent

`git-agent` automatically handles model co-author attribution and commit generation.

## 1. Automatic Model Resolution

`git-agent` automatically inspects environment variables (`PI_MODEL`, `CLAUDE_CODE_MODEL`, `CODEX_MODEL`) to infer the active model identity and attach standard `Co-Authored-By` trailers. Reasoning tier & date suffixes (`-high`, `-thinking`, `-non-reasoning`, `-free`, `-20241022`) are stripped while model variants (`Flash`, `Max`, `Pro`, `Opus`, `Sonnet`) are preserved.

Provider mapping is not required: a session model that maps to no known provider (stealth aliases such as `openrouter/stealth/ox-alpha`) is still attributed as `Co-Authored-By: <Title Cased Model> <noreply@models.git-agent.dev>`, so `require_model_co_author` passes without manual flags. The inference model configured for message drafting (`model:` in `~/.config/git-agent/config.yml`) is never attributed.

> **Note**: Session model environment variables are used strictly for author attribution and never override the LLM inference model.

Manual `--co-author` flags may still be passed to override or append specific co-authors:
```bash
git-agent --intent "<intent>" --co-author "<co-author>"
```

There is no suppression flag: model co-author trailers are inferred automatically whenever a session-model environment variable (`PI_MODEL`, etc.) is set. To commit without them, clear those variables for the invocation.
