---
description: Analyze codebase for refactoring opportunities
---

You are investigating what would make this codebase more maintainable.

## Two Modes of Analysis

**Proactive (default):** What SHOULD be better according to best practices—regardless of whether it's caused problems yet.

**Historical (`$ARGUMENTS` contains `--history`):** What HAS caused problems based on git history and bug patterns.

Most codebases need proactive analysis. Historical analysis is useful when you suspect specific pain points but can't pinpoint them.

## Why Evidence Still Matters

Anyone can say "add more tests" or "this needs error handling." That's generic advice, not analysis.

What makes your analysis valuable is **specificity**: "These 4 services have no test files. This function handles 3 API calls with no try/except. These 12 functions have no type hints in a typed codebase."

**If you can't point to specific files and lines, you don't have a finding.**

## Phase 1: Project Detection

Before spawning analyzers, understand what you're analyzing:

```
1. Detect project type(s):
   - Python: pyproject.toml, requirements.txt, setup.py
   - TypeScript/JS: package.json, tsconfig.json
   - Multi-service: docker-compose.yml, multiple package.json/pyproject.toml
   - Agent system: .claude/agents/, MCP configs

2. Detect existing tooling:
   - Linting: eslint, ruff, pylint, mypy, tsc --strict
   - Testing: pytest, vitest, jest (check for test directories)
   - Formatting: prettier, black, configured in pyproject.toml

3. Read .claude/state.json:
   - Skip issues already in backlog
   - Note currentFocus to avoid conflicts
```

This determines which analyzers to run and what standards to check against.

## Phase 2: Run Analyzers in Parallel

**CRITICAL: Use subagents simultaneously.** These are independent—run them all at once in a single message with multiple Task calls.

### Core Analyzers (Always Run)

