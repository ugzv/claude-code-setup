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

## CI Config is the Source of Truth

**Check CI first.** If `.github/workflows/*.yml` exists, parse it to see what tools the CI actually runs. Your goal is to ensure CI passes, not just "code looks formatted."

**Run what CI runs.** If CI uses `black --check`, run `black .` locally. If CI uses `ruff`, run `ruff`. Don't assume one replaces the other—they have subtle differences that cause CI failures.

## Parallel Detection Phase

**IMPORTANT: Use subagents to detect available tools simultaneously.** Don't wait for CI parsing to finish before checking pyproject.toml.

```
┌─────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)│
├─────────────────────────────────────────────────────────┤
│  1. ci-parser                                           │
│     → Parse .github/workflows/*.yml                     │
│     → Extract: which linters, formatters CI runs        │
│     → Return: {"tools": [...], "commands": [...]}       │
│                                                         │
│  2. python-detector                                     │
│     → Check pyproject.toml for [tool.ruff], [tool.black]│
│     → Check if ruff/black/isort installed               │
│     → Return: {"available": [...], "configured": [...]} │
│                                                         │
│  3. js-detector                                         │
│     → Check package.json devDependencies                │
│     → Look for eslint, prettier, biome configs          │
│     → Return: {"available": [...], "configured": [...]} │
│                                                         │
│  4. config-validator                                    │
│     → Check if detected tools have config files         │
│     → Flag tools without configs (will need setup)      │
│     → Return: {"configured": [...], "missing": [...]}   │
└─────────────────────────────────────────────────────────┘
```

### Detection Priority (After Parallel Results)

1. **CI config** - highest priority, this is what actually runs
2. **pyproject.toml / package.json** - fallback if no CI config
3. **Installed tools** - last resort, detect what's available

### Apply Fixes (Sequential)

After detection, run fixes in the correct order:
- **Lint first** (finds issues), then **format** (may change what lint found)
- For Python with both ruff and black: `ruff check --fix .` then `black .`

### Python

**First, check what CI uses:**
```bash
# Parse CI config for Python tools
grep -E "black|ruff|flake8|isort|mypy" .github/workflows/*.yml
```

**Then run the matching tools:**

```bash
# If CI uses black (even if ruff is also installed)
black .
isort .  # if used

# If CI uses ruff
ruff check --fix .
ruff format .

# If CI uses both (some projects do)
ruff check --fix .
black .  # run black AFTER ruff to ensure black's formatting wins
```

**If no CI config**, fall back to pyproject.toml detection:
- `[tool.ruff]` → run ruff
- `[tool.black]` → run black
- Neither → check what's installed

**If no tools installed**, offer to add ruff:
```bash
uv add --dev ruff   # or: pip install ruff
```

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

**First, check what CI uses:**
```bash
grep -E "eslint|prettier|biome" .github/workflows/*.yml
```

**Then run the matching tools:**
```bash
# If CI uses eslint
npx eslint --fix .

# If CI uses prettier
npx prettier --write .

# If CI uses biome
npx biome check --apply .
```

**If no CI config**, fall back to package.json devDependencies detection.

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
