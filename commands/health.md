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

A codebase with many markers isn't necessarily unhealthy. It might mean the team is disciplined about acknowledging debt. A codebase with zero markers in 50,000 lines is suspicious—either the team is superhuman or they're not noticing problems.

Look at the markers that exist. Are they fresh or ancient? Are they in critical paths or edge cases? Does anyone seem to be addressing them or are they just accumulating?

## What to Report

Don't dump tool output. Synthesize an assessment.

**Can this team ship with confidence?** If yes, say so and note what's working. If not, explain specifically what's broken: "The test suite passes, but it's only covering 30% of the payment module. Two production bugs last month came from untested payment code paths."

**What's the highest-leverage improvement?** Not everything needs fixing. What one thing would most improve this team's ability to ship confidently? Maybe it's adding tests to a critical path. Maybe it's upgrading a vulnerable dependency. Maybe it's fixing the flaky CI that makes people ignore failures.

**What can wait?** Acknowledge what you found that isn't urgent. "There are 12 lint warnings and a package two minor versions behind. These are real but not blocking confidence."

The goal isn't a report card. It's actionable understanding of what's helping and what's hurting this team's ability to ship.

$ARGUMENTS
