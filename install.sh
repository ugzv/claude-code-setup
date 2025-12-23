#!/bin/bash

# Claude Code Setup Installer
# https://github.com/ugzv/claude-code-setup

set -e

echo "Installing Claude Code Setup..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create directories
echo "Creating directories..."
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/templates

# Copy commands
echo "Installing commands..."
cp "$SCRIPT_DIR/commands/"*.md ~/.claude/commands/

# Copy templates
echo "Installing templates..."
cp "$SCRIPT_DIR/templates/"*.md ~/.claude/templates/

# Configure settings (disable co-author in commits)
echo "Configuring settings..."
SETTINGS_FILE=~/.claude/settings.json

if [ -f "$SETTINGS_FILE" ]; then
  # Check if attribution already exists
  if grep -q '"attribution"' "$SETTINGS_FILE"; then
    echo "  Attribution already configured, skipping..."
  else
    # Add attribution to existing settings (after opening brace)
    sed -i.bak 's/^{$/{\n  "attribution": {\n    "commit": ""\n  },/' "$SETTINGS_FILE" && rm -f "$SETTINGS_FILE.bak"
    echo "  Added attribution settings"
  fi
else
  # Create new settings file
  cat > "$SETTINGS_FILE" << 'EOF'
{
  "attribution": {
    "commit": ""
  }
}
EOF
  echo "  Created settings.json"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Commands installed:"
echo ""
echo "  Setup:"
echo "    /migrate       - Set up tracking (new or existing projects)"
echo ""
echo "  Planning:"
echo "    /think         - Think through approach before complex tasks"
echo ""
echo "  Development:"
echo "    /fix           - Auto-fix linting, formatting, unused imports"
echo "    /test          - Run tests"
echo "    /commit        - Clean commits (use --all for batch)"
echo "    /push          - Push + update state"
echo ""
echo "  Analysis:"
echo "    /health        - Project health check (TODO, deps, security)"
echo "    /analyze       - Find refactoring opportunities (includes dead code)"
echo "    /agent         - Audit Agent SDK projects"
echo "    /mcp           - Test MCP server projects"
echo ""
echo "  Prompting:"
echo "    /prompt-guide  - Load philosophy, apply to any prompt work"
echo ""
echo "  Context:"
echo "    /backlog       - Manage backlog items"
echo "    /commands      - List project commands"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to pick up new commands"
echo "  2. In a project, run /migrate to set up tracking"
echo ""
