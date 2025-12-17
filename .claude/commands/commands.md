---
description: List project commands
---

List the custom commands available.

Check both locations for commands:
1. **User-level**: `~/.claude/commands/` (shared across all projects)
2. **Project-level**: `.claude/commands/` (project-specific)

For each `.md` file found, extract the `description:` from frontmatter.

Present as two sections if both exist:
```
USER COMMANDS (~/.claude/commands/)
  /backlog     - Review and manage backlog items
  /commit      - Clean commits
  ...

PROJECT COMMANDS (.claude/commands/)
  /deploy      - Deploy to staging
  ...
```

If only one location has commands, show just that section without the header.

If the user asks about a specific command, read that command's file and explain what it does.

$ARGUMENTS
