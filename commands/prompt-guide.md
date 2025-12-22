---
description: Load prompting philosophy and apply to any prompt work
---

You are now aligned with a specific philosophy for building AI agent prompts. Read and internalize this before doing any prompt work.

---

## The Core Insight

Claude is intelligent. Write prompts for an intelligent collaborator, not a rule-following machine.

When you write rules, you can only cover situations you anticipate. When you teach principles, Claude can reason about novel situations you never imagined. This is the fundamental difference between agents that break on edge cases and agents that handle them gracefully.

---

## Principles Over Rules

**Rules tell Claude what to do. Principles tell Claude what good looks like.**

**Rules (Avoid) → Principles (Prefer):**
- "If the user says X, respond with Y" → "Match the user's level of formality and expertise"
- "Always check the database before responding" → "Verify information before making claims"
- "Never use more than 3 API calls" → "Be efficient with resources while ensuring accuracy"
- "If error code 404, say 'Not found'" → "Explain errors in terms the user can act on"

**Why this matters:** Rules create brittle agents that fail silently on anything you didn't anticipate. Principles create adaptive agents that handle the unexpected intelligently.

**The test:** If your instruction starts with "If... then..." or "When... always...", you're probably writing a rule. Reframe it as a principle.

---

## The Example Trap

Claude 4 models learn intensely from examples in prompts. This is powerful—and dangerous.

**The problem:** When you include examples, Claude treats them as the canonical representation of what you want. Every detail in your examples becomes a pattern to follow, including details you didn't intend to emphasize.

**What goes wrong:**

- 5 examples of customer service responses all happen to be 3 paragraphs → Claude writes 3-paragraph responses even when 1 sentence would suffice
- Examples all use formal language → Claude can't adapt to casual users
- Examples all involve product returns → Claude struggles with unrelated queries
- Examples show specific error handling → Claude looks for those exact errors instead of reasoning about new ones

**What to do instead:**

1. **Use 3-5 diverse examples maximum** that demonstrate the principle, not the pattern
2. **Vary the surface details** while keeping the underlying principle consistent
3. **Include examples of different lengths, tones, and complexity levels**
4. **Explicitly state what the examples demonstrate** so Claude learns the right lesson

```xml
<examples>
These examples demonstrate adapting communication style to context,
not specific phrasings to copy:

<example>
[Short technical query → concise technical response]
</example>

<example>
[Confused beginner → patient, jargon-free explanation]
</example>

<example>
[Complex multi-part request → structured comprehensive response]
</example>
</examples>
```

**The test:** Could Claude reasonably conclude something unintended from your examples? If your examples share incidental similarities, Claude will learn those too.

---

## Explain the Why

Claude 4 models follow instructions better when they understand the reasoning.

**Without Why (Weaker) → With Why (Stronger):**
- "Keep responses under 100 words" → "Keep responses under 100 words because this agent runs in a mobile app where screen space is limited"
- "Always confirm before deleting" → "Always confirm before deleting because users often click accidentally and deletions are irreversible in our system"
- "Use formal language" → "Use formal language because this agent represents our company in enterprise sales contexts"

**Why this matters:** When Claude understands the goal behind an instruction, it can:
- Apply the spirit of the rule in edge cases
- Make intelligent tradeoffs when instructions conflict
- Adapt appropriately to situations you didn't anticipate

---

## Model Selection: Opus 4.5 vs Sonnet 4.5

**Default to Sonnet 4.5** for most agent work. It's the best balance of capability, speed, and cost.

**Use Opus 4.5 when:**
- Tasks require sustained reasoning across 30+ steps
- You're building orchestrator agents that coordinate other agents
- Errors are costly and precision matters more than speed
- The task involves complex multi-step planning with dependencies

**Key behavioral differences:**

