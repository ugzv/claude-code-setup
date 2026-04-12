---
description: "Set up project tracking system (new or existing projects)"
---

Set up the project tracking system for the current CLI. Non-destructive and idempotent.

## 0. Determine Target CLI

First determine which CLI is running this command:

- **Claude Code** → project protocol file is `CLAUDE.md`, template is `~/.claude/templates/CLAUDE.md`, user settings are `~/.claude/settings.json`
- **Codex CLI** → project protocol file is `AGENTS.md`, template is `~/.codex/templates/AGENTS.md`, user config is `~/.codex/config.toml`

If the current CLI is obvious from the environment, use it.

If not obvious, infer from what already exists:
- If only `CLAUDE.md` exists, prefer Claude
- If only `AGENTS.md` exists, prefer Codex
- If both exist, prefer the current CLI and leave the sibling file alone

If still ambiguous, ask one concise question before modifying the protocol file.

State which target you chose before proceeding.

## 1. Audit Existing Setup

```bash
ls -la CLAUDE.md AGENTS.md .state/ .claude/ 2>/dev/null
```

Report what exists.

## 2. Show Setup Plan

Briefly report what will be created/modified, then proceed immediately. The user ran /migrate—that's explicit intent. Don't ask for confirmation.

## 3. Backup Existing Files

```bash
test -f CLAUDE.md && cp CLAUDE.md CLAUDE.md.backup
test -f AGENTS.md && cp AGENTS.md AGENTS.md.backup
test -f .state/state.json && cp .state/state.json .state/state.json.backup
test -f .state/handoffs.json && cp .state/handoffs.json .state/handoffs.json.backup
test -d .state/handoffs && cp -R .state/handoffs .state/handoffs.backup
test -f .claude/state.json && cp .claude/state.json .claude/state.json.backup
test -f .claude/handoffs.json && cp .claude/handoffs.json .claude/handoffs.json.backup
test -d .claude/handoffs && cp -R .claude/handoffs .claude/handoffs.backup
test -f .claude/settings.json && cp .claude/settings.json .claude/settings.json.backup
```

Backups ensure nothing is lost. User can restore if needed.

## 4. Create Structure

```bash
mkdir -p .state/handoffs
```

## 5. Handle the Protocol File

**Session protocol goes at TOP** so the CLI sees it first.

- First set:
  - `PROJECT_PROTOCOL_FILE` = `CLAUDE.md` or `AGENTS.md`
  - `USER_TEMPLATE` = matching template path for the current CLI

- If the protocol file doesn't exist → create from the matching template
- If it exists but has no session protocol → prepend protocol from the matching template, keep ALL existing content below
- If it has protocol but is missing the current template's newer sections:
  1. Find the `# SESSION PROTOCOL` section
  2. Find where it ends (next `---` or `#` heading at same level)
  3. **Preserve any custom rules** the user added (look for additions after "## Rules")
  4. Replace protocol with template version
  5. Re-add any custom rules that were preserved
- If fully up to date → skip

**Key: Never lose user customizations.** If unsure, ask before modifying.

**Do not overwrite the sibling protocol file automatically.** For example, if migrating from Codex, update `AGENTS.md` and leave any existing `CLAUDE.md` alone unless the user explicitly asks to sync both.

## 6. Create/Update `.state/state.json`

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

**Path rules:**
- Use `.state/state.json` as the source of truth
- If `.state/state.json` is missing but legacy `.claude/state.json` exists, migrate/copy the legacy data into `.state/state.json` first
- If both exist, prefer `.state/state.json` and do not overwrite it with legacy content
- If legacy `.claude/handoffs.json` or `.claude/handoffs/` exist and `.state/` copies do not, migrate them into `.state/`

## 7. Verify CLI Integration

### If target is Claude Code

SessionStart hooks are installed at **user level** (`~/.claude/settings.json`) by `install.py`. They load `.state/state.json` and `.state/handoffs.json` on session start, with legacy `.claude/...` fallback during migration.

**Check if installed:**
```bash
cat ~/.claude/settings.json | grep -q "session-start.py" && echo "Hooks installed" || echo "Run install.py first"
```

**If not installed:** Tell the user to run `install.py` from the claude-code-setup repo.

**Project-level settings** (`.claude/settings.json`) are for project-specific overrides only—don't duplicate the SessionStart hooks here.

### If target is Codex CLI

Codex CLI does **not** support SessionStart hooks yet. The session protocol lives in `AGENTS.md`, so no hook check is required.

**Check if installed:**
```bash
test -f ~/.codex/skills/claude-code-setup-migrate/SKILL.md && echo "Skills installed" || echo "Run install.py --cli codex first"
```

If the Codex template or skills were not installed, tell the user to run `python install.py --cli codex` from the claude-code-setup repo.

## 8. Clean Up Old Project-Level Hooks

Old versions of `/migrate` installed SessionStart hooks at project level with `python -c` one-liners that break on Windows. These are legacy Claude artifacts and should be removed if present.

**Check for old hooks:**
```bash
cat .claude/settings.json 2>/dev/null | grep -q "SessionStart" && echo "Found project-level SessionStart hooks"
```

**If found:** Read `.claude/settings.json`, remove the `SessionStart` key from `hooks`, and write back. If the file becomes `{"hooks": {}}` or `{}`, leave it (harmless) or remove the hooks key entirely.

**Why:** User-level hooks handle this now for Claude. For Codex they are unused noise. In both cases, project-level duplicates are wrong.

## 9. Migrate Legacy Runtime State (if found)

Check for legacy runtime files and move them into `.state/`:
- `.claude/state.json` → `.state/state.json`
- `.claude/handoffs.json` → `.state/handoffs.json`
- `.claude/handoffs/` → `.state/handoffs/`

After confirming the `.state/` copies exist and are valid, **delete the legacy copies**:
```bash
# Only after .state/ versions are verified
rm -f .claude/state.json .claude/state.json.backup
rm -f .claude/handoffs.json .claude/handoffs.json.backup
rm -rf .claude/handoffs .claude/handoffs.backup
```

Do **not** delete `.claude/settings.json` or `.claude/commands/` — those belong to the CLI, not to session state.

Also check for older formats like `.claude/progress.md`, `changelog.json`, `backlog.json`. Migrate data and remove old files.

## 10. LSP Setup (Optional)

Detect project language, check if LSP works (`documentSymbol` on a main file). If not available, offer to install appropriate language server.

## 11. Hide State from Git

**Goal:** Keep `.state/` out of version control without leaking its existence into the committed `.gitignore`.

Use `.git/info/exclude` (local-only, never committed) instead of `.gitignore`:

```bash
mkdir -p .git/info
touch .git/info/exclude
```

Add these lines to `.git/info/exclude` if not already present:
```
.state/
```

This single rule covers everything — state, handoffs, backups. No need for granular patterns.

If `.gitignore` currently has `.state/` rules from a prior migration, **remove them** — they belong in exclude now.

**Why not `.gitignore`?** The `.gitignore` is committed and public. Adding `.state/` there tells anyone reading the repo that a tracking system exists. `.git/info/exclude` is local-only and invisible to collaborators.

## 12. Summary

Report what was created/modified. Done.

$ARGUMENTS
