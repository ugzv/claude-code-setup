---
description: Simulate diverse users exploring your app to discover gaps and feature ideas
---

Product discovery through user empathy simulation.

## Philosophy

**This is not QA or stress testing.** You're spawning simulated users with real goals who explore the app and report:
- "I wanted to do X but couldn't"
- "This worked for A but when I tried B it didn't make sense"
- "I expected... but it doesn't"
- "Feature idea: what if..."

**Hypothesis-driven exploration**: Each user forms beliefs about how things should work based on what they see, then tests those beliefs against the actual code. The gap between expectation and reality is where insights live.

## Phase 1: Deep Project Immersion

**Before anything else, thoroughly understand the project.** Users can't form realistic hypotheses without knowing what exists.

Explore:
- **Purpose**: README, package.json description, main entry points - what problem does this solve?
- **User-facing surfaces**: Routes, pages, components, CLI commands - what can users interact with?
- **Data model**: Types, schemas, database models - what entities exist and how do they relate?
- **Core flows**: Follow the main paths through the code - how does data flow from input to output?
- **State**: Where does the app read/write? APIs, databases, files, external services?

You need enough understanding to generate realistic scenarios and to give each agent the context they need to explore meaningfully.

## Phase 2: Generate User Scenarios

Based on your understanding, create 7-10 diverse **goal-based scenarios**. Not skill levels (power user, beginner) - real intentions:

- Range from obvious use cases to edge cases to "what if someone tried..."
- Each scenario should exercise different parts of the app
- Include at least one scenario that might break assumptions the app makes
- Think about what users ACTUALLY want vs what the app was designed for

## Phase 3: Spawn User Agents in Parallel

**CRITICAL: Spawn all at once** in a single message with multiple Task calls.

Each agent needs:
1. **Project context** - share your understanding so they're not starting cold
2. **Their specific goal** - what they're trying to accomplish
3. **The hypothesis principle** - how to explore

```
┌────────────────────────────────────────────────────────────┐
│  AGENT PROMPT PRINCIPLES                                   │
├────────────────────────────────────────────────────────────┤
│  Give each agent:                                          │
│                                                            │
│  1. Project context you gathered (key files, flows, model) │
│                                                            │
│  2. Their goal: "You're a user trying to [SCENARIO]"       │
│                                                            │
│  3. Exploration principle:                                 │
│     "Form hypotheses about how things work based on what   │
│      you see (UI, labels, structure). Then verify against  │
│      the actual code. When expectation ≠ reality, that's   │
│      a finding. When you wish something existed, that's    │
│      a feature idea."                                      │
│                                                            │
│  4. Ground in code:                                        │
│     "Read actual components, routes, handlers. Reference   │
│      specific files and logic in your findings."           │
│                                                            │
│  Findings to report:                                       │
│  - Friction: where you got stuck or confused               │
│  - Logic gaps: works for X but not Y                       │
│  - Missing: I wish I could...                              │
│  - Unexpected: I expected A but got B                      │
└────────────────────────────────────────────────────────────┘
```

## Phase 4: Synthesize Findings

Collect all user reports and organize by type:

### Output Format

```markdown
## UX Audit Summary
**App:** [what it does]
**Users simulated:** [count]
**Key insight:** [one sentence - the biggest gap or opportunity]

## Critical Gaps
Things multiple users hit that block their goals:
### 1. [Gap]
**Scenario:** [which user(s) hit this]
**Expected:** [what they expected]
**Actual:** [what happened]
**Impact:** [why this matters]

## Feature Opportunities
Things users wished existed:
### 1. [Feature idea]
**Scenario:** [who wanted this]
**Use case:** [what they were trying to do]
**Suggestion:** [how it might work]

## Logic Inconsistencies
Works in case A but not case B:
### 1. [Inconsistency]
**Works:** [scenario where it works]
**Breaks:** [scenario where it doesn't]
**Why:** [the underlying assumption that breaks]

## Friction Points
Not blocking but annoying:
- [friction] → [which user, what they expected]

## Edge Cases Discovered
Unusual but valid usage patterns:
- [edge case] → [what would happen]
```

## What Makes Good Findings

- **Grounded in code** - Point to actual components, routes, handlers
- **User-centric** - "As someone trying to X, I expected Y"
- **Actionable** - Clear what would fix or improve it
- **Prioritized** - Multiple users hitting same issue = higher priority

Skip: hypothetical issues not grounded in actual code, pure style preferences, things that would require complete redesign.

## After Audit

Offer to:
1. Add high-priority items to backlog
2. Implement the most impactful quick fix
3. Design a solution for the biggest gap

$ARGUMENTS
