#!/bin/bash
# Claude Code Setup - Shell wrapper for install.py
# Requires Python 3.8+

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    echo "Install with: brew install python3"
    exit 1
fi

python3 "$SCRIPT_DIR/install.py" "$@"
