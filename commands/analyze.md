---
description: Analyze codebase for refactoring opportunities
---

You are an architecture advisor helping make this codebase better organized.

## Philosophy: Constructive, Not Defensive

The question isn't "what's wrong?" but "what could be better?"

**Defensive analysis** finds problems: missing error handling, type gaps, security issues. That's useful but reactive—it's fixing what's broken.

**Constructive analysis** finds opportunities: code that could be unified, patterns worth extracting, modules ready to split, abstractions waiting to emerge. This is proactive—it's making good code better.

This command defaults to constructive. Use `--audit` for defensive issue-detection.

## Modes

| Mode | Focus | Use When |
|------|-------|----------|
| **Default** | Architecture & refactoring opportunities | "How can I make this codebase better?" |
| `--audit` | Issues & gaps to fix | "What problems should I address?" |
| `--history` | Git churn & bug patterns | "What keeps breaking?" |

## Phase 1: Understand the Codebase

Before analyzing, map what exists:

```
1. Codebase shape:
   - Languages and frameworks
   - Directory structure and conventions
   - Entry points and boundaries
   - Shared code locations

2. Scale indicators:
   - Total files by type
   - Largest files (>500 lines)
   - Deepest directories
   - Most imported modules

3. Read .claude/state.json:
   - Skip items already in backlog
   - Note currentFocus to avoid conflicts
```

## Phase 2: Run Analyzers in Parallel

**CRITICAL: Spawn all analyzers at once** in a single message with multiple Task calls.

### Default Mode: Architecture Advisor

```
┌─────────────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. unification-finder                                          │
│     → Find similar code across different files                  │
│     → Look for: similar functions, repeated patterns,           │
│       copy-pasted blocks with minor variations                  │
│     → Output: groups of similar code with unification strategy  │
│                                                                 │
│  2. abstraction-detector                                        │
│     → Find patterns that repeat 3+ times                        │
│     → Look for: inline logic that could be a function,          │
│       function groups that could be a class/module,             │
│       repeated conditionals, similar error handling             │
│     → Output: pattern + locations + suggested abstraction       │
│                                                                 │
│  3. module-health-checker                                       │
│     → Find files that have grown too large (>400 lines)         │
│     → Find files with too many responsibilities                 │
│     → Find directories that could be reorganized                │
│     → Output: candidates for splitting with suggested structure │
│                                                                 │
│  4. dependency-mapper                                           │
│     → Map import relationships                                  │
│     → Find: highly coupled modules, circular deps,              │
│       modules imported everywhere (candidates for /shared)      │
│     → Output: dependency insights + reorganization suggestions  │
│                                                                 │
│  5. consistency-reviewer                                        │
│     → Find same operation done multiple different ways          │
│     → Not "this is wrong" but "pick one and standardize"        │
│     → Output: the variants + which is most common + suggestion  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Project-Type Specific (Auto-Detected)

```
┌─────────────────────────────────────────────────────────────────┐
│  IF Multi-Service (docker-compose, multiple apps)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  6. service-structure-reviewer                                  │
│     → Compare service structures for consistency opportunities  │
│     → Find shared code that lives in individual services        │
│     → Find services that have drifted from common patterns      │
│     → Output: standardization opportunities across services     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  IF Agent System (.claude/agents/, MCP, agent SDK)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  7. agent-pattern-reviewer                                      │
│     → Compare agent implementations for shared patterns         │
│     → Find tool implementations that could be generalized       │
│     → Find prompt patterns that could be templated              │
│     → Output: agent architecture improvement opportunities      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### --audit Mode: Issue Detection

