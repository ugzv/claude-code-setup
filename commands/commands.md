---
description: List project commands
---

List the custom commands available.

## How to Find Commands

Run these commands (single line each):

```bash
for f in ~/.claude/commands/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

```bash
for f in .claude/commands/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

## Output Format

Present as two sections if both exist:
```
USER COMMANDS
  /backlog     - Review and manage backlog items
  /commit      - Clean commits
  ...

PROJECT COMMANDS
  /deploy      - Deploy to staging
  ...
```

If only one location has commands, show just that section without the header.

If the user asks about a specific command, read that command's file and explain what it does.

$ARGUMENTS
