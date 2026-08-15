# git-agent — Commit and push procedure

> **Inline procedure.** Embedded verbatim into the follow-up message by the
> `/git-agent` menu ("Commit and push") via `pi.sendUserMessage` — it is not a
> skill and the menu delivers it inline. `{{PKG_DIR}}` is
> substituted with the package dir at send time.

Create an atomic conventional commit with `git-agent` and push it to the remote.

CRITICAL:
- Do NOT run `git status`, `git diff`, `git log`, or raw `git add`/`git commit` before `git-agent commit`.
- Fully delegate staging, multi-commit splitting (up to 5 atomic commits), auto-scope mining, active model attribution inference (`PI_MODEL`, etc.), and hook validation/retry directly to `git-agent`.
- Execute `git-agent commit` directly.

## Execution

1. **Extract session context first.** Call the `session_context` tool to pull recent user requests and decisions from the current session. (If the tool is unavailable, reconstruct the context from the conversation.)
2. **Build a detailed intent from that context.** The intent is the PRIMARY DIRECTIVE for the commit message generator — the richer it is, the more accurate the message. Cover:
   - **What** the user asked for (their words, not paraphrased into a tagline)
   - **Why** the change exists (decisions, rationale, rejected alternatives)
   - **How** it was verified (tests run, commands executed, quality gates)
   Write 2–4 sentences. Do not compress to a single sentence.
3. Pass `--co-author "<co-author>"` if explicitly requested by the user. (Active session models are inferred automatically from environment variables).
4. Run primary commit command:
   ```bash
   git-agent commit --intent "<intent>"
   ```
5. On auth error (401 / missing key), retry with `--free`:
   ```bash
   git-agent commit --free --intent "<intent>"
   ```
6. On planner timeout (`LLM planner timed out`), raise the budget via `git-agent config set request_timeout 5m` or cap diff with `--max-diff-lines <n>` / `--max-diff-bytes <n>`.
7. Push to remote repository:
   ```bash
   git push
   ```
   (If upstream is not set, use `git push -u origin <branch>`).

CLI Reference: `{{PKG_DIR}}/references/cli.md`
