---
description: Set up Claude tracking system (new or existing projects)
---

Set up the Claude tracking system. Non-destructive and idempotent.

## 1. Audit Existing Setup

```bash
ls -la CLAUDE.md .claude/ 2>/dev/null
```

Report what exists.

## 2. Show Setup Plan

Briefly report what will be created/modified, then proceed immediately. The user ran /migrate—that's explicit intent. Don't ask for confirmation.

## 3. Backup Existing Files

```bash
test -f CLAUDE.md && cp CLAUDE.md CLAUDE.md.backup
test -f .claude/settings.json && cp .claude/settings.json .claude/settings.json.backup
```

## 4. Create Structure

```bash
mkdir -p .claude
```

## 5. Handle CLAUDE.md

**Session protocol goes at TOP** so Claude sees it first.

- If already has "SESSION PROTOCOL" → skip
- If exists but no protocol → prepend protocol, keep existing content below
- If doesn't exist → create with protocol only

The protocol should state that:
1. State is auto-loaded via SessionStart hook
2. Summarize context before proceeding
3. Ask what to work on if no currentFocus

Include rules: only user sets currentFocus, add discoveries during /push, never commit without being asked.

## 6. Create/Update state.json

```json
{
  "project": "[detect from package.json/git/folder]",
  "currentFocus": [],
  "lastSession": {"date": "[today]", "summary": "Initialized tracking", "commits": []},
  "backlog": [],
  "shipped": []
}
```

If exists: upgrade `currentFocus` from null/string to array if needed.

## 7. Configure Hooks

Create/merge `.claude/settings.json` with SessionStart hook:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "cat .claude/state.json 2>/dev/null || echo '{\"note\": \"No state.json found. Run /migrate to set up tracking.\"}'"
      }]
    }]
  }
}
```

SessionStart fires on: startup, resume, /clear, context compaction.

## 8. Migrate Old Format (if found)

Check for `.claude/progress.md`, `changelog.json`, `backlog.json`. Migrate data and remove old files.

## 9. LSP Setup (Optional)

Detect project language, check if LSP works (`documentSymbol` on a main file). If not available, offer to install appropriate language server.

## 10. Update .gitignore

Add `.claude/*.backup` if not present.

## 11. Summary

Report what was created/modified. Done.

$ARGUMENTS
