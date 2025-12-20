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
echo ""
echo "  Setup:"
echo "    /migrate       - Set up tracking (new or existing projects)"
echo ""
echo "  Development:"
echo "    /fix           - Auto-fix linting, formatting, unused imports"
echo "    /test          - Run tests"
echo "    /commit        - Clean commits"
echo "    /commit-all    - Batch commit all changes"
echo "    /push          - Push + update state"
echo ""
echo "  Analysis:"
echo "    /health        - Project health check (includes TODO scanning)"
echo "    /refactor      - Find refactoring opportunities (includes dead code)"
echo "    /deps          - Update dependencies"
echo ""
echo "  Prompting:"
echo "    /prompt        - Load philosophy, apply to any prompt work"
echo ""
echo "  Context:"
echo "    /context       - Quick project orientation"
echo "    /backlog       - Manage backlog items"
echo "    /commands      - List project commands"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to pick up new commands"
echo "  2. In a project, run /migrate to set up tracking"
echo ""
