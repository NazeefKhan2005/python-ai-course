---
name: end-phase
description: Close a finished phase with its exam, portfolio project page and recap (the "At the end of each phase" prompt in spec/11). Use when the owner types /end-phase followed by a phase number.
argument-hint: "[phase number 1-6]"
disable-model-invocation: true
---

Close **phase $0**. First check that it is complete: every module of phase $0 in `spec/02` §2 is done according to `BUILD_LOG.md`. If not, list what's missing and stop.

Then follow the "At the end of each phase" prompt in `spec/11-build-plan-and-prompts.md` for phase $0:

* the phase exam page (`spec/05` §9: a timed in-page quiz and an exam pack). If this is the first exam, implement the `.exam` component in `course.js` with smoke tests first;
* the portfolio project page for `p$0-project` from `spec/09`. Implement the `.rubric` and `.checklist` components first if they don't exist yet;
* a "Phase $0 recap" on the dashboard.

Run `python tools/build.py` and `python tools/ci.py --partial`, quote every step's summary line, update BUILD_LOG.md, commit (`Phase $0: exam, project, recap`) and report in 5–10 lines.
