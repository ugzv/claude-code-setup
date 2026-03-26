---
description: "List available Claude Code commands and Codex prompts"
---

List the custom commands or prompts available for Claude Code and Codex CLI.

## How to Find Commands

Check these locations and include any that exist:

```bash
for f in ~/.claude/commands/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

```bash
for f in .claude/commands/*.md; do [ -f "$f" ] && echo "$(basename "$f" .md): $(grep -m1 '^description:' "$f" | cut -d: -f2-)"; done
```

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

CODEX USER PROMPTS
  /prompt-guide - Prompting philosophy for agent work
  ...

CODEX PROJECT PROMPTS
  /deploy      - Deploy to staging
  ...
```

If only one location has files, show just that section.

If the user asks about a specific command, read that command's file and explain what it does.

$ARGUMENTS
