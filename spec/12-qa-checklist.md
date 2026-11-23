# 12 · QA checklist

Tick these before calling a lesson, module, phase or release done. Record the results in `BUILD_LOG.md`.

## 1. Automated checks

| Command | Must report |
|---|---|
| `python tools/build.py` | wrote only what you expected |
| `python -m pytest tools/tests -q` | all passed |
| `python tools/build.py --check` | all generated files up to date |
| `python tools/check_site.py` | 0 problem(s) |
| `python tools/check_coverage.py --partial` (while building) / without `--partial` (release) | 0 error(s); pending only for modules not built yet |
| `python tools/check_content.py` | 0 problem(s); "skipped" only for `data-python` newer than the checker, or libraries you knowingly lack (`--skip-missing`) |
| `python tools/check_content.py examples/spec05-examples.html` | 0 problem(s) |
| `node tools/smoke_pages.mjs` | all checks passed |
| `python tools/ci.py` | CI passed (runs all of the above in order) |

## 2. Per-lesson checklist

* [ ] Anatomy in order (`spec/06` §2); one `h1`; meta shows the essentials time and the whole-page time.
* [ ] Every teaching section has an honest level; essential → extra → advanced order; no child more essential than its parent.
* [ ] Read with **Show → Essentials**: it stands alone and covers everything the required exercises need.
* [ ] Read in **Everything**: every Essential and Extra & advanced item of the curriculum row is present.
* [ ] Reference: every `Ref:` target declared in `data-api-targets` and complete; rows task-grouped, described in course voice, levelled (about 25 % essential); no `TODO`.
* [ ] Every output came from `--update-outputs` and you read it; sets sorted; random seeded; no addresses or timings unless marked `sample`/`ellipsis`.
* [ ] At least one `pitfall`, one `job` and one `interview` callout; version markers for anything added or changed since 3.8 that the lesson relies on.
* [ ] 2–4 exercises (+ optional ★★★): ≥ 4 tests each, teaching messages, a second data set against hard-coding, 3 hints, `data-notes`; the pack downloads and runs with `{pytest}`; the completion code is accepted by the page.
* [ ] Warm-up (from M02) and end quiz valid; predict answers verified; distractors from real misconceptions.
* [ ] Terms defined with `dfn` and added to the glossary; links to earlier lessons and to official docs.
* [ ] Looks right in light and dark themes, at 390 px, 1024 px and 1440 px wide (the on-this-page rail appears from 1200 px), at the Larger text size, and in print preview; nothing scrolls sideways except code and wide tables.
* [ ] Keyboard only: every control reachable, focus always visible and never under the sticky header; `/`, `[`, `]`, `?` work and stop when turned off in Reading settings.

## 3. Per-module checklist

* [ ] Every lesson passes §2; `course.json` lists them (no stray `planned`).
* [ ] Checkpoint page: 12–20 questions, ~30 % retrieval; optional checkpoint pack validated.
* [ ] Module project brief and rubric (where the curriculum has one).
* [ ] `check_coverage.py --partial` shows this module's targets complete.
* [ ] `BUILD_LOG.md` updated (state, check results, open issues, next step).

## 4. Per-phase checklist

* [ ] Every module mastered-ready (§3); phase exam page and exam pack built and validated.
* [ ] Portfolio project page with rubric, checklist and review prompt (`spec/09`).
* [ ] A learner can go from the phase's first lesson to its exam using only the site.
* [ ] A critic pass (`spec/11`) done on at least one module of the phase, with its top issues fixed.

## 5. Browser and device matrix (release, and after platform changes)

| Browser | Check |
|---|---|
| Chrome / Edge (current) | full smoke test (automated) + a manual read of the sample lesson |
| Firefox (current) | opening from `file://`, Show filter, search, copy, quiz, completion code, theme |
| Safari (current, macOS and iOS) | the same; Download buttons; small-screen menu |
| A phone (390 px) | no sideways scrolling; tables scroll inside their wrapper; menu works |

