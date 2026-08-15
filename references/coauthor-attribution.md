# Co-Author Attribution & Execution Ladder in git-agent

`git-agent` automatically handles model co-author attribution and commit generation.

## 1. Automatic Model Resolution

`git-agent` automatically inspects environment variables (`PI_MODEL`, `CLAUDE_CODE_MODEL`, `CODEX_MODEL`) to infer the active model identity and attach standard `Co-Authored-By` trailers. Reasoning tier & date suffixes (`-high`, `-thinking`, `-non-reasoning`, `-20241022`) are stripped while model variants (`Flash`, `Max`, `Pro`, `Opus`, `Sonnet`) are preserved.

> **Note**: Session model environment variables are used strictly for author attribution and never override the LLM inference model.

Manual `--co-author` flags may still be passed to override or append specific co-authors:
```bash
git-agent commit --intent "<intent>" --co-author "<co-author>"
```

To suppress co-author trailers entirely:
```bash
git-agent commit --no-attribution
```
