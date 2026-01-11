---
description: "Pre-mortem analysis [--staged|--last|--last N|commit-range]"
---

Critical examination of recent changes. Scales from quick sanity checks to deep analysis.

## Philosophy

**Assume something will break.** Your job isn't to validate—it's to find the failure mode before production does.

**Compare states, not just code.** The diff shows what changed. Understanding requires knowing what the old code handled that the new code might not.

**Be specifically wrong rather than vaguely right.** "This might cause issues" is useless. "This will fail when X happens because Y" is actionable.

**Scale to the change.** A typo fix needs a glance. A refactor needs deep analysis. Match effort to risk.

## The Process

### 1. Gather and Assess

**Auto-detect what to analyze:**

1. Check `git status` and `git diff` first
2. If uncommitted changes exist → analyze those
3. If working tree is clean → check recent commits:
   - Look at last few commits (messages, timestamps, files touched)
   - If related (same feature/fix, close in time) → analyze together
   - If unrelated → just analyze the last one
4. If user specifies a scope → use that instead

| Argument | Scope |
|----------|-------|
| (none) | Auto-detect (uncommitted → recent related commits → last commit) |
| `--staged` | Only staged changes |
| `--last` | Last commit |
| `--last N` | Last N commits |
| `[commit-range]` | Specific range (e.g., `main..HEAD`) |

**State what you're analyzing:** "Analyzing [uncommitted changes / last commit / commit range X]"

**Immediately assess the change character:**

- How many files? How many lines?
- What kind of change? (new feature, refactor, bugfix, config, docs, tests)
- What's the risk surface? (data handling, auth, API contracts, UI, internal logic)

### 2. Choose Analysis Depth

Based on your assessment, pick the appropriate depth:

**Quick** (< 30 lines, single file, low-risk area):
- Read the diff and before-state yourself
- Think through failure modes directly
- No agents needed—just analyze and report

**Standard** (moderate changes, some integration points):
- Spawn 2-3 focused critics based on what matters for THIS change
- Pick from the critic types below based on relevance

**Deep** (large refactor, critical system, multiple integration points):
- Spawn all relevant critics in parallel
- Include integration and failure-mode analysis

### 3. Understand Before You Critique

For any depth, first understand:
- What is this change trying to accomplish?
- What did the old code do? (use `git show` / `git diff`)
- What implicit behaviors or contracts existed?

State: "These changes [do X] by [approach Y], assuming [Z]."

### 4. Analyze (Depth-Appropriate)

**Available critic lenses** - use what's relevant:

| Critic | When Relevant | Focus |
|--------|---------------|-------|
| behavioral-diff | Refactors, rewrites | What old code did that new code doesn't |
| assumption-challenger | New logic, conditionals | Assumptions that might be false |
| integration-prober | API/interface changes | Callers and callees still work? |
| edge-case-hunter | Input handling, data processing | Boundaries, nulls, encoding |
| failure-mode-predictor | Critical paths, data mutations | Production symptoms, blast radius |
| state-analyzer | Stateful code, caching | Race conditions, stale state |
| type-boundary-checker | Cross-system data | Serialization, type coercion |

**For Quick analysis**: Just think through the relevant concerns yourself.

**For Standard/Deep**: Spawn critics in parallel. Each critic should be adversarial—job is to find problems, not confirm quality.

### 5. Synthesize

Organize by likelihood × severity. Be specific about mechanisms.

## Output (Scale to Depth)

### Quick Analysis

```markdown
## Reflect: [one-line description]

**Change:** [X lines across Y files - type of change]
**Intent:** [what it's trying to do]

**Verdict:** [Safe / Watch for X / Fix Y first]

[If concerns exist:]
- [Specific concern + mechanism]
```

### Standard Analysis

```markdown
## Reflect: [description]

**Change:** [scope summary]
**Intent:** [what and why]
**Risk surface:** [what areas this touches]

## Concerns

### [Concern Title]
- **What:** [specific scenario]
- **Why:** [mechanism]
- **Likelihood:** [High/Medium/Low]
- **Evidence:** [file:line]

## Assumptions
| Assumption | Breaks When |
|------------|-------------|
| [assumption] | [condition] |

## Verdict
**Confidence:** [High/Medium/Low]
**Recommendation:** [Ship / Fix X first / Reconsider]
```

### Deep Analysis

```markdown
## Pre-Mortem: [description]

**Intent:** [what the changes accomplish]
**Scope:** [files, lines, areas touched]

## Critical Risks
Issues likely to cause production failures.

- **Scenario:** [condition that triggers]
- **Mechanism:** [causal chain]
- **Symptom:** [what users/systems experience]
- **Evidence:** [file:line]

## Likely Issues
Problems that will surface during normal use.

## Edge Cases
Valid scenarios that aren't handled.

## Lost Behaviors
What old code handled that new code doesn't.

## Assumptions at Risk
| Assumption | Breaks When | Consequence |
|------------|-------------|-------------|

## Verdict
**Confidence:** [High/Medium/Low]
**Recommendation:** [Ship / Fix X first / Reconsider approach]
**If shipping:** [What to monitor, rollback triggers]
```

## Quality Principles

**Specific over vague**: "When X happens, Y causes Z" not "this seems risky"

**Testable**: Could write a test or manually verify

**Proportionate**: Match severity to actual risk, not imagination

**Honest**: If it's solid, say why. If uncertain, say that. Truth over pessimism or optimism.

**Scoped**: This change's problems, not pre-existing issues

## Anti-patterns

- Validating ("looks good!") instead of challenging
- Aesthetic criticism disguised as risk
- Hypotheticals with no realistic path
- Over-analyzing trivial changes
- Under-analyzing risky ones

$ARGUMENTS
