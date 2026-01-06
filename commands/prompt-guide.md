---
description: Load prompting philosophy and apply to any prompt work
---

Philosophy for building AI agent prompts. Internalize before any prompt work.

## Core Insight

Claude is intelligent. Write for a collaborator, not a rule-following machine.

Rules cover situations you anticipate. Principles let Claude reason about novel situations you never imagined.

## Principles Over Rules

**Rules** (avoid): "If X then Y", "When X always Y"
**Principles** (prefer): "Match formality to context", "Verify before claiming", "Explain errors actionably"

Rules create brittle agents. Principles create adaptive ones.

## The Example Trap

Claude learns intensely from examples - including incidental details you didn't intend to emphasize.

**Problem**: If all your examples share a trait (length, tone, domain, structure), Claude treats that trait as required.

**Solution**:
- 3-5 diverse examples maximum
- Vary surface details (length, complexity, domain)
- Explicitly state what the examples demonstrate vs. what's incidental

## Explain the Why

Without why: "Keep responses under 100 words"
With why: "Keep responses under 100 words because [your actual constraint]"

Understanding the goal lets Claude apply spirit over letter in edge cases.

## Model Selection

**Sonnet 4.5**: Default for most work. Add "analyze before calling tools" prompts.
**Opus 4.5**: Complex multi-step reasoning, orchestrators, costly-error domains.

**Context anxiety** (both): Models rush to finish as context fills, even with space remaining.
→ Add: "You have abundant context. Take time for thorough analysis."

**Deeper reasoning**: For complex tasks, add "Think through this carefully" or "Explore multiple approaches before concluding."

## Prompt Structure

```xml
<identity>Who and core purpose (1-2 sentences)</identity>
<context>Background, environment, constraints</context>
<principles>What good looks like (NOT if-then rules)</principles>
<tools>When to use each (intent, not mechanics)</tools>
<output_format>Structure if it matters</output_format>
```

## Common Mistakes

1. **Over-specifying procedures** - "First X, then Y, then if Y check Z" → "Verify relevant conditions"
2. **Defensive prompting** - "Do NOT X, never Y, avoid Z" → State what you want
3. **Hand-holding** - Long explanations of obvious concepts → Trust Claude's knowledge
4. **Edge case exhaustion** - 50 rules → 5 generalizing principles
5. **Conflicting instructions** - "Be concise" + "Include all details" → Clear priority
6. **Threshold-based rules** - "If X > 5, flag as high" → Teaches matching, not judgment. Describe patterns that suggest problems instead.

## When Generating Prompts

**Avoid hardcoded examples in your output.** You know The Example Trap—apply it to what you write:
- State principles abstractly, not through specific instances
- If examples are essential, use placeholders like `[domain-specific term]` or describe the pattern generically
- Never use examples that could bias toward a specific language, culture, domain, or style

The agent reading your prompt will learn from every detail. Keep it clean.

## Review Checklist

- [ ] Instructions are principles, not if-then rules?
- [ ] Examples demonstrate principles, not patterns?
- [ ] No hardcoded examples that could bias the target agent?
- [ ] No unnecessary overlap or contradictions?
- [ ] Would removing any instruction improve it?
- [ ] Does Claude understand WHY?

## When Agent Fails

Ask: Did instructions not cover this, or not follow them? Would a principle have generalized better?

---

Apply this philosophy to: creating, auditing, improving, or debugging prompts.

$ARGUMENTS
