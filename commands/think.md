---
description: Spec out complex tasks before implementing
---

You are creating a spec before writing code. This prevents wasted work on wrong approaches.

## When to Plan

Not everything needs a plan. Use judgment:

- **Skip planning:** Simple fixes, single-file changes, clear requirements
- **Do plan:** Multiple files, architectural choices, ambiguous requirements, anything you could get wrong

If the user explicitly ran `/spec`, they want a spec regardless of complexity.

## Phase 1: Understand

Restate what you're being asked to do in one sentence. This catches misunderstandings early.

If anything is unclear, ask now—but batch your questions. Don't ask one thing, wait, ask another. Gather 2-3 clarifying questions max and present them together with options:

```
Before I explore the codebase, a few questions:

1. **Scope:** Should this apply to all users or just admins?
   - A) All users (simpler)
   - B) Admin-only (needs permission check)

2. **Storage:** Where should preferences live?
   - A) localStorage (simple, no sync across devices)
   - B) Database (syncs, requires API work)
```

Use the AskUserQuestion tool for this. Present concrete options with trade-offs, not open-ended questions.

## Phase 2: Explore (Parallel)

Before proposing an approach, understand what exists. **Use subagents to explore in parallel**—these searches are independent.

```
┌─────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)│
├─────────────────────────────────────────────────────────┤
│  1. pattern-finder                                      │
│     → Search for similar features in codebase           │
│     → How was this pattern solved before?               │
│     → Return: relevant file paths + brief summary       │
│                                                         │
│  2. arch-analyzer                                       │
│     → Where does this type of code live?                │
│     → Check directory structure, existing conventions   │
│     → Return: recommended location + reasoning          │
│                                                         │
│  3. dep-checker                                         │
│     → What libraries/utilities are already available?   │
│     → Check package.json/pyproject.toml + src/utils     │
│     → Return: relevant deps + existing helpers          │
└─────────────────────────────────────────────────────────┘
```

**Example subagent prompts:**

```
# Pattern finder
Search this codebase for similar features to: [user's request]
Look for:
1. Similar functionality already implemented
2. Patterns used for comparable features
3. Code that could be extended vs. written fresh

Return: top 3 relevant files with 1-line summary each.
```

```
# Architecture analyzer
For implementing [user's request], determine:
1. Which directory should this code live in?
2. What's the naming convention for similar files?
3. Are there existing patterns to follow?

Return: recommended path + reasoning.
```

```
# Dependency checker
Check what's available for [user's request]:
1. Relevant packages in package.json/pyproject.toml
2. Existing utility functions in src/utils or lib/
3. Helpers that could be reused

Return: available tools + any gaps needing new deps.
```

### Wait and Synthesize

After all subagents return, combine findings into your proposal. Don't dump raw results—synthesize what matters for the approach.

Don't assume. Don't guess based on project name or README. The subagents read actual files.

## Phase 3: Propose

Present your approach concisely:

```
**Approach:**
- Add DarkModeToggle component to SettingsPage
- Store preference in localStorage, apply via class on <body>
- Use existing useLocalStorage hook from src/hooks/

**Files:** 3 touched
- src/components/Settings/DarkModeToggle.tsx (new)
- src/pages/Settings.tsx (import toggle)
- src/styles/globals.css (dark mode styles)

**Open question:** Should we respect system preference as default?
- A) Yes, use prefers-color-scheme
- B) No, default to light

Ready to proceed after your input.
```

If there are meaningful architectural choices, present them with trade-offs. If the approach is straightforward, just confirm and proceed.

## Phase 4: Confirm and Continue

Wait for user confirmation. They might:
- Approve as-is → proceed to implement
- Adjust the approach → update plan, then proceed
- Ask questions → answer, then confirm

Once confirmed, start implementing. No need to save a plan file unless the user asks or the task spans multiple sessions.

## What NOT to Do

- Don't write code during planning
- Don't ask more than 2-3 questions per batch
- Don't ask open-ended questions when you can offer options
- Don't skip exploration and guess at architecture
- Don't create ceremony (plan files, handoff commands) unless needed

## Large Tasks

If the implementation would exceed 10-12 distinct tasks, say so:

```
This is larger than a single planning session. I recommend:
1. Break into phases (Phase 1: X, Phase 2: Y)
2. Plan and implement Phase 1 first
3. Re-plan Phase 2 with learnings

Want to proceed with Phase 1?
```

$ARGUMENTS
