---
description: Analyze codebase for refactoring opportunities
---

Architecture advisor for improving codebase organization.

## Philosophy

**Constructive analysis** finds opportunities: code to unify, patterns to extract, modules to split. Default mode.

**Defensive analysis** finds problems: missing error handling, type gaps, security issues. Use `--audit`.

## Modes

| Mode | Focus |
|------|-------|
| **Default** | Architecture & refactoring opportunities |
| `--audit` | Issues & gaps to fix |
| `--history` | Git churn & bug patterns |

## Phase 1: Understand

Quick scan before spawning analyzers:
- Languages, frameworks, directory structure
- Largest files (>500 lines), deepest directories
- Read `.claude/state.json` to avoid duplicating backlog items

## Phase 2: Spawn Analyzers in Parallel

**CRITICAL: Spawn all at once** in a single message with multiple Task calls.

### Default Mode

```
┌────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                     │
├────────────────────────────────────────────────────────┤
│  1. unification-finder                                 │
│     → Similar code across files, copy-paste variants   │
│     → Output: groups + unification strategy            │
│                                                        │
│  2. abstraction-detector                               │
│     → Patterns repeating 3+ times                      │
│     → Output: pattern + locations + suggested extract  │
│                                                        │
│  3. module-health-checker                              │
│     → Files >400 lines, too many responsibilities      │
│     → Output: split candidates with structure          │
│                                                        │
│  4. dependency-mapper                                  │
│     → Import relationships, circular deps              │
│     → Output: coupling insights + reorganization ideas │
│                                                        │
│  5. consistency-reviewer                               │
│     → Same operation done multiple ways                │
│     → Output: variants + standardization suggestion    │
└────────────────────────────────────────────────────────┘
```

### Project-Type Specific (Auto-Detect)

- **Multi-service** (docker-compose): Add `service-structure-reviewer`
- **Agent system** (.claude/agents/, MCP): Add `agent-pattern-reviewer`

### --audit Mode

```
┌────────────────────────────────────────────────────────┐
│  SPAWN FOR --audit                                     │
├────────────────────────────────────────────────────────┤
│  A. test-coverage-auditor → untested critical paths    │
│  B. type-safety-auditor → missing types, Any abuse     │
│  C. error-handling-auditor → unprotected IO ops        │
│  D. security-auditor → secrets, injection risks        │
│  E. dead-code-finder → unused exports, orphan files    │
└────────────────────────────────────────────────────────┘
```

### --history Mode

```
┌────────────────────────────────────────────────────────┐
│  SPAWN FOR --history                                   │
├────────────────────────────────────────────────────────┤
│  H1. churn-analyzer → most modified, bug correlation   │
│  H2. complexity-analyzer → cyclomatic, nesting depth   │
│  H3. coupling-analyzer → fan-in/out, circular deps     │
└────────────────────────────────────────────────────────┘
```

## Phase 3: Synthesize

Organize findings by impact:

**High Impact**: Unifications saving >50 lines, abstractions simplifying 5+ call sites, splits separating concerns
**Medium Impact**: Duplication reduction, clarity improvements
**Quick Wins**: Minor standardizations

## Output Format

```markdown
## Analysis Summary
**Project:** [type/scale]  **Mode:** [mode]
**Key insight:** [one sentence]

## High-Impact Opportunities
### 1. [Title]
**What:** [description]
**Where:** [files:lines]
**Gain:** [concrete, measured from analysis - e.g., "47 lines → 12", "5 files → 1 shared util", "8 call sites simplified"]
**How:** [implementation approach]

## Quick Wins
- [item] → [gain]

## Observations
[non-actionable insights]
```

**Gain must be factual** - derived from actual line counts, file counts, or call site analysis. Not "improves maintainability" or "saves time" - those are guesses.

## What Makes Good Findings

- **Constructive**: "These could be unified" not "this is duplicated"
- **Specific**: Exact files and lines
- **Actionable**: Clear implementation path
- **Worthwhile**: Improvement justifies effort

Skip: tiny duplications (<5 lines), stylistic preferences, theoretical improvements without concrete path.

## After Analysis

Offer to implement the highest-impact opportunity.

$ARGUMENTS
