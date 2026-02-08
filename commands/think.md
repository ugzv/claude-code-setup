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

## Phase 3.5: Second Opinion (only with `--gpt` flag)

Get a second perspective from GPT via Codex CLI. Useful when you're uncertain about an architectural decision and want fresh eyes on the codebase.

**When `--gpt` is set:**

1. Check if `codex` is installed: `which codex` — if not, skip gracefully and tell the user

2. **Pick reasoning effort based on what you're asking:**

   | Effort | When to use | Example question |
   |--------|-------------|------------------|
   | `low` | Sanity-checking a straightforward decision | "Does this file structure follow the existing pattern?" |
   | `medium` | Reviewing an approach with a few tradeoffs | "Which of these two patterns fits better here?" |
   | `high` | Deep analysis across multiple files/concerns | "Trace all callers of X and check if this refactor is safe" |

   **Default to `medium`** — it's the best speed/depth tradeoff for most second opinions. Only escalate to `high` when the question genuinely requires multi-file exploration or relationship tracing. `low` is for quick validation where you mostly know the answer.

   > Do NOT use `xhigh` — it's benchmark-grade and too slow for interactive work. If the question needs that level of depth, break it into smaller focused questions at `high`.

3. Construct a prompt that enables focused analysis:
   ```
   You are providing a second opinion on a coding decision.

   CONTEXT: [Problem in one sentence]
   APPROACH: [Key decisions, not implementation details]
   TOUCHES: [File list]
   MY CONCERN: [The aspect you're uncertain about]

   QUESTION: [See principles below]
   ```

4. **Principles for the prompt:**
   - Give context that grounds analysis (what you're doing, what you've decided)
   - State your uncertainty explicitly (the model reasons better when it knows where to focus)
   - Ask questions that reward depth over speed (exploration, relationship tracing, completeness checking)
   - Be specific about the dimension needing analysis, not vague quality judgments
   - Do NOT ask it to "think step by step" — reasoning models do this internally already

5. Run with effort-aware invocation:
   ```
   codex exec --full-auto -m gpt-5.3-codex -c model_reasoning_effort="EFFORT" "[your prompt]"
   ```
   Replace `EFFORT` with your chosen level from step 2.

6. Incorporate insights that shift your understanding. Ignore surface-level observations you already knew.

**Why this works:** You see your planned approach clearly. The second model explores the codebase independently. Matching effort to question complexity means fast answers when you need validation and deep analysis only when it matters.

**Setup:** `npm i -g @openai/codex`, then run `codex` once to authenticate.

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
