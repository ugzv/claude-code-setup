---
description: "Spec out complex tasks before implementing"
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

**CRITICAL: Use GPT-5.5 by default. Always pass `-m gpt-5.5` for `--gpt` unless the user explicitly asks for a different model. Run Codex CLI in full-access YOLO mode with `--dangerously-bypass-approvals-and-sandbox` so it can inspect the repo and execute commands without approval prompts.**

**When `--gpt` is set:**

1. Check if `codex` is installed: `which codex` — if not, skip gracefully and tell the user

2. Check Codex CLI basics:

   ```
   codex --version
   grep -E '^model[[:space:]]*=' ~/.codex/config.toml 2>/dev/null || true
   ```

   The config check is diagnostic only. The `--gpt` workflow should still pass `-m gpt-5.5` explicitly by default so the transcript makes the model choice obvious.

3. **Pick reasoning effort based on what you're asking:**

   | Effort | When to use | Example question |
   |--------|-------------|------------------|
   | `low` | Sanity-checking a straightforward decision | "Does this file structure follow the existing pattern?" |
   | `medium` | Reviewing an approach with a few tradeoffs | "Which of these two patterns fits better here?" |
   | `high` | Deep analysis across multiple files/concerns | "Trace all callers of X and check if this refactor is safe" |
   | `xhigh` | Exceptional cases where correctness depends on very deep analysis | "Audit this migration plan across schema, callers, deployment, and rollback paths" |

   Choose the effort yourself based on what the question needs. Do not ask the user which effort to use. Use the minimum effort that can answer the question well, and escalate when the work genuinely needs deeper repo exploration or relationship tracing.

   > For time-sensitive operational decisions, use the lowest effort that can produce a useful recommendation. Do not let the second opinion block an urgent mitigation; ask a narrower question or proceed with the best available evidence.

4. Construct a prompt that enables focused analysis:
   ```
   You are providing a second opinion on a coding decision.

   CONTEXT: [Problem in one sentence]
   APPROACH: [Key decisions, not implementation details]
   TOUCHES: [File list]
   MY CONCERN: [The aspect you're uncertain about]

   QUESTION: [See principles below]
   ```

5. **Principles for the prompt:**
   - Give context that grounds analysis (what you're doing, what you've decided)
   - State your uncertainty explicitly (the model reasons better when it knows where to focus)
   - Ask questions that reward depth over speed (exploration, relationship tracing, completeness checking)
   - Be specific about the dimension needing analysis, not vague quality judgments
   - Do NOT ask it to "think step by step" — reasoning models do this internally already

6. Run this command (replace `EFFORT` and the prompt). Always capture the final answer with `-o` so a timeout or background shell still leaves a readable result. Put the prompt in a temp file instead of a huge inline shell string; this avoids quoting bugs with JSON, SQL, `!`, backticks, and multiline context:
   ```
   PROMPT="$(mktemp -t codex-second-opinion-prompt.XXXXXX.md)"
   OUT="$(mktemp -t codex-second-opinion.XXXXXX.md)"
   cat > "$PROMPT" <<'EOF'
   [your prompt]
   EOF
   codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral -m gpt-5.5 \
     -c model_reasoning_effort="EFFORT" \
     -o "$OUT" \
     - < "$PROMPT"
   cat "$OUT"
   ```
   - Keep `-m gpt-5.5` unless the user explicitly requested a different model
   - Keep `--dangerously-bypass-approvals-and-sandbox` for full-access YOLO mode
   - Replace `EFFORT` with your chosen level from step 3
   - Use a bounded wait: about 2 minutes for `low`, 5 minutes for `medium`, 10 minutes for `high`, and 15 minutes for `xhigh`
   - If Codex is still running after the bounded wait, say so, stop waiting, and continue with your own recommendation
   - Do not leave a background Codex shell unattended; if it must run in the background, record its PID/output path, poll it, and kill it after the bounded wait

7. Incorporate insights that shift your understanding. Ignore surface-level observations you already knew.

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
