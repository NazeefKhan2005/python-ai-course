---
name: fix-ci
description: Find and fix the root cause of a failing check, from a local run or from the latest GitHub Actions run of site.yml. Use when the owner types /fix-ci, optionally with a run id, or when the publish workflow failed.
argument-hint: "[GitHub Actions run id, or nothing for the latest run]"
disable-model-invocation: true
---

1. **Get the failure.** If a run id came with the command ("$0"), or `gh run list --workflow site.yml --limit 5` shows that the latest run failed, read its log with `gh run view <id> --log-failed`. Otherwise run `python tools/ci.py --partial` here. Quote the failing step and the lines that matter.
2. **Reproduce it here** with the same command (`ci.py` prints each step's command). If it passes here but failed on GitHub, the difference is the platform: GitHub runs Ubuntu with the CPU build of PyTorch.
   * An example's output differs: the example prints something that depends on the computer, such as float digits from different maths libraries, paths, user names, line endings or timings. Make it print the same everywhere (round, sort, use relative paths: `spec/06` §8), run `python tools/check_content.py <page> --update-outputs` and read the new output. Use `data-output="sample"` only for output that really varies between machines, with a sentence saying so.
   * A library check differs: compare the installed versions with the pins. Never move a pin to fix a build (CLAUDE.md rule 10).
3. **Fix the root cause** with the smallest change that respects the contracts (CLAUDE.md rule 12, `spec/03` §4, `spec/05` §3). Never weaken a check or a test to make it pass. Run the failing step again, then `python tools/ci.py --partial`.
4. **Commit** (`Fix: <what was wrong>`), explain the cause in two sentences, and ask me before pushing.
