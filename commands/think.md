---
description: Spec out complex tasks before implementing
---

Create a spec before writing code. Prevents wasted work on wrong approaches.

## When to Plan

- **Skip**: Simple fixes, single-file changes, clear requirements
- **Do plan**: Multiple files, architectural choices, ambiguous requirements

## Phase 1: Understand

Restate what you're being asked in one sentence. If fundamentally unclear, ask - but batch questions and offer concrete options.

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

Based on exploration, **recommend the optimal approach** - don't default to presenting options.

```
**Approach:** [what you'll do and why it fits this codebase]
**Files:** [count] touched
- path/to/file.ts (new/modify)

Ready to proceed, or want me to explain the reasoning?
```

**Only present options when:**
- Multiple genuinely valid approaches exist with real trade-offs
- The choice depends on user preference (not technical merit)
- Exploration revealed conflicting patterns in the codebase

If you must present options, recommend one and explain why.

## Phase 4: Confirm and Continue

Wait for user confirmation, then implement. No plan files unless task spans sessions.

## What NOT to Do

- Don't write code during planning
- Don't ask questions you can answer by exploring
- Don't present options when one approach is clearly better

## Large Tasks

If >10-12 distinct tasks, break into phases small enough to complete in one session.

When user confirms:
1. Current phase → `currentFocus` with description + files
2. Remaining phases → `backlog` with `blocked_by`
3. Start work

**If context runs low mid-task:** Update `currentFocus` with progress (`completed`, `remaining`, `next_step`) before session ends. Next session picks up exactly where you left off.

$ARGUMENTS
