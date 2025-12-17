---
description: Analyze codebase for refactoring opportunities
---

You are investigating where this codebase resists change.

## The Problem You're Solving

Refactoring isn't about cleanliness. It's about the gap between how fast this team *could* ship and how fast they *actually* ship. Every hour spent deciphering confusing code, every bug that hides in complexity, every new developer who takes weeks instead of days to contribute—that's the cost of code that resists change.

Your job is to find where that resistance lives and quantify what it's costing.

## What Resistance Looks Like

You're not looking for code that violates style guides. You're looking for code that fights back when someone tries to change it.

The symptoms show up in the team's experience: files everyone dreads touching, functions that break in unexpected ways when modified, areas where only one person knows what's happening, modules where simple features take disproportionately long to add.

The causes are usually structural: responsibilities that should be separate are tangled together, assumptions that should be explicit are buried in logic, complexity that should be isolated has leaked everywhere.

When you find code that resists change, you've found code that's actively slowing down the team.

## Before You Start

Read `.claude/state.json`:
- Check `backlog` - skip issues already being tracked
- Check `currentFocus` - if another session is working on files you might refactor, warn about potential conflicts before proceeding

## How to Investigate

Use whatever analysis tools exist in this project—linters, type checkers, complexity analyzers. But treat their output as evidence, not verdicts.

A linter warning about function length is data. The question is: what does this length *mean*? Is this a god function doing five jobs? A well-organized sequence that happens to be long? A function that grew organically and nobody noticed?

The tools tell you *where* to look. Your job is understanding *why* it matters.

When you find concerning code, trace its impact:
- How often does this file change? (High churn + high complexity = pain)
- What depends on this? (Wide coupling + confusion = cascading bugs)
- Who understands this? (Sole ownership + complexity = risk)

## What to Report

For each opportunity you identify, connect it to outcomes:

**What's the resistance?** Not "this function is 200 lines" but "this function handles authentication, logging, rate limiting, and the actual business logic—you can't change any one of these without understanding all of them."

**What's it costing?** Be specific. "This file has been modified 47 times in the last 6 months with 12 bugs introduced. Each bug took average 4 hours to diagnose because the logic is interleaved." Or "New developers have reported this module as the hardest to understand. Two attempted fixes were reverted."

**What would change look like?** Not "refactor this" but "extract rate limiting into middleware, move auth to a decorator, keep this function focused on the business logic. Result: each concern testable in isolation, future changes scoped to one place."

**What's the investment?** Roughly how much effort to fix, and what does the team get back? "Half-day refactor that would eliminate the recurring auth bugs and cut onboarding time for this module."

## Prioritization

Not everything that could be cleaner should be refactored. Focus on leverage:

Where is the team actually feeling pain? Code that's ugly but stable and rarely touched isn't costing anything. Code that's moderately messy but changes every sprint is costing constantly.

What would unblock future work? Sometimes one refactor enables many features. Sometimes a refactor just makes code prettier without enabling anything.

What's the blast radius of not acting? Some complexity just accumulates developer annoyance. Some complexity is a bug waiting to happen in production.

The best refactoring targets are high-pain, high-leverage, bounded-effort. Find those.

## After Analysis

Don't just report and stop. The user came to you because they want the code to be better, not because they wanted a list of problems.

For the highest-leverage opportunity you found, offer to do it. If it's a bounded refactor—extracting a function, splitting a file, untangling two concerns—offer to execute it now and show what changes.

Before starting any refactor work, register in `currentFocus`:
```json
{
  "description": "refactor: [what you're doing]",
  "files": ["files", "being", "refactored"],
  "started": "YYYY-MM-DD"
}
```

For larger refactors that need more consideration, explain what's involved and offer to start. "This is a half-day effort. Want me to begin with the first piece?"

For things that should wait, add them to `.claude/state.json` backlog with enough context that future-you or future-someone can pick them up without re-investigating.

The goal is code that resists change less than it did before you ran this command.

$ARGUMENTS
