---
description: Spec out complex tasks before implementing
---

Create a spec before writing code. Prevents wasted work on wrong approaches.

## When to Plan

- **Skip**: Simple fixes, single-file changes, clear requirements
- **Do plan**: Multiple files, architectural choices, ambiguous requirements

## Phase 1: Understand

Restate what you're being asked in one sentence.

If unclear, batch 2-3 clarifying questions with concrete options:
```
1. **Scope:** All users or admins only?
   - A) All users (simpler)
   - B) Admin-only (needs permission check)
```

Use AskUserQuestion tool. Options with trade-offs, not open-ended questions.

## Phase 2: Explore (Parallel)

**Spawn all explorers at once:**

```
┌────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                     │
├────────────────────────────────────────────────────────┤
│  1. pattern-finder                                     │
│     → Similar features in codebase                     │
│     → How was this pattern solved before?              │
│     → Return: relevant files + brief summary           │
│                                                        │
│  2. arch-analyzer                                      │
│     → Where does this type of code live?               │
│     → Directory structure, conventions                 │
│     → Return: recommended location + reasoning         │
│                                                        │
│  3. dep-checker                                        │
│     → Available libraries/utilities                    │
│     → Return: relevant deps + existing helpers         │
└────────────────────────────────────────────────────────┘
```

If LSP available, use `workspaceSymbol` and `goToDefinition` for faster exploration.

## Phase 3: Propose

Present approach concisely:
```
**Approach:** [what you'll do]
**Files:** [count] touched
- path/to/file.ts (new/modify)

**Open question:** [if any architectural choice]
- A) Option with trade-off
- B) Alternative with trade-off

Ready to proceed after your input.
```

## Phase 4: Confirm and Continue

Wait for user confirmation, then implement. No plan files unless task spans sessions.

## What NOT to Do

- Don't write code during planning
- Don't ask >3 questions per batch
- Don't skip exploration and guess

## Large Tasks

If >10-12 distinct tasks, suggest breaking into phases. Plan and implement Phase 1 first, re-plan Phase 2 with learnings.

$ARGUMENTS
