---
name: github-ci-npm-publishing
description: pi-git-agent package must be published via GitHub Actions CI workflow on push to main, not manual local pnpm/npm publish
type: project
---

# GitHub CI npm Publishing Workflow

## Why
`pi-git-agent` uses GitHub Actions CI (`.github/workflows/publish.yml`) to automatically publish new releases to npm upon version bump when pushing to the `main` branch. Local publishing fails due to 2FA / OIDC trusted publishing requirements and bypasses automated provenance checks.

## How to apply
1. Bump the version in `package.json`.
2. Commit with `git-agent commit`.
3. Push to `main` via `git push origin main`.
4. GitHub Actions CI detects the version change against npm registry and publishes automatically with provenance. Do NOT run local `pnpm publish` or `npm publish`.

## npm OIDC Trusted Publishing CLI Setup (`npm trust`)
When setting up or updating trusted publishing for GitHub Actions without using the web UI, use npm's built-in `npm trust` CLI command:
```bash
# List existing trust relationships
npm trust list <package-name>

# Add / update trusted publisher for GitHub Actions
npm trust github <package-name> --file <workflow-file.yml> --repo <owner/repo> --allow-publish -y

# Example for pi-git-agent
npm trust github pi-git-agent --file publish.yml --repo GitAgentHQ/pi-git-agent --allow-publish -y

# Revoke old / stale trust configuration
npm trust revoke <package-name> --id=<trust-id>
```
*Note*: `npm trust` requires `npm >= 11.5.0` (Node 22+) and will prompt for a 2FA OTP / browser auth to authorize the security setting change.

## Related
- [[.github/workflows/publish.yml]]
