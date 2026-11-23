---
name: review-module
description: Strict critic pass over a finished module, in a fresh context, by a reviewer that didn't write it (the "Critic pass" in spec/11). Use every 3-4 modules, or when the owner types /review-module followed by a module id.
argument-hint: "[module id, e.g. m07]"
disable-model-invocation: true
context: fork
agent: course-reviewer
background: false
---

Review module **$0** of this course. You did not write it. Its lesson pages are `site/modules/$0-*/l*.html`; its specification is the $0 section of a phase file in `spec/curriculum/` (find it with Grep).

Review against `spec/06` (§3 levels, §4 coverage, §15 self-review), `spec/05` §4 and the lesson and module checklists in `spec/12`. Read each lesson twice: as a beginner with Show set to "Essentials" (only the blocks with `data-level="essential"`), then with Show set to "Everything".

Look for:

* concepts used before they are taught;
* dishonest levels (essential content marked extra, or the reverse), and blocks more essential than their parent;
* reference rows that are vague, wrong or missing;
* examples whose output could differ between operating systems (`spec/06` §8);
* weak tests (a wrong solution that would still pass), and hints that give the answer away;
* quiz distractors that don't come from real misconceptions;
* inaccessible markup;
* APIs that are outdated for the pinned versions (`spec/06` §9), and anything that contradicts the official documentation.

Run `python tools/check_site.py` and `python tools/check_coverage.py --partial` and include their summary lines. Don't edit any file.

Return a table sorted by severity (blocker, major, minor) with file:line, the problem and the fix you would make. Flag only problems that affect correctness, learning, accessibility or the stated requirements, not style preferences. End with the three fixes that matter most.
