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
test -f .claude/state.json && cp .claude/state.json .claude/state.json.backup
test -f .claude/settings.json && cp .claude/settings.json .claude/settings.json.backup
```

Backups ensure nothing is lost. User can restore if needed.

## 4. Create Structure

```bash
mkdir -p .claude
```

## 5. Handle CLAUDE.md

**Session protocol goes at TOP** so Claude sees it first.

- If doesn't exist → create from template (`~/.claude/templates/CLAUDE.md`)
- If exists but no protocol → prepend protocol from template, keep ALL existing content below
- If has protocol but missing "Resuming Handoffs" section:
  1. Find the `# SESSION PROTOCOL` section
  2. Find where it ends (next `---` or `#` heading at same level)
  3. **Preserve any custom rules** the user added (look for additions after "## Rules")
  4. Replace protocol with template version
  5. Re-add any custom rules that were preserved
- If fully up to date → skip

**Key: Never lose user customizations.** If unsure, ask before modifying.

## 6. Create/Update state.json

**If doesn't exist**, create:
```json
{
  "project": "[detect from package.json/git/folder]",
  "currentFocus": [],
  "lastSession": {"date": "[today]", "summary": "Initialized tracking", "commits": []},
  "backlog": [],
  "shipped": []
}
```

**If exists**, preserve ALL existing data:
- Keep `currentFocus`, `backlog`, `shipped`, `lastSession` as-is
- Only upgrade format if needed (e.g., `currentFocus` from null/string → array)
- Never overwrite existing entries

## 7. Configure Hooks

Create/merge `.claude/settings.json` with SessionStart hooks:

**Required hooks:**
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [
        {
          "type": "command",
          "command": "python -c \"import os; f='.claude/state.json'; print('=== ' + f + ' ===' + chr(10) + (open(f).read() if os.path.exists(f) else '{\\\"note\\\": \\\"No state.json found. Run /migrate to set up tracking.\\\"}'))\"",
          "timeout": 5
        },
        {
          "type": "command",
          "command": "python -c \"import os; f='.claude/handoffs.json'; os.path.exists(f) and print('=== ' + f + ' ===' + chr(10) + open(f).read())\"",
          "timeout": 5
        }
      ]
    }]
  }
}
```

**Note:** Uses Python for cross-platform compatibility (works on Windows, macOS, Linux).

**Upgrade logic:**
- If no SessionStart hooks → add both
- If has state.json hook but missing handoffs.json hook → **add** the handoffs hook
- If has both → skip

SessionStart fires on: startup, resume, /clear, context compaction.

The second hook loads active handoffs (if any) so Claude knows what's in progress.

## 8. Migrate Old Format (if found)

Check for `.claude/progress.md`, `changelog.json`, `backlog.json`. Migrate data and remove old files.

## 9. LSP Setup (Optional)

Detect project language, check if LSP works (`documentSymbol` on a main file). If not available, offer to install appropriate language server.

## 10. Update .gitignore

Add `.claude/*.backup` if not present.

## 11. Summary

Report what was created/modified. Done.

$ARGUMENTS
