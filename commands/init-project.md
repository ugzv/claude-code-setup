---
description: Initialize new project with Claude tracking system
---

Set up the Claude tracking system for a NEW project. For existing projects with CLAUDE.md, use `/migrate` instead.

## 1. Check If Already Initialized

```bash
test -f CLAUDE.md && echo "CLAUDE_EXISTS"
test -f .claude/state.json && echo "STATE_EXISTS"
```

If either exists, warn: "Project may already be initialized. Use `/migrate` instead to safely add tracking. Continue anyway? (y/n)"

## 2. Gather Project Info

Detect project name:
```bash
cat package.json 2>/dev/null | grep '"name"' | head -1
git remote get-url origin 2>/dev/null
basename $(pwd)
```

Ask: "Project name detected as `[name]`. Correct? Or enter different name:"

## 3. Create Directory Structure

```bash
mkdir -p .claude
```

## 4. Create CLAUDE.md

Create with session protocol at TOP:

```markdown
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

# [Project Name]

[Add project-specific instructions below this line]
```

## 5. Create State File (.claude/state.json)

Ask: "What's the current focus for this project? (or leave empty)"

```json
{
  "project": "[project name]",
  "currentFocus": "[user input or null]",
  "lastSession": {
    "date": "[today]",
    "summary": "Project initialized with Claude tracking system",
    "commits": []
  },
  "backlog": [],
  "shipped": []
}
```

## 6. Configure Hooks (.claude/settings.json)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/state.json 2>/dev/null || echo '{\"note\": \"No state.json found. Run /migrate to set up tracking.\"}'"
          }
        ]
      }
    ]
  }
}
```

**SessionStart fires on:** startup, resume, /clear, and context compaction.

## 7. Update .gitignore

Ask: "Add `.claude/*.backup` to .gitignore? (recommended)"

If yes and .gitignore exists:
```bash
echo ".claude/*.backup" >> .gitignore
```

## 8. Summary

```
PROJECT INITIALIZED
===================
Created:
  ✓ CLAUDE.md (with session protocol)
  ✓ .claude/state.json
  ✓ .claude/settings.json (with hooks)

Hooks configured:
  • SessionStart → reads state.json on startup/resume/clear/compaction

Commands available:
  • /commit - clean commits
  • /push - push + update state
  • /backlog - manage backlog

Next: Start working! Use /push when ready to ship.
```

## 9. Initial Commit (Optional)

Ask: "Create initial commit with tracking files?"

If yes:
```bash
git add CLAUDE.md .claude/
git commit -m "chore: initialize Claude tracking system"
```

$ARGUMENTS
