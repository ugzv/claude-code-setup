---
description: Create handoff doc for fresh session to execute
---

Create or continue handoffs—structured plans that fresh sessions can execute without original context.

## Modes

**Default (no flags):** Generate a new handoff from the current session's analysis.

**With `--continue`:** Resume an active handoff. Load context, show current state, work through phases, update progress.

**With `--continue {id}`:** Resume a specific handoff by id or partial match.

## When to Create (default)

After analysis sessions (`/think`, `/analyze`, `/ux`, etc.) when:
- Context is bloated, need clean execution
- Task spans multiple sessions
- Want phased, validated progress

## When to Continue (--continue)

When resuming work on an existing handoff:
- Fresh session picking up where another left off
- Returning to a task after interruption
- Executing the next phase of a multi-phase plan

## File Structure

```
.claude/
├── state.json        # session tracking (existing)
├── handoffs.json     # handoff index + progress state
└── handoffs/
    └── {slug}.md     # plan details (static after creation)
```

**Separation:**
- `handoffs.json` = state (progress, validation, learnings) — updates as work happens
- `handoffs/*.md` = plan (goal, philosophy, tasks) — **immutable after creation**

**Plan immutability:** Once a `.md` file is created, it is a contract. Do NOT modify it during execution. If the plan is wrong, create a new handoff. This prevents scope creep and maintains traceability.

## handoffs.json Schema

```json
{
  "active": [
    {
      "id": "{slug}",
      "title": "{Task Title}",
      "file": "handoffs/{slug}.md",
      "created": "{date}",
      "currentPhase": 1,
      "lastTouched": "{ISO timestamp}",
      "phases": [
        {
          "name": "{Phase Name}",
          "status": "complete|in_progress|pending",
          "completedAt": "{date}",
          "validation": {
            "criteria": "{what success looks like}",
            "evidence": "{concrete proof: test output, screenshot, working feature}",
            "confidence": "high|medium|low"
          },
          "learnings": "{what worked, what didn't, what to do differently}"
        },
        {
          "name": "{Phase Name}",
          "status": "in_progress",
          "tasks": {"done": 0, "total": 0},
          "notes": "{current state, next step}",
          "blockers": []
        }
      ]
    }
  ],
  "archived": [
    {
      "id": "{slug}",
      "title": "{title}",
      "completed": "{date}",
      "summary": "{one-line outcome}",
      "totalLearnings": "{key insight from the work}"
    }
  ]
}
```

**Field purposes:**
- `validation.evidence` — concrete proof that phase succeeded
- `validation.confidence` — self-assessment of completion quality
- `learnings` — memory synthesis: insights for future sessions
- `complexity` — optional hint for model selection
- `blockers` — explicit issues preventing progress

## Parallel Sessions

Multiple Claude sessions can run simultaneously if working on **different handoffs**.

**Same handoff in multiple sessions = conflict risk.** Use `lastTouched` to detect:

```
When resuming a handoff:
  If lastTouched < 10 minutes ago:
    → Warn: "This handoff was touched 3 min ago. Another session may be active."
    → Ask user to confirm before continuing
  Else:
    → Safe to continue, update lastTouched
```

**Update `lastTouched`:**
- When starting work on a handoff
- After completing a phase
- When adding progress notes

**Best practice:** One handoff = one session. Multiple handoffs = multiple sessions OK.

## Learnings Capture

Each completed phase should capture learnings—memory synthesis that helps future sessions.

**What to capture:**
- What approach worked (and why)
- What didn't work (save others the pain)
- Unexpected edge cases discovered
- Patterns worth reusing
- What you'd do differently

**Why this matters:**
- Next phase benefits from prior context
- Archived handoffs become institutional memory
- Prevents repeating mistakes across sessions

## Plan File Format (.md)

```markdown
# {Title}

> Created: {date} | Source: {/think, /analyze, etc.}

## Goal

One paragraph: What we're achieving and why.

## Philosophy

- Key constraints
- Patterns to follow
- What to avoid

## Scope

### Files
- `path/to/file.ts` — why

### Out of Scope
- Things NOT to do

## Phases

### Phase 1: {Verb + Noun}
**Goal**: What this achieves
**Files**: which files
**Tasks**:
- Concrete task 1
- Concrete task 2
**Validate**: Observable criteria (test passes, feature works)

### Phase 2: {Verb + Noun}
...
```

