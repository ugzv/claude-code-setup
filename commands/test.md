---
description: Run tests intelligently based on what's available
---

Verify the code works.

## Detect Framework

- `pyproject.toml` / `pytest.ini` / `tests/` → pytest
- `package.json` scripts → jest, vitest, mocha
- `go.mod` + `_test.go` → go test
- `Cargo.toml` → cargo test

## Parallel Execution (Multi-Framework)

**If multiple frameworks detected, spawn all at once:**

```
┌────────────────────────────────────────────────────────┐
│  SPAWN IF MULTIPLE FRAMEWORKS                          │
├────────────────────────────────────────────────────────┤
│  1. python-tests → pytest -v                           │
│  2. js-tests → npm test / vitest / jest                │
│  3. go-tests → go test ./...                           │
│  4. rust-tests → cargo test                            │
└────────────────────────────────────────────────────────┘
```

For single-language projects, run directly (no subagent overhead).

## Run Commands

```bash
# Python
pytest tests/ -v

# JS/TS
npm test  # or: npx vitest run, npx jest

# Go
go test ./...

# Rust
cargo test
```

## Arguments

Pass user arguments through:
- `/test auth` → tests matching "auth"
- `/test -k login` → pytest -k flag
- `/test --watch` → watch mode if supported

## After Running

Report: passed/failed counts, failure details. If failures, offer to investigate and fix.

$ARGUMENTS
