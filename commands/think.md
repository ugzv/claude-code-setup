---
description: Spec out complex tasks before implementing
---

Create a spec before writing code. Prevents wasted work on wrong approaches.

**Flag: `--gpt`** - Get a second opinion from GPT via Codex CLI (optional, requires `codex` installed).

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

## Phase 3.5: GPT Second Opinion (only with `--gpt` flag)

Codex with high reasoning excels at deep code analysis. Use it to surface what you can't see from your current vantage point.

**When `--gpt` is set:**

1. Check if `codex` is installed: `which codex` - if not, skip gracefully
2. Construct a prompt that enables deep analysis:
   ```
   You are providing a second opinion on a coding decision. Use your high reasoning capability to analyze deeply. Take your time - thoroughness matters more than speed.

   CONTEXT: [Problem in one sentence]
   APPROACH: [Key decisions, not implementation details]
   TOUCHES: [File list]
   MY CONCERN: [The aspect you're uncertain about]

   QUESTION: [See principles below]
   ```

3. **Principles for prompting high-reasoning models:**
   - Give context that grounds analysis (what you're doing, what you've decided)
   - State your uncertainty explicitly (the model reasons better when it knows where to focus)
   - Ask questions that reward depth over speed (exploration, relationship tracing, completeness checking)
   - Be specific about the dimension needing analysis, not vague quality judgments

4. Run synchronously: `codex exec --full-auto "[your prompt]"`
   High reasoning explores before answering - let it finish. The depth is the value.

5. Incorporate insights that shift your understanding. Ignore surface-level observations you already knew.

**Why this works:** You see your approach clearly. Codex sees the codebase it can explore. Ask questions that leverage what it can discover that you can't from your planning position.

**Setup:** `npm i -g @openai/codex`, then `codex` once to authenticate and select reasoning level.

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
