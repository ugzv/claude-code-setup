---
description: "Analyze codebase [--audit|--clarity|--deps|--naming|--comments|--debt|--history]"
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
| `--deps` | Dependency health (outdated, unused, vulnerable) |
| `--naming` | Naming consistency and clarity |
| `--comments` | Comment quality (stale, misleading, redundant) |
| `--debt` | Technical debt markers (TODOs, FIXMEs, temporary hacks) |
| `--clarity` | AI comprehension audit—where assumptions don't match reality |

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

### --deps Mode

Dependency health check. No parallel agents needed—sequential analysis:

1. **Scan dependency files** (package.json, requirements.txt, go.mod, Cargo.toml, etc.)
2. **Check for issues:**
   - Outdated packages (major versions behind)
   - Unused dependencies (declared but not imported)
   - Duplicate dependencies (same thing, different packages)
   - Known vulnerabilities (if audit tools available: `npm audit`, `pip-audit`, etc.)
   - Pinning issues (loose versions that could break)

**Output focus:** Actionable list with upgrade commands or removal candidates.

### --naming Mode

Naming consistency analysis. Spawn if codebase is large, otherwise analyze directly:

- **Inconsistent conventions**: camelCase vs snake_case mixing, abbreviation inconsistency
- **Misleading names**: functions that do something different from what name suggests
- **Naming drift**: same concept with different names across files
- **Vague names**: `data`, `info`, `handle`, `process`, `manager` without specificity
- **Boolean naming**: missing `is`/`has`/`should` prefixes causing ambiguity

**Why this matters for AI:** Claude infers behavior from names. Misleading names = wrong assumptions.

### --comments Mode

Comment quality analysis. Focus on AI-readability:

- **Stale comments**: describe behavior that code no longer has
- **Contradicting comments**: say one thing, code does another
- **Obvious comments**: `// increment i` above `i++`
- **Commented-out code**: dead code preserved "just in case"
- **Missing context**: complex logic with no explanation of WHY

**How to detect stale comments:**
- Compare comment claims to actual code behavior
- Look for comments referencing removed variables/functions
- Check git blame—old comment on recently changed code is suspect

**Output:** List with recommendation (update, delete, or add context).

### --debt Mode

Technical debt inventory:

- **TODO/FIXME/HACK/XXX markers**: extract with context
- **Temporary solutions**: `// temporary`, `// workaround`, `// quick fix`
- **Disabled tests**: skipped tests with excuses
- **Dead feature flags**: toggles that are always on/off
- **Age analysis**: how old is each debt marker? (git blame)

**Output format:**
```markdown
| Marker | Location | Age | Context |
|--------|----------|-----|---------|
| TODO | file:line | 6mo | "add validation" |
```

Oldest debt = most likely forgotten. Offer to convert high-priority items to backlog.

### --clarity Mode

AI comprehension audit. Tests how easily an AI (or new developer) can understand the codebase correctly.

**The process:**

1. **First pass - Form assumptions** (before reading implementation):
   - Scan file names, function names, class names, comments
   - What do you think each module/function does?
   - What's the assumed architecture?
   - Document these assumptions explicitly

2. **Second pass - Verify assumptions:**
   - Read the actual implementations
   - Where were you wrong?
   - What misled you?

3. **Report the gaps:**

| What I assumed | What it actually does | What misled me |
|----------------|----------------------|----------------|
| `handleAuth()` manages login | It only refreshes tokens | Name suggests broader scope |
| `utils/` has generic helpers | It has business logic | Directory name |
| `// validates input` | It transforms, doesn't validate | Stale comment |

**Categories of misleading signals:**
- **Names that lie**: Function/file/class names suggesting wrong behavior
- **Comments that mislead**: Descriptions that don't match code
- **Structure that confuses**: Files in wrong directories, unclear boundaries
- **Missing context**: Complex logic with no explanation of WHY
- **Tribal knowledge**: Things you can only understand if you already know

**Output:**
```markdown
## Clarity Audit: [Project]

**First impression:** [What you thought this codebase was about]
**Reality:** [What it actually is]

## Where I Was Misled

### 1. [Misleading element]
- **Assumed:** [what you thought]
- **Actually:** [what it does]
- **Misled by:** [name/comment/structure]
- **Suggestion:** [how to fix]

## Suggestions for Clarity
[Prioritized list of changes that would help AI/new devs understand faster]
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
