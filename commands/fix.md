---
description: Auto-fix all linting, formatting, and code quality issues
---

Clean up the codebase - fix everything that can be auto-fixed.

## CI Config is Source of Truth

**Check CI first.** Parse `.github/workflows/*.yml` to see what tools CI actually runs. Your goal is CI passing, not just "code looks formatted."

## Parallel Detection Phase

**Spawn all detectors at once:**

```
┌────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                     │
├────────────────────────────────────────────────────────┤
│  1. ci-parser                                          │
│     → Parse .github/workflows/*.yml                    │
│     → Return: {"tools": [...], "commands": [...]}      │
│                                                        │
│  2. python-detector                                    │
│     → Check pyproject.toml for ruff/black configs      │
│     → Return: {"available": [...], "configured": [...]}│
│                                                        │
│  3. js-detector                                        │
│     → Check package.json, eslint/prettier configs      │
│     → Return: {"available": [...], "configured": [...]}│
│                                                        │
│  4. lockfile-checker                                   │
│     → Verify lockfile matches manifest                 │
│     → Return: {"in_sync": bool, "issues": [...]}       │
└────────────────────────────────────────────────────────┘
```

## Detection Priority

1. **CI config** - what actually runs in CI
2. **pyproject.toml / package.json** - fallback
3. **Installed tools** - last resort

## Apply Fixes (Sequential)

Run fixes in correct order: **lint first** (finds issues), then **format** (may change what lint found).

### Python
```bash
# Match what CI uses
ruff check --fix . && ruff format .  # or
black . && isort .                    # if CI uses these
```

### JavaScript/TypeScript
```bash
npx eslint --fix .
npx prettier --write .
# or: npx biome check --apply .
```

### Go
```bash
gofmt -w . && goimports -w . && go mod tidy
```

### Rust
```bash
cargo fmt && cargo clippy --fix
```

### PHP/Laravel
```bash
./vendor/bin/pint                    # Laravel Pint (official style fixer)
./vendor/bin/php-cs-fixer fix .      # or PHP-CS-Fixer if not Laravel
./vendor/bin/phpstan analyse         # static analysis (won't auto-fix, but reports issues)
```

### WordPress
```bash
./vendor/bin/phpcbf --standard=WordPress .   # auto-fix WP coding standards
./vendor/bin/phpcs --standard=WordPress .    # lint (reports remaining issues)
npm run build                                 # theme/plugin asset compilation if present
```

## Lockfile Sync

**Critical** - out-of-sync lockfiles pass locally but fail CI.

| Lockfile | Check | Fix |
|----------|-------|-----|
| `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` | `pnpm install` |
| `package-lock.json` | `npm ci` | `npm install` |
| `yarn.lock` | `yarn install --frozen-lockfile` | `yarn install` |
| `uv.lock` | `uv lock --check` | `uv lock` |
| `poetry.lock` | `poetry check --lock` | `poetry lock` |
| `composer.lock` | `composer validate` | `composer update --lock` |

## Tools Need Configs

If a tool is installed but unconfigured, create an appropriate config for the project type before running. Match existing project style (line length, quote style) by sampling files.

## What to Fix

- Unused imports - remove
- Unused variables - remove or prefix with `_`
- Import sorting - consistent ordering
- Formatting - consistent style
- Simple lint errors - auto-fixable issues

## What NOT to Do

- Don't change logic or behavior
- Don't remove code that might be dynamically used
- Don't commit - that's `/commit`

## After Fixing

Report: which tools ran, summary of changes, any errors that couldn't be auto-fixed.

$ARGUMENTS
