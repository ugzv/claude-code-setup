---
description: Find unused code, exports, and dependencies
---

You are finding what this codebase is carrying but not using.

## Why This Matters

Every line of code that exists but doesn't run has costs that aren't obvious until you add them up.

Developers read it, trying to understand the system, wasting time on paths that don't matter. It gets updated during refactors—effort spent maintaining nothing. It ships to users as bundle weight, slowing load times. It sits in dependencies with potential vulnerabilities, expanding attack surface for code that provides no value.

The cleanest code is code that doesn't exist. Your job is to find what can be removed.

## The Challenge of "Unused"

Not everything that looks unused is actually dead. Your job is distinguishing genuine dead weight from code that's alive in ways the tools can't see.

**Genuinely dead:** Functions nothing calls. Exports nothing imports. Dependencies with no import statements. These are safe to remove.

**Alive but invisible:** Dynamic imports load code by variable name. Plugin systems discover code by convention. Public APIs expose code for external consumers. Test utilities only run in test environments. These look dead to static analysis but aren't.

**Dead but intentional:** Deprecation wrappers during migrations. Emergency rollback code. Reference implementations kept for documentation. These are dead but kept for reasons.

The tools find candidates. Your job is understanding which candidates are actually safe to remove.

## Investigation

Use the analysis tools available—knip, depcheck, vulture, ts-prune, whatever this project has or can easily add. They're good at finding things nothing references.

But before recommending removal, verify:

Is there dynamic loading nearby? `import()` with variables, `require()` with computed paths, plugin registration patterns—these make static analysis blind.

Is this a public API? Libraries and CLIs expose code for external consumers. Nothing *internal* imports it, but that doesn't mean nothing uses it.

Is this test infrastructure? Utilities only imported in test files might look unused from the source code's perspective.

When you're confident something is genuinely dead, note the evidence. When you're uncertain, say so.

## What Removal Gains

For each thing you identify as removable, connect it to outcomes:

**Dead code:** "This 200-line module hasn't been imported since the 2023 refactor. Removing it eliminates confusion for new developers and stops it from showing up in searches."

**Unused dependencies:** "Lodash is in package.json but nothing imports it. Removing it drops 70KB from the bundle and eliminates one more package to audit for vulnerabilities."

**Dead exports:** "These 12 functions are exported but never imported. They're cluttering the API surface and making it harder to understand what this module actually provides."

Don't just list what can be removed. Explain why removal makes things better.

## Taking Action

For high-confidence removals—dead internal code, clearly unused dependencies—offer to execute the cleanup directly.

For uncertain cases, recommend investigation rather than immediate removal. "This looks unused but there's a dynamic import pattern in the codebase. Verify with the team before removing."

For large cleanups that might need coordination, suggest adding to the backlog with context about what's involved.

The goal isn't maximum deletion. It's removing what's genuinely dead weight while avoiding false positives that break things.

$ARGUMENTS