Also open one lesson from a downloaded zip of the site (no server) and from GitHub Pages.

## 6. Accessibility audit (WCAG 2.2 AA)

* [ ] Keyboard only: reach and use search (`/`, arrows, Enter, Escape), Show, theme, every Copy/Download, hints, solution, completion-code box, every quiz type (including ↑/↓ order buttons), pager.
* [ ] Screen reader (NVDA or VoiceOver) on the sample lesson: headings outline, level badges read as words, callout kinds announced, live-region messages heard, tables have captions and headers.
* [ ] Contrast of any new colour pair ≥ 4.5:1 (text) / 3:1 (UI); nothing conveyed by colour alone.
* [ ] Zoom to 200 % and to 400 % (reflow at 320 px): nothing lost.
* [ ] `prefers-reduced-motion` respected.

## 7. Performance

* [ ] `course.js` + `course.css` + `prism.bundle.js` < 160 KB uncompressed; fonts self-hosted (a lesson loads ≤ 3 files); no third-party requests.
* [ ] axe-core (in `smoke_pages.mjs`) reports 0 WCAG 2.2 A/AA problems on every page type in both themes; add new page types (exam, project, glossary) to the smoke test as they are built.
* [ ] Lesson HTML < 400 KB; search index loaded only on first use.
* [ ] Examples < 10 s each (most < 2 s); exercise test files < 15 s each on a laptop.

## 8. Content accuracy

* [ ] Every API, parameter and behaviour checked against the official docs of the pinned versions; outputs produced by running.
* [ ] Version markers correct (feature, version, change type); anything newer than the course's Python is a version callout with `data-python` on its examples.
* [ ] No "latest version", price, model name or free-tier claims as facts; links instead.
* [ ] Datasets synthetic or licensed with attribution; no personal data.
* [ ] Coverage exclusions in `tools/coverage.json` reviewed: each still needed, each reason true.

## 9. Security and privacy

* [ ] No learner text reaches `innerHTML`; no inline event handlers (`check_site.py`).
* [ ] No secrets, keys or tokens anywhere (search the repository); `.env` git-ignored; examples read keys from environment variables.
* [ ] No network access needed by any example or test; HTTP and LLM calls use `course_mocks` in tests.
* [ ] Lessons on `pickle`, `eval`, `subprocess`, SQL and scraping carry their `security` callouts.

## 10. Release checklist

* [ ] `python tools/ci.py` (no `--partial`) green on Python 3.15 with the pinned requirements, locally and in GitHub Actions: run the publishing workflow by hand with `release` ticked, because pushes run `--partial` (this includes `check_libraries.py` with no skips).
* [ ] `python tools/check_pins.py` reports no pin that can move up, or each one left behind has a reason in `DECISIONS.md`; `spec/02` §5.1 re-checked.
* [ ] Course-wide coverage complete: required targets, keywords (`kw:` rows and usage), every AST node type, the standard-library atlas.
* [ ] §5–§9 done and recorded.
* [ ] `course.json` "version" bumped; `CHANGELOG.md` written; `README.md` describes how to use the course locally.
* [ ] `site/downloads/all-exercises.zip` and the six requirements files download from the published site; in a fresh Python 3.15 environment, installing them in the setup page's order succeeds.
* [ ] GitHub Pages deployment succeeded; the published home page, setup page, sample lesson and API index load without console errors.

## 11. After release

* Watch for issues from learners (broken commands on a platform, outputs that differ with a library version) and fix them with the same checks.
* Each year: move to the next Python version once the pinned libraries support it (`spec/11` "Move to a new Python version"), re-run `--update-outputs`, and re-read every changed output.
* Pins: act on the weekly `pins.yml` failures with the `spec/11` "Refresh the library pins" prompt, rather than letting versions drift for a year.
