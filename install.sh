#!/bin/bash

# Claude Code Setup Installer
# https://github.com/ugzv/claude-code-setup

set -e

echo "Installing Claude Code Setup..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create directories
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/templates

# Clean up obsolete commands
if ls ~/.claude/commands/*.md >/dev/null 2>&1; then
  for file in ~/.claude/commands/*.md; do
    name=$(basename "$file")
    if [ ! -f "$SCRIPT_DIR/commands/$name" ]; then
      rm "$file"
      echo "Removed obsolete: $name"
    fi
  done
fi

# Copy files
echo "Installing commands..."
cp "$SCRIPT_DIR/commands/"*.md ~/.claude/commands/

echo "Installing templates..."
cp "$SCRIPT_DIR/templates/"*.md ~/.claude/templates/

# Configure settings (disable co-author in commits)
SETTINGS_FILE=~/.claude/settings.json

if [ -f "$SETTINGS_FILE" ]; then
  if grep -q '"attribution"' "$SETTINGS_FILE"; then
    echo "Settings already configured"
  else
    sed -i.bak 's/^{$/{\n  "attribution": {\n    "commit": ""\n  },/' "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "Updated settings.json"
  fi
else
  cat > "$SETTINGS_FILE" << 'EOF'
{
  "attribution": {
    "commit": ""
  }
}
EOF
  echo "Created settings.json"
fi

echo ""
echo "Done. Commands installed:"
echo ""
echo "  /migrate        Set up tracking in a project"
echo "  /think          Plan approach before complex tasks"
echo "  /fix            Auto-fix linting and formatting"
echo "  /test           Run tests intelligently"
echo "  /commit         Commit changes with clean messages"
echo "  /push           Push and update state tracking"
echo "  /health         Check project health"
echo "  /analyze        Find code that resists change"
echo "  /backlog        Review and manage backlog"
echo "  /agent          Audit Agent SDK projects"
echo "  /mcp            Validate MCP server projects"
echo "  /prompt-guide   Load prompting philosophy"
echo "  /commands       List project commands"
echo ""
echo "Next: Restart Claude Code, then run /migrate in a project"
echo ""
