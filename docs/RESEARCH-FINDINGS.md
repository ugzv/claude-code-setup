# Claude Code Best Practices Research

> Research compiled: 2025-12-17
> Based on practices from experienced developers and official Anthropic recommendations

## Executive Summary

Your current setup is **well-aligned** with Anthropic's recommendations for long-running agents. The state management approach, SessionStart hook, and slash commands cover the core workflow. Below are findings from researching how power users maximize Claude Code, with specific suggestions for your setup.

---

## What Your Setup Does Well

### 1. State Persistence (Excellent)
Your `state.json` approach directly implements Anthropic's guidance on maintaining context for long-running agents. The separation of concerns (`currentFocus`, `lastSession`, `backlog`, `shipped`) is clean.

### 2. SessionStart Hook (Solid)
Automatically loading state at session start ensures Claude never loses context. This is a key pattern used by advanced users.

### 3. Clean Commits (Good Practice)
The `/commit` command enforcing conventional commits without AI mentions is aligned with professional workflows.

### 4. Backlog Management (Valuable)
Auto-discovery of tech debt during `/push` is a sophisticated feature that most setups lack.

---

## Suggestions for Improvement

### 1. Add Sub-agents for Specialized Tasks

**Why:** Sub-agents are "specialized mini-agents with their own system prompt, tool permissions, and independent context window." They reduce context pollution and improve reliability.

**Recommendation:** Add a `.claude/agents/` directory with specialized agents:

```markdown
# .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Review code changes for bugs, security issues, and best practices
tools: Read, Grep, Glob
---
You are a senior code reviewer. Focus on:
- Logic errors and edge cases
- Security vulnerabilities (OWASP top 10)
- Performance issues
- Code style consistency

Review the specified files and provide actionable feedback.
Do NOT make changes - only report issues.
```

```markdown
# .claude/agents/test-writer.md
---
name: test-writer
description: Generate tests for code changes
tools: Read, Write, Edit, Bash, Glob, Grep
---
You are a test engineer. Given code changes:
1. Analyze the code to understand behavior
2. Write comprehensive tests covering happy path and edge cases
3. Use the project's existing test framework/patterns
4. Run tests to verify they pass
```

### 2. Enhance CLAUDE.md with Project-Specific Pointers

**Why:** "Prefer pointers to copies. Don't include code snippets - they become out-of-date. Include `file:line` references instead."

**Current Issue:** Your CLAUDE.md template is protocol-focused but lacks guidance on WHERE to find things.

**Recommendation:** Add a "Project Map" section to the template:

```markdown
## Project Map

### Key Directories
- `src/` - Main source code
- `tests/` - Test files (run with `npm test`)
- `docs/` - Documentation

### Critical Files
- `src/config.ts:1-50` - All configuration options
- `src/types.ts` - Core type definitions
- `.env.example` - Required environment variables

### When Debugging
- For auth issues, start at `src/auth/index.ts`
- For API errors, check `src/api/client.ts:handleError`
```

### 3. Add Pre-Commit Hook for Quality Gates

**Why:** Hooks can run before edits are accepted (Prettier, type-check) or after (tests).

**Recommendation:** Add to settings.json template:

```json
{
  "hooks": {
    "SessionStart": [...],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Editing file - will run lint on save'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATH 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### 4. Add `/clear` Workflow Reminder

**Why:** "Use `/clear` often. Every time you start something new, clear the chat. You don't need all that history eating your tokens."

**Recommendation:** Add to CLAUDE.md protocol:

```markdown
## Context Hygiene
- Use `/clear` between distinct tasks
- After `/clear`, state.json is automatically reloaded via hook
- Don't let conversation grow beyond current task
```

### 5. Add Planning Mode Trigger

**Why:** "Asking Claude to research and plan first significantly improves performance for problems requiring deeper thinking upfront."

**Recommendation:** Create `/plan` command:

```markdown
# commands/plan.md
---
description: Research and plan before implementing
---

Before writing any code, follow this process:

## 1. Understand the Request
- What is the user asking for?
- What are the acceptance criteria?

## 2. Research the Codebase
- Find existing patterns for similar features
- Identify files that will need changes
- Note any constraints or dependencies

## 3. Create Implementation Plan
Write a numbered plan with:
- Files to create/modify
- Order of changes
- Potential risks or blockers

## 4. Get Approval
Present the plan and ask: "Does this approach look right?"

Only proceed to implementation after user approves.

$ARGUMENTS
```

### 6. Add Test-Driven Development Command

**Why:** "TDD becomes even more powerful with agentic coding."

**Recommendation:** Create `/tdd` command:

```markdown
# commands/tdd.md
---
description: Test-driven development workflow
---

Follow strict TDD for this feature:

## Phase 1: Write Tests FIRST
1. Write tests based on expected input/output
2. Do NOT write implementation yet
3. Run tests - they should FAIL

## Phase 2: Implement
1. Write minimal code to make tests pass
2. Run tests after each change
3. Stop as soon as tests pass

## Phase 3: Refactor (Optional)
1. Clean up implementation
2. Ensure tests still pass

