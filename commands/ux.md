---
description: Simulate real users exploring your app to discover dead paths, inconsistencies, and opportunities
---

Product discovery through user empathy simulation.

## Philosophy

**Ground users in reality.** Don't invent hypothetical personas—discover who this product actually serves from the codebase itself, then simulate those specific users with their real contexts and goals.

**Hypothesis-driven exploration.** Users form beliefs about how things should work based on what they see. Then they act. The gap between expectation and reality is where insights live.

**Experience over implementation.** Report what users experience, not what code does. "I clicked Save and nothing happened" is a finding. "The handler doesn't call the API" is supporting evidence.

## The Process

### 1. Discover Target Users

Before simulating anyone, find who this app is built for:

- What does the README/docs say about target users?
- What user types appear in onboarding, marketing, or feature design?
- What problems does the app claim to solve, and for whom?
- What assumptions does the UI make about user knowledge/context?

**Output this explicitly**: "This app serves [User Type A] who needs X, [User Type B] who needs Y..."

This grounds everything that follows.

### 2. Understand the Product

Explore until you can map:
- What can users see and interact with?
- What are the main journeys through the app?
- What data matters? What can users create, view, modify?

### 3. Generate Grounded Scenarios

Create 7-10 scenarios FROM the discovered user types:

- Each scenario is a specific user type with a specific goal
- Cover the obvious use cases AND the edge cases
- Include scenarios that might break assumptions the app makes
- At least one "what if this user tried something the designers didn't anticipate"

**List scenarios in your output** so readers understand coverage.

### 4. Spawn User Agents

**CRITICAL: Spawn all at once** in a single message with multiple Task calls.

Each agent receives:
- Who they are (the discovered user type, their context)
- What they're trying to accomplish
- The exploration principle below

```
EXPLORATION PRINCIPLE

You are [USER TYPE] trying to [GOAL].

Navigate as this user would. At each step:
- What do I see? (read the actual UI)
- What do I expect will happen?
- What actually happens?
- Gap? Confusion? Delight?

Think out loud in first person. Report experiences, not implementation.
Include file:line as evidence, not as the finding itself.
```

### 5. Synthesize Findings

Collect reports. **Count convergence** - issues multiple users hit independently matter more.

## Output

```markdown
## UX Audit: [App Name]

**Built for:** [discovered user types and their needs]
**Key insight:** [one sentence - the most important finding]

## Scenarios Simulated
[List all scenarios with user type + goal]

## Critical Gaps
Issues that blocked users from achieving their goals.
- What happened (user experience framing)
- Who hit it (N of M, which scenarios)
- Impact on user goal
- Evidence (file:line)

## Dead Paths
Features or flows that exist but don't work or lead nowhere.

## Behavioral Inconsistencies
Same action, different results in different contexts.
- Works when: [condition]
- Breaks when: [condition]

## Feature Opportunities
Things users wanted but couldn't do.
- The need (what they were trying to accomplish)
- Who wanted it

## Friction Points
Minor annoyances that didn't block goals.

## Edge Cases
Unusual but valid usage and what would happen.
```

## What Makes Good Findings

**Grounded**: Findings come from simulating discovered users, not invented personas

**Convergent**: Multiple users hitting the same issue independently signals importance

**Actionable**: Clear what would improve the experience

**Experience-framed**: "I tried to X, expected Y, got Z" - not "the code does W"

## After the Audit

Offer to:
1. Generate handoff blocks for issues to address later
2. Add items to backlog
3. Fix something immediately if confident

## Handoff Blocks

Generate copy-paste ready prompts for new Claude Code sessions. Each handoff should trigger investigation, validation, and proper solution design—not blind fixing.

**Structure each handoff as:**

```markdown
## Issue: [Short descriptive title]

### The Problem
[User experience framing: "When a user tries to X, they expect Y but get Z"]

### Evidence from Audit
- Observed behavior: [what happened]
- Affected scenarios: [which user types hit this]
- Relevant files (hypothesis, verify these): [file:line references]

### Your Task
1. **Verify** this issue exists—reproduce the problem, understand the actual behavior
2. **Investigate** root cause—the files above are starting points, not conclusions
3. **Propose** your solution approach before implementing—explain tradeoffs
4. **Implement** only after you understand the problem fully

### Success Criteria
[Observable outcome: "User can now X and sees Y"]

### Questions to Answer First
- Is this actually a bug, or intentional behavior?
- What's the minimal change that fixes this?
- Are there other places with the same pattern that need the same fix?
```

**Principle**: The receiving session should think "let me understand this" not "let me implement this fix." Investigation prevents wrong solutions.

$ARGUMENTS
