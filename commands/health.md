---
description: Check overall project health
---

Assess whether this team can ship with confidence.

## What Health Means

A healthy project has feedback loops: tests catch bugs, types catch mistakes, linting catches patterns that correlate with problems, CI fails before broken code reaches production.

An unhealthy project has hope instead of feedback.

## Run Checks in Parallel

**Spawn all checks at once:**

```
┌────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                     │
├────────────────────────────────────────────────────────┤
│  1. security-check                                     │
│     → npm audit / pip-audit / govulncheck / composer audit │
│     → Return: {critical, high, details}                │
│                                                        │
│  2. type-check                                         │
│     → tsc / mypy / pyright / phpstan                   │
│     → Return: pass/fail + error count                  │
│                                                        │
│  3. test-runner                                        │
│     → pytest / npm test / go test / phpunit            │
│     → Return: pass/fail + failure summary              │
│                                                        │
│  4. lint-check                                         │
│     → eslint / ruff / golangci-lint / pint / phpcs     │
│     → Return: error/warning counts                     │
│                                                        │
│  5. outdated-check                                     │
│     → npm outdated / pip list --outdated / composer outdated │
│     → Return: packages behind + severity               │
│                                                        │
│  6. debt-scan                                          │
│     → grep TODO/FIXME + git blame for age              │
│     → Return: count by age + critical path markers     │
└────────────────────────────────────────────────────────┘
```

## Interpreting Results

- **Tests pass** = floor, not ceiling. Do they cover what matters?
- **Tests fail** = one failing in active area might be mid-work; 100 ignored for weeks means broken loop
- **Type errors cluster** = might indicate design problem in that module
- **Security vulnerabilities** = HIGH/CRITICAL get fixed now, not flagged for later

## Dependencies

- **Vulnerabilities**: Fix immediately or document why not
- **Outdated**: Patch updates almost always safe; major updates one at a time
- **Unused**: Remove them - zero leverage, full risk

## Tech Debt Markers

Search for TODO, FIXME, HACK, XXX. Use git blame to date them:
- 2-week-old TODO = maybe active work
- 2-year-old FIXME = broken promise
- Clusters in one area = rushed module
- Markers in critical paths (auth, payments) = real risk

## What to Report

Synthesize, don't dump tool output.

**Can this team ship with confidence?** If not, explain specifically what's broken.

**What's the highest-leverage improvement?** One thing that would most improve confidence.

**What can wait?** Acknowledge real but non-urgent findings.

## After Assessment

Don't just diagnose. Offer to execute the highest-leverage fix now.

$ARGUMENTS
