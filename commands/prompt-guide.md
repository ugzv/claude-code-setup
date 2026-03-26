---
description: "Load prompting philosophy and apply to any prompt work"
---

Philosophy for building AI agent prompts. Internalize before any prompt work.

## Philosophy for Building AI Agent Prompts

The model is intelligent. Write for a collaborator that can reason, generalize, and recover from novelty, not a system that only matches patterns.

The goal of a good prompt is not to pre-script every case. The goal is to make good judgment likely, make hard boundaries explicit, and keep the model aligned with the real objective.

## Core Approach

Prefer principles for behavior that requires judgment:

- prioritization
- tone
- tradeoffs
- ambiguity handling
- error handling
- adaptation to unfamiliar situations

Use explicit rules for things that are genuinely non-negotiable:

- safety boundaries
- permission boundaries
- tool-use restrictions
- required formats or schemas
- escalation conditions
- product or policy constraints

Principles should carry the reasoning. Rules should define the edges.

## Principles Over Procedures

Avoid over-specifying step-by-step procedures unless exact sequencing truly matters.

Rigid procedures are brittle. They fail when the situation is slightly different from what the prompt anticipated.

Prefer instructions that describe what good judgment looks like:

- understand the task before acting
- verify claims when correctness may have changed
- make tradeoffs visible when multiple valid paths exist
- match tone and depth to user context
- explain failures in a way that helps the next action

If a process must be followed exactly, say so explicitly and explain why.

## Explain the Why

Whenever an instruction matters, include the purpose behind it.

A model that understands the goal can preserve the intent in edge cases instead of obeying the wording mechanically.

Good prompts do not just say what to do. They make clear what outcome the instruction is protecting.

## Use Examples Carefully

Examples are powerful and dangerous.

Models learn not only the intended pattern, but also incidental details such as:

- length
- tone
- structure
- domain
- language
- style

Use examples only when they materially clarify the intended behavior.

When examples are necessary:

- keep them few
- vary irrelevant surface details
- state explicitly what the example demonstrates
- avoid letting all examples share the same accidental pattern

Do not let examples silently become the policy.

## Prefer Clear Priorities Over Many Instructions

Too many instructions create collisions, dilution, and hidden contradictions.

Prefer a small set of high-value instructions with clear priority.

If two goals can conflict, specify which one wins.
For example:

- correctness over speed
- safety over completeness
- schema compliance over prose quality
- user intent over generic thoroughness

A prompt is better when removing an instruction improves clarity.

## Avoid Defensive Prompting

Do not fill prompts with long lists of prohibitions just because failure is possible.

State the desired behavior directly and positively whenever possible.

Use negative instructions only when they define a real boundary or prevent a costly failure.

The issue is not saying "do not." The issue is using prohibitions as a substitute for clear intent.

## Avoid Brittle Threshold Thinking Unless It Is Policy

Do not encode arbitrary thresholds when what you really want is judgment.

If the system needs heuristic evaluation, describe the pattern that should trigger concern rather than forcing shallow classification rules.

But if a threshold is part of the actual product, policy, or safety requirement, keep it explicit.

Use judgment where judgment is needed.
Use thresholds where compliance is required.

## Match Prompting Style to Model and Task

Use lighter prompts when the task is straightforward and the model already knows the domain well.

Use more guidance when:

- the task is high stakes
- tool use is involved
- multiple objectives must be balanced
- the model may otherwise optimize for the wrong thing
- the environment has important local constraints

Do not add structure for its own sake. Add it to reduce real failure modes.

## Recommended Prompt Shape

```xml
<identity>Who the agent is and what it is fundamentally trying to do</identity>
<context>Relevant environment, constraints, and operating assumptions</context>
<principles>What good behavior and judgment look like</principles>
<rules>Only the hard boundaries and non-negotiable requirements</rules>
<tools>When each tool should be used and what kind of intent should trigger it</tools>
<output_format>Only if response structure truly matters</output_format>
```

Not every prompt needs every section. Include only what improves performance.

## Common Failure Modes

Avoid:

- procedural micromanagement when judgment would generalize better
- too many examples that accidentally teach the wrong pattern
- hardcoded examples that bias toward one domain, tone, or culture when abstraction would work better
- conflicting instructions with no priority ordering
- vague principles where hard constraints are actually required
- hard constraints where contextual judgment is actually required
- repetition that adds length but not clarity

## Review Standard

Check whether:

- the prompt distinguishes principles from hard rules
- hard boundaries are explicit but minimal
- instructions reflect the actual goal, not cargo-cult wording
- examples, if any, teach only what they are meant to teach
- priorities are clear where tradeoffs may occur
- any instruction can be removed without loss
- the model would understand not just what to do, but why

## Practical Test

If the task changes slightly, would the prompt still produce good behavior?

If yes, the prompt likely teaches principles well.
If no, it is probably overfit to anticipated cases.

## Summary

Good prompts do three things:

- teach judgment through principles
- define boundaries through explicit rules
- preserve clarity by saying only what matters

That is the balance: not over-enforced, not under-specified, and robust to situations you did not predict.

---

Apply this philosophy to: creating, auditing, improving, or debugging prompts.

$ARGUMENTS
