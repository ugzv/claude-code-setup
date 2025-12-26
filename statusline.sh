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

# Parse values
model=$(echo "$input" | jq -r '.model.display_name // "claude"' | tr '[:upper:]' '[:lower:]')
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
usage=$(echo "$input" | jq -r '.context_window.current_usage // empty')

# Calculate context percentage
if [ -n "$usage" ] && [ "$usage" != "null" ]; then
    input_tokens=$(echo "$usage" | jq -r '.input_tokens // 0')
    cache_create=$(echo "$usage" | jq -r '.cache_creation_input_tokens // 0')
    cache_read=$(echo "$usage" | jq -r '.cache_read_input_tokens // 0')
    total_tokens=$((input_tokens + cache_create + cache_read))
    percent=$((total_tokens * 100 / context_size))
else
    percent=0
fi

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
    printf "%s │ %s │ ${color}%s  %d%%${RESET}\n" "$model" "$branch" "$bar" "$percent"
else
    printf "%s │ ${color}%s  %d%%${RESET}\n" "$model" "$bar" "$percent"
fi
