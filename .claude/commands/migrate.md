---
description: Set up Claude tracking system (new or existing projects)
---

Set up the Claude tracking system. Works for both new and existing projects. NON-DESTRUCTIVE and IDEMPOTENT—safe to run multiple times.

## 1. Audit Existing Setup

```bash
ls -la CLAUDE.md .claude/ .claude/settings.json 2>/dev/null
cat CLAUDE.md 2>/dev/null | grep -c "SESSION PROTOCOL" || echo "0"
test -f .claude/state.json && echo "STATE_EXISTS" || echo "NO_STATE"
```

Report findings to user.

## 2. Show Setup Plan

BEFORE making changes, show:

```
SETUP PLAN
==========
CLAUDE.md:
  - [EXISTS/MISSING]
  - Has Session Protocol? [YES=skip / NO=prepend at TOP]

.claude/state.json:    [EXISTS=check format / MISSING=create]
  - currentFocus format: [array=ok / null/string=upgrade to array]
.claude/settings.json: [EXISTS=merge hooks / MISSING=create with hooks]

Hooks to configure:
  - SessionStart: Read state.json on startup, resume, /clear, compaction

Proceed? (y/n)
```

STOP and wait for confirmation.

## 3. Backup Existing Files

```bash
test -f CLAUDE.md && cp CLAUDE.md CLAUDE.md.backup
test -f .claude/settings.json && cp .claude/settings.json .claude/settings.json.backup
```

## 4. Create .claude Directory

```bash
mkdir -p .claude
```

## 5. Handle CLAUDE.md - PREPEND at TOP

**IMPORTANT: Session protocol goes at the TOP of CLAUDE.md so Claude sees it first!**

**If CLAUDE.md already has "SESSION PROTOCOL":**
- SKIP - already migrated

**If CLAUDE.md exists but no protocol:**
- Read existing content
- Create NEW file with protocol at TOP, then existing content below:

```markdown
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

[EXISTING CLAUDE.md CONTENT GOES HERE]
```

**If CLAUDE.md doesn't exist:**
- Create with just the protocol section above (without the placeholder line)

## 6. Create/Update State File (.claude/state.json)

**If it doesn't exist**, create it:

```json
{
  "project": "[detect from package.json name, git remote, or folder name]",
  "currentFocus": [],
  "lastSession": {
    "date": "[today]",
    "summary": "Initialized Claude tracking system",
    "commits": []
  },
  "backlog": [],
  "shipped": []
}
```

Note: `currentFocus` is an array to support multiple parallel Claude sessions. Each focus item looks like:
```json
{
  "description": "what you're working on",
  "files": ["src/auth.ts", "src/api/login.ts"],
  "started": "YYYY-MM-DD"
}
```

**If it exists**, check for format upgrades:
- If `currentFocus` is `null` or a string → convert to `[]`
- If `currentFocus` is already an array → leave it alone

## 7. Configure Hooks (.claude/settings.json)

Create or merge into `.claude/settings.json`:

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

**SessionStart fires on:** startup, resume, /clear, and context compaction - all scenarios where Claude needs fresh context.

**If settings.json already exists:**
- Read existing content
- Merge the hooks (don't overwrite other settings)
- If SessionStart hook already exists for state.json, skip

## 8. Remove Old Files (if migrating from previous version)

Check for old format files:
```bash
ls .claude/progress.md .claude/changelog.json .claude/backlog.json 2>/dev/null
```

If found, ask: "Found old tracking files. Migrate data to state.json and remove them?"

If yes:
- Read progress.md → extract to lastSession.summary
- Read changelog.json → extract recent entries to shipped
- Read backlog.json → merge into backlog
- Remove old files after migration

## 9. Update .gitignore (Optional)

Ask: "Add `.claude/*.backup` to .gitignore? (recommended)"

If yes:
```bash
echo ".claude/*.backup" >> .gitignore
```

## 10. Summary

```
SETUP COMPLETE
==============
Created:
  ✓ .claude/state.json
  ✓ .claude/settings.json (with hooks)

Modified:
  ✓ CLAUDE.md (protocol prepended at TOP)

Backups:
  • CLAUDE.md.backup
  • .claude/settings.json.backup (if existed)

Hooks configured:
  • SessionStart → reads state.json on startup/resume/clear/compaction

Next steps:
  1. Review CLAUDE.md - customize if needed
  2. Update .claude/state.json with current project state
  3. Delete .backup files when satisfied
  4. Commit: git add CLAUDE.md .claude/ && git commit -m "chore: add Claude tracking"
```

## 11. Commit (Optional)

Ask: "Commit tracking files now?"

If yes:
```bash
git add CLAUDE.md .claude/state.json .claude/settings.json
git commit -m "chore: set up Claude tracking system"
```

Do NOT add .backup files.

$ARGUMENTS
