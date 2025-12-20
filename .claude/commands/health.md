---
description: Check overall project health
---

You are assessing whether this team can ship with confidence.

## What Health Actually Means

Project health isn't about metrics hitting thresholds. It's about answering one question: when this team pushes code, do they know it works?

A healthy project has feedback loops. Tests catch bugs before users do. Types catch mistakes before runtime does. Linting catches patterns that correlate with problems. CI fails before broken code reaches production.

An unhealthy project has hope instead of feedback. "I think this works." "It worked on my machine." "We'll find out in production." Every push is a small gamble.

Your job is to assess how much this team is gambling versus knowing.

## The Investigation

Run whatever checks this project has: type checker, test suite, linter, build. But you're not collecting numbers to report. You're understanding what the numbers reveal about the team's ability to ship confidently.

**If tests pass**, that's a floor, not a ceiling. Do the tests cover the code that matters? Are they testing behavior or implementation? Would they catch the kinds of bugs that actually happen here?

**If tests fail**, that's not automatically bad. One failing test in an active area might mean someone is mid-work. A hundred failing tests that nobody's looked at in weeks means the feedback loop is broken.

**If the type checker complains**, where do the complaints cluster? Scattered `any` types might just be laziness. Concentrated type errors in one module might indicate a design problem.

**If linting shows warnings**, which warnings? Unused variables are noise. Possible null dereferences are signal.

The tools generate data. Your job is interpretation.

## Dependencies Are Attack Surface

Every dependency is code you don't control. That's fine—leverage is valuable—but it's also risk.

Security vulnerabilities in dependencies are non-negotiable. If there's a known CVE in a package this project uses, that's not a "concern"—that's an open door.

Staleness is different. A package two years behind latest might be fine if it's stable and working. Or it might be accumulating debt that makes the eventual upgrade painful. The question is: what's the cost of staying where we are versus the cost of upgrading?

Check what's vulnerable. Check what's outdated. But interpret what you find.

## Technical Debt Markers

TODOs, FIXMEs, HACKs—these are the team's notes to their future selves. They represent known gaps between "what we shipped" and "what we wanted."

Search for TODO, FIXME, HACK, XXX, BUG markers. Use git blame to date them—a two-week-old TODO might be active work, a two-year-old FIXME is a broken promise.

**What matters:**
- **Markers in critical paths** (auth, payments, data integrity) represent real risk
- **Ancient markers** (6+ months) need conscious decisions: fix, document why blocked, or remove
- **Clusters** in one area suggest that module was rushed or needs focused cleanup
- **Context decay**—cryptic markers like "TODO: fix the thing" that nobody understands anymore

A codebase with zero markers in 50,000 lines is suspicious—either superhuman or not noticing problems. Many markers might mean the team acknowledges debt. The question is: are they being addressed or just accumulating?

## What to Report

Don't dump tool output. Synthesize an assessment.

**Can this team ship with confidence?** If yes, say so and note what's working. If not, explain specifically what's broken: "The test suite passes, but it's only covering 30% of the payment module. Two production bugs last month came from untested payment code paths."

**What's the highest-leverage improvement?** Not everything needs fixing. What one thing would most improve this team's ability to ship confidently? Maybe it's adding tests to a critical path. Maybe it's upgrading a vulnerable dependency. Maybe it's fixing the flaky CI that makes people ignore failures.

**What can wait?** Acknowledge what you found that isn't urgent. "There are 12 lint warnings and a package two minor versions behind. These are real but not blocking confidence."

## After Assessment

Don't just diagnose and stop. The user wants to ship with more confidence, not just understand why they can't.

For the highest-leverage improvement you identified, offer to do it. If it's running an audit fix, updating a vulnerable package, or adding a critical test—offer to execute it now.

For improvements that need more work, explain what's involved and offer to start. "The payment module needs tests. Want me to add coverage for the checkout flow?"

For stale TODO markers that no longer make sense—offer to remove them. For markers in critical paths—offer to investigate what fixing would involve. For markers worth tracking—offer to add to backlog.

For things that are real but not urgent, note them so they don't get forgotten. Add to backlog if they warrant tracking.

The goal is a project that can ship with more confidence than before you ran this command.

$ARGUMENTS
