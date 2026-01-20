---
description: Audit visual consistency, component patterns, and implementation quality
---

Deep visual interface audit using parallel specialized agents.

## Philosophy

**Implementation reveals intent.** The codebase shows what designers decided mattered. Find where reality drifts from that intent—inconsistent spacing, orphaned styles, missing states.

**Patterns over instances.** One hardcoded color is a typo. Ten hardcoded colors is a missing abstraction. Look for what the codebase is trying to systematize and where it fails.

**The "AI-generated look" test.** Would a design-conscious user perceive this as polished or generic? Professional UIs have intentional hierarchy, harmonious colors, and information density that respects scanning. Generic UIs have formulaic layouts, clashing accents, walls of text, and components that feel "off."

**Cross-page consistency.** The same component must look and behave identically everywhere. Drift between pages signals a missing abstraction or implementation sloppiness.

**Production-ready = complete.** Every interaction path must feel finished: hover, focus, loading, error, empty, disabled. Half-implemented states make the whole UI feel unfinished.

**Engagement over transaction.** Sticky apps (WhatsApp, Telegram, TikTok) reward interaction through micro-feedback loops: instant acknowledgment when you act, progress that motivates continuation, anticipation of what's next, social proof that others are present, notification gravity that pulls return visits. A UI that just "works" but doesn't create these moments feels dead. Audit for: does interaction feel rewarding, or merely functional?

## The Audit

### Phase 1: Understand Before Judging

Before spawning auditors, discover what "consistent" means for THIS project. What design system exists? What's enforced? What patterns repeat? Map the pages and components.

This context shapes everything—auditors need to know the intended standard, not just look for generic best practices.

### Phase 2: Spawn Parallel Auditors

**Why parallel?** Each visual dimension requires exhaustive checking. A single pass skims; specialized auditors catch drift that only emerges when checking ALL instances.

**CRITICAL: Spawn all at once** in a single message with multiple Task calls.

Design auditors around what Phase 1 revealed matters for this project. Common concerns:

- **Token adherence** — are design system values used, or hardcoded?
- **Component consistency** — same concept implemented the same way everywhere?
- **Cross-page uniformity** — navigation, headers, footers identical across app?
- **State coverage** — every interactive element has all states?
- **Animation coherence** — timing, easing, feedback feel unified?
- **Engagement mechanics** — does the UI reward interaction and create return motivation?
- **Production polish** — sizing, targets, truncation, stacking all feel right?

But adapt. A component library project needs different auditors than a marketing site. Let the codebase tell you what to check.

**Give auditors permission to think deeply.** "You have abundant context. Check ALL instances. Report patterns, not just violations."

### Phase 3: Synthesize

**Convergence = importance.** Issues flagged by multiple auditors from different angles are confirmed systematic problems.

**Categorize by root cause** (systematic gap, drift over time, never implemented, needs polish) and **prioritize by user impact** (blocking, degraded, polish).

### Output

Answer: "What would a design-conscious user notice as 'off'?"

Be specific—file:line references, scope counts, concrete fix approaches. Vague findings aren't actionable. Structure around findings, not auditor reports.

## After the Audit

**Handoff if warranted.** Group findings into phases that build on each other and leave the codebase working after each. Phase structure emerges from findings.

**Fix quick wins** if user wants immediate improvement.

**Backlog** issues that don't need immediate attention.

## What Good Looks Like

Deep, not wide. Convergent. Actionable. Prioritized by impact. Honest—if the UI is solid, say so.

$ARGUMENTS