```
┌─────────────────────────────────────────────────────────────────┐
│  ONLY WHEN --audit FLAG IS PRESENT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  A. test-coverage-auditor                                       │
│     → Source files with no corresponding test                   │
│     → Critical paths that are untested                          │
│                                                                 │
│  B. type-safety-auditor                                         │
│     → Missing type hints, Any abuse                             │
│     → TypeScript strict mode violations                         │
│                                                                 │
│  C. error-handling-auditor                                      │
│     → Unprotected API/DB/IO operations                          │
│     → Swallowed errors, inconsistent error responses            │
│                                                                 │
│  D. security-auditor                                            │
│     → Hardcoded secrets, missing validation                     │
│     → Injection risks                                           │
│                                                                 │
│  E. dead-code-finder                                            │
│     → Unused exports, orphan files                              │
│     → Unused dependencies                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### --history Mode: Churn Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│  ONLY WHEN --history FLAG IS PRESENT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  H1. churn-analyzer                                             │
│      → Most modified files, bug-fix correlation                 │
│      → Classify commits: bug-fix vs feature vs refactor         │
│                                                                 │
│  H2. complexity-analyzer                                        │
│      → Cyclomatic complexity, function length, nesting          │
│      → Correlate with churn for priority ranking                │
│                                                                 │
│  H3. coupling-analyzer                                          │
│      → High fan-in/fan-out, circular dependencies               │
│      → Correlate with churn for architectural problems          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Example Subagent Prompts

```
# unification-finder
Find code that could be unified in this codebase at [path].

Look for:
1. Functions that do similar things in different files
   - Same/similar name, different implementation
   - Different name, same logic
   - Copy-pasted with minor modifications

2. Repeated code blocks (>5 lines appearing 2+ times)
   - Exact duplicates
   - Near-duplicates (same structure, different variables)

3. Similar classes/modules that could share a base
   - Services with same method signatures
   - Components with same patterns

For each finding:
- Show the similar code snippets side-by-side
- Explain what makes them candidates for unification
- Suggest HOW to unify (shared function, base class, utility module)
- Note any variations that would need to be parameterized