- **Verbosity:** Sonnet is concise, may skip summaries. Opus gives more thorough explanations.
- **Tool calling:** Sonnet benefits from "analyze before calling" prompts. Opus automatically considers tool necessity.
- **Extended thinking:** Sonnet needs "think hard" / "think step by step". Opus naturally engages deeper reasoning.
- **Token efficiency:** Opus uses up to 65% fewer tokens for same tasks.

**Prompting adjustment for Sonnet:** Add explicit instructions like "Before using any tool, briefly analyze whether it's necessary and what information you need from it."

**Prompting adjustment for Opus:** Can handle more ambiguity; focus prompts on goals rather than procedures.

---

## Prompt Structure for Agents

Use clear XML sections. This prevents Claude from mixing up different types of information:

```xml
<identity>
Who the agent is and its core purpose.
Keep this brief—1-2 sentences.
</identity>

<context>
Background information the agent needs.
Project details, environment, constraints.
</context>

<principles>
The heuristics that guide decision-making.
These are the "what good looks like" statements.
NOT a list of if-then rules.
</principles>

<tools>
Available tools and when to use them.
Focus on intent, not mechanics.
"Use search_documents when you need to find specific information"
NOT "Call search_documents with query parameter set to..."
</tools>

<output_format>
What the final output should look like.
Be specific about structure if it matters.
</output_format>
```

---

## Common Mistakes That Limit Agents

**1. Over-specifying procedures**
- Bad: "First check X, then check Y, then if Y is true check Z..."
- Good: "Verify all relevant conditions before proceeding"

**2. Defensive prompting**
- Bad: "Do NOT do X. Never do Y. Always avoid Z. Remember to not..."
- Good: State what you want, not everything you don't want

**3. Assuming Claude needs hand-holding**
- Bad: Long explanations of obvious concepts
- Good: Trust Claude's knowledge; focus on your specific context

**4. Trying to cover every edge case**
- Bad: 50 rules covering every scenario you can imagine
- Good: 5 principles that generalize to scenarios you can't imagine

**5. Conflicting instructions**
- Bad: "Be concise" + "Be thorough" + "Include all details" + "Keep it brief"
- Good: Clear priority ("Prioritize clarity; be as concise as possible while being complete")

**6. Copy-pasting examples without review**
- Bad: Examples from one use case applied to another
- Good: Examples crafted specifically to demonstrate your principles

---

## The Prompt Development Process

1. **Start minimal.** Write the shortest prompt that could possibly work.

2. **Test with diverse inputs.** Not just happy paths—weird inputs, edge cases, adversarial attempts.

3. **Identify failure modes.** Where does the agent break? What does it misunderstand?

4. **Add targeted principles.** Address failures with principles, not rules. Ask: "What heuristic would prevent this class of failure?"

5. **Re-test.** Did your addition help? Did it hurt anything else?

6. **Iterate.** Prompting is empirical. What works is what works, not what should theoretically work.

---

## Quick Reference

**Before writing a prompt, ask:**
- What principles should guide this agent's decisions?
- What does "good" look like for this task?
- What context does the agent need that it wouldn't have by default?

**When reviewing a prompt, check:**
- [ ] Are instructions principles (what good looks like) or rules (if-then logic)?
- [ ] Do examples demonstrate principles or patterns?
- [ ] Is there unnecessary overlap or contradiction between instructions?
- [ ] Would removing any instruction make the prompt better?
- [ ] Does the agent understand WHY it should follow each instruction?

**When an agent fails, ask:**
- Did it fail to follow instructions, or did the instructions not cover this case?
- Would a principle have generalized better than the rule that failed?
- Is this a gap in context, not a gap in instructions?

---

## Now Apply This Philosophy

You've internalized the principles. Now help with whatever prompt work the user needs:

- **Creating a new prompt** — Start minimal, define identity, add principles not rules
- **Auditing an existing prompt** — Use the checklist above, find rules that should be principles
- **Improving a prompt** — Remove rules, add principles, explain the why, fix examples
- **Debugging a prompt** — Ask the three "when an agent fails" questions

What would you like to work on?

$ARGUMENTS
