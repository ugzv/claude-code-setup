# SESSION PROTOCOL

> **IMPORTANT: Follow this protocol at the start of EVERY conversation and after /clear**

## On Session Start

1. **State is auto-loaded** via SessionStart hook

2. **Summarize** your understanding before proceeding:
   ```
   "Based on state.json: Last session you [X]. Current focus is [Y].
   There are [N] open backlog items. Ready to continue."
   ```

3. **If no currentFocus**: Ask "What should we work on today?"

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
