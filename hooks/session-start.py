#!/usr/bin/env python3
"""Cross-platform SessionStart hook for Claude Code.

Outputs state.json and handoffs.json contents on session start.
Handles missing files gracefully without errors.
"""
import os
import sys

def read_file(path):
    """Read file if exists, return None otherwise."""
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception:
        pass
    return None

def main():
    # State file
    state_path = '.claude/state.json'
    state_content = read_file(state_path)
    if state_content:
        print(f'=== {state_path} ===')
        print(state_content)
    else:
        print(f'=== {state_path} ===')
        print('{"note": "No state.json found. Run /migrate to set up tracking."}')

    # Handoffs file
    handoffs_path = '.claude/handoffs.json'
    handoffs_content = read_file(handoffs_path)
    if handoffs_content:
        print(f'=== {handoffs_path} ===')
        print(handoffs_content)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Fail silently - don't break session start
        print(f'=== .claude/state.json ===')
        print('{"note": "Hook error"}')
        sys.exit(0)  # Exit cleanly even on error
