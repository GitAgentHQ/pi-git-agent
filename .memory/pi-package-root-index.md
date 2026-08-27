---
name: pi-package-root-index
description: pi-git-agent uses a root index.ts entrypoint like sibling pi-packages packages
type: decision
---

# Pi package root entrypoint

## Why
Pi package loading should use one explicit root entrypoint instead of pointing
Pi at the `extensions/` directory. This matches the sibling packages under
`/Users/FradSer/Developer/FradSer/pi-packages`, makes extension composition
explicit, and avoids directory discovery or ordering ambiguity.

## How to apply
Keep `package.json` configured with `pi.extensions: ["./index.ts"]` and ship
`index.ts` plus the composition implementation under `src/`. The root entry
should delegate to `src/index.ts`, which registers each extension exactly once
in deterministic order. Include the entrypoint files in the package `files`
allowlist and keep README file trees accurate.

## Related
- [[skill-stub-symlink-to-repo]]
