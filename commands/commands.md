---
description: "List available Claude Code commands and Codex skills"
---

List the custom commands or skills available for Claude Code and Codex CLI.

## How to Find Commands

Check these locations and include any that exist:

```bash
for f in ~/.claude/commands/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

```bash
for f in .claude/commands/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

```bash
for f in ~/.codex/skills/*/SKILL.md; do [ -f "$f" ] && display="$(grep -m1 'display_name:' "${f%/SKILL.md}/agents/openai.yaml" 2>/dev/null | cut -d: -f2- | sed 's/^ *//' )"; desc="$(grep -m1 'short_description:' "${f%/SKILL.md}/agents/openai.yaml" 2>/dev/null | cut -d: -f2- | sed 's/^ *//' )"; [ -n "$display" ] || display="$(basename "$(dirname "$f")")"; [ -n "$desc" ] || desc="$(grep -m1 '^description:' "$f" | cut -d: -f2-)"; echo "$display: $desc"; done
```

```bash
for f in .codex/skills/*/SKILL.md; do [ -f "$f" ] && display="$(grep -m1 'display_name:' "${f%/SKILL.md}/agents/openai.yaml" 2>/dev/null | cut -d: -f2- | sed 's/^ *//' )"; desc="$(grep -m1 'short_description:' "${f%/SKILL.md}/agents/openai.yaml" 2>/dev/null | cut -d: -f2- | sed 's/^ *//' )"; [ -n "$display" ] || display="$(basename "$(dirname "$f")")"; [ -n "$desc" ] || desc="$(grep -m1 '^description:' "$f" | cut -d: -f2-)"; echo "$display: $desc"; done
```

Legacy compatibility locations:

```bash
for f in ~/.codex/prompts/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

```bash
for f in .codex/prompts/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

## Output Format

Present one section per location that has files:
```
CLAUDE USER COMMANDS
  /backlog     - Review and manage backlog items
  /commit      - Clean commits
  ...

CLAUDE PROJECT COMMANDS
  /deploy      - Deploy to staging
  ...

CODEX USER SKILLS
  /commit      - Commit changes [select from /skills]
  /migrate     - Set up tracking [select from /skills]
  ...

CODEX PROJECT SKILLS
  /deploy      - Deploy to staging
  ...

CODEX USER PROMPTS (LEGACY)
  /prompt-guide - Legacy custom prompt installation for older Codex builds
  ...
```

If only one location has files, show just that section.

If the user asks about a specific command, read that command's file and explain what it does.

$ARGUMENTS
