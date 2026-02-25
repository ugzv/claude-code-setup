---
description: "Find duplicate code and plan consolidation [--aggressive]"
---

Deep duplicate and similar-code detector with concrete merge plans.

## Philosophy

**Duplication is a spectrum.** Copy-paste is obvious. But the dangerous duplicates are *structural clones*—functions that do the same thing with different variable names, validation blocks repeated across handlers, the same helper reinvented in three modules because nobody knew it existed.

**Comments are the canary.** When similar functions have contradicting docstrings, one is lying. Finding doc divergence across clones reveals not just duplication but *misinformation* baked into the codebase.

**Plans, not lists.** Listing duplicates is easy. The hard part is: which version becomes canonical? What edge cases does each variant handle that the others don't? What's the merge strategy? This command produces consolidation plans, not inventories.

**Relationship to `/analyze`:** `/analyze` is the X-ray—broad sweep, finds areas of concern. `/dedup` is the MRI—deep focus on duplication with surgical merge plans.

## Phase 1: Understand

Quick scan before spawning analyzers:
- Languages, frameworks, directory structure
- Utility/helper directories (utils/, helpers/, lib/, shared/, common/)
- Read `.claude/state.json` to check for known duplication items in backlog
- Scope from `$ARGUMENTS` — if a path or module is specified, focus there; otherwise scan the full project

## Phase 2: Spawn Analyzers in Parallel

**CRITICAL: Spawn all 4 at once** in a single message with multiple Task calls.

```
┌─────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                      │
├─────────────────────────────────────────────────────────┤
│  1. clone-detector                                      │
│     → Function/method-level clones across files         │
│     → Compare bodies structurally (ignore var names)    │
│     → Skip trivial duplications (<5 lines)              │
│     → Output: clone groups with locations, similarity   │
│       percentage, and key diffs between variants        │
│                                                         │
│  2. pattern-repeater                                    │
│     → Inline code blocks repeated 3+ times              │
│     → Focus: validation, error handling, config         │
│       assembly, data transformation, API call patterns  │
│     → Output: occurrences with locations + suggested    │
│       extraction (function name, signature, module)     │
│                                                         │
│  3. utility-fragmenter                                  │
│     → Same helper reimplemented in multiple places      │
│     → Look for similar function names across files,     │
│       similar logic with different wrappers             │
│     → Output: grouped implementations + which is most   │
│       complete (canonical candidate) + import paths     │
│                                                         │
│  4. doc-divergence-checker                              │
│     → Similar-named or similar-bodied functions with    │
│       contradicting comments, docstrings, or types      │
│     → Does its own scan for similar functions           │
│       (independent of agents 1-3)                       │
│     → Compares: docstrings, JSDoc, type annotations,    │
│       inline comments describing behavior               │
│     → Output: divergence pairs with which doc is        │
│       truthful (verified against code) + canonical docs │
└─────────────────────────────────────────────────────────┘
```

Each analyzer should use Glob and Grep to find candidates, then Read to compare implementations. They report raw findings—synthesis happens in Phase 3.

## Phase 3: Synthesize

Cross-reference findings from all 4 analyzers:

1. **Deduplicate overlap** — clone-detector and utility-fragmenter may flag the same code; merge into one group
2. **Enrich with doc info** — attach doc-divergence findings to relevant clone groups
3. **Build Consolidation Groups** — each group is a set of variants that should become one thing
4. **Order by impact** — lines saved, files simplified, call sites reduced

For each Consolidation Group, determine:
- **Canonical version**: Which variant is most complete/correct?
- **Edge cases**: What does each variant handle that others don't?
- **Merge strategy**: Concrete steps to consolidate (create shared util, update imports, add missing edge cases, fix docs)
- **Risk**: What could break? Which callers need testing?

## Output Format

```markdown
## Dedup Report: [Project]
**Scanned:** [N files across M directories]
**Found:** [X consolidation groups, Y total duplicate instances, ~Z lines recoverable]

## Consolidation Groups

### Group 1: [Descriptive name, e.g., "Date formatting helpers"]
**Impact:** ~[N] lines recoverable across [M] files

| Location | Variant | Edge Cases | Docs Accurate? |
|----------|---------|------------|----------------|
| file:line | [brief diff] | [what's unique] | [yes/no/missing] |

**Merge strategy:**
1. [Where to place canonical version]
2. [What to merge from each variant]
3. [Which call sites to update]
4. [Which docs to fix]

### Group 2: ...

## Doc Divergences (not tied to clones)
| Function A | Function B | Divergence | Truthful |
|------------|------------|------------|----------|
| file:line  | file:line  | [what contradicts] | [which is correct] |

## Summary
| Metric | Value |
|--------|-------|
| Clone groups found | [N] |
| Repeated patterns | [N] |
| Fragmented utilities | [N] |
| Doc divergences | [N] |
| Estimated lines recoverable | [N] |
| Files that would be simplified | [N] |
```

**Gain must be factual** — derived from actual line counts, file counts, and call site analysis. Not "improves maintainability" — concrete numbers only.

## After Report

Offer to implement the highest-impact consolidation group.

If `--aggressive` is passed: still show the full report first, then ask for confirmation before implementing the top group. Aggressive means "plan to act," not "act blindly."

$ARGUMENTS