Note: No progress tracking in .md — that lives in `handoffs.json`.

## Generation Process

1. **Create slug** from title (e.g., "User Authentication" → `user-authentication`)
2. **Write plan** to `.claude/handoffs/{slug}.md`
3. **Add entry** to `.claude/handoffs.json` with all phases as `pending`
4. **Confirm** with user

## Continue Process (--continue)

### 1. Load and Select

```
Read .claude/handoffs.json

If no active handoffs:
  → "No active handoffs. Use /handoff to create one."
  → Stop

If 1 active handoff:
  → Use it automatically

If multiple active handoffs AND no id specified:
  → List them: "N active handoffs: {id1} (Phase X/Y), {id2} (Phase X/Y)..."
  → Ask: "Which one? (Use /handoff --continue {id})"
  → Stop

If id specified:
  → Match by id or partial match on title
  → If no match: "No handoff matching '{id}'. Active: {list ids}"
```

### 2. Check Parallel Session Safety

```
If lastTouched < 10 minutes ago:
  → Warn: "This handoff was touched {N} min ago. Another session may be active."
  → Ask user to confirm before continuing
Else:
  → Safe to proceed
```

### 3. Load Context

Read the handoff .md file. Understand:
- Goal and philosophy
- Scope (files in play, out of scope)
- All phases and their structure

Review handoffs.json for this handoff:
- Current phase number
- Prior phase learnings (critical context)
- Any notes or blockers from previous session

### 4. Present Current State

```
"Continuing: {title}

Phase {N}/{total}: {phase name}
Status: {in_progress|pending}
[If notes exist: "Last session notes: {notes}"]
[If blockers exist: "Blockers: {blockers}"]

Tasks for this phase:
{list from .md file}

Ready to work on this phase."
```

### 5. Execute with Parallel Agents

**Philosophy:** Main agent coordinates; subagents execute. This keeps main context fresh for validation and synthesis while leveraging parallel execution for independent tasks.

**Immediately after loading:**
- Update `lastTouched` to current ISO timestamp

**Analyze task independence:**

```
Review the phase's tasks. Ask:
- Can tasks run without depending on each other's output?
- Do tasks modify different files/areas?
- Would running them in parallel cause conflicts?

Independent tasks → Spawn parallel agents
Sequential dependencies → Execute in order (or spawn first, then continue)
Single complex task → Single agent or main handles directly
```

**Spawn parallel agents when beneficial:**

**CRITICAL: Spawn all at once** in a single message with multiple Task calls.

```
For each independent task group:
  → Spawn agent with:
    - Task description from handoff .md
    - Relevant file scope
    - Philosophy/constraints from handoff
    - Clear success criteria
    - "Report what you changed and any issues encountered"
```

Example spawn pattern:
```
┌────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                     │
├────────────────────────────────────────────────────────┤
│  Task 1 Agent: "Implement X in files A, B"             │
│  Task 2 Agent: "Implement Y in files C, D"             │
│  Task 3 Agent: "Add tests for feature Z"               │
└────────────────────────────────────────────────────────┘
```

**Main agent role during execution:**
- Monitor agent completion
- Do NOT duplicate work agents are doing
- Prepare validation criteria

**After agents complete — Validate:**

Main agent validates ALL changes before marking phase complete:
1. Review what each agent changed
2. Run tests/builds to verify nothing broke
3. Check changes align with handoff philosophy
4. Resolve any conflicts between agent changes

**Update handoffs.json after validation:**
```json
{
  "status": "complete",
  "completedAt": "{date}",
  "validation": {
    "criteria": "{from .md}",
    "evidence": "{concrete proof: test output, build success}",
    "confidence": "high|medium|low"
  },
  "learnings": "{what worked, what agents found, insights}"
}
```

Advance `currentPhase` and update `lastTouched`.

