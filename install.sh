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

echo ""
echo "Installation complete!"
echo ""
echo "Commands installed:"
echo "  /init-project  - Initialize new project"
echo "  /migrate       - Add tracking to existing project"
echo "  /commit        - Clean commits"
echo "  /push          - Push + update state"
echo "  /backlog       - Manage backlog"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to pick up new commands"
echo "  2. In a project, run /migrate or /init-project"
echo ""
