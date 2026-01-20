# ABOUT THIS PROJECT

This is a **meta-project**: we're building a Claude Code command and tracking system here that gets installed and used in OTHER projects.

**When working here, you are:**
- Building/improving commands that other Claude sessions will use
- Testing and refining the tracking system itself
- The developer of the system, not just a user

**The chicken-egg situation:**
Running commands like `/analyze` or `/commit` on THIS project is both:
1. **Testing** - Does the command work correctly?
2. **Improving** - Use insights to make the command better

This is intentional. Eat your own dogfood.

**The commands in `.claude/commands/` are:**
- The SOURCE files that get copied to `~/.claude/commands/` via `install.sh`
- Meant to help developers in their actual coding projects
- Designed with philosophy-driven prompts (explain WHY, not just WHAT)

**When evaluating commands, ask:**
- "Would this help a developer during a real coding session?"
- "Is this command used frequently enough to justify existing?"
- "Could this be consolidated with another command?"

---

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

When user says "continue" or "resume" and there's an active handoff:

**Principles:**
- **Context first** — read the .md file for goal/philosophy; review prior learnings before acting
- **Parallel session awareness** — if `lastTouched` is recent, warn about possible conflict
- **No rushing** — you have abundant context; thoroughness over speed
- **Validate before marking complete** — concrete evidence must exist; stay in_progress if uncertain
- **Capture learnings** — what worked, what didn't, insights for future sessions
- **Clean handoffs** — if context runs low, update notes so next session continues seamlessly

**Parallel sessions:** Multiple handoffs = multiple sessions OK. Same handoff = one session only.

## Commands Available
- `/commit` - Commit changes (clean, no AI mentions)
- `/push` - Push + update state.json + archive completed handoffs
- `/backlog` - Review and manage backlog items
- `/handoff` - Create phased plan for fresh session execution

## Rules
- Only USER sets `currentFocus` - never assume or change it
- Add discoveries to backlog during `/push`, not randomly
- Keep backlog clean - resolve items when addressed
- **Handoffs**: Update `handoffs.json` progress after completing phases
- **Never commit on your own** - wait for user to run `/commit`. Exception: post-commit fixes (e.g., hook failures)

---
