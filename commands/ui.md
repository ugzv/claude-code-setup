---
description: Audit visual consistency, component patterns, and implementation quality
---

Systematic visual interface review.

## Philosophy

**Implementation reveals intent.** The codebase shows what designers decided mattered. Find where reality drifts from that intent—inconsistent spacing, orphaned styles, missing states.

**Patterns over instances.** One hardcoded color is a typo. Ten hardcoded colors is a missing abstraction. Look for what the codebase is trying to systematize and where it fails.

**Balance the audit.** Visual consistency, component quality, state coverage, and responsiveness matter as much as accessibility. Don't let any single dimension dominate findings.

## The Process

### 1. Discover the Design System

Before auditing, understand what consistency means for this project:

- Does a design system exist? (tokens, theme files, component library)
- What conventions are established? (naming, spacing scale, color palette)
- What's intentionally flexible vs. accidentally inconsistent?

**Output this explicitly**: "Design system: [description]. Conventions found: [list]. Gaps: [list]."

This prevents flagging intentional variation as bugs.

### 2. Audit Dimensions

Review each dimension, noting patterns not just instances:

**Visual Consistency**
- Color usage: palette adherence, semantic meaning
- Typography: hierarchy, font stacks, size scales
- Spacing: consistent rhythm or arbitrary values
- Component styling: similar elements styled similarly

**Component Quality**
- Reusability: props-driven or copy-pasted variants
- Composition: flexible or rigid structures
- Naming: semantic intent or visual description

**State Coverage**
- Loading states: skeleton, spinner, or nothing?
- Empty states: helpful or blank?
- Error states: actionable or cryptic?
- Edge cases: long text, missing images, slow connections

**Responsiveness**
- Breakpoint strategy: consistent or ad-hoc?
- Touch targets on mobile
- Content priority: what shows/hides at each breakpoint

**Accessibility**
- Keyboard navigation and focus states
- Screen reader compatibility where relevant
- Contrast issues if visually obvious

### 3. Categorize Findings

**Systematic issues**: Missing abstraction, need design system work
**Drift**: Started consistent, became inconsistent over time
**Oversight**: Never implemented (a11y, states, responsiveness)
**Technical debt**: Worked around limitation, now cruft

## Output

```markdown
## UI Audit: [App Name]

**Design system status:** [exists/partial/none] - [brief description]
**Key insight:** [one sentence - the most important finding]

## Systematic Issues
Problems requiring design system or architectural changes.
- Pattern observed
- Why it matters (user/developer impact)
- Scope (how widespread)
- Evidence (file:line examples)

## Inconsistencies
Same concept, different implementations.
- What varies
- Examples of the variations
- Suggested canonical version

## Missing States
UI conditions not handled.
- Component/flow
- Missing state (loading/empty/error/edge)
- User impact

## Component Opportunities
Duplication that could become abstraction.
- Pattern appearing multiple times
- Variations that exist
- Consolidation approach

## Quick Wins
Low-effort, high-impact fixes.
```

## What Makes Good Findings

**Systematic**: Identifies patterns, not just instances

**Impact-aware**: Explains why it matters to users or developers

**Proportionate**: Distinguishes "fix now" from "consider eventually"

**Evidence-based**: Points to code, not hypotheticals

## After the Audit

Offer to:
1. Generate handoff blocks for issues to address later
2. Fix quick wins immediately
3. Propose design system improvements if none exists
4. Add items to backlog

## Handoff Blocks

Generate copy-paste ready prompts for new Claude Code sessions. Each handoff should trigger investigation, validation, and proper solution design—not blind fixing.

**Structure each handoff as:**

```markdown
## Issue: [Short descriptive title]

### The Problem
[What's wrong: "The app has inconsistent X" or "Component Y lacks Z"]

### Evidence from Audit
- What was observed: [specific inconsistencies/gaps found]
- Scope: [how widespread—one component or systemic]
- Relevant files (hypothesis, verify these): [file:line references]

### Your Task
1. **Verify** the issue—check the referenced files, confirm the problem exists as described
2. **Assess** scope—is this isolated or part of a pattern? Are there other instances?
3. **Evaluate** options—what are the tradeoffs? (quick fix vs. systematic solution)
4. **Propose** your approach before implementing—explain your reasoning
5. **Implement** the solution you've validated

### Success Criteria
[Observable outcome: "All buttons use consistent padding" or "Error states show actionable messages"]

### Questions to Answer First
- Is this actually inconsistent, or intentional variation?
- Should this be fixed in place, or does it need a design system change?
- What's the blast radius of the fix?
```

**Principle**: The receiving session should think "let me understand this" not "let me implement this fix." Investigation prevents wrong solutions and over-engineering.

$ARGUMENTS
