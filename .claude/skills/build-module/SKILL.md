---
name: build-module
description: Build one course module with the module loop (CLAUDE.md §7 and the Stage 5 prompt in spec/11). Use when the owner types /build-module followed by a module id such as m05.
argument-hint: "[module id, e.g. m05]"
disable-model-invocation: true
---

Build module **$0** following CLAUDE.md §7 and the Stage 5 module prompt in `spec/11-build-plan-and-prompts.md`.

**Start.** Read `BUILD_LOG.md` and `course.json`. If $0 is already done, or a module it needs isn't (the "Needs" column of `spec/02` §2), say so and stop. If BUILD_LOG.md shows $0 half-built, continue from its next step instead of starting over. Then read only: the $0 section of its phase file in `spec/curriculum/`, `spec/06`, `spec/07`, `spec/05` §2–§5, and the rows for $0's lessons in `spec/02` §4.

**1. Plan, then stop.** For each lesson: its sections with levels (essential, then extra, then advanced), its reference targets and row groups, the examples (which are predict-first, which end in an error on purpose), the exercises (signatures, key edge cases, kind), data files, and minutes for the essentials path and for the whole page. Then wait for my OK.

**2. Build lesson by lesson.** Reference rows first (`python tools/api_skeleton.py <target>`), then the teaching sections, then code → `python tools/check_content.py <page> --update-outputs` → read every output you accepted → prose. Outputs must be the same on every operating system (`spec/06` §8). Before the next lesson, run `python tools/check_coverage.py --partial` and `python tools/check_content.py <page>`, then commit the lesson (`<lesson id>: <title>`) and note it in BUILD_LOG.md, so another session can pick up from there.

**3. Module pages.** The module project brief and the checkpoint page (12–20 questions, about 30 % retrieval from earlier modules).

**4. Wire up and verify.** Add the lessons to `course.json`, run `python tools/build.py`, update the glossary, then run `python tools/ci.py --partial` and quote every step's summary line. Work through the module checklist in `spec/12`.

**Finish.** Update BUILD_LOG.md (current state, check results, open issues, next step), commit, and report in 5–10 lines: what was built, the check results, and which pages to open for review. If $0 is the last module of its phase (`spec/02` §2), say that the next step is `/end-phase <phase number>`. Every third or fourth module, suggest `/review-module $0`.

If the context fills up before the module is done, finish the current lesson, commit, record the next step in BUILD_LOG.md, and tell me to continue in a new session with `/build-module $0`.
