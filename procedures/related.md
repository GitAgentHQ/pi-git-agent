# git-agent — Related files & tests procedure

> **Inline procedure.** Embedded verbatim into the follow-up message by the
> `/git-agent` menu ("Related files & tests") via `pi.sendUserMessage` — it is
> not a skill and the menu delivers it inline. `{{PKG_DIR}}` is
> substituted with the package dir at send time.

Mine git history to find files and test suites that historically change
together with the given target files (co-change relations). Language-agnostic,
offline, and zero API cost.

## Recommended Coding Agent Loop

1. `git-agent related <files...>` — query historical blast radius and the `commits` array explaining why files move together (temporal context).
2. Pair with Grep / Read / File search — inspect exact symbols and current structure (spatial context).
3. `git-agent related <files...> --tests` — query which tests to run before concluding work.

## Execution

Execute `git-agent related` to query co-change relations (offline and read-only; auto-indexes on first run):

1. **Find coupled files given seeds**:
   ```bash
   git-agent related <file-paths...>
   ```
2. **Find coupled files from current working tree changes**:
   ```bash
   git-agent related
   ```
3. **Find related tests**:
   ```bash
   git-agent related --tests <file-paths...>
   ```
4. **Structured JSON output for programmatic evaluation**:
   ```bash
   git-agent related -o json <file-paths...>
   ```

Report the historically coupled files and tests to guide code edits and test
suite execution.

CLI Reference: `{{PKG_DIR}}/references/cli.md`
