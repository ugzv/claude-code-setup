---
description: Analyze dependencies and update to latest versions
---

You are managing the code this project imports but doesn't control.

## The Dependency Bargain

Every dependency is a trade: you get leverage (someone else solved this problem) in exchange for risk (you're running code you didn't write and can't fully verify).

Good dependency management isn't about having the newest versions of everything. It's about being conscious of the trade you're making and keeping the risk side of the bargain under control.

Your job is to find where the risk has grown without the team noticing, and bring it back under control.

## Security Is Non-Negotiable

A known vulnerability in a dependency is an open door. It doesn't matter if the package is working fine, if the team is busy, if the upgrade looks annoying. An attacker doesn't care about your roadmap.

Check for vulnerabilities first. If you find HIGH or CRITICAL severity issues, those get fixed before anything else gets discussed. Not flagged for later—fixed now, or a very good reason documented for why not.

This isn't about best practices. It's about not leaving doors open.

## Staleness Is Contextual

A package being outdated isn't automatically a problem. The question is: what's accumulating while you wait?

**Security patches you're missing:** Even non-critical vulnerabilities accumulate. The package that's "fine" today might have three CVEs by next quarter.

**Bug fixes you'd benefit from:** If the team has worked around a bug that's fixed upstream, staying outdated is choosing continued pain.

**Migration distance:** The further behind you fall, the harder the eventual upgrade. Going from v1 to v2 is usually documented. Going from v1 to v5 means reading four migration guides and hoping they compose.

**Ecosystem compatibility:** Fall too far behind and other packages stop supporting your version. Now you're blocked from upgrading anything until you upgrade this.

But also: a stable, working package with no security issues that you're two minor versions behind on? That might be fine. The cost of upgrading is real too.

Assess what waiting is actually costing, not just that a newer version exists.

## Unused Dependencies Are Pure Risk

A package in your dependency list that nothing imports is the worst trade: you're getting zero leverage (no code using it) in exchange for full risk (vulnerabilities, bundle size, audit surface).

Find these and remove them. There's no upside to keeping them.

## Taking Action

Don't just report what you find. Execute improvements.

**Security vulnerabilities:** Fix them. Run the audit fix command, or manually upgrade the affected packages. If something blocks the fix, explain specifically what and why.

**Patch updates:** These are almost always safe. Update them in batch.

**Minor updates:** Usually safe, occasionally contain surprises. Update them but verify the project still builds and tests pass.

**Major updates:** These need care. Do them one at a time, check release notes for breaking changes, verify thoroughly between each.

**Unused packages:** Remove them. No reason to keep paying the cost.

After making changes, run the test suite and build to verify nothing broke. Report what you updated, what you removed, what you couldn't fix and why.

## What Success Looks Like

After this runs, the project should be:
- **Secure:** No known vulnerabilities, or documented exceptions with timeline
- **Current:** Not bleeding edge, but not accumulating debt
- **Minimal:** Not carrying packages that provide no value

If major upgrades need to wait for good reasons, add them to the backlog with context so they don't get forgotten.

$ARGUMENTS
