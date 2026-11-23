---
name: wrap-up
description: End-of-session routine from spec/11 - rebuild, run the checks, update BUILD_LOG.md and commit. Use when the owner types /wrap-up or says the session is ending.
allowed-tools: Bash(python tools/*) Bash(git status *) Bash(git add *) Bash(git commit *)
---

1. Run `python tools/build.py`, then `python tools/ci.py --partial`. Fix anything red at its root cause, with the smallest change that respects the contracts (CLAUDE.md rule 12, `spec/03` §4, `spec/05` §3), and run the checks again.
2. Update `BUILD_LOG.md`: the "Current state / Next step" block at the top, what was done, each check's summary line, open issues.
3. Commit everything with a message that says what the session did.
4. List the files you created or changed, and give the exact command that starts the next session's work (for example `/build-module m06`).
