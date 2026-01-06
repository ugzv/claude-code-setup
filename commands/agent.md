---
description: Audit Claude Agent SDK projects for architecture issues
---

Audit agent projects for structural problems before production failures.

**Not about prompt style** (that's `/prompt-guide`). This is about architecture: agent loop, tool definitions, safety.

## Run Audits in Parallel

**Spawn all auditors at once:**

```
┌────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE                                     │
├────────────────────────────────────────────────────────┤
│  1. loop-auditor                                       │
│     → gather → act → verify phases present?            │
│     → Missing phases = unreliable agent                │
│                                                        │
│  2. tool-auditor                                       │
│     → Names action-oriented? Descriptions say WHEN?    │
│     → Parameters typed with descriptions?              │
│     → Return: quality score per tool                   │
│                                                        │
│  3. prompt-auditor                                     │
│     → Identity clear? Principles vs rules?             │
│     → Conflicting instructions?                        │
│                                                        │
│  4. safety-auditor                                     │
│     → Destructive actions need confirmation?           │
│     → Input validation? Rate/loop limits?              │
│     → Return: gaps with severity                       │
└────────────────────────────────────────────────────────┘
```

## The Agent Loop

Every effective agent: **gather context → take action → verify work → repeat**

- **Gather**: Tools to fetch info before acting (not guessing from prompt)
- **Act**: Well-scoped tools, confirmations for destructive ops, timeouts
- **Verify**: Validation tools (lint, test, schema check) before returning

Missing phase = unreliable agent.

## Tool Quality

**Name**: Action-oriented, specific (`check_order_status` not `helper`)
**Description**: WHEN to use, not just WHAT ("Use after looking up customer ID")
**Parameters**: Typed with descriptions
**Returns**: Structured errors, not exceptions

## Subagent Architecture

- Single clear purpose per subagent
- Tool restrictions (read-only agents shouldn't have Edit)
- Context isolation (large searches in subagents, return only relevant findings)

## Safety Checks

- Destructive actions require confirmation
- Input validation schemas
- Secrets not leaked in responses
- maxTurns or loop limits

## Report

- Architecture grade (gather → act → verify?)
- Critical issues (will cause failures)
- Improvements (reliability gains)
- Missing pieces (tools/capabilities needed)

Be specific - point to actual code.

$ARGUMENTS
