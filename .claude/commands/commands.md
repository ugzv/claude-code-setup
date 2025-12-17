---
description: List project commands
---

List the custom commands available.

## How to Find Commands

Use bash to list commands from both locations:

```bash
# User-level commands (expand ~ properly)
ls ~/.claude/commands/*.md 2>/dev/null | while read f; do
  name=$(basename "$f" .md)
  desc=$(grep -m1 "^description:" "$f" | sed 's/description: *//')
  echo "/$name - $desc"
done

# Project-level commands
ls .claude/commands/*.md 2>/dev/null | while read f; do
  name=$(basename "$f" .md)
  desc=$(grep -m1 "^description:" "$f" | sed 's/description: *//')
  echo "/$name - $desc"
done
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
