---
description: Simulate diverse users exploring your app to discover gaps and feature ideas
---

Product discovery through user empathy simulation.

## Philosophy

**This is not QA or stress testing.** You're simulating real users with real goals who navigate your app and report what they experience - not what the code does internally.

**Hypothesis-driven exploration**: Users form beliefs about how things should work based on what they see (labels, layout, affordances). Then they act. The gap between expectation and reality is where insights live.

**User experience, not implementation details**: Report what users *experience*, not internal code behavior. "I clicked Research and nothing happened" matters. "The handler doesn't call the API" is implementation detail - only include it as supporting evidence.

## Phase 1: Deep Project Immersion

**Understand what exists before simulating users.** You can't form realistic hypotheses about an app you don't know.

Explore until you can answer:
- What problem does this app solve? Who is it for?
- What can users see and interact with? (pages, buttons, forms, flows)
- What are the main journeys through the app?
- What data matters to users? What can they create, view, modify?

## Phase 2: Generate User Scenarios

Create 7-10 diverse **goal-based scenarios**. These are intentions, not personas:

- What are users actually trying to accomplish?
- Range from obvious use cases to edge cases to "what if someone tried..."
- Each scenario should exercise different parts of the app
- Include at least one that might break assumptions the app makes

**List your scenarios in the output** so readers understand the coverage.

## Phase 3: Spawn User Agents in Parallel

**CRITICAL: Spawn all at once** in a single message with multiple Task calls.

Each agent needs:
1. **Project context** - what the app does, key flows, what's where
2. **Their specific goal** - what they're trying to accomplish
3. **The exploration principle** - how to think

```
┌────────────────────────────────────────────────────────────┐
│  AGENT PROMPT PRINCIPLES                                   │
├────────────────────────────────────────────────────────────┤
│  You're a user trying to: [GOAL]                           │
│                                                            │
│  Navigate the app as that user would. At each step:        │
│                                                            │
│  1. What do I see? (read the actual UI)                    │
│  2. What do I expect will happen if I do X?                │
│  3. What actually happens? (verify against code)           │
│  4. Was there a gap? Confusion? Delight?                   │
│                                                            │
│  Think out loud: "I see a Search button. I expect it to    │
│  search all my projects. Let me check... it only searches  │
│  the current one. That's confusing because..."             │
│                                                            │
│  Report experiences, not implementation:                   │
│  - "I couldn't find how to export" (experience)            │
│  - "The export function isn't wired up" (implementation)   │
│                                                            │
│  Include file:line references as supporting evidence,      │
│  not as the primary finding.                               │
└────────────────────────────────────────────────────────────┘
```

## Phase 4: Synthesize Findings

Collect all user reports. **Count how many users hit each issue** - convergence signals importance.

### Output Format

```markdown
## UX Audit Summary
**App:** [what it does]
**Key insight:** [one sentence - the most important finding]

## Scenarios Simulated
[List all 7-10 scenarios so readers understand coverage]

## Critical Gaps (blocked multiple users)
### 1. [Gap - user experience framing]
**Who hit this:** [N of M users - which scenarios]
**The experience:** "I tried to... I expected... but..."
**Impact:** [why this blocks the user's goal]
**Evidence:** [file:line references]

## Feature Opportunities
### 1. [What users wished existed]
**Who wanted this:** [which scenarios]
**The need:** [what they were trying to do]
**Idea:** [how it might work]

## Logic Inconsistencies
### 1. [Works sometimes, breaks other times]
**Works when:** [scenario/condition]
**Breaks when:** [scenario/condition]
**The experience:** [what the user sees]

## Friction Points
Minor annoyances that didn't block goals:
- [experience] → [N users, which scenarios]

## Edge Cases
Unusual but valid usage discovered:
- [what a user might try] → [what would happen]
```

## What Makes Good Findings

**User-centric framing**: "As someone trying to X, I expected Y" - not "the code does Z"

**Convergence matters**: Issues multiple users hit independently are more important than edge cases one user found

**Experience over implementation**: The finding is what users experience. Code references are evidence, not the finding itself.

**Actionable**: Clear what would improve the experience

Skip: pure implementation details not tied to user experience, style preferences, complete redesigns

## After Audit

Offer to:
1. Add high-priority items to backlog
2. Implement the most impactful quick fix
3. Design a solution for the biggest gap

$ARGUMENTS
