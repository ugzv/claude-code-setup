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

## 7. Verify Hooks

SessionStart hooks are installed at **user level** (`~/.claude/settings.json`) by `install.py`. They load `state.json` and `handoffs.json` on session start.

**Check if installed:**
```bash
cat ~/.claude/settings.json | grep -q "session-start.py" && echo "Hooks installed" || echo "Run install.py first"
```

**If not installed:** Tell user to run `install.py` from the claude-code-setup repo.

**Project-level settings** (`.claude/settings.json`) are for project-specific overrides only—don't duplicate the SessionStart hooks here.

## 8. Clean Up Old Project-Level Hooks

Old versions of `/migrate` installed SessionStart hooks at project level with `python -c` one-liners that break on Windows. These must be removed.

**Check for old hooks:**
```bash
cat .claude/settings.json 2>/dev/null | grep -q "SessionStart" && echo "Found project-level SessionStart hooks"
```

**If found:** Read `.claude/settings.json`, remove the `SessionStart` key from `hooks`, and write back. If the file becomes `{"hooks": {}}` or `{}`, leave it (harmless) or remove the hooks key entirely.

**Why:** User-level hooks handle this now. Project-level duplicates cause errors and run twice.

## 9. Migrate Old Format (if found)

Check for `.claude/progress.md`, `changelog.json`, `backlog.json`. Migrate data and remove old files.

## 10. LSP Setup (Optional)

Detect project language, check if LSP works (`documentSymbol` on a main file). If not available, offer to install appropriate language server.

## 11. Update .gitignore

**Goal:** Track `.claude/` in git (for multi-PC sync) but ignore backup files.

1. If `.gitignore` contains `.claude/` or `.claude` → **remove it** (user wants tracking)
2. Add `.claude/*.backup` if not present (backups don't need tracking)

## 12. Summary

Report what was created/modified. Done.

$ARGUMENTS