Output format:
## Unification Opportunity: [Name]
**What:** [Description of the similar code]
**Where:**
- file1.py:45-67 - [brief description]
- file2.py:23-41 - [brief description]
**Similarity:** [What's the same]
**Differences:** [What varies - these become parameters]
**Suggested approach:** [How to unify]
**Estimated impact:** [Lines saved, maintenance benefit]
```

```
# abstraction-detector
Find patterns worth abstracting in this codebase at [path].

Look for:
1. Inline logic that repeats (candidates for functions)
   - Same conditional patterns
   - Same data transformations
   - Same validation sequences

2. Function groups that belong together (candidates for modules/classes)
   - Functions that always get imported together
   - Functions that operate on same data structures
   - Related utilities scattered across files

3. Repeated structural patterns (candidates for base classes/mixins)
   - Same method signatures across classes
   - Same initialization patterns
   - Same lifecycle hooks

For each pattern:
- Show 3+ examples of where it appears
- Suggest the abstraction (function signature, class interface, etc.)
- Explain the benefit (DRY, single point of change, clearer intent)

Output format:
## Abstraction Candidate: [Name]
**Pattern:** [What repeats]
**Occurrences:**
1. file1.py:34 - `code snippet`
2. file2.py:89 - `code snippet`
3. file3.py:12 - `code snippet`
**Suggested abstraction:**
```python
def suggested_function(param1, param2):
    # unified implementation
```
**Benefits:** [Why this abstraction helps]
```

```
# module-health-checker
Analyze module health and find splitting opportunities at [path].

Look for:
1. Large files (>400 lines)
   - What distinct responsibilities exist?
   - Where are the natural split points?
   - What would the resulting modules be?

2. Files with too many imports (>15)
   - Sign of too many responsibilities
   - Which imports cluster together?

3. Files with too many exports (>10)
   - Might be doing too much
   - Which exports are related?

4. Directories that have grown messy
   - Mix of related and unrelated files
   - Missing subdirectory organization

For each candidate:
- Current state (lines, imports, exports, responsibilities)
- Suggested split (new file names, what goes where)
- Migration path (how to split without breaking imports)

Output format:
## Split Candidate: [filename]
**Current state:**
- Lines: X
- Imports: Y
- Exports: Z
- Responsibilities: [list them]

**Suggested split:**
1. `new_file1.py` - [responsibility A]
   - Move: function1, function2, ClassA
2. `new_file2.py` - [responsibility B]
   - Move: function3, ClassB

**Migration:** [How to do it safely]
```

```
# consistency-reviewer
Find inconsistent patterns that should be standardized at [path].

Look for variations in:
1. How common operations are done
   - HTTP clients (fetch vs axios vs httpx)
   - Date handling (libraries, formats)
   - Logging (console vs logger, formats)
   - Error creation and handling

2. Naming conventions
   - File naming (UserService.ts vs user-service.ts)
   - Function naming (camelCase vs snake_case)
   - Variable naming patterns

3. Code organization
   - Import ordering
   - Function ordering within files
   - Directory structure across similar modules

For each inconsistency:
- Show the variants that exist
- Count occurrences of each
- Recommend which to standardize on (usually the most common)
- Note any cases where variation is actually appropriate

Output format:
## Inconsistency: [What varies]
**Variants found:**
1. Pattern A (15 occurrences): `example`
2. Pattern B (8 occurrences): `example`
3. Pattern C (3 occurrences): `example`

**Recommendation:** Standardize on Pattern A
**Rationale:** [Why - most common, clearest, matches conventions]
**Exception:** [If any variant is appropriate in certain contexts]
```

```
# service-structure-reviewer (multi-service only)
Compare service structures to find standardization opportunities at [path].

1. Map each service's structure:
   - Directory layout
   - Common files (main.py, config.py, etc.)
   - Patterns used (how endpoints defined, how errors handled)

2. Find inconsistencies:
   - Service A does X, Service B does Y for same thing
   - Some services have feature Z, others don't

3. Find shared code opportunities:
   - Similar utilities in multiple services
   - Same patterns reimplemented differently

Output format:
## Service Structure Comparison

| Aspect | service-a | service-b | service-c |
|--------|-----------|-----------|-----------|
| Config pattern | X | Y | X |
| Error handling | A | A | B |
| ...

## Standardization Opportunities
1. [Description of what could be unified]
2. ...

## Shared Code Candidates
1. [Code that exists in multiple services, could move to shared/]
```

## Phase 3: Synthesize and Prioritize

After analyzers return, organize findings by impact:

### Priority Framework

**High Impact** (do these first):
- Unifications that save >50 lines across files
- Abstractions that simplify 5+ call sites
- Splits that separate genuinely different concerns
- Consistency fixes that affect >10 files

**Medium Impact** (good improvements):
- Unifications that reduce duplication
- Abstractions that clarify intent
- Reorganizations that improve discoverability

**Lower Impact** (nice to have):
- Minor consistency standardizations
- Small-scale cleanups
- Stylistic improvements

### Output Format

```markdown
## Analysis Summary

**Project:** [type and scale]
**Mode:** [Default/Audit/History]
**Key insight:** [One sentence - the most important finding]

---

## High-Impact Opportunities

### 1. [Title - what could be better]
**What:** [Clear description]
**Where:** [Files involved]
**Why it matters:** [Benefit - maintenance, clarity, DRY]
**How:** [Concrete steps to implement]
**Scope:** [Rough size - small/medium/large refactor]

### 2. ...

---

## Medium-Impact Opportunities

### 3. ...

---

## Quick Wins

- [Small improvement 1]
- [Small improvement 2]

---

## Observations

[Any architectural insights that aren't actionable but worth noting]
```

## What Makes a Good Finding

**Constructive:** "These could be unified" not "this is duplicated"
**Specific:** Exact files and line numbers, not vague areas
**Actionable:** Clear path to implementation
**Worthwhile:** The improvement justifies the effort

## What to Leave Out

- Tiny duplications (2-3 lines) - not worth abstracting
- Stylistic preferences without consistency benefit
- Theoretical improvements without concrete path
- Refactors that would require rewriting everything
- "Best practices" that don't fit this codebase's context

## After Analysis

Offer to implement the highest-impact opportunity:

"The biggest win here is [X]. Want me to start on that?"

For refactoring work:
1. Register in `currentFocus` before starting
2. Make changes incrementally with tests passing
3. Commit logical chunks, not one massive commit

The measure of success: code that's easier to understand, modify, and extend—not just "cleaner" in abstract terms.

$ARGUMENTS
