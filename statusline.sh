#!/bin/bash

# Claude Code Statusline
# Minimal, monochrome with semantic color shifts
# Format: model │ branch │ ●●●●○○○○○○ 42%

# ANSI codes
RESET='\033[0m'
DIM='\033[2m'
BOLD='\033[1m'
YELLOW='\033[33m'
RED='\033[31m'

# Read JSON from stdin
input=$(cat)

# Parse values (single jq call for efficiency)
eval "$(echo "$input" | jq -r '
    @sh "model=\(.model // "claude" | ascii_downcase | sub("^claude-";"") | sub("-\\d.*$";""))",
    @sh "percent=\(.context_window.used_percentage // 0)"
')"

# Get git branch
branch=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git branch --show-current 2>/dev/null)
fi

# Build progress bar (10 dots)
filled=$((percent / 10))
[ $filled -gt 10 ] && filled=10
empty=$((10 - filled))

# Choose color based on usage (only bar changes)
if [ $percent -ge 90 ]; then
    color="$RED"
elif [ $percent -ge 75 ]; then
    color="$YELLOW"
elif [ $percent -ge 60 ]; then
    color="$BOLD"
else
    color=""
fi

# Build the bar
bar=""
for ((i=0; i<filled; i++)); do
    bar="${bar}●"
done
for ((i=0; i<empty; i++)); do
    bar="${bar}○"
done

# Output - uniform when calm, bar+percent get color when attention needed
if [ -n "$branch" ]; then
    printf "%s │ %s │ ${color}%s  %d%%${RESET}" "$model" "$branch" "$bar" "$percent"
else
    printf "%s │ ${color}%s  %d%%${RESET}" "$model" "$bar" "$percent"
fi
