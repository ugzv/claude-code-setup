---
description: Commit all uncommitted changes, grouped intelligently into multiple commits
---

Find ALL uncommitted changes and commit them properly, grouping related changes into separate commits. Execute without asking for confirmation.

## Why Grouping Matters

A commit should tell one story. Someone reading the history should understand what happened. Someone reverting should only undo related changes—not unravel three unrelated fixes tangled together.

When multiple changes exist, the question isn't "how do I commit everything" but "what are the logical units here?" A config change and a bugfix that happened in the same session are two stories, not one.

## What Makes Changes Related

Changes belong together when they serve the same purpose. Ask: "If I had to revert this, what would make sense to undo as a unit?"

Files implementing the same feature belong together. Files fixing the same bug belong together. A refactor that touches many files but serves one goal is one commit.

Files that happen to be nearby in the directory tree but serve different purposes are separate commits. Proximity isn't relationship.

## Safety Awareness

Some files should never be committed regardless of context: secrets (`.env`, `*.pem`, `*.key`), build artifacts that should be gitignored (`node_modules/`, `dist/`, `.next/`).

If you encounter these, skip them silently and mention in the summary. Don't ask, don't commit, don't stop—just note what was skipped and why.

## Commit Quality

Each commit follows the same standards as `/commit`: conventional format, imperative mood, under 72 characters, no AI fingerprints.

The goal is a git history that looks like a thoughtful developer made deliberate, atomic commits—because that's what's happening, even if the developer is assisted.

## Handling Problems

If something fails (merge conflict, staging error), skip that file and continue with others. Report what couldn't be committed and why, but don't let one problem stop the whole operation.

## After Committing

Report what was committed, how it was grouped, and what was skipped. The user should understand the shape of what just happened to their history.

Don't push—that's `/push` when ready.

$ARGUMENTS
