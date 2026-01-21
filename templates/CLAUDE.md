# SESSION PROTOCOL

> **IMPORTANT: Follow this protocol at the start of EVERY conversation and after /clear**

## On Session Start

1. **State is auto-loaded** via SessionStart hook (state.json + handoffs.json)

2. **Brief summary** (don't force handoff engagement):
   ```
   "Last session: [X]. [N] backlog items.
   [If handoffs exist: '1 active handoff: auth-system (Phase 2/3)']
   What would you like to work on?"
   ```

3. **Let user drive** — they might:
   - Say "continue auth" → pick up the handoff
   - Say "start the server" → do that, handoff stays pending
   - Say "what's the handoff about?" → explain it
   - Say anything else → do that

**Don't ask "Continue?" about handoffs** — just mention they exist. User decides.

## Resuming Handoffs

When user runs `/handoff --continue` or says "continue" and there's an active handoff:

1. **Read the handoff file** (`.claude/handoffs/{id}.md`) for goal, phases, and learnings
2. **Check `lastTouched`** — if recent, warn about possible session conflict
3. **Update `handoffs.json`** as you complete phases (set `status: "complete"`, add `learnings`)
4. **Capture insights** — what worked, what didn't, for future sessions

**Principles:**
- **Context first** — review prior learnings before acting
- **No rushing** — thoroughness over speed
- **Validate before marking complete** — concrete evidence must exist
- **Clean handoffs** — if context runs low, update notes so next session continues seamlessly

**Parallel sessions:** Multiple handoffs = multiple sessions OK. Same handoff = one session only.

## Commands Available
- `/commit` - Commit changes (clean, no AI mentions)
- `/push` - Push + update state.json + clean up completed handoffs
- `/backlog` - Review and manage backlog items
- `/handoff` - Create handoff (`--continue` to resume active one)

## Rules
- Only USER sets `currentFocus` - never assume or change it
- Add discoveries to backlog during `/push`, not randomly
- Keep backlog clean - resolve items when addressed
- **Never commit on your own** - wait for user to run `/commit`
- **Handoffs**: Update `handoffs.json` progress after completing phases

---

# Project Name

[Add project-specific instructions below this line]
