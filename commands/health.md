---
description: Check overall project health
---

You are assessing whether this team can ship with confidence.

## What Health Actually Means

Project health isn't about metrics hitting thresholds. It's about answering one question: when this team pushes code, do they know it works?

A healthy project has feedback loops. Tests catch bugs before users do. Types catch mistakes before runtime does. Linting catches patterns that correlate with problems. CI fails before broken code reaches production.

An unhealthy project has hope instead of feedback. "I think this works." "It worked on my machine." "We'll find out in production." Every push is a small gamble.

Your job is to assess how much this team is gambling versus knowing.

## Run Checks in Parallel

**IMPORTANT: Use subagents to run all checks simultaneously.** These checks are independent—there's no reason to wait for security audit to finish before starting type checking.

### Detection Phase (Quick)

First, quickly detect what tools are available:

```bash
# Detect project type and available tools
ls package.json pyproject.toml go.mod Cargo.toml 2>/dev/null
```

### Parallel Execution Phase

**Spawn subagents for each category simultaneously.** Use the Task tool with multiple parallel invocations:

```
┌─────────────────────────────────────────────────────────┐
│  SPAWN ALL AT ONCE (single message, multiple Task calls)│
├─────────────────────────────────────────────────────────┤
│  1. security-check    → npm audit / pip-audit / govuln  │
│  2. type-check        → tsc / mypy / pyright            │
│  3. test-runner       → pytest / npm test / go test     │
│  4. lint-check        → eslint / ruff / golangci-lint   │
│  5. outdated-check    → npm outdated / pip list         │
│  6. debt-scan         → grep TODO/FIXME + git blame     │
└─────────────────────────────────────────────────────────┘
```

Each subagent should:
- Run the appropriate tool for the detected project type
- Capture output and exit code
- Return a structured summary: status (pass/warn/fail), count of issues, key findings

**Example prompt for a subagent:**
```
You are a security scanner. Run the appropriate security audit for this project:
- JS/TS: npm audit (or pnpm/yarn audit)
- Python: pip-audit or safety check
- Go: govulncheck

Return: {"status": "pass|warn|fail", "critical": N, "high": N, "details": "..."}
```

### Wait and Synthesize

After spawning all subagents, wait for results and synthesize:
- Collect all subagent outputs
- Prioritize findings (security > failing tests > type errors > lint)
- Create unified health report

## Interpreting Results

**If tests pass**, that's a floor, not a ceiling. Do the tests cover the code that matters? Are they testing behavior or implementation? Would they catch the kinds of bugs that actually happen here?

**If tests fail**, that's not automatically bad. One failing test in an active area might mean someone is mid-work. A hundred failing tests that nobody's looked at in weeks means the feedback loop is broken.

**If the type checker complains**, where do the complaints cluster? Scattered `any` types might just be laziness. Concentrated type errors in one module might indicate a design problem.

**If linting shows warnings**, which warnings? Unused variables are noise. Possible null dereferences are signal.

The tools generate data. Your job is interpretation.

## Dependencies Are Attack Surface

Every dependency is code you don't control. That's fine—leverage is valuable—but it's also risk. Your job is to find where the risk has grown without the team noticing.

### Security Is Non-Negotiable

A known vulnerability in a dependency is an open door. It doesn't matter if the package is working fine, if the team is busy, if the upgrade looks annoying. An attacker doesn't care about your roadmap.

Check for vulnerabilities first. If you find HIGH or CRITICAL severity issues, those get fixed before anything else gets discussed. Not flagged for later—fixed now, or a very good reason documented for why not.

**Use the right tools:**
- **JS/TS:** `npm audit`, `pnpm audit`, or `yarn audit`
- **Python:** `pip-audit` (install with `pip install pip-audit`), or `safety check`
- **Go:** `govulncheck` (install with `go install golang.org/x/vuln/cmd/govulncheck@latest`)

If security tooling isn't installed, offer to add it.

### Staleness Is Contextual

A package being outdated isn't automatically a problem. The question is: what's accumulating while you wait?

- **Security patches you're missing:** Even non-critical vulnerabilities accumulate
- **Bug fixes you'd benefit from:** Workarounds for bugs fixed upstream are chosen pain
- **Migration distance:** v1 to v2 is documented. v1 to v5 means four migration guides
- **Ecosystem compatibility:** Fall too far behind and other packages stop supporting you

But also: a stable package with no security issues that's two minor versions behind? That might be fine.

**Check for outdated packages:**
- **JS/TS:** `npm outdated`, `pnpm outdated`, or `yarn outdated`
- **Python:** `pip list --outdated`, or `uv pip list --outdated`

### Unused Dependencies Are Pure Risk

A package in your dependency list that nothing imports is the worst trade: zero leverage, full risk. Find these and remove them.

### Taking Action on Dependencies

Don't just report—execute improvements:

- **Security vulnerabilities:** Fix them now. Run audit fix, or manually upgrade
- **Patch updates:** Almost always safe. Batch update them
- **Minor updates:** Usually safe. Update and verify tests pass
- **Major updates:** Do one at a time, check release notes, verify thoroughly
- **Unused packages:** Remove them

After changes, run the test suite and build to verify nothing broke.

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
