---
description: Auto-fix all linting, formatting, and code quality issues
---

You are cleaning up the codebase - fixing everything that can be auto-fixed.

## Why This Matters

Manual cleanup is tedious. Unused imports, inconsistent formatting, simple lint errors - these accumulate and make code harder to read. Modern tools can fix most of these automatically. Your job is to run everything available and make the codebase cleaner.

## Detect and Run Everything

First, figure out what this project uses. Check config files:
- `pyproject.toml`, `setup.py`, `requirements.txt` → Python
- `package.json` → JS/TS
- `go.mod` → Go
- `Cargo.toml` → Rust

Then run ALL available fixers. Don't just format - fix everything that's auto-fixable.

### Python

**Ruff is the modern standard** - it replaces black, isort, flake8, and more in one fast tool.

```bash
# If ruff is available (check pyproject.toml or try running it)
ruff check --fix .                    # Fix lint issues (unused imports, variables, etc.)
ruff format .                         # Format code

# If only black/isort available
black .
isort .

# If flake8 with autoflake
autoflake --in-place --remove-all-unused-imports --recursive .
```

**If no tools installed**, offer to add ruff:
```bash
uv add --dev ruff   # or: pip install ruff
```

Ruff fixes: unused imports (F401), unused variables (F841), import sorting, formatting, and 700+ other rules.

### JavaScript/TypeScript

```bash
# ESLint for lint fixes (unused vars, imports, etc.)
npx eslint --fix .

# Prettier for formatting
npx prettier --write .

# If using Biome (newer, faster)
npx biome check --apply .
```

**If no tools installed**, offer to add eslint + prettier:
```bash
npm install -D eslint prettier eslint-config-prettier
```

### Go

```bash
gofmt -w .                    # Format
goimports -w .                # Fix imports (install: go install golang.org/x/tools/cmd/goimports@latest)
go mod tidy                   # Clean up go.mod
```

### Rust

```bash
cargo fmt                     # Format
cargo clippy --fix            # Lint fixes
```

## What to Fix

Run everything that auto-fixes. Common categories:

- **Unused imports** - Remove them, they're clutter
- **Unused variables** - Remove or prefix with `_` if intentional
- **Import sorting** - Consistent ordering
- **Formatting** - Consistent style
- **Simple lint errors** - Whatever the linter can auto-fix

## What NOT to Do

- Don't change logic or behavior
- Don't remove code that looks unused but might be (check for dynamic usage)
- Don't fix things that require human judgment
- Don't commit - that's `/commit` when the user is ready

## After Fixing

Report what was fixed:
- Which tools ran
- Summary of changes (e.g., "Removed 12 unused imports, formatted 8 files")
- Any errors or files that couldn't be fixed

If significant unused code was found, mention it but don't delete functions/classes automatically - that needs human review.

$ARGUMENTS
