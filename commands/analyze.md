---
description: Analyze codebase for refactoring opportunities
---

You are investigating where this codebase resists change.

## Why Verification Is Everything

Anyone can look at code and say "this seems complex" or "this probably causes problems." That's worthless. The user doesn't need intuition—they have their own.

What makes your analysis valuable is **evidence that can't be argued with**. When you say "this file has been modified 47 times in 6 months with 8 bug-fix commits," that's a fact. When you say "this seems to change a lot," that's an opinion dressed as insight.

The difference between useful analysis and noise is whether your claims are backed by data you actually gathered, or assumptions that felt reasonable.

**If you haven't verified something, you don't know it.** And if you don't know it, don't say it.

## Run Analysis in Parallel

**IMPORTANT: Use subagents to gather evidence simultaneously.** These analyses are independent—run them all at once.

```
┌─────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)│
├─────────────────────────────────────────────────────────┤
│  1. complexity-analyzer                                 │
│     → Find files with high cyclomatic complexity        │
│     → Tools: radon (Python), eslint-complexity (JS)     │
│     → Fallback: count lines, nesting depth, branches    │
│                                                         │
│  2. churn-analyzer                                      │
│     → git log --numstat analysis                        │
│     → Find: most-modified files, bug-fix correlations   │
│     → Output: file, change_count, bug_fix_count         │
│                                                         │
│  3. dead-code-finder                                    │
│     → knip (JS/TS), vulture (Python)                    │
│     → Find: unused exports, unreferenced files          │
│     → Verify: check for dynamic imports before flagging │
│                                                         │
│  4. coupling-analyzer                                   │
│     → Trace import graphs                               │
│     → Find: files imported by many, circular deps       │
│     → Output: coupling score, dependency list           │
└─────────────────────────────────────────────────────────┘
```

**Example subagent prompts:**

```
# Churn analyzer
Analyze git history for this project. Find:
1. Files modified most often (git log --numstat)
2. Files with most bug-fix commits (grep for "fix" in commit messages)
3. Correlation between change frequency and bug frequency

Return top 10 files by churn with bug correlation data.
```

```
# Coupling analyzer
Analyze the import/dependency graph. Find:
1. Files imported by 10+ other files (high fan-in)
2. Files that import 10+ other files (high fan-out)
3. Any circular dependencies

Return coupling hotspots with specific file paths.
```

### Wait and Correlate

After all subagents return, **correlate findings**:
- High complexity + high churn = **priority refactor target**
- High coupling + high churn = **architectural problem**
- Dead code = **quick wins to remove**

## What You're Looking For

Code that resists change has a cost: the gap between how fast this team *could* ship and how fast they *actually* ship. Your job is finding where that resistance lives and proving what it's costing.

The symptoms are structural: responsibilities tangled together, assumptions buried in logic, complexity that leaked everywhere. But symptoms aren't proof—you need to connect what you see in the code to what's happening in the project's history.

High complexity alone means nothing. High complexity in a file that changes constantly and correlates with bugs? That's a problem worth solving.

## Before You Analyze

Read `.claude/state.json`:
- Skip issues already in `backlog`
- Warn about conflicts with `currentFocus`

Understand what verification tools exist in this project. Different codebases have different tooling—linters, type checkers, complexity analyzers, dependency graphers. Know what you can measure before you start measuring.

If critical tools are missing, that's worth noting. "I can't verify complexity scores because no analyzer is configured" is honest and useful. Guessing is neither.

## The Standard for Claims

Every factual claim needs evidence from this session:

- Claims about change frequency → verify against actual commit history
- Claims about complexity → verify against actual analysis output
- Claims about coupling → verify against actual import/dependency tracing
- Claims about bugs → verify against actual commit messages or issue references

This isn't about following a checklist. It's about understanding that unverified claims actively harm the user by sending them chasing problems that might not exist.

## What Makes a Finding Valuable

**Evidence of resistance:** Not "this looks complex" but what specifically makes it resist change, backed by measurements you took.

**Evidence of cost:** Not "this causes problems" but how you know it causes problems—commit patterns, bug correlations, things you can point to.

**A path forward:** Not "refactor this" but what specifically would change, which concerns would separate, what the result would look like.

**Honest scope:** How much code is involved, what would need to change, what the user is signing up for.

## Dead Code and Unused Dependencies

Every line of code that exists but doesn't run has hidden costs: developers read it trying to understand the system, it gets updated during refactors, it ships as bundle weight, it sits in dependencies with potential vulnerabilities.

**Use the right tools.** Check what's installed, and offer to add what's missing:
- **JS/TS:** `npx knip` (best all-in-one), or `depcheck`, `ts-prune`
- **Python:** `vulture`, `ruff check --select F401,F841` (unused imports/vars)

If the user declines installation, fall back to manual methods: grep for exports then grep for their imports, check package.json deps against actual imports, look for files with no inbound imports.

### Configure Tools Before Running

An unconfigured analysis tool will flood you with false positives. **Knip** on an MCP server flags every tool handler as "unused" because it can't see the MCP runtime. That's noise, not signal.

**Before running knip**, check if `knip.json` exists. If not, create one tuned for the project:

For **MCP servers** (TypeScript):
```json
{
  "$schema": "https://unpkg.com/knip@latest/schema.json",
  "entry": ["src/index.ts"],
  "project": ["src/**/*.ts"],
  "ignore": ["dist/**", "build/**"],
  "ignoreDependencies": ["@modelcontextprotocol/sdk"]
}
```

For **standard TypeScript projects**:
```json
{
  "$schema": "https://unpkg.com/knip@latest/schema.json",
  "entry": ["src/index.ts", "src/main.ts"],
  "project": ["src/**/*.ts"],
  "ignore": ["**/*.test.ts", "**/*.spec.ts", "dist/**"]
}
```

For **Python with vulture**, create `.vulture_whitelist.py` for false positives:
```python
# Vulture whitelist - intentionally unused code
_.on_startup  # FastAPI/FastMCP lifecycle hooks
_.on_shutdown
_.tool  # MCP tool decorators register handlers dynamically
```

**The principle:** A well-configured analysis that finds 3 real issues beats an unconfigured analysis that finds 50 false positives. Configure first, then run.

**Before recommending removal, verify:**
- Dynamic imports make static analysis blind—check for `import()` with variables
- Public APIs expose code for external consumers that nothing internal imports
- Test utilities only run in test environments

For high-confidence removals, offer to execute. For uncertain cases, recommend investigation first.

## What to Leave Out

- Ugly but stable code that nobody touches (no cost = no priority)
- Style preferences without evidence of impact
- Patterns that "could be better" but aren't causing measurable problems
- Anything you couldn't verify

The goal isn't a comprehensive list of everything imperfect. It's finding the high-leverage changes that would make this codebase resist change less.

## When You Can't Verify

Say so. "I suspect this module has issues based on its size, but I couldn't run complexity analysis. To investigate properly, we'd need [specific tooling]."

This is more valuable than a false claim. It tells the user exactly what's missing and lets them decide whether to address the tooling gap.

## After Analysis

Don't just report. The user wants the code to be better.

For the highest-leverage verified finding, offer to execute it. Register in `currentFocus` before starting work on files.

For findings that need more investigation, add to backlog with the evidence you gathered—so future sessions don't need to re-verify.

The measure of success: code that resists change less, proven by the same evidence you used to find the problems.

$ARGUMENTS
