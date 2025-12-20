---
description: Run tests intelligently based on what's available
---

You are verifying the code works.

## Detect Test Framework

Check what this project uses:
- `pyproject.toml` or `pytest.ini` or `tests/` → pytest (Python)
- `package.json` scripts → jest, vitest, mocha (JS/TS)
- `go.mod` with `_test.go` files → go test (Go)
- `Cargo.toml` → cargo test (Rust)

## Run Tests

### Python
```bash
# pytest is standard
pytest tests/ -v

# With coverage if available
pytest tests/ -v --cov=src --cov-report=term-missing

# Skip slow tests (if marked)
pytest tests/ -v -m "not slow"
```

### JavaScript/TypeScript
```bash
# Check package.json scripts
npm test           # or: yarn test, pnpm test

# Direct runners
npx vitest run     # Vitest
npx jest           # Jest
```

### Go
```bash
go test ./...      # All packages
go test -v ./...   # Verbose
```

### Rust
```bash
cargo test
```

## Arguments

If the user provides arguments, pass them through:
- `/test auth` → run tests matching "auth"
- `/test -k login` → pytest with -k flag
- `/test --watch` → watch mode if supported

## After Running

Report results clearly:
- How many tests passed/failed
- Which tests failed and why (show error messages)
- If all passed, confirm briefly

If tests fail, offer to investigate and fix the failures.

$ARGUMENTS
