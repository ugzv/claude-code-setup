# SESSION PROTOCOL

> **IMPORTANT: Follow this protocol at the start of EVERY conversation and after /clear**

## On Session Start

1. **Read Project State**:
   ```bash
   cat .claude/state.json
   ```

2. **Understand Context**:
   - `currentFocus` → What we're working on (set by user)
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

---

# Project Name

[Add project-specific instructions below this line]
