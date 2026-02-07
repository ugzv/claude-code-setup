---
description: Auto-fix all linting, formatting, and code quality issues
---

Clean up the codebase — fix everything that can be auto-fixed.

## Why This Exists

Developers accumulate lint warnings, formatting drift, and import clutter. Running fixers manually is tedious. This command detects what the project uses and runs everything in one pass.

**Goal:** Make CI pass. Not "code looks formatted" — actually passing the same checks CI runs.

**IMPORTANT: Use direct Bash calls, NOT Task/sub-agents.** Detection is just reading config files. Fixing is just running CLI tools. Neither needs agent overhead.

**Only run tools you confirmed exist.** Never guess CLI flags — if unsure about a flag, check `--help` or skip it. Don't assume directory paths exist (e.g., `web/`, `tests/`) — verify first.

## Step 1: Detect (direct Read/Bash calls)

Read these files to understand what the project uses. Do this with direct tool calls, not sub-agents:

- **CI config** (`.github/workflows/*.yml`, `.gitlab-ci.yml`) — what CI actually runs is the source of truth
- **Config files** (`pyproject.toml`, `package.json`, `composer.json`, `go.mod`, `Cargo.toml`) — what's installed
- **Lockfiles** (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `uv.lock`, `poetry.lock`, `composer.lock`) — which package manager is active
- **Tool configs** (`.eslintrc*`, `.prettierrc*`, `biome.json`, `ruff.toml`) — what's configured

**Priority:** CI config > project config > installed tools. If CI runs `ruff`, use `ruff` even if `black` is also installed.

## Step 2: Fix (parallel Bash calls)

Run all detected fixers simultaneously. Send them as parallel Bash tool calls in a single message:

- **Formatting** — prettier --write / black / gofmt -w / cargo fmt / pint (auto-fix mode)
- **Linting** — eslint --fix / ruff check --fix / goimports -w / cargo clippy --fix (auto-fix mode)
- **Lockfile sync** — pnpm install / npm install / yarn install / uv lock / poetry lock / composer update --lock (only if out of sync)
- **Import sorting** — isort / ruff's isort rules (if configured separately from linting)

Only run tools that exist in the project. Skip what doesn't apply.

## Step 3: Verify (parallel Bash calls)

Re-run tools in **check mode** to confirm fixes worked:

- Formatters with --check flags
- Linters without --fix
- Lockfile validation (--frozen-lockfile / --check variants)

This catches issues fixers couldn't resolve automatically — those need manual attention.

## Boundaries

**Do:**
- Remove unused imports and variables (prefix with `_` if removal is risky)
- Fix import ordering
- Fix formatting inconsistencies
- Fix auto-fixable lint errors

**Don't:**
- Change logic or behavior
- Remove code that might be dynamically used
- Create tool configs that don't exist — that's project setup, not fixing
- Commit — that's `/commit`

## After Fixing

Report concisely:
- Which tools ran
- Summary of changes (files touched, types of fixes)
- Any errors that couldn't be auto-fixed (these need manual attention)

$ARGUMENTS
