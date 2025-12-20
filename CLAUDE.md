# ABOUT THIS PROJECT

This is a **meta-project**: we're building a Claude Code command and tracking system here that gets installed and used in OTHER projects.

**When working here, you are:**
- Building/improving commands that other Claude sessions will use
- Testing and refining the tracking system itself
- NOT a user of the system—you're the developer of it

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

1. **Read Project State**:
   ```bash
   cat .claude/state.json
   ```

2. **Understand Context**:
   - `currentFocus` → Array of active work (multiple sessions supported)
   - `lastSession` → What happened last time
   - `backlog` → Open items to potentially work on
   - `shipped` → Recent completions

3. **Summarize**: Briefly state your understanding before proceeding:
   ```
   "Based on state.json: Last session you [X]. Current focus is [Y].
   There are [N] open backlog items. Ready to continue."
   ```

4. **If no currentFocus**: Ask "What should we work on today?"

## Commands Available
- `/commit` - Commit changes (clean, no AI mentions)
- `/push` - Push + update state.json + backlog check
- `/backlog` - Review and manage backlog items

## Rules
- Only USER sets `currentFocus` - never assume or change it
- Add discoveries to backlog during `/push`, not randomly
- Keep backlog clean - resolve items when addressed
- **Never commit on your own** - wait for user to run `/commit`. Exception: post-commit fixes (e.g., hook failures)

---
