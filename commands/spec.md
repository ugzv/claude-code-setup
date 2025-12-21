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

## Phase 2: Explore

Before proposing an approach, understand what exists. Read the codebase:

- Find similar features (how did they solve this pattern before?)
- Check the architecture (where does this type of code live?)
- Look at dependencies (what's already available?)
- Find related tests (what's the testing pattern?)

Don't assume. Don't guess based on project name or README. Read actual files.

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
