---
description: Review and manage backlog items
---

Review, clean up, and manage backlog items in `.claude/state.json`.

## 1. Read Current Backlog

```bash
cat .claude/state.json 2>/dev/null || echo "NO_STATE_FILE"
```

If no state file exists, inform user: "No state.json found. Run `/migrate` first."

## 2. Display Backlog Summary

Show all items grouped by status:

```
BACKLOG SUMMARY
===============

Open (3):
  #1 [tech-debt] Refactor status constants into enum
     Context: Found while fixing typing indicator
     Added: 2025-12-17

  #2 [bug] Mobile menu doesn't close on navigation
     Context: Noticed during dark mode testing
     Added: 2025-12-16

  #3 [idea] Add keyboard shortcuts for common actions
     Context: User mentioned in feedback
     Added: 2025-12-15

Recently Resolved (2):
  #4 [improvement] Add loading spinner - resolved 2025-12-17
  #5 [tech-debt] Remove unused imports - resolved 2025-12-16
```

## 3. Ask What To Do

```
What would you like to do?
1. Mark item(s) as resolved
2. Mark item(s) as wont-do
3. Remove item(s) completely
4. Add new item
5. Edit an item
6. Clean up (remove all resolved items older than 7 days)
7. Done - exit
```

Wait for user response.

## 4. Handle Actions

**Mark as resolved:**
- Ask: "Which item numbers? (e.g., 1,3)"
- Update status to "resolved", set resolved date to today

**Mark as wont-do:**
- Ask: "Which item numbers?"
- Ask: "Brief reason?" (optional)
- Update status to "wont-do", set resolved date, add reason

**Remove items:**
- Ask: "Which item numbers?"
- Confirm: "Remove items #X, #Y permanently?"
- Delete from array

**Add new item:**
- Ask: "Task description?"
- Ask: "Type? (tech-debt / bug / idea / improvement)"
- Ask: "Priority? (high / medium / low)"
- Ask: "Any context?"
- Add to backlog with status "open", today's date

**Edit item:**
- Ask: "Which item number?"
- Show current values
- Ask what to change

**Clean up:**
- Remove all resolved/wont-do items older than 7 days
- Report: "Removed X old items"

## 5. Save Changes

After any modification:
- Write updated state.json
- Show brief confirmation

## 6. Arguments

If `$ARGUMENTS` contains:
- `clean` → Jump directly to cleanup action
- `add <description>` → Jump to add with pre-filled description
- A number → Show details for that item

$ARGUMENTS
