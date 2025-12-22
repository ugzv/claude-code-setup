---
description: Audit Claude Agent SDK projects for architecture issues
---

You are auditing an agent project to find structural problems before they cause failures in production.

## What This Is NOT

This is not about prompt writing style (that's `/prompt`). This is about agent **architecture**:
- Does the agent loop work correctly?
- Are tools well-defined?
- Will subagents behave predictably?
- Are there safety gaps?

## Run Audits in Parallel

**IMPORTANT: Use subagents to audit different aspects simultaneously.** These checks are independent.

```
┌─────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)│
├─────────────────────────────────────────────────────────┤
│  1. loop-auditor                                        │
│     → Check: gather → act → verify phases present?      │
│     → Find: context tools, action tools, validation     │
│     → Flag: missing phases, broken feedback loops       │
│                                                         │
│  2. tool-auditor                                        │
│     → Check: naming, descriptions, parameter types      │
│     → Flag: vague names, missing "when to use"          │
│     → Return: tool quality scores                       │
│                                                         │
│  3. prompt-auditor                                      │
│     → Check: identity, principles vs rules, conflicts   │
│     → Flag: if-then rules, contradictions               │
│     → Return: prompt structure assessment               │
│                                                         │
│  4. safety-auditor                                      │
│     → Check: destructive action confirmations           │
│     → Check: input validation, rate limits, secrets     │
│     → Flag: missing safeguards                          │
└─────────────────────────────────────────────────────────┘
```

**Example subagent prompts:**

```
# Tool auditor
Find all tool definitions in this project. For each tool, assess:
1. Name: Is it action-oriented and specific? (not "do_thing", "helper")
2. Description: Does it explain WHEN to use, not just WHAT?
3. Parameters: Are they typed with descriptions?
4. Error handling: Does it return structured errors?

Return a quality score (1-5) for each tool with specific issues.
```

```
# Safety auditor
Check this agent project for safety gaps:
1. Do destructive actions (delete, modify, send) require confirmation?
2. Are there input validation schemas?
3. Could the agent leak secrets in responses?
4. Is there a maxTurns or similar loop limit?

Return: list of safety gaps with severity (critical/high/medium).
```

### Wait and Synthesize

After all auditors return, create a unified report:
- Architecture grade (does it implement gather → act → verify?)
- Critical issues (must fix before production)
- Improvements (would make agent more reliable)
- Missing pieces (tools or capabilities needed)

## The Agent Loop

Every effective agent follows: **gather context → take action → verify work → repeat.**

Check if this project implements all three phases:

**Gather context:**
- Does the agent have tools to fetch information before acting?
- Can it search, read, query what it needs?
- Or does it guess based on the prompt alone?

**Take action:**
- Are the action tools well-scoped?
- Do destructive actions require confirmation?
- Are there appropriate timeouts and error handling?

**Verify work:**
- Does the agent check its own output before returning?
- Are there validation tools (linting, testing, schema checks)?
- Or does it just trust that actions succeeded?

If any phase is missing, the agent will be unreliable.

## Tool Definition Quality

Find all tool definitions. For each, check:

**Name:** Action-oriented and specific?
- Good: `check_order_status`, `send_notification`
- Bad: `do_thing`, `helper`, `process`

**Description:** Does it explain WHEN to use, not just WHAT it does?
- Good: "Get order status. Use after looking up customer ID. Returns shipping status, tracking number, and ETA."
- Bad: "Gets order status."

**Parameters:** Are they typed with descriptions?
- Good: `customer_id: z.string().describe("Customer ID from lookup_customer")`
- Bad: `id: any`

**Return value:** Does the agent know what it will get back?

**Error handling:** Does the tool return structured errors, not throw exceptions?

## Subagent Architecture

If the project uses subagents, check:

**Purpose clarity:** Does each subagent have a single, clear purpose?
- Good: "Security code reviewer - checks for vulnerabilities"
- Bad: "Helper agent"

**Tool restrictions:** Are subagents limited to necessary tools?
- Read-only analysis agents should NOT have Edit/Write
- Test runners need Bash but probably not Write

**Context isolation:** Are subagents used to prevent context pollution?
- Large searches should go to subagents, return only relevant findings
- Main agent shouldn't be flooded with intermediate results

**Parallelization opportunities:** Could independent work run in parallel?

## System Prompt Structure

Check the main agent's system prompt for:

**Identity:** Is it clear who this agent is? (1-2 sentences)

**Principles vs rules:** Does it explain WHY (principles) or just WHAT (if-then rules)?
- Principles generalize to novel situations
- Rules break on edge cases

**Tool guidance:** Does it tell the agent when to use each tool, not just how?

**Conflicting instructions:** Are there contradictions?
- "Be concise" + "Include all details" = confusion

## Safety Checks

**Destructive actions:**
- Do delete/modify/send operations require confirmation?
- Is there a `confirm: true` pattern or similar?

**Input validation:**
- Are schemas enforcing constraints?
- Could malformed input cause problems?

**Sensitive data:**
- Are credentials handled safely?
- Could the agent leak secrets in responses?

**Rate limiting:**
- Could the agent loop infinitely?
- Are there maxTurns or similar limits?

## What to Report

After analyzing the project, report:

**Architecture grade:**
- Does it implement gather → act → verify?
- Are tools well-defined?
- Is the system prompt principle-based?

**Critical issues:** Things that will cause production failures.

**Improvements:** Things that would make the agent more reliable.

**Missing pieces:** Tools or capabilities the agent probably needs but doesn't have.

Be specific. Point to actual code. Don't just say "improve tool descriptions" - say which tool and how.

$ARGUMENTS