**When NOT to use parallel agents:**
- Tasks with sequential dependencies (B needs A's output)
- Single focused task that's easier to do directly
- Tasks that modify the same files (conflict risk)
- Simple changes where coordination overhead exceeds benefit

**If blocked:**
- Add to `blockers` array with specific issue
- Add `notes` explaining current state
- Keep status as `in_progress`
- Update `lastTouched`

**If context running low:**
- Update `notes` with detailed state for next session
- Update `lastTouched`
- Tell user: "Context getting heavy. Good stopping point—notes saved for next session."

### 6. Report Progress

After each phase or at end of session:
```
"Phase {N} complete. Evidence: {brief description}

[If more phases remain:]
Starting Phase {N+1}: {name}...

[If all phases complete:]
All phases complete. Run /push to archive this handoff."
```

## Resume Principles

- **Context first** — read the .md file for goal/philosophy before acting; review prior learnings
- **No rushing** — you have abundant context; thoroughness over speed
- **Validate before marking complete** — concrete evidence must exist; if uncertain, stay in_progress
- **Capture learnings** — what worked, what didn't, what you'd do differently
- **Clean handoffs** — if context runs low, update notes so next session can continue seamlessly

**What to update in handoffs.json:**
- `lastTouched` when starting and finishing work
- `validation.evidence` with concrete proof
- `learnings` with insights for future sessions
- `blockers` if stuck (don't mark complete when blocked)

## Phase Design

**Good phases:**
- Vertical slices (not horizontal layers)
- Leave codebase working
- Have observable validation
- Reduce risk early, add polish late

**Validation examples:**
- "tests pass"
- "builds successfully"
- "feature renders"
- "API returns expected response"

## Integration with /push

`/push` handles cleanup automatically:

```
For each active handoff:
  If ALL phases complete AND all files committed:
    → Move to archived[] with summary
    → Delete .md file (lives in git history)
    → Log: "Archived handoff: {title}"
  Else:
    → Keep as-is
```

This means:
- Incomplete handoffs persist across pushes
- Complete handoffs auto-archive only after code is committed
- Archived list provides history without clutter

## Multiple Handoffs

System supports multiple active handoffs.

**Session start summary:**
- 1 handoff: "1 active handoff: {id} (Phase N/M)"
- 2-3 handoffs: list them briefly
- 4+ handoffs: just count, offer to list on request

**When user says "continue":**
- 1 active: use it automatically
- Multiple active: ask which one
- Partial name works: "continue {partial}" matches by id or title

**Implicit handoff work:**
If user asks about something that overlaps an active handoff's scope, mention the connection: "This might relate to your {handoff} (Phase N covers this area). Work within that context, or treat as separate?" Let user decide.

## Example Flow

```
# Session 1: Analysis
User: /think [complex task]
Claude: [analyzes, proposes approach]
User: /handoff
Claude: Creates .claude/handoffs/{slug}.md + updates handoffs.json
        "Handoff created: {slug}. N phases. Ready for fresh session."

# Session 2: Execution with parallel agents
User: /handoff --continue
Claude: [reads handoffs.json, checks lastTouched, reads .md]
        "Continuing: {title}
         Phase 1/3: {name}
         Tasks:
         - Add user service (files: src/services/)
         - Add user API routes (files: src/routes/)
         - Add user tests (files: tests/)

         These tasks are independent. Spawning 3 parallel agents."

        [Spawns all agents in single message]
        ┌─────────────────────────────────────────┐
        │ Agent 1: Implement user service         │
        │ Agent 2: Implement API routes           │
        │ Agent 3: Write tests                    │
        └─────────────────────────────────────────┘

        [Agents complete, main validates:]
        "All agents complete. Validating changes..."
        [runs tests, checks for conflicts]

        "Phase 1 complete. Evidence: 12 tests pass, build succeeds.
         Learnings: Service pattern worked well.
         Starting Phase 2..."

# Session 3: Sequential phase (no parallel needed)
User: /handoff --continue
Claude: "Continuing: {title}
         Phase 2/3: Integration
         Tasks: Wire components together

         Single task with dependencies—handling directly."
        [executes, validates]
        "Phase 2 complete."

# When all phases done
User: /push
Claude: [pushes, archives handoff]
        "Archived handoff: {title}"
```

## Arguments

`--continue` — Resume an active handoff. If one active handoff exists, continues it automatically. If multiple exist, lists them and asks which one.

`--continue {id}` — Resume a specific handoff by id or partial match on title. Example: `/handoff --continue auth` matches handoff with id "user-authentication".

$ARGUMENTS
