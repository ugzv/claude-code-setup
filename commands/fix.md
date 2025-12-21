---
description: Auto-fix all linting, formatting, and code quality issues
---

You are cleaning up the codebase - fixing everything that can be auto-fixed.

## Why This Matters

Manual cleanup is tedious. Unused imports, inconsistent formatting, simple lint errors - these accumulate and make code harder to read. Modern tools can fix most of these automatically. Your job is to run everything available and make the codebase cleaner.

## Tools Need Configs to Work Well

A tool without a config is a tool waiting to fail. Running `ruff check` with no config uses defaults that might be too strict or too loose for the project. Running `eslint --fix` without a config often does nothing useful.

**Your job isn't just to run tools—it's to ensure they're set up correctly for this specific project.**

When you find a tool installed but unconfigured:
1. Check if a config file exists (pyproject.toml sections, eslint.config.js, etc.)
2. If missing, create one tuned for the project type (MCP server, Agent SDK, web app)
3. Match existing project style (line length, quote style) by sampling a few files
4. Then run the tool

A well-configured linter that catches real issues is infinitely more valuable than an unconfigured one that spews noise or misses everything.

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

**If ruff is installed but no config exists** (`[tool.ruff]` missing from pyproject.toml), create one tuned for the project:

```toml
[tool.ruff]
line-length = 120  # Or match existing style
target-version = "py311"  # Match project's Python version

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "I",      # isort
    "UP",     # pyupgrade
    "B",      # flake8-bugbear (catches real bugs)
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # Line length (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
```

For **MCP servers** (FastMCP/Python), add:
```toml
[tool.ruff.lint.per-file-ignores]
"src/server.py" = ["ARG001"]  # Unused args OK in tool handlers
```

For **Agent SDK projects**, add:
```toml
[tool.ruff.lint]
extend-ignore = ["PLR0913"]  # Allow many args in agent configs
```

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

**If eslint is installed but no config exists**, create one tuned for the project:

For **TypeScript projects** (MCP servers, etc.), create `eslint.config.js`:
```javascript
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
  {
    ignores: ['dist/', 'build/', 'node_modules/'],
  }
);
```

For **Prettier**, create `.prettierrc`:
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

**If using Biome** (faster alternative), create `biome.json`:
```json
{
  "organizeImports": { "enabled": true },
  "linter": { "enabled": true },
  "formatter": { "enabled": true, "indentStyle": "space" }
}
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