IMPORTANT: Do NOT use mocks unless absolutely necessary.

$ARGUMENTS
```

### 7. Environment Variable Persistence in SessionStart

**Why:** SessionStart hooks can persist environment variables using `$CLAUDE_ENV_FILE`.

**Recommendation:** Enhance the SessionStart hook:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/state.json 2>/dev/null || echo '{\"note\": \"No state.json found.\"}'"
          },
          {
            "type": "command",
            "command": "test -f .env && echo 'PROJECT_HAS_ENV=true' >> \"$CLAUDE_ENV_FILE\" || true"
          },
          {
            "type": "command",
            "command": "git branch --show-current | xargs -I {} echo 'CURRENT_BRANCH={}' >> \"$CLAUDE_ENV_FILE\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### 8. Add MCP Server Documentation

**Why:** "MCP is Anthropic's open standard for connecting AI assistants to external tools and data sources."

**Recommendation:** Add a section to README about MCP integration:

```markdown
## Optional: MCP Integrations

For enhanced capabilities, configure MCP servers in `~/.claude/settings.json`:

### GitHub Integration
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

### Linear/Jira Integration
For issue tracking integration, see: https://modelcontextprotocol.io
```

### 9. Add Review Command Before Push

**Why:** "Despite its intelligence, always check every line."

**Recommendation:** Create `/review` command:

```markdown
# commands/review.md
---
description: Self-review changes before committing
---

Review all staged/unstaged changes:

## 1. Show Changes
```bash
git diff
git diff --cached
```

## 2. Self-Review Checklist
For each changed file, verify:
- [ ] No hardcoded secrets or credentials
- [ ] No debug console.logs left behind
- [ ] Error handling is appropriate
- [ ] No obvious performance issues
- [ ] Types are correct (if applicable)

## 3. Report
List any issues found. If clean, say "Ready to commit."

$ARGUMENTS
```

### 10. Parallel Instance Awareness

**Why:** "You can have multiple Claude Code instances running simultaneously."

**Recommendation:** Add to state.json a session lock:

```json
{
  "project": "my-app",
  "activeSession": {
    "pid": null,
    "startedAt": null
  },
  "currentFocus": "..."
}
```

Update SessionStart hook to check/set this, warning if another session may be active.

---

## Additional Tips from Power Users

### Keyboard Shortcuts
- `Ctrl+V` (not Cmd+V) to paste images
- `Escape` to stop Claude (not Ctrl+C)
- `Escape` twice to see message history

### Install GitHub App
Run `/install-github-app` to enable automatic PR reviews. "Claude often finds bugs that humans miss."

### Use `/compact` for Long Sessions
When context gets large, use `/compact` to summarize and free up tokens.

### Image Support
Claude Code can read images, PDFs, and Jupyter notebooks. Useful for:
- Debugging from screenshots
- Understanding design mockups
- Analyzing error reports

---

## Recommended Directory Structure

```
your-project/
├── CLAUDE.md                    # Session protocol + project map
├── .claude/
│   ├── state.json               # Session state
│   ├── settings.json            # Hooks configuration
│   ├── settings.local.json      # Personal settings (gitignored)
│   └── agents/                  # Sub-agents
│       ├── code-reviewer.md
│       ├── test-writer.md
│       └── debugger.md
└── ...
```

Global (user-level):
```
~/.claude/
├── settings.json                # User preferences
├── commands/                    # Global commands
│   ├── init-project.md
│   ├── commit.md
│   ├── push.md
│   ├── plan.md
│   ├── tdd.md
│   └── review.md
├── templates/                   # Templates
│   └── CLAUDE.md
└── agents/                      # Global agents
    └── researcher.md
```

---

## Sources

- [Claude Code: Best practices for agentic coding - Anthropic](https://www.anthropic.com/engineering/claude-code-best-practices)
- [How I use Claude Code (+ my best tips) - Builder.io](https://www.builder.io/blog/claude-code)
- [How I Use Every Claude Code Feature - Shrivu Shankar](https://blog.sshh.io/p/how-i-use-every-claude-code-feature)
- [Claude Code Best Practices: Tips from Power Users 2025 - Sidetool](https://www.sidetool.co/post/claude-code-best-practices-tips-power-users-2025/)
- [Get started with Claude Code hooks - Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)
- [Subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Best practices for Claude Code subagents - PubNub](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)
- [VoltAgent/awesome-claude-code-subagents - GitHub](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [Writing a good CLAUDE.md - HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [Claude Code Configuration Guide - ClaudeLog](https://claudelog.com/configuration/)

---

## Implementation Priority

| Priority | Suggestion | Effort | Impact |
|----------|------------|--------|--------|
| High | Add sub-agents (code-reviewer, test-writer) | Medium | High |
| High | Add `/plan` command | Low | High |
| High | Enhance CLAUDE.md with project pointers | Low | Medium |
| Medium | Add `/tdd` command | Low | Medium |
| Medium | Add pre/post hooks for formatting | Medium | Medium |
| Medium | Add `/review` command | Low | Medium |
| Low | Add MCP documentation | Low | Low |
| Low | Add parallel instance awareness | Medium | Low |