```
┌─────────────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. test-coverage-auditor                                       │
│     → Find source files with NO corresponding test file         │
│     → Find exported functions never imported in tests           │
│     → Check: test directory exists? CI runs tests?              │
│     → Output: list of untested files/functions with impact      │
│                                                                 │
│  2. type-safety-auditor                                         │
│     → Python: functions missing type hints, Any usage           │
│       Run: mypy --strict (if available) or grep patterns        │
│     → TypeScript: any/unknown abuse, missing return types       │
│       Run: tsc --noEmit --strict or grep for ": any"            │
│     → Output: files with type safety gaps, severity             │
│                                                                 │
│  3. error-handling-auditor                                      │
│     → Find API calls, DB operations, file I/O without try/catch │
│     → Find catch blocks that swallow errors silently            │
│     → Find inconsistent error response formats                  │
│     → Output: unprotected operations with file:line             │
│                                                                 │
│  4. consistency-auditor                                         │
│     → Find same operation done multiple ways                    │
│       (e.g., 3 different HTTP client patterns)                  │
│     → Find naming convention violations                         │
│     → Find copy-pasted code blocks (>10 similar lines)          │
│     → Output: inconsistencies with examples of each variant     │
│                                                                 │
│  5. security-auditor                                            │
│     → Hardcoded secrets (API keys, passwords in code)           │
│     → Env vars used but not in .env.example                     │
│     → Missing input validation at API boundaries                │
│     → SQL/command injection patterns                            │
│     → Output: security issues with severity rating              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Project-Type Specific Analyzers

```
┌─────────────────────────────────────────────────────────────────┐
│  IF Multi-Service Architecture (docker-compose, multiple apps)  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  6. service-consistency-auditor                                 │
│     → Port conflicts or gaps in registry                        │
│     → Docker vs deployment config drift                         │
│     → Missing health checks                                     │
│     → Inconsistent service structure (some have X, others don't)│
│     → Env var requirements differ between services              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  IF Agent System (.claude/agents/, MCP configs, agent SDK)      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  7. agent-architecture-auditor                                  │
│     → Prompt format consistency (YAML frontmatter, structure)   │
│     → MCP config completeness (tools declared but not configured)│
│     → Tool/capability alignment (agent says it can do X,        │
│       but no tool provides X)                                   │
│     → Timeout and error handling in agent runners               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  IF --history flag (Historical Analysis)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  8. churn-analyzer                                              │
│     → git log --numstat for change frequency                    │
│     → Classify commits: bug-fix, feature, refactor              │
│       - Conventional commits (fix:, feat:, refactor:)           │
│       - Non-conventional: analyze diff size + message keywords  │
│     → Correlate: files with >50% bug-fix commits                │
│                                                                 │
│  9. complexity-analyzer                                         │
│     → Cyclomatic complexity (radon, eslint-complexity)          │
│     → Function length (>50 lines)                               │
│     → Nesting depth (>4 levels)                                 │
│     → Correlate with churn data                                 │
│                                                                 │
│  10. coupling-analyzer                                          │
│      → Files imported by 10+ others (high fan-in)               │
│      → Files importing 10+ others (high fan-out)                │
│      → Circular dependencies                                    │
│      → WITH LSP: findReferences for precise counts              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Dead Code Analyzer (Always Run)

```
┌─────────────────────────────────────────────────────────────────┐
│  11. dead-code-finder                                           │
├─────────────────────────────────────────────────────────────────┤
│     → JS/TS: npx knip (configure first if no knip.json)         │
│     → Python: vulture, ruff --select F401,F841                  │
│     → Unused dependencies in package.json/pyproject.toml        │
│     → Files with no inbound imports                             │
│     → VERIFY before flagging:                                   │
│       - Check for dynamic imports                               │
│       - Check if it's a public API entry point                  │
│       - Check if it's test utilities                            │
│     → WITH LSP: findReferences returning 0 = truly unused       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Example Subagent Prompts

```
# test-coverage-auditor
Analyze test coverage for this project at [path].

1. Find all source directories (src/, lib/, app/, services/)
2. Find all test directories (tests/, __tests__/, *.test.*, *.spec.*)
3. For each source file, check if a corresponding test file exists
4. For key exported functions, grep test files to see if they're imported

Output format:
- Untested files: [list with paths]
- Untested critical functions: [function names + file:line]
- Test infrastructure: [exists/missing, framework used]
- Estimated coverage gap: [high/medium/low based on findings]
```

```
# error-handling-auditor
Analyze error handling patterns in [path].

Look for:
1. HTTP/fetch calls without try/catch or .catch()
2. Database operations (query, insert, update) without error handling
3. File I/O (read, write, open) without error handling
4. Catch blocks that only log or do nothing (swallowed errors)
5. Inconsistent error response formats across API endpoints

For each finding, provide:
- File and line number
- The unprotected operation
- Severity (critical if user-facing, medium if internal, low if dev-only)
```

```
# consistency-auditor
Analyze code consistency in [path].

Find:
1. Same operation implemented differently:
   - HTTP clients (fetch vs axios vs httpx patterns)
   - Date handling (multiple libraries or manual formatting)
   - Error creation (new Error vs custom classes vs objects)
   - Logging (console.log vs logger vs print)

2. Naming violations:
   - Mixed camelCase/snake_case in same language
   - Inconsistent file naming (UserService.ts vs user-service.ts)

3. Duplicate code:
   - Blocks >10 lines that appear multiple times
   - Same logic copy-pasted with minor variations

For each finding:
- Show 2-3 examples of the different approaches
- Identify which pattern is most common (likely the "right" one)
```

```
# churn-analyzer (for --history mode)
Analyze git history for [path].

1. Run: git log --numstat --since="6 months ago" --pretty=format:"%H|%s"
2. Parse output to get: file, commit_hash, commit_message, lines_changed

3. Classify each commit:
   - bug-fix: message contains fix/bug/patch/issue/error/crash OR
              message starts with "fix:" OR
              diff is small (<50 lines) and touches existing code
   - feature: message contains feat/add/implement/new OR
              message starts with "feat:" OR
              creates new files
   - refactor: message contains refactor/clean/rename/move OR
               message starts with "refactor:"
   - chore: everything else

4. For each file, calculate:
   - Total changes
   - Bug-fix ratio (bug-fix commits / total commits)
   - Last bug-fix date

Output the top 15 files by churn with bug-fix correlation.
```

## Phase 3: Correlate and Prioritize

After all subagents return, synthesize findings:

### Priority Matrix

| Finding Type | Impact | Effort | Priority |
|--------------|--------|--------|----------|
| Security issue (hardcoded secret) | Critical | Low | **P0 - Fix Now** |
| No error handling on user-facing API | High | Low | **P1 - Quick Win** |
| Critical path with no tests | High | Medium | **P1** |
| Type safety gaps in shared code | Medium | Medium | **P2** |
| Inconsistent patterns | Low | High | **P3 - Backlog** |
| Dead code | Low | Low | **P3 - Quick cleanup** |

### For --history mode, add correlations:
- High complexity + high churn + high bug-ratio = **P0 refactor target**
- High coupling + high churn = **architectural problem**

## LSP Enhancement (Optional)

If LSP is available, it provides more accurate analysis:

```
Check LSP availability:
→ Try: LSP documentSymbol on a main source file
→ If works: Use for coupling/dead-code (findReferences, incomingCalls)
→ If errors: Fall back to grep/static analysis

LSP advantages:
- findReferences: exact call sites, not grep matches in comments
- incomingCalls/outgoingCalls: precise call hierarchy
- Dead code: findReferences returning 0 = truly unused
```

**Don't block on LSP.** Proceed with standard tools if unavailable.

## Configure Tools Before Running

Unconfigured tools produce noise. Before running analysis tools:

**For knip (JS/TS dead code):**
```json
{
  "$schema": "https://unpkg.com/knip@latest/schema.json",
  "entry": ["src/index.ts"],
  "project": ["src/**/*.ts"],
  "ignore": ["dist/**", "**/*.test.ts"]
}
```

**For vulture (Python dead code):**
Create `.vulture_whitelist.py` for framework hooks:
```python
# Vulture whitelist
_.on_startup  # FastAPI lifecycle
_.tool  # MCP decorators
```

**For mypy (Python types):**
Check if `pyproject.toml` has `[tool.mypy]`. If not, run with `--ignore-missing-imports`.

## Output Format

Structure your findings clearly:

```markdown
## Analysis Summary

**Project Type:** [Python/TypeScript/Multi-service/Agent System]
**Mode:** [Proactive/Historical]
**Analyzers Run:** [list]

## Critical Findings (Fix Now)

### [Finding Title]
- **What:** [Specific issue]
- **Where:** [file:line or list of files]
- **Why it matters:** [Impact]
- **Fix:** [Specific action]

## High Priority (Quick Wins)

...

## Medium Priority

...

## Low Priority / Backlog

...

## What I Couldn't Verify

[List anything you suspected but couldn't confirm with tooling]
```

## What to Leave Out

- Findings without specific file/line references
- Style preferences without consistency violations
- "Best practices" that don't apply to this project type
- Anything you couldn't verify with actual tool output
- Suggestions that would require major rewrites without clear benefit

## After Analysis

Don't just report. Offer to act:

1. **For P0 issues:** Offer to fix immediately
2. **For P1 quick wins:** Offer to fix a batch
3. **For P2/P3:** Add to backlog with evidence gathered

Ask: "Want me to start with [highest priority finding]?"

The measure of success: concrete improvements the user can verify, not a list of theoretical problems.

$ARGUMENTS
