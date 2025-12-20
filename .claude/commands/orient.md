---
description: Get oriented in the project quickly
---

You are getting oriented so you can contribute immediately.

## The Problem You're Solving

Every Claude session starts without memory. The state.json and hooks help, but sometimes you need to actually understand what you're working with—not just what the last session did, but what this project is, how it's structured, and where it's going.

Good context loading means you can start doing useful work in minutes instead of spending the first half hour asking clarifying questions and reading random files.

## What You Need to Know

**What is this project?** Read package.json, README, whatever defines what this thing does and why it exists. Understand the purpose, not just the technology.

**What's the current state?** Read .claude/state.json if it exists. What's the current focus? What happened last session? What's in the backlog? What's been shipped recently?

**How is it structured?** Look at the directory layout. Identify where the core logic lives versus configuration versus tests versus build artifacts. Understand the shape before diving into details.

**What's happening right now?** Check git status and recent commits. Is there work in progress? What branch is this? What's changed recently?

**What's the technology?** Identify the framework, language version, key dependencies. These affect how you'll approach any task.

## What You Don't Need

Don't read every file. Don't trace every import. Don't build a complete mental model of the entire codebase before doing anything.

Context loading is about getting oriented enough to start, not achieving complete understanding before beginning. You'll learn more as you work. The goal is avoiding obvious mistakes from ignorance, not eliminating all uncertainty.

## Synthesis, Not Summary

After gathering information, synthesize it into orientation that helps you (and the user) understand where we are.

What is this? One sentence on purpose and technology.

Where are we? Current focus, recent work, active branch.

What's waiting? Open backlog items, especially high priority.

What's the shape? Key directories and what lives where.

Present this as orientation, not as a report. The output should feel like "here's what I understand, ready to work" not "here's everything I found organized into categories."

## What Comes Next

End with direction. Based on what you found:

If there's a current focus, summarize where it left off and confirm that's what we're continuing.

If there's high-priority backlog, surface it as an option.

If there's nothing obvious, ask what the user wants to work on.

Don't just load context and stop. Context serves action. Point toward what's next.

$ARGUMENTS
