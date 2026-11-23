# 04 · Reference implementation

The complete, tested source of the platform. **Copy each file to the path in its heading, byte for byte.** Everything here passed `python tools/ci.py --partial` on Python 3.15.2, with every pinned library installed, before the kit was assembled: 40 unit tests for the tools, `check_libraries.py` (the 65 pinned libraries import; 21 functional checks pass), ruff on `tools/` (0 findings), `check_site.py` (0 problems), `check_coverage.py` (6 targets complete), `check_content.py` (29 examples run twice, 9 sessions, 4 exercises, 2 quizzes; plus the 6 validated pattern exercises and their quiz; 0 problems) and 51 headless-Chrome checks over `file://`, including axe-core's WCAG 2.2 A/AA rules on every page type in both themes and on the lesson at phone width (nine page states, 0 problems). It was then rebuilt from this Markdown alone and passed again.

The CSS is in `spec/08` §8; the sample lesson page is in `spec/07`; validated exercise patterns are in `spec/05`. The only files not printed here are generated from pinned npm packages: the Prism bundle and the course fonts (§21).

## Contents

| § | File | Lines | Role |
|---|---|---|---|
| 1 | `course.json` | 30 | Course metadata, phases, modules, lessons (`planned` lessons appear in the nav as "coming soon") |
| 2 | `templates/page-shell.html` | 36 | Shell for non-lesson pages; also used by the build for `api-index.html` |
| 3 | `templates/lesson-template.html` | 187 | Annotated starting point for every lesson |
| 4 | `site/assets/js/course.js` | 1124 | All page behaviour (classic script, no modules) |
| 5 | `site/index.html` | 73 | Home: how the course works, dashboard, settings |
| 6 | `site/setup.html` | 205 | Set up your computer (also M00-L03's companion) |
| 7 | `tools/pagekit.py` | 261 | Strict-HTML parser with source offsets, `dedent`, `replace_scripts`, `api_id` |
| 8 | `tools/packs.py` | 109 | The single definition of an exercise's files and a lesson's pack |
| 9 | `tools/check_site.py` | 304 | Structure, accessibility, markers, reference rows, links, manifest |
| 10 | `tools/check_content.py` | 401 | Runs every example, session, exercise and quiz answer; `--update-outputs` |
| 11 | `tools/check_coverage.py` | 288 | Reference coverage of targets; keywords, AST nodes, stdlib atlas |
| 12 | `tools/coverage.json` | 65 | Required targets, ignored dunders, exclusions with reasons |
| 13 | `tools/api_skeleton.py` | 105 | Draft reference rows for a target |
| 14 | `tools/export_exercises.py` | 81 | Deterministic exercise packs |
| 15 | `tools/build.py` | 146 | Manifest, search index, API index, packs; `--check` |
| 16 | `tools/ci.py` | 54 | Every check in CI order |
| 17 | `tools/learner/conftest.py` | 83 | pytest plugin in every pack: import path, completion codes |
| 18 | `tools/learner/course_helpers.py` | 96 | `run_program`, `assert_fast_enough`, `assert_no_syntax`, `check_tests` |
| 19 | `tools/learner/course_mocks.py` | 72 | `MockLLM`, `HashEmbedder`, `fake_get` |
| 20 | `tools/smoke_pages.mjs` | 266 | Headless-Chrome checks over `file://` |
| 21 | `tools/vendor/build_prism.py`, `build_fonts.py` | 25 | Build `site/assets/vendor/prism.bundle.js`; copy the fonts into `site/assets/fonts/` |
| 22 | `tools/tests/test_tools.py` + fixtures, `examples/spec05-examples.html` | 331 | Unit tests for the tools; the validated exercise patterns |
| 23 | `tools/requirements-dev.txt` and the six `site/downloads/requirements-*.txt` | | Every library pinned, one learner file per phase; the builder's file includes them all |
| 24 | `.github/workflows/site.yml`, `pins.yml` | 50 | CI and GitHub Pages deployment; the weekly check for newer releases |
| 25 | `tools/check_pins.py` | 160 | Which pins have a newer release that installs on the course's Python |
| 26 | `tools/check_libraries.py` | 514 | Every pinned library imports and works; the API generation lessons must use |

## 1. `course.json`

````json
{
  "id": "pyai",
  "title": "Python for AI: Zero to Job-Ready",
  "version": "2026.11",
  "python": "3.15",
  "repo": "",
  "branch": "main",
  "base_url": "",
  "phases": [
    {"id": "p0", "title": "Orientation"},
    {"id": "p1", "title": "Python Foundations"},
    {"id": "p2", "title": "Intermediate Python & Engineering"},
    {"id": "p3", "title": "Data Science"},
    {"id": "p4", "title": "Machine Learning"},
    {"id": "p5", "title": "Deep Learning & Generative AI"},
    {"id": "p6", "title": "Production & Career"}
  ],
  "modules": [
    {"id": "m03", "title": "Core Data Structures", "phase": "p1", "path": "modules/m03-data-structures/",
     "lessons": [
       {"id": "m03-l01", "title": "Lists", "file": "l01-lists.html", "minutes": 75, "planned": true},
       {"id": "m03-l02", "title": "Mutability & references", "file": "l02-mutability-references.html", "minutes": 60, "planned": true},
       {"id": "m03-l03", "title": "Tuples & unpacking", "file": "l03-tuples.html", "minutes": 60, "planned": true},
       {"id": "m03-l04", "title": "Dictionaries", "file": "l04-dictionaries.html", "minutes": 120},
       {"id": "m03-l05", "title": "Sets", "file": "l05-sets.html", "minutes": 75, "planned": true},
       {"id": "m03-l06", "title": "Comprehensions", "file": "l06-comprehensions.html", "minutes": 75, "planned": true},
       {"id": "m03-l07", "title": "Choosing the right structure", "file": "l07-choosing-structures.html", "minutes": 75, "planned": true}
     ]}
  ]
}
````

## 2. `templates/page-shell.html`

````html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{title}} · Python for AI</title>
  <meta name="description" content="{{description}}">
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="{{root}}assets/css/course.css">
  <script>
    // Apply the saved theme, text size and reading depth before first paint (no flash).
    try { var s = JSON.parse(localStorage.getItem("pyai.progress.v1") || "{}").settings || {}, d = document.documentElement; if (s.theme) d.dataset.theme = s.theme; if (s.text) d.dataset.text = s.text; d.dataset.depth = s.depth || "all"; } catch (e) { document.documentElement.dataset.depth = "all"; }
  </script>
  <script defer src="{{root}}assets/vendor/prism.bundle.js"></script>
  <script defer src="{{root}}assets/js/manifest.js"></script>
  <script defer src="{{root}}assets/js/course.js"></script>
</head>
<body data-page="{{page}}" data-root="{{root}}" data-generated="">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <button class="icon-btn nav-toggle" type="button" aria-expanded="false" aria-controls="sidebar"><svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 5.5h14M3 10h14M3 14.5h14"></path></svg><span class="nav-toggle-label">Contents</span></button>
    <a class="brand" href="{{root}}index.html"><span class="brand-prompt" aria-hidden="true">&gt;&gt;&gt;</span><span class="brand-name">Python for AI</span></a>
    <div class="site-search" role="search"></div>
    <div class="depth-control"></div>
    <div class="display-menu"></div>
    <button class="icon-btn theme-toggle" type="button" aria-label="Switch between light and dark theme"><svg aria-hidden="true" viewBox="0 0 20 20"><circle cx="10" cy="10" r="7.25" fill="none" stroke="currentColor" stroke-width="1.6"></circle><path d="M10 2.75a7.25 7.25 0 0 1 0 14.5z" fill="currentColor"></path></svg></button>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar"><nav class="course-nav" aria-label="Course contents"></nav></aside>
    <main id="main" class="content">
      <h1>{{title}}</h1>
      {{content}}
    </main>
  </div>
</body>
</html>
````

## 3. `templates/lesson-template.html`

````html
<!doctype html>
<!-- Lesson template. Copy to site/modules/<module-slug>/lNN-<slug>.html, replace every {{...}},
     delete the blocks you don't need, then run: python tools/build.py && python tools/ci.py --partial
     Rules: spec/06-content-style-guide.md (markers, voice) and spec/05-exercises-and-assessment.md. -->
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{Lesson title}} · {{MNN Module title}} · Python for AI</title>
  <meta name="description" content="{{One sentence: what the learner can do after this lesson.}}">
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="../../assets/css/course.css">
  <script>
    // Apply the saved theme, text size and reading depth before first paint (no flash).
    try { var s = JSON.parse(localStorage.getItem("pyai.progress.v1") || "{}").settings || {}, d = document.documentElement; if (s.theme) d.dataset.theme = s.theme; if (s.text) d.dataset.text = s.text; d.dataset.depth = s.depth || "all"; } catch (e) { document.documentElement.dataset.depth = "all"; }
  </script>
  <script defer src="../../assets/vendor/prism.bundle.js"></script>
  <script defer src="../../assets/js/manifest.js"></script>
  <script defer src="../../assets/js/course.js"></script>
</head>
<body data-page="lesson" data-lesson-id="{{mNN-lNN}}" data-root="../../">
  <a class="skip-link" href="#main">Skip to lesson</a>
  <header class="site-header">
    <button class="icon-btn nav-toggle" type="button" aria-expanded="false" aria-controls="sidebar"><svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 5.5h14M3 10h14M3 14.5h14"></path></svg><span class="nav-toggle-label">Contents</span></button>
    <a class="brand" href="../../index.html"><span class="brand-prompt" aria-hidden="true">&gt;&gt;&gt;</span><span class="brand-name">Python for AI</span></a>
    <div class="site-search" role="search"></div>
    <div class="depth-control"></div>
    <div class="display-menu"></div>
    <button class="icon-btn theme-toggle" type="button" aria-label="Switch between light and dark theme"><svg aria-hidden="true" viewBox="0 0 20 20"><circle cx="10" cy="10" r="7.25" fill="none" stroke="currentColor" stroke-width="1.6"></circle><path d="M10 2.75a7.25 7.25 0 0 1 0 14.5z" fill="currentColor"></path></svg></button>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar"><nav class="course-nav" aria-label="Course contents"></nav></aside>
    <main id="main" class="content">
      <p class="breadcrumb">Phase {{N}} · {{MNN Module title}} · Lesson {{n}} of {{total}}</p>
      <h1>{{Lesson title: plain promise}}</h1>
      <ul class="lesson-meta" aria-label="Lesson details">
        <li>⏱ Essentials {{NN}} min · whole page about {{N}} h</li>
        <li>Level: {{Beginner | Intermediate | Advanced}}</li>
        <li>Needs: <a href="{{lNN-prev.html}}">{{Previous lesson}}</a></li>
        <li>Python 3.15</li>
      </ul>

      <section class="outcomes" id="outcomes">
        <h2>What you'll be able to do</h2>
        <ul><li>{{Observable outcome, starting with a verb}}</li></ul>
      </section>

      <section class="run-locally" id="run">
        <h2>Run the code yourself</h2>
        <p>{{Standard paragraph: nothing runs in the browser; outputs are real; link to ../../setup.html.}}</p>
        <ol>
          <li>Copy or download an example, then run it:
            <script type="text/x-shell">
            {python} {{first_example}}.py
            </script>
          </li>
          <li><a class="btn btn--small" data-pack href="../../downloads/{{mNN-lNN}}.zip" download>Download the exercise pack</a>, unzip it, and run the tests:
            <script type="text/x-shell">
            cd {{mNN-lNN}}
            {pytest}
            </script>
          </li>
        </ol>
      </section>

      <!-- A content section. data-level is required: essential | extra | advanced.
           Children may be LESS essential than their section, never more. -->
      <section id="{{slug}}" data-level="essential">
        <h2>{{Section title}}</h2>
        <p>{{Explanation. Define new terms with <dfn id="term-x">term</dfn>.}} <span class="version" data-version="3.9" data-change="added"></span></p>

        <!-- Verified example: the x-output must be exactly what Python prints (check_content.py runs it twice).
             Optional: data-predict (hide output until revealed), data-raises="KeyError" (output ends with
             "Traceback (most recent call last):\n  ...\nKeyError: 'x'"), data-output="sample", data-match="ellipsis",
             data-args="--name Ada", data-exit="2", data-requires="numpy pandas", data-python="3.16", data-timeout="120". -->
        <figure class="example" id="ex-{{slug}}">
          <script type="text/x-file" data-name="{{data.csv}}">
          {{optional data file, created next to the example before it runs}}
          </script>
          <script type="text/x-python" data-file="{{name}}.py">
          {{code}}
          </script>
          <script type="text/x-stdin">
          {{optional: what the learner types when input() asks}}
          </script>
          <script type="text/x-output">
          {{exact output}}
          </script>
          <figcaption>{{optional caption}}</figcaption>
        </figure>

        <!-- Interactive session, verified with doctest. -->
        <figure class="session">
          <script type="text/x-pycon">
          >>> {{expression}}
          {{result}}
          </script>
        </figure>

        <!-- Other code: x-code with data-lang (json, sql, yaml, toml, bash, ini, docker, markup) is shown, not run. -->
        <script type="text/x-code" data-lang="json" data-file="{{config.json}}">
        {"key": "value"}
        </script>

        <!-- Kind callouts: tip | pitfall | version (needs data-version) | interview | job | hood | try |
             deprecated | performance | security | note. Optional <p class="callout-title"> and data-level. -->
        <aside class="callout" data-kind="pitfall">
          <p class="callout-title">{{optional short title}}</p>
          <p>{{text}}</p>
        </aside>

        <section id="{{slug-detail}}" data-level="extra">
          <h3>{{Deeper subsection}}</h3>
          <p data-level="advanced">{{An advanced paragraph inside an extra subsection is fine.}}</p>
        </section>
      </section>

      <!-- Reference: one row per public name of every target (tools/api_skeleton.py drafts the rows;
           tools/check_coverage.py proves nothing is missing). Several names may share one row. -->
      <section class="api-reference" id="reference" data-api-targets="{{class:dict module:json expr:Alias=expression}}">
        <h2>Reference: {{everything X can do}}</h2>
        <div class="table-wrap">
          <table class="api-table">
            <caption>{{Group name}}</caption>
            <thead><tr><th scope="col">Code</th><th scope="col">What it does</th><th scope="col">Notes</th></tr></thead>
            <tbody>
              <tr id="api-{{dict-get}}" data-api="{{dict.get}}" data-level="essential"><td><code>{{d.get(k, default=None)}}</code></td><td>{{what}}</td><td>{{notes, versions, pitfalls}}</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="exercises" id="exercises">
        <h2>Exercises</h2>
        <!-- data-kind: function | program | fix | refactor | write_tests. data-file: eN_<name>.py.
             write_tests: scripts target (the code under test), starter/solution are TEST files, mutants is JSON
             {"description of the bug": "buggy source"}. Add data-optional for stretch exercises. -->
        <article class="exercise" id="{{mNN-lNN}}-e1" data-kind="function" data-file="e1_{{name}}.py">
          <h3>Exercise 1 · {{Title}}</h3>
          <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
          <div class="exercise-task">
            <p>{{Task: inputs, outputs, edge cases, constraints.}}</p>
          </div>
          <script type="text/x-python" data-role="starter">
          def {{name}}({{params}}):
              """{{docstring}}"""
              raise NotImplementedError
          </script>
          <script type="text/x-python" data-role="tests">
          from e1_{{name}} import {{name}}


          def test_{{behaviour}}():
              assert {{name}}({{args}}) == {{expected}}, "{{message that teaches}}"
          </script>
          <script type="text/x-python" data-role="solution" data-notes="{{why this solution, complexity}}">
          {{solution}}
          </script>
          <ol class="hints">
            <li>{{Hint 1: strategy}}</li>
            <li>{{Hint 2: the tool to use}}</li>
            <li>{{Hint 3: nearly the line}}</li>
          </ol>
        </article>
      </section>

      <section class="quiz" id="{{mNN-lNN}}-quiz">
        <h2>Check your understanding</h2>
        <script type="application/json" class="quiz-spec">
        {"id": "{{mNN-lNN}}-quiz", "questions": [
          {"type": "mcq", "prompt": "...", "options": ["...", "..."], "answer": 0, "explanation": "..."},
          {"type": "predict", "prompt": "What does this print?", "code": "print(1 + 1)", "answer": "2", "explanation": "..."}
        ]}
        </script>
      </section>

      <section class="summary" id="summary">
        <h2>Summary</h2>
        <ul><li data-level="essential">{{key point}}</li></ul>
      </section>

      <div class="lesson-complete"></div>
      <nav class="pager" aria-label="Previous and next lesson"></nav>
    </main>
  </div>
</body>
</html>
````

## 4. `site/assets/js/course.js`

Rendering rules worth knowing before you change it: badges come from `data-level` (rows get theirs in the first cell, sections in their heading); callouts get a kind label; every `figure.example` becomes file panels, the code panel, a run command, an optional stdin panel and the output panel (hidden behind "Predict" when `data-predict` is set); `x-shell` and run commands are re-rendered whenever the runner setting changes; exercises are rendered from their `data-role` scripts and never execute anything; the completion code is FNV-1a 32-bit of `"pyai:" + exercise id`, exactly as in `conftest.py`.

````javascript
/* course.js: everything interactive on the course pages. Spec: spec/04-reference-implementation.md, spec/08.
 * Classic script (no modules, no fetch) so pages work from file:// as well as from a web server.
 * Python is never run in the browser: learners copy or download code and run it on their computer.
 */
(function () {
  "use strict";

  var STORE_KEY = "pyai.progress.v1";
  var SECTIONS = ["lessons", "exercises", "quizzes", "exams", "rubrics", "checklists", "settings"];
  var LEVELS = {
    essential: { label: "Essential", icon: "●", help: "You need this to continue the course." },
    extra: { label: "Extra info", icon: "◆", help: "Deepens understanding; safe to skip on a first pass." },
    advanced: { label: "Advanced", icon: "▲", help: "Edge cases, internals and rarely needed details." },
  };
  var KINDS = {
    tip: ["Tip", "✦"], pitfall: ["Common mistake", "⚠"], version: ["Version note", "⧗"], interview: ["Interview", "◎"],
    job: ["On the job", "⚒"], hood: ["Under the hood", "⚙"], try: ["Try it yourself", "✎"], deprecated: ["Deprecated", "⊘"],
    performance: ["Performance", "⏱"], security: ["Security", "⛨"], note: ["Note", "ℹ"],
  };
  var CHANGES = { added: "New in", changed: "Changed in", deprecated: "Deprecated since", removed: "Removed in" };
  var DEPTHS = { all: "Everything", core: "Core", essential: "Essentials" };
  var DEPTH_HELP = { all: "Show every part of every page", core: "Hide advanced parts", essential: "Show only what you need to continue: hides extra and advanced parts" };
  var TEXT_SIZES = { s: "Smaller", m: "Standard", l: "Larger" };
  var THEMES = { system: "System", light: "Light", dark: "Dark" };
  var RUNNERS = {
    python: { label: "python (macOS/Linux with python on PATH)", python: "python", pytest: "python -m pytest", pip: "python -m pip" },
    python3: { label: "python3 (macOS/Linux default)", python: "python3", pytest: "python3 -m pytest", pip: "python3 -m pip" },
    py: { label: "py (Windows launcher)", python: "py", pytest: "py -m pytest", pip: "py -m pip" },
    uv: { label: "uv (no activation needed)", python: "uv run python", pytest: "uv run --with pytest pytest", pip: "uv pip" },
  };
  var ICONS = {
    type: '<svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 15.5 7 4.5l4.5 11M4.2 11.5h5.6M12.5 15.5l2.75-7 2.75 7M13.4 13.2h3.7"/></svg>',
  };
  var COURSE = window.COURSE || { id: "pyai", phases: [], modules: [] };
  var ROOT = (document.body && document.body.dataset.root) || "";
  var WIDE = "(min-width: 75rem)";

  // ------------------------------------------------------------------ progress store
  // localStorage can be missing, full or blocked (private windows, strict settings): never crash.
  var store = {
    data: null,
    load: function () {
      if (this.data) return this.data;
      var parsed = null;
      try { parsed = JSON.parse(localStorage.getItem(STORE_KEY)); } catch (e) { /* ignore */ }
      this.data = parsed && parsed.version === 1 ? parsed : { version: 1 };
      for (var i = 0; i < SECTIONS.length; i++) this.data[SECTIONS[i]] = this.data[SECTIONS[i]] || {};
      return this.data;
    },
    save: function (quiet) {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(this.data)); } catch (e) { /* ignore */ }
      if (!quiet) document.dispatchEvent(new CustomEvent("progress-change"));
    },
    get: function (section, id) { return this.load()[section][id] || null; },
    set: function (section, id, patch, quiet) {
      var d = this.load();
      d[section][id] = Object.assign({}, d[section][id] || {}, patch, { updatedAt: new Date().toISOString() });
      this.save(quiet);
      return d[section][id];
    },
    setting: function (name, fallback) {
      var v = this.load().settings[name];
      return v == null ? fallback : v;
    },
    setSetting: function (name, value, quiet) {
      this.load().settings[name] = value;
      this.save(true);
      if (!quiet) document.dispatchEvent(new CustomEvent("settings-change", { detail: { name: name, value: value } }));
    },
  };

  // ------------------------------------------------------------------ helpers
  function h(tag, attrs) {
    var el = document.createElement(tag);
    attrs = attrs || {};
    Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v == null || v === false) return;
      if (k === "class") el.className = v;
      else if (k === "text") el.textContent = v;
      else if (k === "html") el.innerHTML = v; // trusted course content only, never learner input
      else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    });
    for (var i = 2; i < arguments.length; i++) append(el, arguments[i]);
    return el;
  }
  function append(el, kid) {
    if (kid == null || kid === false) return;
    if (Array.isArray(kid)) { kid.forEach(function (k) { append(el, k); }); return; }
    el.append(kid);
  }
  function button(label, onclick, cls, attrs) {
    return h("button", Object.assign({ class: cls || "btn", type: "button", onclick: onclick }, attrs || {}), label);
  }
  /** Replace an element's children, skipping null and false (replaceChildren would print "null"). */
  function fill(el, kids) { el.replaceChildren(); append(el, kids); return el; }
  function icon(name) { var s = h("span", { class: "icon", html: ICONS[name] }); return s.firstChild; }

  /** Same rules as tools/pagekit.py dedent(): the closing line's indent is the base indent. */
  function dedent(text) {
    var lines = String(text).replace(/\r\n?/g, "\n").split("\n");
    var base = null;
    if (lines.length > 1 && /^ *$/.test(lines[lines.length - 1])) { base = lines.pop().length; }
    lines = lines.map(function (l) { return l.replace(/\s+$/, ""); });
    if (base === null) {
      var pads = lines.filter(Boolean).map(function (l) { return l.match(/^ */)[0].length; });
      base = pads.length ? Math.min.apply(null, pads) : 0;
    }
    lines = lines.map(function (l) { return l.slice(Math.min(base, l.match(/^ */)[0].length)); });
    while (lines.length && !lines[0]) lines.shift();
    while (lines.length && !lines[lines.length - 1]) lines.pop();
    return lines.join("\n");
  }
  function normalizeText(s) {
    return String(s).replace(/\r\n?/g, "\n").split("\n").map(function (l) { return l.replace(/\s+$/, ""); }).join("\n").replace(/^\n+|\n+$/g, "");
  }
  function parseJSON(text) { try { return JSON.parse(text); } catch (e) { return null; } }
  function plain(html) { var t = document.createElement("span"); t.innerHTML = html; return t.textContent; }
  function headingText(head) {
    var copy = head.cloneNode(true);
    copy.querySelectorAll(".badge, .anchor").forEach(function (n) { n.remove(); });
    return copy.textContent.trim();
  }

  var live = null;
  function announce(message) {
    if (!live) { live = h("div", { class: "toast", role: "status", "aria-live": "polite" }); document.body.append(live); }
    live.textContent = message;
    live.classList.add("is-visible");
    clearTimeout(announce.timer);
    announce.timer = setTimeout(function () { live.classList.remove("is-visible"); }, 3200);
  }

  function copyText(text, what) {
    function done() { announce((what || "Code") + " copied to the clipboard"); }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text) && done(); });
    } else if (fallbackCopy(text)) done();
  }
  function fallbackCopy(text) {
    var area = h("textarea", { class: "visually-hidden", readonly: true });
    area.value = text;
    document.body.append(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    area.remove();
    if (!ok) announce("Copy failed: select the code and press Ctrl+C (⌘C on a Mac)");
    return ok;
  }
  function download(name, text) {
    var url = URL.createObjectURL(new Blob([text.endsWith("\n") ? text : text + "\n"], { type: "text/plain" }));
    var a = h("a", { href: url, download: name });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  /** FNV-1a 32-bit, same as conftest.py completion_code(). */
  function completionCode(exerciseId) {
    var bytes = new TextEncoder().encode("pyai:" + exerciseId);
    var value = 0x811c9dc5;
    for (var i = 0; i < bytes.length; i++) { value ^= bytes[i]; value = Math.imul(value, 0x01000193) >>> 0; }
    var hex = ("00000000" + value.toString(16).toUpperCase()).slice(-8);
    return hex.slice(0, 4) + "-" + hex.slice(4);
  }

  // ------------------------------------------------------------------ course data
  function lessonList() {
    var out = [];
    COURSE.modules.forEach(function (m) {
      m.lessons.forEach(function (l, i) { out.push({ l: l, m: m, n: i + 1, of: m.lessons.length, href: ROOT + m.path + l.file }); });
    });
    return out;
  }
  function flatLessons() { return lessonList().filter(function (x) { return !x.l.planned; }); }
  function findLesson(id) { return lessonList().filter(function (x) { return x.l.id === id; })[0] || null; }
  function phaseOf(m) {
    var p = (COURSE.phases || []).filter(function (x) { return x.id === m.phase; })[0];
    return p ? { id: p.id, n: p.id.replace(/^p/, ""), title: p.title } : null;
  }
  function lessonCounts(lessonId, exercises) {
    var required = (exercises || []).filter(function (x) { return !x.optional; });
    var passed = required.filter(function (x) { var r = store.get("exercises", x.id); return r && (r.status === "passed" || r.status === "done"); });
    return { passed: passed.length, total: required.length };
  }
  function lessonState(l) {
    if ((store.get("lessons", l.id) || {}).completed) return "done";
    var touched = (l.exercises || []).some(function (x) { var r = store.get("exercises", x.id); return r && r.status; })
      || (l.quiz && store.get("quizzes", l.quiz)) || (store.setting("resume", {}) || {}).lesson === l.id;
    return touched ? "started" : "new";
  }

  // ------------------------------------------------------------------ code rendering
  function highlight(code, lang) {
    var P = window.Prism;
    var grammar = P && P.languages[lang];
    var el = h("code", { class: "language-" + lang });
    if (grammar) el.innerHTML = P.highlight(code, grammar, lang);
    else el.textContent = code;
    return el;
  }
  function runner() {
    var saved = store.setting("runner", null);
    if (saved && RUNNERS[saved]) return RUNNERS[saved];
    return /Win/.test(navigator.platform || navigator.userAgent) ? RUNNERS.py : RUNNERS.python3;
  }
  function fillCommand(template) {
    var r = runner();
    return template.replace(/\{(python|pytest|pip)\}/g, function (_, k) { return r[k]; });
  }
  /** Shell commands: one line each; the "$" prompt is drawn by CSS, so copying never includes it. */
  function shellCode(text) {
    var el = h("code", { class: "language-shell" });
    text.split("\n").forEach(function (line, i) {
      if (i) el.append("\n");
      el.append(h("span", { class: /^\s*#/.test(line) ? "sh-comment" : line.trim() ? "sh-line" : null, text: line }));
    });
    return el;
  }
  /** Interactive sessions: prompts styled apart from code, Python's answers dimmed. */
  function pyconCode(text) {
    var el = h("code", { class: "language-pycon" });
    text.split("\n").forEach(function (line, i) {
      if (i) el.append("\n");
      var m = line.match(/^(>>>|\.\.\.)( |$)/);
      if (m) { el.append(h("span", { class: "py-prompt", text: line.slice(0, m[0].length) })); el.append.apply(el, Array.prototype.slice.call(highlight(line.slice(m[0].length), "python").childNodes)); }
      else el.append(h("span", { class: "py-out", text: line }));
    });
    return el;
  }

  /** A code panel: label, Copy and Download buttons, highlighted code. */
  function codePanel(opts) {
    var copyValue = opts.copy || opts.code;
    var name = opts.label || "code";
    var tools = h("div", { class: "code-tools" },
      button("Copy", function () { copyText(typeof copyValue === "function" ? copyValue() : copyValue, opts.what); }, "btn btn--small", { "aria-label": "Copy " + name }),
      opts.file ? button("Download", function () { download(opts.file, opts.code); }, "btn btn--small", { "aria-label": "Download " + opts.file }) : null);
    var body = opts.lang === "shell" ? shellCode(opts.code) : opts.lang === "pycon" ? pyconCode(opts.code) : highlight(opts.code, opts.lang);
    var pre = h("pre", { class: "code code--" + opts.lang, tabindex: "0" }, body);
    if (opts.label) pre.setAttribute("aria-label", opts.label);
    return h("div", { class: "code-panel" + (opts.lang === "shell" ? " code-panel--shell" : "") + (opts.cls ? " " + opts.cls : "") },
      h("div", { class: "code-head" }, h("span", { class: "code-label", text: opts.label || "" }), tools), pre);
  }
  function outputPanel(text, label, cls) {
    return h("div", { class: "output-panel " + (cls || "") },
      h("div", { class: "code-head" }, h("span", { class: "code-label", text: label })),
      h("pre", { class: "output", tabindex: "0", "aria-label": label }, h("samp", { text: text })));
  }
  /** The command between code and output: what the learner types to run it. */
  function runBar(template) {
    return h("div", { class: "run-bar" },
      h("span", { class: "visually-hidden", text: "Run it with: " }),
      h("span", { class: "run-prompt", "aria-hidden": "true", text: "$" }),
      h("code", { class: "fill-cmd", "data-template": template }),
      button("Copy", function () { copyText(fillCommand(template), "Command"); }, "btn btn--small btn--on-dark", { "aria-label": "Copy the command" }));
  }
  function scriptsIn(el, type) {
    return Array.prototype.filter.call(el.children, function (n) { return n.tagName === "SCRIPT" && n.type === type; });
  }

  function renderExample(fig) {
    var py = scriptsIn(fig, "text/x-python")[0];
    if (!py) return;
    var file = py.dataset.file || (fig.id ? fig.id.replace(/^ex-/, "").replace(/-/g, "_") + ".py" : "example.py");
    var cell = h("div", { class: "run-cell" });
    scriptsIn(fig, "text/x-file").forEach(function (s) {
      var name = s.dataset.name;
      cell.append(codePanel({ code: dedent(s.textContent), lang: langOf(name), label: name + " (data file: save it next to " + file + ")", file: name, what: name, cls: "code-panel--file" }));
    });
    cell.append(codePanel({ code: dedent(py.textContent), lang: "python", label: file, file: file }));
    var args = fig.dataset.args;
    cell.append(runBar("{python} " + file + (args ? " " + args : "")));
    scriptsIn(fig, "text/x-stdin").forEach(function (s) {
      cell.append(outputPanel(dedent(s.textContent), "Type this when the program asks", "output-panel--stdin"));
    });
    var out = scriptsIn(fig, "text/x-output")[0];
    if (out) {
      var text = dedent(out.textContent);
      var sample = fig.dataset.output === "sample";
      var label = fig.dataset.raises ? "Output (ends with an error, on purpose)" : sample ? "Sample output (yours will differ)" : "Output";
      var panel = outputPanel(text, label, fig.dataset.raises ? "output-panel--error" : "");
      if (fig.hasAttribute("data-predict")) {
        panel.hidden = true;
        var box = h("div", { class: "predict" }, h("p", { class: "predict-prompt", text: "Predict first: what will this print? Say it out loud or write it down." }));
        var reveal = button("Reveal the output", function () { panel.hidden = false; box.remove(); panel.querySelector("pre").focus(); }, "btn btn--primary btn--small predict-btn");
        box.append(reveal);
        cell.append(box, panel);
      } else cell.append(panel);
    }
    fig.insertBefore(cell, fig.firstChild);
  }
  function langOf(name) {
    var ext = (name || "").split(".").pop();
    return { py: "python", csv: "none", json: "json", toml: "toml", yaml: "yaml", yml: "yaml", sql: "sql", sh: "bash", txt: "none", ini: "ini", cfg: "ini", md: "none" }[ext] || "none";
  }

  function renderStandalone(script) {
    var t = script.type, code = dedent(script.textContent), panel;
    if (t === "text/x-python") {
      panel = codePanel({ code: code, lang: "python", label: script.dataset.file || "Python", file: script.dataset.file });
    } else if (t === "text/x-pycon") {
      panel = codePanel({ code: code, lang: "pycon", label: "Interactive session (>>> is the prompt)", what: "The lines after >>>", copy: function () { return pyconInput(code); } });
    } else if (t === "text/x-shell") {
      var tpl = code;
      panel = codePanel({ code: fillCommand(tpl), lang: "shell", label: script.dataset.label || "Terminal", what: "Command", copy: function () { return fillCommand(tpl); } });
      var pre = panel.querySelector("pre");
      pre.dataset.template = tpl;
      pre.classList.add("fill-pre");
    } else if (t === "text/x-code") {
      panel = codePanel({ code: code, lang: script.dataset.lang, label: script.dataset.file || script.dataset.lang.toUpperCase(), file: script.dataset.file });
    } else return;
    script.parentNode.insertBefore(panel, script);
  }
  function pyconInput(code) {
    return code.split("\n").filter(function (l) { return /^(>>>|\.\.\.)( |$)/.test(l); }).map(function (l) { return l.slice(4); }).join("\n");
  }
  function refreshCommands() {
    document.querySelectorAll(".fill-cmd").forEach(function (el) { el.textContent = fillCommand(el.dataset.template); });
    document.querySelectorAll("pre.fill-pre").forEach(function (pre) { pre.replaceChildren(shellCode(fillCommand(pre.dataset.template))); });
  }

  function renderCode(root) {
    root.querySelectorAll("figure.example").forEach(renderExample);
    root.querySelectorAll('script[type="text/x-python"], script[type="text/x-pycon"], script[type="text/x-shell"], script[type="text/x-code"]').forEach(function (s) {
      if (s.closest("figure.example") || s.dataset.role) return;
      renderStandalone(s);
    });
    refreshCommands();
  }

  // ------------------------------------------------------------------ markers
  function levelBadge(level, compact) {
    var info = LEVELS[level];
    if (compact) {
      return h("span", { class: "badge badge--level badge--compact", "data-level": level, title: info.label + ": " + info.help },
        h("span", { "aria-hidden": "true", text: info.icon }), h("span", { class: "visually-hidden", text: "(" + info.label + ")" }));
    }
    return h("span", { class: "badge badge--level", "data-level": level, title: info.help },
      h("span", { "aria-hidden": "true", text: info.icon }), info.label);
  }
  function renderMarkers(root) {
    root.querySelectorAll("[data-level]").forEach(function (el) {
      var level = el.dataset.level;
      if (!LEVELS[level] || el === document.documentElement || el.classList.contains("badge")) return;
      if (el.tagName === "TR") {
        var cell = el.querySelector("td, th");
        if (cell) cell.append(" ", levelBadge(level, true));
      } else if (/^(SECTION|ARTICLE|DIV|ASIDE|DETAILS)$/.test(el.tagName)) {
        var head = el.querySelector(":scope > h2, :scope > h3, :scope > h4, :scope > summary, :scope > .callout-title");
        if (head) head.append(" ", levelBadge(level)); else el.prepend(levelBadge(level), " ");
      } else el.prepend(levelBadge(level), " ");
    });
    root.querySelectorAll("aside.callout").forEach(function (aside) {
      var kind = KINDS[aside.dataset.kind] || KINDS.note;
      var label = kind[0] + (aside.dataset.version ? " · Python " + aside.dataset.version : "");
      var title = aside.querySelector(":scope > .callout-title");
      var tag = h("span", { class: "callout-kind" }, h("span", { "aria-hidden": "true", text: kind[1] + " " }), label);
      if (title) title.prepend(tag, title.textContent.trim() ? ": " : "");
      else aside.prepend(h("p", { class: "callout-title" }, tag));
      aside.setAttribute("aria-label", label);
    });
    root.querySelectorAll("span.version").forEach(function (span) {
      if (!span.textContent.trim()) span.textContent = (CHANGES[span.dataset.change] || "Version") + " " + span.dataset.version;
    });
    root.querySelectorAll("section.api-reference").forEach(function (sec) {
      var head = sec.querySelector(":scope > h2");
      if (head) head.append(" ", h("span", { class: "badge badge--ref" }, h("span", { "aria-hidden": "true", text: "≡" }), "Reference"));
    });
  }

  function legend(main) {
    var anchor = main.querySelector(".lesson-status") || main.querySelector(".lesson-meta");
    if (!anchor) return;
    var kinds = {};
    main.querySelectorAll("aside.callout").forEach(function (a) { kinds[a.dataset.kind] = true; });
    var levelItems = Object.keys(LEVELS).map(function (k) { return h("li", {}, levelBadge(k), " ", LEVELS[k].help); });
    var kindItems = Object.keys(KINDS).filter(function (k) { return kinds[k]; }).map(function (k) {
      return h("li", {}, h("span", { class: "callout-kind callout-kind--" + k }, h("span", { "aria-hidden": "true", text: KINDS[k][1] + " " }), KINDS[k][0]));
    });
    anchor.after(h("details", { class: "legend" },
      h("summary", {}, "How to read this page"),
      h("p", { text: "Every part of the lesson is marked by how much you need it. Use Show to hide what you don't need right now: Essentials turns the page, reference tables included, into a cheat sheet. In the reference tables, essential names are highlighted." }),
      h("ul", { class: "legend-list" }, levelItems),
      kindItems.length ? [h("p", { text: "Boxes on this page:" }), h("ul", { class: "legend-list legend-kinds" }, kindItems)] : null,
      h("p", { html: "All code was run with Python " + (COURSE.python || "3.15") + ", and each output is what it really printed. Run it yourself: copy or download it, then type the command shown under the code (<a href=\"" + ROOT + "setup.html\">setup guide</a>)." }),
      h("p", { html: "Keyboard: <kbd>/</kbd> search, <kbd>[</kbd> and <kbd>]</kbd> previous and next lesson, <kbd>?</kbd> all shortcuts." })));
  }

  // ------------------------------------------------------------------ depth filter (the "Show" setting)
  function hiddenBy(el, depth) {
    if (depth === "all") return false;
    return Boolean(el.closest('[data-level="advanced"]' + (depth === "essential" ? ', [data-level="extra"]' : "")));
  }
  function applyDepth(depth, quiet) {
    if (!DEPTHS[depth]) depth = "all";
    document.documentElement.dataset.depth = depth;
    document.querySelectorAll(".depth-select").forEach(function (s) { s.value = depth; });
    document.querySelectorAll(".depth-group input").forEach(function (i) { i.checked = i.value === depth; });
    var main = document.getElementById("main");
    if (!main) return;
    var note = main.querySelector(".depth-note");
    var count = depth === "all" ? 0 : main.querySelectorAll(depth === "core" ? '[data-level="advanced"]' : '[data-level="extra"], [data-level="advanced"]').length;
    if (!count) { if (note) note.remove(); return; }
    if (!note) {
      note = h("p", { class: "depth-note", role: "status" });
      var anchor = main.querySelector(".legend") || main.querySelector(".lesson-status") || main.querySelector("h1");
      anchor.after(note);
    }
    note.replaceChildren("Show: " + DEPTHS[depth] + ". " + count + " marked part" + (count === 1 ? " is" : "s are") + " hidden on this page. ",
      button("Show everything", function () { setDepth("all"); }, "btn btn--small"));
    if (!quiet) announce("Show: " + DEPTHS[depth]);
  }
  function setDepth(depth) { store.setSetting("depth", depth); applyDepth(depth); }
  var groups = 0;
  /** A row of radio buttons drawn as a segmented control. */
  function segmented(legendText, options, value, onChange, cls, help) {
    var name = "seg-" + (++groups);
    var seg = h("div", { class: "seg" }, Object.keys(options).map(function (k) {
      var input = h("input", { type: "radio", name: name, value: k, checked: k === value, onchange: function () { if (input.checked) onChange(k); } });
      return h("label", { title: help ? help[k] : null }, input, h("span", { text: options[k] }));
    }));
    return h("fieldset", { class: cls }, h("legend", { text: legendText }), seg);
  }
  function mountDepthControl(el) {
    el.append(segmented("Show", DEPTHS, store.setting("depth", "all"), setDepth, "depth-switch depth-group", DEPTH_HELP));
  }
  function revealTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    var target = id && document.getElementById(id);
    if (!target) return;
    var depth = document.documentElement.dataset.depth;
    if (hiddenBy(target, depth)) {
      setDepth("all");
      announce("Showing everything so you can see the linked part");
    }
    var details = target.closest("details");
    if (details && !details.classList.contains("solution")) details.open = true;
    target.classList.add("is-target");
    requestAnimationFrame(function () { target.scrollIntoView({ block: "start" }); });
  }

  // ------------------------------------------------------------------ theme and text size
  function themeSetting() { return store.setting("theme", null) || "system"; }
  function applyTheme(value) {
    if (value === "system") delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = value;
    store.setSetting("theme", value === "system" ? null : value, true);
    document.querySelectorAll(".theme-group input").forEach(function (i) { i.checked = i.value === value; });
    document.querySelectorAll("#set-theme").forEach(function (s) { s.value = value; });
  }
  function applyText(size) {
    if (!TEXT_SIZES[size]) size = "m";
    if (size === "m") delete document.documentElement.dataset.text; else document.documentElement.dataset.text = size;
    store.setSetting("text", size === "m" ? null : size, true);
    document.querySelectorAll(".text-group input").forEach(function (i) { i.checked = i.value === size; });
    document.querySelectorAll("#set-text").forEach(function (s) { s.value = size; });
  }
  function initTheme() {
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var cur = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
        applyTheme(cur === "dark" ? "light" : "dark");
      });
    });
  }

  // ------------------------------------------------------------------ reading settings panel (header "Aa")
  function mountDisplayMenu(el) {
    var panel = h("div", { class: "display-panel", id: "display-panel", role: "dialog", "aria-label": "Reading settings", hidden: true });
    var btn = h("button", { class: "icon-btn display-btn", type: "button", "aria-expanded": "false", "aria-controls": "display-panel", "aria-label": "Reading settings", title: "Reading settings" }, icon("type"));
    var shortcuts = h("input", { type: "checkbox", id: "display-shortcuts", checked: store.setting("shortcuts", true), onchange: function () { store.setSetting("shortcuts", shortcuts.checked); } });
    panel.append(h("p", { class: "display-title", text: "Reading settings" }),
      segmented("Show", DEPTHS, store.setting("depth", "all"), setDepth, "display-row depth-group", DEPTH_HELP),
      segmented("Text size", TEXT_SIZES, store.setting("text", null) || "m", applyText, "display-row text-group"),
      segmented("Theme", THEMES, themeSetting(), applyTheme, "display-row theme-group"),
      h("label", { class: "display-check", for: "display-shortcuts" }, shortcuts, h("span", { html: "Single-key shortcuts: <kbd>/</kbd> search, <kbd>[</kbd> <kbd>]</kbd> lessons, <kbd>?</kbd> list" })),
      h("p", { class: "display-foot" }, h("a", { href: ROOT + "index.html#settings", text: "All settings and your progress file" })));
    function open(state) {
      panel.hidden = !state;
      btn.setAttribute("aria-expanded", String(state));
      if (state) { var first = panel.querySelector("input:checked") || panel.querySelector("input"); if (first) first.focus(); }
    }
    btn.addEventListener("click", function () { open(panel.hidden); });
    document.addEventListener("click", function (e) { if (!panel.hidden && !el.contains(e.target)) open(false); });
    el.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { open(false); btn.focus(); } });
    document.addEventListener("settings-change", function (e) { if (e.detail.name === "shortcuts") shortcuts.checked = e.detail.value; });
    el.append(btn, panel);
  }

  // ------------------------------------------------------------------ keyboard shortcuts (can be turned off: WCAG 2.1.4)
  var shortcutsDialog = null;
  function openShortcuts() {
    if (!shortcutsDialog) {
      var off = button("Turn single-key shortcuts off", function () { store.setSetting("shortcuts", false); shortcutsDialog.close(); announce("Single-key shortcuts are off. Turn them on again in Reading settings."); }, "btn");
      shortcutsDialog = h("dialog", { class: "shortcuts-dialog", "aria-labelledby": "shortcuts-title" },
        h("p", { class: "dialog-title", id: "shortcuts-title", text: "Keyboard shortcuts" }),
        h("dl", {},
          h("dt", {}, h("kbd", { text: "/" })), h("dd", { text: "Search the course" }),
          h("dt", {}, h("kbd", { text: "[" })), h("dd", { text: "Previous lesson" }),
          h("dt", {}, h("kbd", { text: "]" })), h("dd", { text: "Next lesson" }),
          h("dt", {}, h("kbd", { text: "?" })), h("dd", { text: "This list" }),
          h("dt", {}, h("kbd", { text: "Esc" })), h("dd", { text: "Close menus and this dialog" })),
        h("div", { class: "toolbar" }, button("Close", function () { shortcutsDialog.close(); }, "btn btn--primary"), off));
      document.body.append(shortcutsDialog);
    }
    if (typeof shortcutsDialog.showModal === "function") shortcutsDialog.showModal(); else shortcutsDialog.setAttribute("open", "");
  }
  function initShortcuts() {
    document.addEventListener("keydown", function (e) {
      var t = e.target;
      if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey) return;
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable) return;
      if (!store.setting("shortcuts", true)) return;
      if (e.key === "/") { var input = document.querySelector(".search-input"); if (input) { e.preventDefault(); input.focus(); } }
      else if (e.key === "?") { e.preventDefault(); openShortcuts(); }
      else if (e.key === "[" || e.key === "]") {
        var link = document.querySelector(e.key === "[" ? ".pager-prev" : ".pager-next");
        if (link) location.href = link.href; else announce(e.key === "[" ? "This is the first lesson" : "This is the last lesson so far");
      }
    });
  }

  // ------------------------------------------------------------------ headings, anchors, on-this-page navigation
  function addAnchors(main) {
    main.querySelectorAll("h2[id], h3[id], section[id] > h2, section[id] > h3, article.exercise[id] > h3, article.exercise[id] > .ex-head > h3").forEach(function (head) {
      var id = head.id || (head.parentElement.classList.contains("ex-head") ? head.parentElement.parentElement.id : head.parentElement.id);
      if (!id || head.querySelector(".anchor")) return;
      head.append(h("a", { class: "anchor", href: "#" + id, "aria-label": "Link to this section" }, "#"));
    });
    main.querySelectorAll("tr[data-api][id]").forEach(function (row) {
      var cell = row.querySelector("td, th");
      if (cell) cell.prepend(h("a", { class: "anchor anchor--row", href: "#" + row.id, "aria-label": "Link to " + row.dataset.api.split(" ")[0] }, "#"));
    });
  }
  function buildToc(main) {
    var heads = main.querySelectorAll(":scope > section[id] > h2");
    if (heads.length < 3 || document.body.dataset.page === "home") return null;
    var list = h("ol", {});
    heads.forEach(function (head) {
      var sec = head.parentElement;
      var level = sec.dataset.level || "";
      list.append(h("li", { "data-level": level || null, class: sec.classList.contains("api-reference") ? "toc-ref" : null },
        h("a", { href: "#" + sec.id }, h("span", { text: headingText(head) }),
          level ? h("span", { class: "toc-level", "data-level": level, title: LEVELS[level].label, "aria-label": "(" + LEVELS[level].label + ")", text: LEVELS[level].icon }) : null)));
    });
    var nav = h("nav", { class: "toc", "aria-label": "On this page" }, h("p", { class: "toc-title", text: "On this page" }), list);
    placeToc(nav, main, heads.length);
    return nav;
  }
  /** One navigation element, moved between a sticky rail (wide screens) and a collapsible block. */
  function placeToc(nav, main, count) {
    var layout = main.closest(".layout");
    var rail = h("aside", { class: "toc-rail", "aria-label": "Sections of this page" });
    var inline = h("details", { class: "toc-inline" }, h("summary", { text: "On this page (" + count + " sections)" }));
    var query = matchMedia(WIDE);
    function place() {
      if (query.matches && layout) {
        rail.append(nav);
        if (!rail.isConnected) layout.append(rail);
        layout.classList.add("has-rail");
        inline.remove();
      } else {
        inline.append(nav);
        if (!inline.isConnected) {
          var anchor = main.querySelector(".legend") || main.querySelector(".lesson-status") || main.querySelector(".lesson-meta") || main.querySelector("h1");
          anchor.after(inline);
        }
        rail.remove();
        if (layout) layout.classList.remove("has-rail");
      }
    }
    place();
    query.addEventListener("change", place);
  }

  // ------------------------------------------------------------------ lesson header: breadcrumb, status, reading position
  function enhanceLessonHead(main, lessonId) {
    var info = findLesson(lessonId);
    if (!info) return;
    var crumb = main.querySelector("p.breadcrumb");
    var phase = phaseOf(info.m);
    if (crumb) {
      var nav = h("nav", { class: "breadcrumb", "aria-label": "Breadcrumb" }, h("ol", {},
        h("li", {}, h("a", { href: ROOT + "index.html", text: "Course" })),
        phase ? h("li", {}, h("a", { href: ROOT + "index.html#map-" + phase.id, text: "Phase " + phase.n + ": " + phase.title })) : null,
        h("li", {}, h("a", { href: ROOT + "index.html#map-" + info.m.id, text: info.m.id.toUpperCase() + " " + info.m.title })),
        h("li", { "aria-current": "page", text: "Lesson " + info.n + " of " + info.of })));
      crumb.replaceWith(nav);
    }
    var meta = main.querySelector(".lesson-meta");
    if (!meta) return;
    var resume = store.setting("resume", null);
    var strip = h("div", { class: "lesson-status", role: "group", "aria-label": "Your progress in this lesson" });
    function draw() {
      var ex = Array.prototype.map.call(main.querySelectorAll("article.exercise"), function (x) { return { id: x.id, optional: x.hasAttribute("data-optional") }; });
      var c = lessonCounts(lessonId, ex);
      var quiz = main.querySelector('section.quiz[id$="-quiz"]');
      var best = quiz && store.get("quizzes", quiz.id);
      var done = (store.get("lessons", lessonId) || {}).completed;
      fill(strip, [h("span", { class: "status-label", text: done ? "✓ Lesson completed" : "Your progress" }),
        c.total ? h("span", { class: "status-item" + (c.passed === c.total ? " is-good" : "") }, "Exercises ", h("strong", { text: c.passed + " of " + c.total })) : null,
        quiz ? h("span", { class: "status-item" + (best && best.best === 100 ? " is-good" : "") }, "Quiz ", h("strong", { text: best ? "best " + best.best + "%" : "not taken" })) : null,
        resume && resume.lesson === lessonId && resume.section && !location.hash && resume.section !== firstSectionId(main)
          ? h("a", { class: "resume-link", href: "#" + resume.section, text: "Continue at: " + resume.title }) : null]);
    }
    meta.after(strip);
    draw();
    document.addEventListener("progress-change", draw);
  }
  function firstSectionId(main) { var s = main.querySelector(":scope > section[id]"); return s ? s.id : ""; }

  /** One scroll handler: reading-progress line, current section in the rail, resume position. */
  function initReading(main, lessonId, nav) {
    var header = document.querySelector(".site-header");
    var bar = null;
    if (header && document.body.dataset.page === "lesson") {
      bar = h("span");
      header.append(h("div", { class: "reading-progress", "aria-hidden": "true" }, bar));
    }
    var sections = Array.prototype.slice.call(main.querySelectorAll(":scope > section[id]"));
    var links = {};
    if (nav) nav.querySelectorAll("a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    var current = null, saveTimer = null, ticking = false;
    function update() {
      ticking = false;
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      if (bar) bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, window.scrollY / max) : 0) + ")";
      var line = (header ? header.offsetHeight : 0) + 96, active = null;
      for (var i = 0; i < sections.length; i++) {
        if (!sections[i].getClientRects().length) continue;
        if (sections[i].getBoundingClientRect().top <= line) active = sections[i]; else break;
      }
      if (active === current) return;
      if (current && links[current.id]) links[current.id].removeAttribute("aria-current");
      current = active;
      if (current && links[current.id]) {
        var link = links[current.id], rail = link.closest(".toc-rail");
        link.setAttribute("aria-current", "location");
        if (rail) { // keep the current entry visible in a long rail
          var r = link.getBoundingClientRect(), box = rail.getBoundingClientRect();
          if (r.top < box.top || r.bottom > box.bottom) rail.scrollTop += r.top - box.top - box.height / 3;
        }
      }
      if (lessonId && current) {
        clearTimeout(saveTimer);
        var section = current;
        saveTimer = setTimeout(function () {
          var head = section.querySelector(":scope > h2");
          store.setSetting("resume", { lesson: lessonId, section: section.id, title: head ? headingText(head) : section.id, at: new Date().toISOString() }, true);
        }, 800);
      }
    }
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  // ------------------------------------------------------------------ exercises (run locally with pytest)
  function mountExercise(el) {
    var id = el.id;
    var file = el.dataset.file;
    var writeTests = el.dataset.kind === "write_tests";
    var testFile = writeTests ? "test_" + file.replace(/\.py$/, "") + "_check.py" : "test_" + file;
    var lessonId = document.body.dataset.lessonId;
    var roles = {};
    el.querySelectorAll("script[data-role]").forEach(function (s) { roles[s.dataset.role] = s; });
    var status = h("p", { class: "ex-status", "aria-live": "polite" });
    function refresh() {
      var rec = store.get("exercises", id) || {};
      el.dataset.status = rec.status || "todo";
      status.replaceChildren(rec.status === "passed"
        ? h("span", { class: "chip chip--success" }, "✓ Passed (completion code checked)")
        : rec.status === "done" ? h("span", { class: "chip chip--info" }, "✓ Marked as done (not verified)")
          : h("span", { class: "chip" }, "Not passed yet"));
    }
    var head = h("div", { class: "ex-head" });
    var title = el.querySelector(":scope > h3"), meta = el.querySelector(":scope > .ex-meta");
    el.prepend(head);
    append(head, [title, meta, status]);
    var editName = writeTests ? "test_" + file : file;
    var parts = [];
    if (writeTests && roles.target) {
      parts.push(codePanel({ code: dedent(roles.target.textContent), lang: "python", label: file + " (the code to test: don't change it)", file: file, what: file }));
    }
    if (roles.starter) parts.push(codePanel({ code: dedent(roles.starter.textContent), lang: "python", label: editName + " (your file: start here)", file: editName, what: editName }));
    if (roles.tests) {
      parts.push(h("details", { class: "tests" }, h("summary", {}, "Tests: what pytest checks (" + testFile + ")"),
        codePanel({ code: dedent(roles.tests.textContent), lang: "python", label: testFile, file: testFile, what: testFile })));
    }
    var input = h("input", { class: "ex-code-input", type: "text", inputmode: "text", autocomplete: "off", spellcheck: "false", placeholder: "XXXX-XXXX", "aria-label": "Completion code for " + id });
    var feedback = h("p", { class: "ex-feedback", "aria-live": "polite" });
    function verify() {
      var given = input.value.toUpperCase().replace(/[^0-9A-F]/g, "");
      if (given === completionCode(id).replace("-", "")) {
        store.set("exercises", id, { status: "passed", verified: true });
        feedback.textContent = "Code accepted: exercise recorded as passed.";
      } else {
        feedback.textContent = given ? "That code doesn't match this exercise. Check you pasted the code printed for " + id + "." : "Paste the code pytest printed first.";
      }
    }
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") verify(); });
    var cmd = "{pytest} " + testFile;
    var terminal = codePanel({ code: fillCommand(cmd), lang: "shell", label: "Terminal, in the " + lessonId + " folder", what: "Command", copy: function () { return fillCommand(cmd); } });
    var pre = terminal.querySelector("pre");
    pre.dataset.template = cmd;
    pre.classList.add("fill-pre");
    var steps = h("ol", { class: "ex-steps" },
      h("li", {}, h("strong", { text: "Get the files. " }), "Download the exercise pack once per lesson and unzip it, or use the Download buttons above. ",
        h("a", { class: "btn btn--small", href: ROOT + "downloads/" + lessonId + ".zip", download: true, text: "Download the exercise pack" })),
      h("li", {}, h("strong", { text: "Write your solution " }), "in ", h("code", { text: editName }), " in your editor."),
      h("li", {}, h("strong", { text: "Run the tests " }), "in a terminal opened in the ", h("code", { text: lessonId }), " folder:", terminal),
      h("li", {}, h("strong", { text: "Record your result. " }), "When every test passes, pytest prints a completion code. Paste it here:",
        h("div", { class: "toolbar" }, input, button("Record result", verify, "btn btn--primary"),
          button("I can't run pytest: mark as done", function () { store.set("exercises", id, { status: "done", verified: false }); }, "btn btn--ghost btn--small")),
        feedback));
    var hints = el.querySelector("ol.hints");
    var hintBox = null;
    if (hints) {
      var items = Array.prototype.slice.call(hints.children);
      hints.hidden = true;
      var shown = h("ol", { class: "hints-shown" });
      var hintBtn = button("Show a hint (1 of " + items.length + ")", function () {
        var n = shown.children.length;
        if (n < items.length) shown.append(items[n].cloneNode(true));
        var used = shown.children.length;
        store.set("exercises", id, { hints: Math.max(used, (store.get("exercises", id) || {}).hints || 0) }, true);
        if (used >= items.length) hintBtn.remove();
        else hintBtn.textContent = "Show the next hint (" + (used + 1) + " of " + items.length + ")";
      }, "btn btn--small");
      hintBox = h("div", { class: "hints-box" }, shown, hintBtn);
    }
    var solutionBox = null;
    if (roles.solution) {
      var solution = h("details", { class: "solution" }, h("summary", {}, "Solution"));
      var gate = h("div", { class: "solution-gate" },
        h("p", { text: "You learn most from the solution after a real attempt: run the tests, read the failure, try a hint. Show it anyway?" }),
        button("Show the solution", function () {
          gate.replaceWith(codePanel({ code: dedent(roles.solution.textContent), lang: "python", label: "One good solution (" + editName + ")", file: "solution_" + editName, what: "Solution" }),
            roles.solution.dataset.notes ? h("p", { text: roles.solution.dataset.notes }) : null);
          store.set("exercises", id, { solutionViewed: true }, true);
        }, "btn btn--small"));
      solution.append(gate);
      solutionBox = solution;
    }
    var box = h("div", { class: "ex-work" }, parts, h("h4", { class: "ex-steps-title", text: "Run it on your computer" }), steps, hintBox, solutionBox);
    (hints || el.lastElementChild).after(box);
    document.addEventListener("progress-change", refresh);
    refresh();
  }

  // ------------------------------------------------------------------ quizzes (in the browser)
  function stableShuffle(items, seedText) {
    var seed = Array.prototype.reduce.call(seedText, function (acc, ch) { return (acc * 31 + ch.charCodeAt(0)) >>> 0; }, 7);
    function rand() { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; }
    var out = items.slice();
    for (var i = out.length - 1; i > 0; i--) { var j = Math.floor(rand() * (i + 1)); var t = out[i]; out[i] = out[j]; out[j] = t; }
    if (out.length > 1 && out.every(function (x, k) { return x === items[k]; })) out.push(out.shift());
    return out;
  }
  function mountQuiz(el) {
    var specNode = el.querySelector("script.quiz-spec");
    var spec = specNode && parseJSON(specNode.textContent);
    if (!spec || !spec.questions) { console.error("Quiz is missing its spec", el); return; }
    var form = h("form", { class: "quiz-form", novalidate: true });
    var total = spec.questions.length;
    var items = spec.questions.map(function (q, i) { return renderQuestion(q, spec.id + "-q" + (i + 1), i + 1, total); });
    var score = h("p", { class: "quiz-score", "aria-live": "polite" });
    items.forEach(function (x) { form.append(x.node); });
    form.append(h("div", { class: "toolbar" }, h("button", { class: "btn btn--primary", type: "submit" }, "Check answers"), score));
    var prev = store.get("quizzes", spec.id);
    if (prev) score.textContent = "Best so far: " + prev.best + "%";
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var right = items.filter(function (item) { return item.check(); }).length;
      var pct = Math.round((100 * right) / items.length);
      score.textContent = right + " of " + items.length + " correct (" + pct + "%)" + (right === items.length ? ". Well done." : ". Read the feedback and try again.");
      var old = store.get("quizzes", spec.id) || {};
      store.set("quizzes", spec.id, { score: pct, best: Math.max(old.best || 0, pct), attempts: (old.attempts || 0) + 1 });
    });
    el.append(form);
  }
  function renderQuestion(q, name, n, total) {
    var feedback = h("div", { class: "q-feedback", hidden: true, "aria-live": "polite" });
    var node = h("fieldset", { class: "q q--" + q.type },
      h("legend", {}, h("span", { class: "q-num", text: String(n) }), h("span", { class: "visually-hidden", text: "Question " + n + " of " + total + ": " }), h("span", { html: q.prompt })));
    var read;
    if (q.type === "mcq" || q.type === "multi") {
      var inputs = q.options.map(function (opt, i) {
        var input = h("input", { type: q.type === "mcq" ? "radio" : "checkbox", name: name, value: String(i) });
        node.append(h("label", { class: "q-option" }, input, h("span", { html: opt })));
        return input;
      });
      read = function () { return inputs.reduce(function (acc, inp, i) { if (inp.checked) acc.push(i); return acc; }, []); };
    } else if (q.type === "order") {
      var list = h("ol", { class: "q-order" });
      var current = stableShuffle(q.items, name);
      var move = function (i, step) {
        var j = i + step;
        if (j < 0 || j >= current.length) return;
        current = current.slice();
        var t = current[i]; current[i] = current[j]; current[j] = t;
        draw();
        var target = list.children[j] && list.children[j].querySelector(step < 0 ? ".q-up" : ".q-down");
        if (target) target.focus();
      };
      var draw = function () {
        list.replaceChildren.apply(list, current.map(function (item, i) {
          return h("li", { class: "q-order-item" }, h("span", { class: "q-order-text", html: item }),
            h("button", { class: "btn btn--ghost btn--icon q-up", type: "button", "aria-label": "Move up: " + plain(item), onclick: function () { move(i, -1); } }, "↑"),
            h("button", { class: "btn btn--ghost btn--icon q-down", type: "button", "aria-label": "Move down: " + plain(item), onclick: function () { move(i, 1); } }, "↓"));
        }));
      };
      draw();
      node.append(list);
      read = function () { return current; };
    } else {
      if (q.code) node.append(h("pre", { class: "code q-code", tabindex: "0", "aria-label": "Code for question " + n }, highlight(dedent(q.code), "python")));
      var input = q.type === "predict"
        ? h("textarea", { class: "q-answer", rows: 3, spellcheck: "false", "aria-label": "Your predicted output" })
        : h("input", { class: "q-answer", type: "text", "aria-label": "Your answer" });
      node.append(input);
      read = function () { return input.value; };
    }
    node.append(feedback);
    function check() {
      var got = read(), ok = false, explain = q.explanation || "";
      if (q.type === "mcq") { ok = got[0] === q.answer; if (q.explanations && got.length) explain = q.explanations[got[0]]; }
      else if (q.type === "multi") ok = got.length === q.answer.length && q.answer.every(function (i) { return got.indexOf(i) >= 0; });
      else if (q.type === "order") ok = got.every(function (item, i) { return item === q.items[i]; });
      else if (q.type === "predict") ok = normalizeText(got) === normalizeText(q.answer);
      else ok = (q.accept || []).some(function (a) { return a.trim().toLowerCase() === got.trim().toLowerCase(); }) || (q.accept_regex ? new RegExp(q.accept_regex, "i").test(got.trim()) : false);
      var unanswered = Array.isArray(got) ? got.length === 0 : !got.trim();
      node.classList.toggle("q--correct", ok);
      node.classList.toggle("q--incorrect", !ok);
      feedback.hidden = false;
      fill(feedback, [h("strong", { text: ok ? "✓ Correct. " : unanswered ? "No answer yet. " : "✗ Not quite. " }), h("span", { html: explain }),
        !ok && q.type === "predict" ? h("pre", { class: "output" }, h("samp", { text: q.answer })) : null]);
      return ok;
    }
    return { node: node, check: check };
  }

  // ------------------------------------------------------------------ finishing a lesson, navigation
  function mountLessonComplete(el, lessonId) {
    var summary = h("p", { class: "lesson-summary" });
    var btn = button("", function () { store.set("lessons", lessonId, { completed: !(store.get("lessons", lessonId) || {}).completed }); }, "btn btn--primary");
    function refresh() {
      var done = Boolean((store.get("lessons", lessonId) || {}).completed);
      btn.textContent = done ? "✓ Lesson completed" : "Mark lesson as complete";
      btn.setAttribute("aria-pressed", String(done));
      var ex = Array.prototype.map.call(document.querySelectorAll("article.exercise"), function (x) { return { id: x.id, optional: x.hasAttribute("data-optional") }; });
      var c = lessonCounts(lessonId, ex);
      summary.textContent = c.total ? "Exercises passed: " + c.passed + " of " + c.total : "Read it, run the examples, take the quiz.";
    }
    document.addEventListener("progress-change", refresh);
    el.append(h("p", { class: "finish-title", text: "Finish this lesson" }), summary, btn);
    refresh();
  }
  function renderNav(nav, lessonId) {
    function lessonItem(m, l) {
      var state = lessonState(l);
      var said = { done: " (completed)", started: " (started)", new: "" }[state];
      if (l.planned) {
        return h("li", {}, h("span", { class: "is-planned" }, h("span", { class: "nav-status", "data-state": "planned", "aria-hidden": "true" }),
          h("span", {}, l.title, h("span", { class: "nav-soon", "aria-hidden": "true", text: "soon" }), h("span", { class: "visually-hidden", text: " (coming soon)" }))));
      }
      return h("li", {}, h("a", { href: ROOT + m.path + l.file, "aria-current": l.id === lessonId ? "page" : null, class: state === "done" ? "is-done" : null },
        h("span", { class: "nav-status", "data-state": state, "aria-hidden": "true" }), h("span", {}, l.title, said ? h("span", { class: "visually-hidden", text: said }) : null)));
    }
    function moduleItem(m) {
      var built = m.lessons.filter(function (l) { return !l.planned; });
      var done = built.filter(function (l) { return lessonState(l) === "done"; }).length;
      var current = m.lessons.some(function (l) { return l.id === lessonId; });
      return h("li", {}, h("details", { open: current || COURSE.modules.length === 1 },
        h("summary", {}, h("span", { class: "nav-mod-id", text: m.id.toUpperCase() }), h("span", { text: m.title }),
          built.length ? h("span", { class: "nav-mod-count", title: done + " of " + built.length + " written lessons completed", text: done + "/" + built.length }) : null),
        h("ol", { class: "nav-lessons" }, m.lessons.map(function (l) { return lessonItem(m, l); }))));
    }
    function draw() {
      var phases = (COURSE.phases && COURSE.phases.length) ? COURSE.phases : [{ id: null, title: "" }];
      var blocks = phases.map(function (p) {
        var mods = COURSE.modules.filter(function (m) { return p.id === null || m.phase === p.id; });
        if (!mods.length) return null;
        return h("div", { class: "nav-phase" }, p.id ? h("p", { class: "nav-phase-title", text: "Phase " + p.id.replace(/^p/, "") + ": " + p.title }) : null,
          h("ol", { class: "nav-modules" }, mods.map(moduleItem)));
      });
      nav.replaceChildren.apply(nav, blocks.filter(Boolean).concat([h("ul", { class: "nav-extra" },
        h("li", {}, h("a", { href: ROOT + "index.html", text: "Course home and progress" })),
        h("li", {}, h("a", { href: ROOT + "setup.html", text: "Set up your computer" })),
        h("li", {}, h("a", { href: ROOT + "api-index.html", text: "API index" })))]));
    }
    draw();
    document.addEventListener("progress-change", draw);
  }
  function renderPager(pager, lessonId) {
    var all = flatLessons();
    var i = all.findIndex(function (x) { return x.l.id === lessonId; });
    if (i < 0) { pager.hidden = true; return; }
    function link(x, rel, label) { return x ? h("a", { class: "pager-" + rel, href: x.href, rel: rel }, h("span", { class: "pager-label", text: label }), h("span", { class: "pager-title", text: x.l.title })) : null; }
    var prev = link(all[i - 1], "prev", "Previous lesson"), next = link(all[i + 1], "next", "Next lesson");
    pager.replaceChildren.apply(pager, [prev, next].filter(Boolean));
    pager.hidden = !prev && !next;
  }

  // ------------------------------------------------------------------ home: continue card, course map, settings
  function mountContinue(el) {
    function draw() {
      var resume = store.setting("resume", null);
      var info = resume && findLesson(resume.lesson);
      var card;
      if (info && !info.l.planned) {
        card = h("div", { class: "continue-card" },
          h("p", { class: "continue-label", text: "Continue where you left off" }),
          h("p", { class: "continue-title", text: info.l.title + (resume.title ? ": " + resume.title : "") }),
          h("a", { class: "btn btn--primary", href: info.href + (resume.section ? "#" + resume.section : ""), text: "Continue" }));
      } else {
        var first = flatLessons()[0];
        card = h("div", { class: "continue-card" },
          h("p", { class: "continue-label", text: "New here? Start in two steps" }),
          h("p", { class: "continue-title", text: "Set up your computer, then open your first lesson" + (first ? ": " + first.l.title : "") + "." }),
          h("a", { class: "btn btn--primary", href: ROOT + "setup.html", text: "Set up your computer" }));
      }
      el.replaceChildren(card);
    }
    draw();
    document.addEventListener("progress-change", draw);
  }
  function meter(pct, label) {
    return h("div", { class: "meter", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(pct), "aria-label": label }, h("span", { style: "width:" + pct + "%" }));
  }
  function mountDashboard(el) {
    var totals = { lessons: 0, done: 0, ex: 0, passed: 0 };
    var phases = (COURSE.phases && COURSE.phases.length) ? COURSE.phases : [{ id: null, title: "Modules" }];
    var blocks = phases.map(function (p) {
      var mods = COURSE.modules.filter(function (m) { return p.id === null || m.phase === p.id; });
      var phaseBuilt = 0, phaseDone = 0, phaseTouched = false;
      var cards = mods.map(function (m) {
        var built = m.lessons.filter(function (l) { return !l.planned; });
        var done = built.filter(function (l) { return (store.get("lessons", l.id) || {}).completed; }).length;
        var ex = built.reduce(function (acc, l) { var c = lessonCounts(l.id, l.exercises); acc.p += c.passed; acc.t += c.total; return acc; }, { p: 0, t: 0 });
        totals.lessons += built.length; totals.done += done; totals.ex += ex.t; totals.passed += ex.p;
        phaseBuilt += built.length; phaseDone += done;
        phaseTouched = phaseTouched || built.some(function (l) { return lessonState(l) !== "new"; });
        var pct = built.length ? Math.round((100 * done) / built.length) : 0;
        var first = built[0];
        return h("li", { class: "module-card", id: "map-" + m.id },
          h("a", { href: first ? ROOT + m.path + first.file : "#map-" + m.id }, h("span", { class: "module-id", text: m.id.toUpperCase() }), h("span", { class: "module-title", text: m.title })),
          meter(pct, m.title + ": " + pct + "% of lessons complete"),
          h("span", { class: "module-pct", text: done + " of " + built.length + " lessons · " + ex.p + " of " + ex.t + " exercises" + (built.length < m.lessons.length ? " · " + (m.lessons.length - built.length) + " lessons coming" : "") }));
      });
      var state = phaseBuilt && phaseDone === phaseBuilt ? "done" : phaseTouched ? "started" : "new";
      return h("section", { class: "phase-block" + (cards.length ? "" : " is-empty"), id: p.id ? "map-" + p.id : null, "data-n": p.id ? p.id.replace(/^p/, "") : null, "data-state": state, "aria-label": p.id ? "Phase " + p.id.replace(/^p/, "") : null },
        h("h3", { text: p.id ? "Phase " + p.id.replace(/^p/, "") + ": " + p.title : p.title }),
        cards.length ? h("ol", { class: "module-grid" }, cards) : h("p", { class: "phase-empty", text: "Lessons for this phase aren't published yet." }));
    });
    el.replaceChildren(h("p", { class: "dash-total", text: "Overall: " + totals.done + " of " + totals.lessons + " lessons complete, " + totals.passed + " of " + totals.ex + " exercises passed." }),
      h("div", { class: "course-map" }, blocks));
  }
  function mountSettings(el) {
    var themeSel = h("select", { id: "set-theme", onchange: function () { applyTheme(themeSel.value); } },
      Object.keys(THEMES).map(function (k) { return h("option", { value: k, text: k === "system" ? "Follow my system" : THEMES[k] }); }));
    themeSel.value = themeSetting();
    var textSel = h("select", { id: "set-text", onchange: function () { applyText(textSel.value); } },
      Object.keys(TEXT_SIZES).map(function (k) { return h("option", { value: k, text: TEXT_SIZES[k] }); }));
    textSel.value = store.setting("text", null) || "m";
    var depthSel = h("select", { id: "set-depth", class: "depth-select", onchange: function () { setDepth(depthSel.value); } }, Object.keys(DEPTHS).map(function (k) { return h("option", { value: k, text: DEPTHS[k] + ": " + DEPTH_HELP[k].charAt(0).toLowerCase() + DEPTH_HELP[k].slice(1) }); }));
    depthSel.value = store.setting("depth", "all");
    var runSel = h("select", { id: "set-runner", onchange: function () { store.setSetting("runner", runSel.value); } }, Object.keys(RUNNERS).map(function (k) { return h("option", { value: k, text: RUNNERS[k].label }); }));
    runSel.value = store.setting("runner", null) || (runner() === RUNNERS.py ? "py" : "python3");
    var keys = h("input", { type: "checkbox", id: "set-shortcuts", checked: store.setting("shortcuts", true), onchange: function () { store.setSetting("shortcuts", keys.checked); } });
    document.addEventListener("settings-change", function (e) { if (e.detail.name === "shortcuts") keys.checked = e.detail.value; });
    var preview = h("code", { class: "fill-cmd", "data-template": "{python} example.py   ·   {pytest} test_e1_word_freq.py" });
    el.append(h("div", { class: "settings-grid" },
      h("label", { for: "set-theme", text: "Theme" }), themeSel,
      h("label", { for: "set-text", text: "Text size" }), textSel,
      h("label", { for: "set-depth", text: "Reading depth" }), depthSel,
      h("label", { for: "set-runner", text: "How you run Python" }), h("div", {}, runSel, h("p", { class: "muted" }, "Commands on every page will read: ", preview)),
      h("label", { for: "set-shortcuts", text: "Keyboard shortcuts" }), h("div", { class: "display-check" }, keys, h("span", { html: "Single-key shortcuts (<kbd>/</kbd> <kbd>[</kbd> <kbd>]</kbd> <kbd>?</kbd>)" }))));
    mountProgressTools(el);
  }
  function mountProgressTools(el) {
    var fileInput = h("input", { type: "file", accept: "application/json", class: "visually-hidden", id: "progress-import" });
    var status = h("p", { "aria-live": "polite" });
    var armed = false;
    var reset = button("Reset all progress", function () {
      if (!armed) { armed = true; reset.textContent = "Click again to erase everything"; return; }
      try { localStorage.removeItem(STORE_KEY); } catch (e) { /* ignore */ }
      store.data = null; store.load(); store.save(); status.textContent = "Progress erased."; armed = false; reset.textContent = "Reset all progress";
    }, "btn btn--danger");
    fileInput.addEventListener("change", function () {
      var f = fileInput.files[0];
      if (!f) return;
      f.text().then(function (text) {
        var data = parseJSON(text);
        if (!data || data.version !== 1) throw new Error("not a progress file from this course");
        store.data = data; store.load(); store.save(); status.textContent = "Progress imported.";
      }).catch(function (err) { status.textContent = "Import failed: " + err.message; });
    });
    el.append(h("div", { class: "toolbar" },
      button("Export progress", function () { download((COURSE.id || "course") + "-progress.json", JSON.stringify(store.load(), null, 2)); }),
      h("label", { class: "btn", for: "progress-import" }, "Import progress"), fileInput, reset), status);
  }

  // ------------------------------------------------------------------ search (index loaded on first use)
  function mountSearch(el) {
    var input = h("input", { type: "search", class: "search-input", placeholder: "Search the course", "aria-label": "Search the course", "aria-keyshortcuts": "/", autocomplete: "off", role: "combobox", "aria-expanded": "false", "aria-controls": "search-results", "aria-autocomplete": "list" });
    var list = h("ul", { class: "search-results", id: "search-results", role: "listbox", "aria-label": "Search results", hidden: true });
    var active = -1, results = [];
    el.append(input, list);
    function load(then) {
      if (window.SEARCH_INDEX) return then();
      if (load.pending) { load.pending.push(then); return; }
      load.pending = [then];
      var s = h("script", { src: ROOT + "assets/js/search-index.js" });
      s.onload = function () { var q = load.pending; load.pending = null; q.forEach(function (f) { f(); }); };
      s.onerror = function () { list.hidden = false; list.replaceChildren(h("li", { class: "search-empty", text: "Search index not found. Run python tools/build.py." })); };
      document.head.append(s);
    }
    function score(entry, tokens) {
      var title = entry.t.toLowerCase(), api = (entry.a || "").toLowerCase(), hay = entry.hay || (entry.hay = (entry.t + " " + (entry.a || "") + " " + (entry.s || "") + " " + (entry.m || "")).toLowerCase());
      var total = 0;
      for (var i = 0; i < tokens.length; i++) {
        var tok = tokens[i];
        if (hay.indexOf(tok) < 0) return 0;
        if (api && (" " + api + " ").match(new RegExp("[ .]" + tok.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "[ (]"))) total += 12;
        if (title.indexOf(tok) === 0) total += 10;
        else if (title.indexOf(tok) > 0) total += 5;
        else total += 1;
      }
      return total + ({ api: 2, lesson: 3, term: 2 }[entry.k] || 0) + (entry.l === "essential" ? 1 : 0);
    }
    function search() {
      var q = input.value.trim().toLowerCase();
      if (!q) { close(); return; }
      load(function () {
        var tokens = q.split(/\s+/);
        results = window.SEARCH_INDEX.map(function (e) { return { e: e, s: score(e, tokens) }; })
          .filter(function (x) { return x.s > 0; }).sort(function (a, b) { return b.s - a.s; }).slice(0, 15);
        active = results.length ? 0 : -1;
        draw();
      });
    }
    function draw() {
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
      if (!results.length) { list.replaceChildren(h("li", { class: "search-empty", text: "No matches. Try fewer or shorter words." })); return; }
      list.replaceChildren.apply(list, results.map(function (r, i) {
        var e = r.e;
        return h("li", { id: "sr-" + i, role: "option", class: "search-hit" + (i === active ? " is-active" : ""), "aria-selected": String(i === active), onmousedown: function (ev) { ev.preventDefault(); go(i); } },
          h("span", { class: "hit-kind", text: { api: "API", section: "Section", lesson: "Lesson", term: "Term", exercise: "Exercise" }[e.k] || "Page" }),
          h("span", { class: "hit-title", text: e.t }), e.l && LEVELS[e.l] ? h("span", { class: "toc-level", "data-level": e.l, "aria-label": "(" + LEVELS[e.l].label + ")", text: LEVELS[e.l].icon }) : null,
          h("span", { class: "hit-where", text: e.m || "" }), e.s ? h("span", { class: "hit-snippet", text: e.s }) : null);
      }));
      input.setAttribute("aria-activedescendant", active >= 0 ? "sr-" + active : "");
    }
    function go(i) { var r = results[i]; if (r) { location.href = ROOT + r.e.u; close(); } }
    function close() { list.hidden = true; input.setAttribute("aria-expanded", "false"); input.removeAttribute("aria-activedescendant"); }
    input.addEventListener("focus", function () { load(function () {}); });
    input.addEventListener("input", search);
    input.addEventListener("blur", function () { setTimeout(close, 150); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!results.length) return;
        active = (active + (e.key === "ArrowDown" ? 1 : results.length - 1)) % results.length;
        draw();
      } else if (e.key === "Enter") { e.preventDefault(); go(Math.max(active, 0)); }
      else if (e.key === "Escape") { close(); input.blur(); }
    });
  }

  // ------------------------------------------------------------------ boot
  function initNavToggle() {
    document.querySelectorAll(".nav-toggle").forEach(function (btn) {
      function set(open) { btn.setAttribute("aria-expanded", String(open)); document.body.classList.toggle("nav-open", open); }
      btn.addEventListener("click", function () { set(btn.getAttribute("aria-expanded") !== "true"); });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape" && document.body.classList.contains("nav-open")) { set(false); btn.focus(); } });
      document.addEventListener("click", function (e) {
        if (document.body.classList.contains("nav-open") && !e.target.closest(".sidebar") && !e.target.closest(".nav-toggle")) set(false);
      });
    });
  }
  function init() {
    var body = document.body;
    var main = document.getElementById("main");
    var lessonId = body.dataset.lessonId;
    initTheme();
    initNavToggle();
    initShortcuts();
    document.querySelectorAll(".site-search").forEach(mountSearch);
    document.querySelectorAll(".depth-control").forEach(mountDepthControl);
    document.querySelectorAll(".display-menu").forEach(mountDisplayMenu);
    document.querySelectorAll(".course-nav").forEach(function (nav) { renderNav(nav, lessonId); });
    if (main) {
      renderMarkers(main);
      renderCode(main);
      if (lessonId) enhanceLessonHead(main, lessonId);
      legend(main);
      addAnchors(main);
      main.querySelectorAll("article.exercise").forEach(mountExercise);
      main.querySelectorAll("section.quiz").forEach(mountQuiz);
      main.querySelectorAll(".lesson-complete").forEach(function (el) { mountLessonComplete(el, lessonId); });
      main.querySelectorAll(".pager").forEach(function (el) { renderPager(el, lessonId); });
      main.querySelectorAll(".continue").forEach(mountContinue);
      main.querySelectorAll(".dashboard").forEach(function (el) { mountDashboard(el); document.addEventListener("progress-change", function () { mountDashboard(el); }); });
      main.querySelectorAll(".settings").forEach(mountSettings);
      var toc = buildToc(main);
      if (lessonId || toc) initReading(main, lessonId, toc);
    }
    applyDepth(document.documentElement.dataset.depth || store.setting("depth", "all"), true);
    document.addEventListener("settings-change", function (e) { if (e.detail.name === "runner") refreshCommands(); });
    window.addEventListener("hashchange", revealTarget);
    if (location.hash) revealTarget();
    document.documentElement.classList.add("js-ready");
  }

  window.CourseUI = { dedent: dedent, completionCode: completionCode, normalizeText: normalizeText, store: store, fillCommand: fillCommand };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
````

## 5. `site/index.html`

````html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Python for AI: Zero to Job-Ready</title>
  <meta name="description" content="A complete Python course for CS (AI) students: from first program to machine learning, deep learning and LLM apps, with a full reference for every topic.">
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/css/course.css">
  <script>
    // Apply the saved theme, text size and reading depth before first paint (no flash).
    try { var s = JSON.parse(localStorage.getItem("pyai.progress.v1") || "{}").settings || {}, d = document.documentElement; if (s.theme) d.dataset.theme = s.theme; if (s.text) d.dataset.text = s.text; d.dataset.depth = s.depth || "all"; } catch (e) { document.documentElement.dataset.depth = "all"; }
  </script>
  <script defer src="assets/vendor/prism.bundle.js"></script>
  <script defer src="assets/js/manifest.js"></script>
  <script defer src="assets/js/course.js"></script>
</head>
<body data-page="home" data-root="">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <button class="icon-btn nav-toggle" type="button" aria-expanded="false" aria-controls="sidebar"><svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 5.5h14M3 10h14M3 14.5h14"></path></svg><span class="nav-toggle-label">Contents</span></button>
    <a class="brand" href="index.html"><span class="brand-prompt" aria-hidden="true">&gt;&gt;&gt;</span><span class="brand-name">Python for AI</span></a>
    <div class="site-search" role="search"></div>
    <div class="depth-control"></div>
    <div class="display-menu"></div>
    <button class="icon-btn theme-toggle" type="button" aria-label="Switch between light and dark theme"><svg aria-hidden="true" viewBox="0 0 20 20"><circle cx="10" cy="10" r="7.25" fill="none" stroke="currentColor" stroke-width="1.6"></circle><path d="M10 2.75a7.25 7.25 0 0 1 0 14.5z" fill="currentColor"></path></svg></button>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar"><nav class="course-nav" aria-label="Course contents"></nav></aside>
    <main id="main" class="content">
      <div class="hero">
        <h1>Python for AI: Zero to Job-Ready</h1>
        <p class="lead">From your first program to machine learning, deep learning and LLM applications. Every lesson teaches the essentials first and then documents the whole topic, so the course stays useful as a reference long after you finish it.</p>
        <div class="continue"></div>
      </div>

      <section id="start">
        <h2>How the course works</h2>
        <ol class="steps-list">
          <li><strong>Set up your computer</strong> (30 minutes, once): install Python, an editor and the course tools with the <a href="setup.html">setup guide</a>.</li>
          <li><strong>Read a lesson</strong> with the essentials marked, and run every example yourself: each one shows the command to type.</li>
          <li><strong>Do the exercises</strong> in your editor and check them with pytest. A passing run prints a completion code that records your progress here.</li>
          <li><strong>Take the quiz</strong> at the end of the lesson. It runs in the page and explains every answer.</li>
        </ol>
      </section>

      <section id="how">
        <h2>How the lessons work</h2>
        <p>Everything in a lesson is marked by how much you need it:</p>
        <ul>
          <li><span class="badge" data-level="essential"><span aria-hidden="true">●</span>Essential</span> what you need to continue the course;</li>
          <li><span class="badge" data-level="extra"><span aria-hidden="true">◆</span>Extra info</span> deeper understanding, safe to skip on a first pass;</li>
          <li><span class="badge" data-level="advanced"><span aria-hidden="true">▲</span>Advanced</span> edge cases and internals, for later and for reference.</li>
        </ul>
        <p>Use <strong>Show</strong> in the header, or the reading settings (<strong>Aa</strong>), to choose how much you see: <strong>Essentials</strong> turns any lesson, its reference tables included, into a cheat sheet. Coloured boxes mark tips, common mistakes, version notes, interview questions and what the topic looks like on the job.</p>
        <p>Python never runs inside these pages. Each example shows the output that real Python printed when the course was built, with the command that runs it; copy or download it and run it yourself. That is how professionals work, and it means the course works offline.</p>
        <p>Looking for one function? Press <kbd>/</kbd> to search, or open the <a href="api-index.html">API index</a>. Press <kbd>?</kbd> for every keyboard shortcut.</p>
      </section>

      <section id="progress">
        <h2>Your course map</h2>
        <p>Progress is saved in this browser only. Export it in Settings to move it to another computer.</p>
        <div class="dashboard"></div>
      </section>

      <section id="settings">
        <h2>Settings</h2>
        <div class="settings"></div>
      </section>
    </main>
  </div>
</body>
</html>
````

## 6. `site/setup.html`

````html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Set up your computer · Python for AI</title>
  <meta name="description" content="Install Python 3.15, an editor and pytest; create a virtual environment; run the examples and check exercises on your own computer.">
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/css/course.css">
  <script>
    // Apply the saved theme, text size and reading depth before first paint (no flash).
    try { var s = JSON.parse(localStorage.getItem("pyai.progress.v1") || "{}").settings || {}, d = document.documentElement; if (s.theme) d.dataset.theme = s.theme; if (s.text) d.dataset.text = s.text; d.dataset.depth = s.depth || "all"; } catch (e) { document.documentElement.dataset.depth = "all"; }
  </script>
  <script defer src="assets/vendor/prism.bundle.js"></script>
  <script defer src="assets/js/manifest.js"></script>
  <script defer src="assets/js/course.js"></script>
</head>
<body data-page="setup" data-root="">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <button class="icon-btn nav-toggle" type="button" aria-expanded="false" aria-controls="sidebar"><svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 5.5h14M3 10h14M3 14.5h14"></path></svg><span class="nav-toggle-label">Contents</span></button>
    <a class="brand" href="index.html"><span class="brand-prompt" aria-hidden="true">&gt;&gt;&gt;</span><span class="brand-name">Python for AI</span></a>
    <div class="site-search" role="search"></div>
    <div class="depth-control"></div>
    <div class="display-menu"></div>
    <button class="icon-btn theme-toggle" type="button" aria-label="Switch between light and dark theme"><svg aria-hidden="true" viewBox="0 0 20 20"><circle cx="10" cy="10" r="7.25" fill="none" stroke="currentColor" stroke-width="1.6"></circle><path d="M10 2.75a7.25 7.25 0 0 1 0 14.5z" fill="currentColor"></path></svg></button>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar"><nav class="course-nav" aria-label="Course contents"></nav></aside>
    <main id="main" class="content">
      <h1>Set up your computer</h1>
      <p class="lead">You will run every example and exercise of this course on your own computer, exactly as you will at work. This takes about 30 minutes, once.</p>

      <section id="what" data-level="essential">
        <h2>What you will install</h2>
        <ul>
          <li><strong>Python 3.15</strong>: the course is checked with it, and lessons use its new features (lazy imports, <code>frozendict</code>, <code>sentinel</code>, unpacking in comprehensions). Older versions run most of the code but not all of it.</li>
          <li><strong>An editor</strong>: Visual Studio Code with the Python extension is a good free choice; PyCharm, Zed or any editor you like also work.</li>
          <li><strong>pytest</strong> and the course's other code-quality tools: pytest checks your exercise solutions. Data, machine-learning and deep-learning libraries come later, one file per phase (<a href="#libraries">step 6</a>).</li>
        </ul>
      </section>

      <section id="python" data-level="essential">
        <h2>1. Install Python</h2>
        <h3 id="python-windows">Windows 10 or 11</h3>
        <ol>
          <li>Install the <strong>Python install manager</strong> from <a href="https://www.python.org/downloads/">python.org/downloads</a> or from the Microsoft Store app.</li>
          <li>Open <strong>Terminal</strong> (or PowerShell) and install Python 3.15:
            <script type="text/x-shell" data-label="PowerShell (Windows)">
            py install 3.15
            py list
            </script>
          </li>
          <li>If the installer offers to add a folder to your PATH, accept: it lets you type <code>python</code> as well as <code>py</code>.</li>
        </ol>
        <h3 id="python-macos">macOS</h3>
        <p>Download the macOS installer for Python 3.15 from <a href="https://www.python.org/downloads/">python.org/downloads</a> and run it. Afterwards use <code>python3</code> in the Terminal app (the plain <code>python</code> command may not exist).</p>
        <h3 id="python-linux">Linux</h3>
        <p>Your distribution's Python is probably older than 3.15. Check with <code>python3 --version</code>; if it is older, the quickest route is uv (below), or your distribution's newer packages.</p>
        <section id="python-uv" data-level="extra">
          <h3>Any system: uv</h3>
          <p><a href="https://docs.astral.sh/uv/">uv</a> is a fast tool that installs Python versions and packages without touching your system Python. After installing uv, run:</p>
          <script type="text/x-shell" data-label="Terminal">
          uv python install 3.15
          </script>
          <p>Then choose <strong>uv</strong> under "How you run Python" in <a href="index.html#settings">Settings</a>, and every command in the course will be shown in its uv form.</p>
        </section>
      </section>

      <section id="check" data-level="essential">
        <h2>2. Check that it works</h2>
        <p>Open a new terminal and run the command below. It should print <code>Python 3.15</code> followed by a patch number.</p>
        <script type="text/x-shell">
        {python} --version
        </script>
        <p>The command shown depends on your setting under "How you run Python" in <a href="index.html#settings">Settings</a>: <code>py</code> on Windows, <code>python3</code> on macOS and Linux, or uv. Change it once and every page follows.</p>
      </section>

      <section id="folder" data-level="essential">
        <h2>3. Make a course folder and a virtual environment</h2>
        <p>A <dfn id="term-venv">virtual environment</dfn> is a private copy of Python for one project, so the libraries you install for this course don't clash with anything else. Create a folder (for example <code>python-for-ai</code>), open a terminal in it, and run:</p>
        <script type="text/x-shell">
        {python} -m venv .venv
        </script>
        <p>Activate it every time you open a new terminal for the course:</p>
        <script type="text/x-shell" data-label="PowerShell (Windows)">
        .venv\Scripts\Activate.ps1
        </script>
        <script type="text/x-shell" data-label="Terminal (macOS and Linux)">
        source .venv/bin/activate
        </script>
        <p>Your prompt now starts with <code>(.venv)</code>. Download <a href="downloads/requirements-tools.txt" download>requirements-tools.txt</a> into the course folder: it lists pytest and the other tools of the course, each pinned to the version the course was checked with. Install them:</p>
        <script type="text/x-shell">
        {pip} install -r requirements-tools.txt
        </script>
        <aside class="callout" data-kind="pitfall">
          <p>On Windows, PowerShell may refuse to run <code>Activate.ps1</code> ("running scripts is disabled"). Run <code>Set-ExecutionPolicy -Scope CurrentUser RemoteSigned</code> once, then try again.</p>
        </aside>
      </section>

      <section id="first-run" data-level="essential">
        <h2>4. Run your first program</h2>
        <p>In your editor, create <code>hello.py</code> in the course folder:</p>
        <figure class="example" id="ex-hello">
          <script type="text/x-python" data-file="hello.py">
          import sys

          print("Hello from Python", sys.version_info.major, sys.version_info.minor)
          </script>
          <script type="text/x-output">
          Hello from Python 3 15
          </script>
        </figure>
        <p>Every example in the course shows the command to run it and the output to expect, like the one above. Experiment as well: change the code, predict the new output, run it again.</p>
        <p>You can also try single lines in the <strong>interactive shell</strong>: run <code>python</code> (or <code>py</code>, or <code>python3</code>) with no file name, type code after the <code>&gt;&gt;&gt;</code> prompt, and leave with <code>exit()</code>.</p>
      </section>

      <section id="exercises" data-level="essential">
        <h2>5. Check an exercise with pytest</h2>
        <ol>
          <li>On a lesson page, click <strong>Download the exercise pack</strong> and unzip it into your course folder. You get a folder such as <code>m03-l04</code> with starter files (<code>e1_word_freq.py</code>, ...) and their tests (<code>test_e1_word_freq.py</code>, ...).</li>
          <li>Open the starter file in your editor and write your solution.</li>
          <li>In the terminal, go into the folder and run the tests for that exercise:
            <script type="text/x-shell">
            cd m03-l04
            {pytest} test_e1_word_freq.py
            </script>
          </li>
          <li>Read the first failure: pytest shows the line that failed and the values it compared. Fix, save, run again.</li>
          <li>When a whole test file passes, pytest prints a <strong>completion code</strong> such as <code>5F2A-91C3</code>. Paste it into the exercise on the lesson page to record it as passed.</li>
        </ol>
        <aside class="callout" data-kind="tip">
          <p>Run plain <code>pytest</code> (no file name) to check every exercise in the pack at once; add <code>-x</code> to stop at the first failure.</p>
        </aside>
      </section>

      <section id="libraries" data-level="essential">
        <h2>6. Install the course libraries, phase by phase</h2>
        <p>Each file below pins its libraries to the exact versions the course was checked with on Python 3.15, so your output matches the pages. When you reach a phase, download its file into the course folder and install it into the same virtual environment. Install them in this order: each file adds to the ones before it.</p>
        <div class="table-wrap">
          <table>
            <caption>Requirements files of the course</caption>
            <thead><tr><th scope="col">File</th><th scope="col">When</th><th scope="col">What it adds</th></tr></thead>
            <tbody>
              <tr><td><a href="downloads/requirements-tools.txt" download>requirements-tools.txt</a></td><td>From the start (step 3)</td><td>pytest, pytest-cov, Hypothesis, ruff, mypy, pre-commit</td></tr>
              <tr><td><a href="downloads/requirements-core.txt" download>requirements-core.txt</a></td><td>Phase 3 (data science)</td><td>NumPy, pandas, PyArrow, Polars, DuckDB, Matplotlib, seaborn, Plotly, Altair, SciPy, statsmodels, scikit-learn, JupyterLab, requests, httpx, Beautiful Soup, lxml, pydantic, SQLAlchemy, pandera, PyYAML, python-dotenv, rich</td></tr>
              <tr><td><a href="downloads/requirements-ml.txt" download>requirements-ml.txt</a></td><td>Phase 4 (machine learning)</td><td>XGBoost, LightGBM, SHAP, Optuna, imbalanced-learn, UMAP, MLflow</td></tr>
              <tr><td><a href="downloads/requirements-deep-learning.txt" download>requirements-deep-learning.txt</a></td><td>Phase 5 (deep learning and LLM apps)</td><td>PyTorch, torchvision, transformers, datasets, tokenizers, tiktoken, sentence-transformers, FAISS, bm25s, the Anthropic and OpenAI SDKs, MCP</td></tr>
              <tr><td><a href="downloads/requirements-production.txt" download>requirements-production.txt</a></td><td>Phase 6 (production)</td><td>FastAPI, Uvicorn, Streamlit, Gradio, skops, ONNX, skl2onnx, River, Locust, DVC</td></tr>
              <tr><td><a href="downloads/requirements-electives.txt" download>requirements-electives.txt</a></td><td>Electives, after Phase 3</td><td>Prophet, OpenCV, Gymnasium, NetworkX, GeoPandas, Shapely, PySpark</td></tr>
            </tbody>
          </table>
        </div>
        <p>For example, at the start of Phase 3:</p>
        <script type="text/x-shell">
        {pip} install -r requirements-core.txt
        </script>
        <aside class="callout" data-kind="pitfall">
          <p>On Linux, the standard PyTorch package also downloads NVIDIA's CUDA libraries, about 4 GB. Every graded exercise runs on the CPU, so without an NVIDIA graphics card, first install PyTorch with the CPU-only command from <a href="https://pytorch.org/get-started/locally/">pytorch.org</a>, then install <code>requirements-deep-learning.txt</code>.</p>
        </aside>
        <aside class="callout" data-kind="note">
          <p>Every pinned library installs from ready-made packages (wheels) on Windows 10 or 11 (x64), on macOS 15 or later with Apple silicon, and on Linux with glibc 2.39 or later, such as Ubuntu 24.04. The exceptions:</p>
          <ul>
            <li><strong>Windows:</strong> FAISS (Phase 5) has no Windows packages. <code>requirements-deep-learning.txt</code> skips it there, and the FAISS part of lesson M23-L05 runs in WSL 2.</li>
            <li><strong>Intel Macs:</strong> PyTorch (Phase 5) has no packages for them. Use a Linux virtual machine or another computer for Phase 5.</li>
            <li><strong>Older Linux:</strong> pip has to build orjson, which Gradio needs in Phase 6, from source with the Rust compiler. A newer distribution, or WSL 2 with Ubuntu 24.04, avoids that.</li>
          </ul>
        </aside>
        <aside class="callout" data-kind="note">
          <p>PySpark (elective E4) also needs Java 17 or later. Start it from the activated environment: its worker processes run the <code>python3</code> on your PATH, and a different Python version stops them with <code>PYTHON_VERSION_MISMATCH</code>.</p>
        </aside>
        <aside class="callout" data-kind="tip">
          <p>Libraries you try outside the course may not support Python 3.15 yet (pip finds no matching version, or starts compiling C code). Give that experiment its own virtual environment with an older Python, for example <code>uv venv --python 3.14</code>, rather than changing the course environment.</p>
        </aside>
      </section>

      <section id="notebooks" data-level="extra">
        <h2>Notebooks and GPUs (later in the course)</h2>
        <p>Data-science lessons use Jupyter notebooks for exploration. Run them locally with <code>python -m jupyter lab</code> after installing <code>requirements-core.txt</code>, or open the <code>.ipynb</code> file in VS Code.</p>
        <p>Every graded exercise runs on an ordinary laptop CPU. A few optional deep-learning experiments train faster on a GPU; if you don't have one, any hosted notebook service you choose will run the same notebook files.</p>
      </section>

      <section id="troubleshooting" data-level="essential">
        <h2>Troubleshooting</h2>
        <div class="table-wrap">
          <table>
            <caption>Common problems and fixes</caption>
            <thead><tr><th scope="col">You see</th><th scope="col">Fix</th></tr></thead>
            <tbody>
              <tr><td><code>python: command not found</code> or <code>'python' is not recognized</code></td><td>Use <code>python3</code> (macOS, Linux) or <code>py</code> (Windows), and set the matching option in <a href="index.html#settings">Settings</a>. Open a new terminal after installing.</td></tr>
              <tr><td>Windows opens the Microsoft Store when you type <code>python</code></td><td>Install the Python install manager (step 1), or turn off the "App execution aliases" for python in Windows settings.</td></tr>
              <tr><td><code>pytest: command not found</code></td><td>Run it through Python: <code>python -m pytest</code>. Check the virtual environment is active.</td></tr>
              <tr><td><code>ModuleNotFoundError: No module named 'e1_word_freq'</code></td><td>Run pytest from inside the pack folder, and keep the starter file's name unchanged.</td></tr>
              <tr><td><code>ModuleNotFoundError: No module named 'pandas'</code> (or another library)</td><td>Activate the virtual environment, then install the requirements file of that phase (<a href="#libraries">step 6</a>), for example <code>python -m pip install -r requirements-core.txt</code>.</td></tr>
              <tr><td><code>No matching distribution found</code>, or pip starts compiling a library</td><td>Check that <code>python --version</code> shows 3.15 inside the active virtual environment. The course's files only list libraries that install on 3.15; for other libraries, see the tip in <a href="#libraries">step 6</a>.</td></tr>
              <tr><td>VS Code runs a different Python</td><td>Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>, choose "Python: Select Interpreter" and pick the one in <code>.venv</code>.</td></tr>
              <tr><td>Your output differs slightly from the page</td><td>Check your Python and library versions; outputs on the pages come from the versions in the requirements files (<a href="#libraries">step 6</a>). Random numbers and timings differ on purpose and are labelled "Sample output".</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</body>
</html>
````

## 7. `tools/pagekit.py`

````python
"""pagekit: read course pages for the build and check tools (standard library only).

Course pages are strict HTML: every non-void element is closed explicitly, so a small parser can
build a full tree, report the exact source offsets of every <script>, and let tools rewrite
script contents in place (check_content.py --update-outputs).
"""
from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
RAW_TEXT = {"script", "style"}
LEVELS = ("essential", "extra", "advanced")
LEVEL_RANK = {name: rank for rank, name in enumerate(LEVELS)}
LEVEL_LABELS = {"essential": "Essential", "extra": "Extra info", "advanced": "Advanced"}
KINDS = {
    "tip": "Tip", "pitfall": "Common mistake", "version": "Version note", "interview": "Interview",
    "job": "On the job", "hood": "Under the hood", "try": "Try it yourself", "deprecated": "Deprecated",
    "performance": "Performance", "security": "Security", "note": "Note",
}
CHANGES = {"added", "changed", "deprecated", "removed"}
CODE_TYPES = {"text/x-python", "text/x-output", "text/x-pycon", "text/x-shell", "text/x-stdin", "text/x-file",
              "text/x-code", "application/json"}
EXERCISE_KINDS = {"function", "program", "fix", "refactor", "write_tests"}


def dedent(text: str) -> str:
    """Normalise the text of a <script> code block. course.js implements the same rules.

    If the last line (the one holding </script>) is whitespace-only, its width is the base indent;
    otherwise the common indent of the non-blank lines is used. Each line loses at most the base
    indent, trailing whitespace is dropped, and so are blank lines at the start and the end.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    base = None
    if len(lines) > 1 and lines[-1].strip(" ") == "":
        base = len(lines[-1])
        lines = lines[:-1]
    lines = [line.rstrip() for line in lines]
    if base is None:
        base = min((len(line) - len(line.lstrip(" ")) for line in lines if line), default=0)
    out = [line[min(base, len(line) - len(line.lstrip(" "))):] for line in lines]
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


@dataclass(eq=False)
class Node:
    tag: str
    attrs: dict
    parent: Node | None
    line: int
    start: int
    children: list = field(default_factory=list)  # Node or str, in document order
    content_start: int = -1  # raw-text elements only: offsets of the text between the tags
    content_end: int = -1

    def get(self, name: str, default=None):
        return self.attrs.get(name, default)

    @property
    def classes(self) -> set[str]:
        return set((self.attrs.get("class") or "").split())

    def has_class(self, name: str) -> bool:
        return name in self.classes

    def iter(self):
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed([c for c in node.children if isinstance(c, Node)]))

    def elements(self):
        return [c for c in self.children if isinstance(c, Node)]

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def closest(self, predicate):
        return next((a for a in self.ancestors() if predicate(a)), None)

    def text(self) -> str:
        parts = []
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
            elif child.tag not in RAW_TEXT:
                parts.append(child.text())
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def describe(self) -> str:
        ident = f"#{self.attrs['id']}" if self.attrs.get("id") else ""
        return f"<{self.tag}{ident}> line {self.line}"


class _Parser(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_starts = [0] + [m.end() for m in re.finditer("\n", source)]
        self.root = Node("#document", {}, None, 1, 0)
        self.stack = [self.root]
        self.errors: list[str] = []

    def abs_pos(self) -> int:
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        names = [name for name, _ in attrs]
        if len(names) != len(set(names)):
            self.errors.append(f"line {self.getpos()[0]}: duplicate attribute on <{tag}>")
        node = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.stack[-1],
                    self.getpos()[0], self.abs_pos())
        self.stack[-1].children.append(node)
        if tag in RAW_TEXT:
            node.content_start = node.start + len(self.get_starttag_text())
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID:
            self.errors.append(f"line {self.getpos()[0]}: <{tag}/> is not a void element; close it with </{tag}>")
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        line = self.getpos()[0]
        if tag in VOID:
            self.errors.append(f"line {line}: </{tag}> closes a void element")
            return
        if self.stack[-1].tag == tag:
            node = self.stack.pop()
        elif any(n.tag == tag for n in self.stack[1:]):
            self.errors.append(f"line {line}: </{tag}> closes <{self.stack[-1].tag}> opened on line {self.stack[-1].line}")
            while self.stack[-1].tag != tag:
                self.stack.pop()
            node = self.stack.pop()
        else:
            self.errors.append(f"line {line}: stray </{tag}>")
            return
        if tag in RAW_TEXT:
            node.content_end = self.abs_pos()

    def handle_data(self, data):
        if self.stack[-1].tag not in RAW_TEXT:
            self.stack[-1].children.append(data)

    def close(self):
        super().close()
        for node in self.stack[1:]:
            self.errors.append(f"line {node.line}: <{node.tag}> is never closed")


class Page:
    def __init__(self, path: Path | str, source: str | None = None):
        self.path = Path(path)
        self.source = source if source is not None else self.path.read_text(encoding="utf-8")
        parser = _Parser(self.source)
        parser.feed(self.source)
        parser.close()
        self.root = parser.root
        self.errors = parser.errors
        self._line_starts = parser.line_starts

    # ------------------------------------------------------------------ queries
    def all(self, tag: str | None = None, cls: str | None = None, **attrs):
        out = []
        for node in self.root.iter():
            if node is self.root or (tag and node.tag != tag) or (cls and not node.has_class(cls)):
                continue
            if all((node.get(k.replace("_", "-")) == v) if v is not True else (k.replace("_", "-") in node.attrs)
                   for k, v in attrs.items()):
                out.append(node)
        return out

    def first(self, tag=None, cls=None, **attrs):
        found = self.all(tag, cls, **attrs)
        return found[0] if found else None

    @property
    def body(self) -> Node | None:
        return self.first("body")

    @property
    def kind(self) -> str:
        return (self.body.get("data-page") if self.body else None) or "page"

    def ids(self) -> dict[str, Node]:
        return {n.attrs["id"]: n for n in self.root.iter() if n.attrs.get("id")}

    def raw(self, node: Node) -> str:
        return self.source[node.content_start:node.content_end]

    def code(self, node: Node) -> str:
        return dedent(self.raw(node))

    def scripts(self, type_: str | None = None) -> list[Node]:
        return [n for n in self.all("script") if type_ is None or n.get("type") == type_]

    def line_of(self, offset: int) -> int:
        return bisect.bisect_right(self._line_starts, offset)

    @staticmethod
    def level_of(node: Node) -> str | None:
        for candidate in (node, *node.ancestors()):
            if candidate.get("data-level"):
                return candidate.get("data-level")
        return None


def replace_scripts(page: Page, replacements: dict[Node, str]) -> str:
    """Return page.source with the given <script> nodes' text replaced by `text` (dedented form).

    The new text is indented to the width of the existing closing line (or the <script> line),
    so the rewritten block reads exactly like a hand-written one.
    """
    source = page.source
    for node, text in sorted(replacements.items(), key=lambda item: -item[0].content_start):
        raw = page.raw(node)
        last = raw.replace("\r\n", "\n").split("\n")[-1]
        if "\n" in raw and last.strip(" ") == "":
            base = len(last)
        else:
            line_start = page._line_starts[page.line_of(node.start) - 1]
            base = len(source[line_start:node.start]) - len(source[line_start:node.start].lstrip(" "))
        pad = " " * base
        body = "\n".join((pad + line) if line else "" for line in text.split("\n"))
        source = source[:node.content_start] + "\n" + body + "\n" + pad + source[node.content_end:]
    return source


def site_pages(site: Path) -> list[Path]:
    return sorted(p for p in site.rglob("*.html") if "assets" not in p.relative_to(site).parts)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def api_id(name: str) -> str:
    """Anchor id of a reference row: api- + its first data-api name, dots as dashes (dict.get -> api-dict-get)."""
    return "api-" + re.sub(r"[^A-Za-z0-9_-]+", "-", name.replace(":", "-").replace(".", "-")).strip("-")


def root_prefix(site: Path, page: Path) -> str:
    """The data-root value a page needs: "" at the site root, "../../" two folders down."""
    return "../" * (len(page.relative_to(site).parts) - 1)
````

## 8. `tools/packs.py`

````python
"""Exercise packs: the single definition of which files an exercise produces.

check_content.py builds the "solution" variant to prove the tests pass, and the "starter" variant to
prove they fail before the learner starts; export_exercises.py zips the starter variant for learners.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pagekit import Node, Page

LEARNER = Path(__file__).resolve().parent / "learner"
SHARED_FILES = ("conftest.py", "course_helpers.py", "course_mocks.py")
TESTED_ON = "3.15"


@dataclass
class Exercise:
    page: Page
    node: Node
    id: str
    title: str
    kind: str
    file: str
    optional: bool
    roles: dict[str, str] = field(default_factory=dict)  # starter/tests/solution/target -> code
    mutants: dict[str, str] = field(default_factory=dict)
    data_files: dict[str, str] = field(default_factory=dict)

    @property
    def stem(self) -> str:
        return self.file.removesuffix(".py")

    @property
    def test_file(self) -> str:
        """The file whose full pass earns the completion code."""
        return f"test_{self.stem}_check.py" if self.kind == "write_tests" else f"test_{self.file}"

    def files(self, variant: str) -> dict[str, str]:
        """Files for one exercise. variant: "starter" (what learners get) or "solution"."""
        files = dict(self.data_files)
        if self.kind == "write_tests":
            files[self.file] = self.roles["target"]
            files[f"test_{self.file}"] = self.roles[variant] + "\n"
            files[f"{self.stem}_mutants.json"] = json.dumps(self.mutants, indent=2) + "\n"
            files[self.test_file] = (
                f'"""Checks YOUR tests in test_{self.file}: they must pass on {self.file} and catch every bug."""\n'
                "from course_helpers import check_tests\n\n\n"
                "def test_your_tests_catch_every_bug():\n"
                f'    check_tests("test_{self.file}", module="{self.stem}", mutants="{self.stem}_mutants.json")\n')
        else:
            files[self.file] = self.roles[variant] + "\n"
            files[self.test_file] = self.roles["tests"] + "\n"
        return files


def exercises(page: Page) -> list[Exercise]:
    out = []
    for node in page.all("article", cls="exercise"):
        heading = next((n for n in node.iter() if n.tag in ("h3", "h4")), None)
        ex = Exercise(page, node, node.get("id", ""), heading.text() if heading else node.get("id", ""),
                      node.get("data-kind", "function"), node.get("data-file", ""), "data-optional" in node.attrs)
        for script in (n for n in node.iter() if n.tag == "script"):
            role, kind = script.get("data-role"), script.get("type")
            if kind == "text/x-file":
                ex.data_files[script.get("data-name", "")] = page.code(script) + "\n"
            elif role == "mutants":
                ex.mutants = json.loads(page.raw(script))
            elif role:
                ex.roles[role] = page.code(script)
        out.append(ex)
    return out


def pack_files(page: Page, lesson_title: str, lesson_url: str) -> dict[str, str]:
    """All files of a lesson's pack (starter variant), keyed by path inside the pack folder."""
    lesson = page.body.get("data-lesson-id")
    items = exercises(page)
    files: dict[str, str] = {}
    for ex in items:
        for name, text in ex.files("starter").items():
            if name in files and files[name] != text:
                raise ValueError(f"{lesson}: two exercises write different {name}")
            files[name] = text
    for name in SHARED_FILES:
        files[name] = (LEARNER / name).read_text(encoding="utf-8")
    meta = {"lesson": lesson, "title": lesson_title, "python": TESTED_ON,
            "exercises": [{"id": ex.id, "title": ex.title, "file": ex.file, "tests": ex.test_file,
                           "optional": ex.optional} for ex in items]}
    files["pack.json"] = json.dumps(meta, indent=2) + "\n"
    lines = [f"# {lesson.upper()} · {lesson_title} — exercise pack", "",
             f"Lesson page: {lesson_url}", "",
             "## How to work on these exercises", "",
             "1. Open this folder in your editor and in a terminal (see the course setup page).",
             "2. Install pytest once per environment: `python -m pip install pytest`",
             "3. Run every exercise's tests: `python -m pytest`",
             "   or a single exercise: `python -m pytest test_e1_....py`",
             "4. Edit the `eN_*.py` files until their tests pass. When a whole test file passes, pytest",
             "   prints a completion code: paste it into the exercise on the lesson page.", "",
             "On Windows use `py` instead of `python`; with uv use `uv run --with pytest pytest`.", "",
             "## Exercises", ""]
    for ex in items:
        extra = " (optional)" if ex.optional else ""
        edit = f"test_{ex.file}" if ex.kind == "write_tests" else ex.file
        lines.append(f"- **{ex.id}** {ex.title}{extra}: edit `{edit}`, check with `python -m pytest {ex.test_file}`")
    files["README.md"] = "\n".join(lines) + "\n"
    return dict(sorted(files.items()))
````

## 9. `tools/check_site.py`

````python
"""Static checks for every page: structure, accessibility, markers, reference rows, links, manifest.

  python tools/check_site.py            # all pages under site/
  python tools/check_site.py PAGE...    # some pages (links to other pages are still checked)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pagekit import (
    CHANGES,
    CODE_TYPES,
    EXERCISE_KINDS,
    KINDS,
    LEVEL_RANK,
    LEVELS,
    Page,
    api_id,
    root_prefix,
    site_pages,
)

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PAGE_KINDS = {"home", "lesson", "setup", "reference", "project", "exam", "index"}
SCRIPTS = ["assets/vendor/prism.bundle.js", "assets/js/manifest.js", "assets/js/course.js"]
SPECIAL_SECTIONS = {"outcomes", "run-locally", "api-reference", "exercises", "quiz", "summary", "next-steps"}
TOKENS = {"python", "pytest", "pip"}
MAX_MINOR = 15


def load_manifest(site: Path) -> dict:
    text = (site / "assets/js/manifest.js").read_text(encoding="utf-8")
    match = re.search(r"^window\.COURSE = (\{.*\});\s*$", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit("manifest.js must contain one line: window.COURSE = {...};")
    return json.loads(match.group(1))


def planned_files(site: Path, manifest: dict) -> set[Path]:
    return {(site / m["path"] / l["file"]).resolve() for m in manifest["modules"] for l in m["lessons"] if l.get("planned")}


def check_page(page: Page, site: Path, manifest: dict, cache: dict) -> list[str]:
    errs: list[str] = [f"structure: {e}" for e in page.errors]
    add = errs.append
    rel = page.path.relative_to(site).as_posix()
    html_el, body = page.first("html"), page.body
    if not page.source.lstrip().lower().startswith("<!doctype html>"):
        add("must start with <!doctype html>")
    if html_el is None or not html_el.get("lang"):
        add('<html> needs lang="en"')
    if not page.first("meta", charset="utf-8"):
        add('missing <meta charset="utf-8">')
    if not page.first("meta", name="viewport"):
        add("missing viewport meta")
    title = page.first("title")
    if title is None or not title.text():
        add("missing <title>")
    if body is None:
        return errs + ["missing <body>"]
    kind = body.get("data-page")
    if kind not in PAGE_KINDS:
        add(f"body data-page must be one of {sorted(PAGE_KINDS)}")
    prefix = root_prefix(site, page.path)
    if body.get("data-root") != prefix:
        add(f'body data-root must be "{prefix}"')
    srcs = [n.get("src") for n in page.all("script") if n.get("src")]
    if [s.removeprefix(prefix) for s in srcs] != SCRIPTS:
        add(f"scripts must be exactly {SCRIPTS} (relative to data-root), in that order")
    for node in page.all("script"):
        if node.get("src") and "defer" not in node.attrs:
            add(f"{node.describe()}: external scripts need defer")
        if node.get("type") == "module":
            add(f"{node.describe()}: no ES modules (pages must work from file://)")
        if not node.get("src") and node.get("type") not in CODE_TYPES and node.parent.tag != "head":
            add(f"{node.describe()}: unknown script type {node.get('type')!r}")
    if not page.first("link", rel="stylesheet"):
        add("missing course.css stylesheet")

    ids = {}
    for node in page.root.iter():
        for attr in node.attrs:
            if attr.startswith("on"):
                add(f"{node.describe()}: inline event handler {attr}= (use course.js)")
        if (ident := node.get("id")) is not None:
            if not re.fullmatch(r"[A-Za-z][\w.:-]*", ident):
                add(f"{node.describe()}: invalid id {ident!r}")
            if ident in ids:
                add(f"duplicate id {ident!r} (lines {ids[ident].line} and {node.line})")
            ids[ident] = node

    # headings: one h1, no skipped levels
    heads = [n for n in page.root.iter() if re.fullmatch(r"h[1-6]", n.tag)]
    if sum(1 for n in heads if n.tag == "h1") != 1:
        add("exactly one <h1> per page")
    last = 0
    for n in heads:
        level = int(n.tag[1])
        if level > last + 1:
            add(f"{n.describe()}: heading skips from h{last} to h{level}")
        last = level
        if not n.text():
            add(f"{n.describe()}: empty heading")

    # images, links
    for img in page.all("img"):
        if "alt" not in img.attrs:
            add(f"{img.describe()}: missing alt")
        elif not img.get("src", "").startswith(("http", "data:")) and not (page.path.parent / img.get("src", "")).exists():
            add(f"{img.describe()}: image not found: {img.get('src')}")
    for a in page.all("a"):
        href = a.get("href")
        if href is None:
            add(f"{a.describe()}: <a> without href")
            continue
        if not a.text() and not a.get("aria-label"):
            add(f"{a.describe()}: link without text")
        if a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
            add(f"{a.describe()}: target=_blank needs rel=noopener")
        parts = urlsplit(href)
        if parts.scheme or href.startswith(("//", "mailto:")):
            continue
        target = (page.path.parent / unquote(parts.path)).resolve() if parts.path else page.path
        if parts.path and not target.exists():
            if target in cache.setdefault("planned", planned_files(site, manifest)):
                continue  # a lesson listed in course.json as planned: allowed, shown as "coming soon"
            if not (a.get("data-pack") is not None and target.suffix == ".zip"):  # packs appear after build
                add(f"{a.describe()}: broken link {href}")
            continue
        if parts.fragment and target.suffix == ".html":
            other = cache.setdefault(target, Page(target) if target != page.path else page)
            if parts.fragment not in other.ids() and parts.fragment not in ("main", "top"):
                add(f"{a.describe()}: missing anchor #{parts.fragment} in {target.name}")

    # levels and markers
    for node in page.root.iter():
        level = node.get("data-level")
        if level is None:
            continue
        if level not in LEVELS:
            add(f"{node.describe()}: data-level must be one of {LEVELS}")
            continue
        outer = next((a.get("data-level") for a in node.ancestors() if a.get("data-level") in LEVEL_RANK), None)
        if outer and LEVEL_RANK[level] < LEVEL_RANK[outer]:
            add(f"{node.describe()}: {level} content inside {outer} content (a child can't be more essential)")
    main = page.first("main")
    if kind == "lesson" and main is not None:
        for sec in main.elements():
            if sec.tag == "section" and not (sec.classes & SPECIAL_SECTIONS) and not sec.get("data-level"):
                add(f"{sec.describe()}: content sections need data-level ({'/'.join(LEVELS)})")
            if sec.tag == "section" and not sec.get("id"):
                add(f"{sec.describe()}: sections need an id (for links and the table of contents)")
    for aside in page.all("aside", cls="callout"):
        if aside.get("data-kind") not in KINDS:
            add(f"{aside.describe()}: callout data-kind must be one of {sorted(KINDS)}")
        if aside.get("data-kind") == "version" and not aside.get("data-version"):
            add(f"{aside.describe()}: version callouts need data-version")
    for node in page.root.iter():
        version = node.get("data-version")
        if version is not None and not re.fullmatch(rf"3\.(\d|1[0-{MAX_MINOR - 10}])", version):
            add(f"{node.describe()}: data-version must look like 3.12 (3.0-3.{MAX_MINOR})")
    for span in page.all("span", cls="version"):
        if span.get("data-change") not in CHANGES or not span.get("data-version"):
            add(f"{span.describe()}: span.version needs data-version and data-change ({'/'.join(sorted(CHANGES))})")

    # reference rows
    for node in page.root.iter():
        names = (node.get("data-api") or "").split()
        if not node.get("data-api") and "data-api" not in node.attrs:
            continue
        if not names:
            add(f"{node.describe()}: empty data-api")
            continue
        if not node.closest(lambda a: a.has_class("api-reference")):
            add(f"{node.describe()}: data-api rows belong inside section.api-reference")
        if node.get("id") != api_id(names[0]):
            add(f"{node.describe()}: id must be {api_id(names[0])!r}")
        if node.get("data-level") not in LEVELS and not any(a.get("data-level") for a in node.ancestors()):
            add(f"{node.describe()}: reference rows need data-level")
        if node.text().startswith("TODO") or "TODO " in node.text():
            add(f"{node.describe()}: unfinished row (TODO)")
    for sec in page.all("section", cls="api-reference"):
        if not sec.get("data-api-targets") and not sec.get("data-api-free"):
            add(f"{sec.describe()}: api-reference sections declare data-api-targets")
        for table in (n for n in sec.iter() if n.tag == "table"):
            heads = [n for n in table.iter() if n.tag == "th"]
            if not heads or any(th.get("scope") not in ("col", "row") for th in heads):
                add(f"{table.describe()}: table headers need scope=col/row")
            if not any(n.tag == "caption" for n in table.iter()):
                add(f"{table.describe()}: tables need a <caption>")

    # code blocks
    for node in page.all("script"):
        stype = node.get("type")
        holder = node.parent
        if stype == "text/x-output" and not (holder.has_class("example") and any(
                n.get("type") == "text/x-python" for n in holder.elements())):
            add(f"{node.describe()}: x-output belongs in figure.example next to its x-python")
        if stype in ("text/x-stdin", "text/x-file") and not (holder.has_class("example") or holder.has_class("exercise")):
            add(f"{node.describe()}: {stype} belongs in figure.example or article.exercise")
        if stype == "text/x-file" and not node.get("data-name"):
            add(f"{node.describe()}: x-file needs data-name")
        if stype == "text/x-shell":
            for token in re.findall(r"\{(\w+)\}", page.raw(node)):
                if token not in TOKENS:
                    add(f"{node.describe()}: unknown command token {{{token}}} (use {sorted(TOKENS)})")
        if stype == "text/x-code" and not node.get("data-lang"):
            add(f"{node.describe()}: x-code needs data-lang")
        if "\t" in page.raw(node):
            add(f"{node.describe()}: tabs in code (use spaces)")
    for fig in page.all("figure", cls="example"):
        n_py = sum(1 for n in fig.elements() if n.get("type") == "text/x-python")
        if n_py != 1:
            add(f"{fig.describe()}: an example has exactly one x-python block")
        if fig.get("data-raises") and not re.fullmatch(r"[A-Z]\w*(Error|Exception|Warning|Exit|Interrupt|Group)?", fig.get("data-raises")):
            add(f"{fig.describe()}: data-raises must be an exception class name")

    # lesson parts
    lesson_id = body.get("data-lesson-id")
    if kind == "lesson":
        lessons = {l["id"]: (m, l) for m in manifest["modules"] for l in m["lessons"]}
        if lesson_id not in lessons:
            add(f"lesson id {lesson_id!r} is not in course.json")
        else:
            m, l = lessons[lesson_id]
            if f"{m['path']}{l['file']}" != rel:
                add(f"course.json says {lesson_id} lives at {m['path']}{l['file']}, not {rel}")
        if not page.first("meta", name="description"):
            add("lesson pages need <meta name=description>")
        for cls in ("outcomes", "run-locally", "summary"):
            if not page.first("section", cls=cls):
                add(f"lesson pages need section.{cls}")
        run = page.first("section", cls="run-locally")
        if run and page.first("article", cls="exercise"):
            packs = [a for a in run.iter() if a.tag == "a" and "data-pack" in a.attrs]
            if not packs or packs[0].get("href") != f"{prefix}downloads/{lesson_id}.zip":
                add(f"section.run-locally needs <a data-pack href=\"{prefix}downloads/{lesson_id}.zip\">")
    numbers = []
    for ex in page.all("article", cls="exercise"):
        ident, file = ex.get("id", ""), ex.get("data-file", "")
        match = re.fullmatch(rf"{re.escape(lesson_id or '')}-e(\d+)", ident)
        if not match:
            add(f"{ex.describe()}: exercise ids are {lesson_id}-eN")
        else:
            numbers.append(int(match.group(1)))
            if not re.fullmatch(rf"e{match.group(1)}_[a-z0-9_]+\.py", file):
                add(f"{ex.describe()}: data-file must be e{match.group(1)}_<name>.py")
        if ex.get("data-kind") not in EXERCISE_KINDS:
            add(f"{ex.describe()}: data-kind must be one of {sorted(EXERCISE_KINDS)}")
        roles = [n.get("data-role") for n in ex.iter() if n.tag == "script" and n.get("data-role")]
        need = {"starter", "solution"} | ({"target", "mutants"} if ex.get("data-kind") == "write_tests" else {"tests"})
        if set(need) - set(roles) or len(roles) != len(set(roles)):
            add(f"{ex.describe()}: needs exactly one script for each of {sorted(need)}")
        if not any(n.tag == "ol" and n.has_class("hints") for n in ex.iter()):
            add(f"{ex.describe()}: add an <ol class=\"hints\"> (2-3 graded hints)")
        if not any(n.tag in ("h3", "h4") for n in ex.iter()):
            add(f"{ex.describe()}: exercise needs a heading")
    if numbers and sorted(numbers) != list(range(1, len(numbers) + 1)):
        add("exercises must be numbered e1, e2, ... without gaps")
    for quiz in page.all("section", cls="quiz"):
        if quiz.get("id") not in (f"{lesson_id}-quiz", f"{lesson_id}-warmup"):
            add(f"{quiz.describe()}: quiz id must be {lesson_id}-quiz (or {lesson_id}-warmup for the opening retrieval quiz)")
    if kind == "lesson":
        kinds = {a.get("data-kind") for a in page.all("aside", cls="callout")}
        for needed in ("pitfall", "job", "interview"):
            if needed not in kinds:
                add(f"lesson pages need at least one {needed!r} callout (spec/06 §5)")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pages", nargs="*", type=Path)
    ap.add_argument("--site", type=Path, default=SITE)
    args = ap.parse_args(argv)
    site = args.site.resolve()
    manifest = load_manifest(site)
    paths = [p.resolve() for p in args.pages] or site_pages(site)
    cache: dict = {}
    total = 0
    for path in paths:
        page = cache.setdefault(path, Page(path))
        for err in check_page(page, site, manifest, cache):
            print(f"{path.relative_to(site)}: {err}")
            total += 1
    known = {f"{m['path']}{l['file']}" for m in manifest["modules"] for l in m["lessons"] if not l.get("planned")}
    if not args.pages:
        for rel in sorted(known):
            if not (site / rel).exists():
                print(f"course.json: lesson file {rel} does not exist")
                total += 1
    print(f"check_site: {len(paths)} page(s), {total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 10. `tools/check_content.py`

````python
"""Verify every piece of code on the course pages by running it with real Python.

  python tools/check_content.py                     # all pages under site/
  python tools/check_content.py site/modules/m03-data-structures/l04-dictionaries.html
  python tools/check_content.py --update-outputs    # rewrite x-output blocks from real runs
  python tools/check_content.py -j 8 --skip-missing # parallel; skip examples whose libraries are absent

Checks: x-python blocks compile; examples (figure.example) print exactly their x-output, twice, under
two hash seeds; x-pycon sessions pass doctest; exercise tests pass on the solution and fail on the
starter (write_tests: catch every mutant); quiz specs are valid and predict answers match real output.
"""
from __future__ import annotations

import argparse
import difflib
import doctest
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packs import LEARNER, SHARED_FILES, exercises
from pagekit import Node, Page, dedent, replace_scripts, site_pages

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SEEDS = ("0", "1")

HARNESS = r'''
import builtins, doctest, os, runpy, sys, traceback
sys.path[0] = os.getcwd()  # import helper files that sit next to the example, like `python example.py` would
sys.stderr = sys.stdout  # interleave like a terminal does
def _input(prompt=""):
    sys.stdout.write(str(prompt))
    line = sys.stdin.readline()
    if not line:
        raise EOFError("EOF when reading a line")
    line = line.rstrip("\n")
    print(line)  # a terminal echoes what you type
    return line
builtins.input = _input
mode, path = sys.argv[1], sys.argv[2]
if mode == "pycon":
    flags = doctest.ELLIPSIS if sys.argv[3] == "ellipsis" else 0
    text = open(path, encoding="utf-8").read()
    test = doctest.DocTestParser().get_doctest(text, {"__name__": "__main__"}, "session", path, 0)
    runner = doctest.DocTestRunner(verbose=False, optionflags=flags | doctest.REPORT_UDIFF)
    result = runner.run(test, out=sys.stdout.write, clear_globs=True)
    sys.exit(1 if result.failed else 0)
sys.argv = [path, *sys.argv[3:]]
try:
    runpy.run_path(path, run_name="__main__")
except SystemExit:
    raise
except BaseException as exc:
    sys.stdout.flush()
    print("Traceback (most recent call last):\n  ...")
    print("".join(traceback.format_exception_only(exc)), end="")
    sys.exit(1)
'''


def normalize(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n")


@dataclass
class Problem:
    page: Page
    node: Node
    message: str

    def __str__(self) -> str:
        return f"{self.page.path.relative_to(ROOT) if self.page.path.is_relative_to(ROOT) else self.page.path}:{self.node.line}: {self.message}"


@dataclass
class Report:
    problems: list[Problem] = field(default_factory=list)
    updates: dict = field(default_factory=dict)  # Page -> {node: new text}
    counts: dict = field(default_factory=lambda: {"compiled": 0, "examples": 0, "sessions": 0,
                                                  "exercises": 0, "quizzes": 0, "skipped": 0})


class Checker:
    def __init__(self, python: str, jobs: int, skip_missing: bool, update: bool):
        self.python, self.jobs, self.skip_missing, self.update = python, jobs, skip_missing, update
        self.report = Report()
        self.tmp = Path(tempfile.mkdtemp(prefix="course-check-"))
        (self.tmp / "harness.py").write_text(HARNESS, encoding="utf-8")
        self.missing_cache: dict[str, bool] = {}
        out = subprocess.run([python, "-c", "import sys; print(*sys.version_info[:2])"], capture_output=True, text=True,
                             check=True)
        self.version = tuple(int(x) for x in out.stdout.split())

    def too_new(self, node: Node) -> bool:
        """data-python="3.16" on the block or an ancestor: only checked by that Python or newer."""
        holder = node if node.get("data-python") else node.closest(lambda a: a.get("data-python"))
        if holder is None:
            return False
        if tuple(int(x) for x in holder.get("data-python").split(".")) > self.version:
            self.report.counts["skipped"] += 1
            return True
        return False

    # ------------------------------------------------------------------ running
    def env(self, seed: str) -> dict:
        keep = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "SYSTEMROOT", "TMP", "TEMP", "LANG")}
        return {**keep, "PYTHONHASHSEED": seed, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
                "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg", "NO_COLOR": "1", "PYTHON_COLORS": "0",
                "TERM": "dumb", "COLUMNS": "80", "LINES": "24"}

    def run(self, args: list[str], cwd: Path, seed="0", stdin="", timeout=60) -> tuple[int, str]:
        try:
            done = subprocess.run([self.python, *args], cwd=cwd, input=stdin, capture_output=True, text=True,
                                  timeout=timeout, env=self.env(seed), check=False)
        except subprocess.TimeoutExpired:
            return -1, f"(timed out after {timeout} s)"
        output = (done.stdout + done.stderr).replace(str(cwd) + os.sep, "")
        return done.returncode, output

    def workdir(self, name: str, files: dict[str, str]) -> Path:
        folder = Path(tempfile.mkdtemp(prefix=re.sub(r"\W", "_", name)[:40] + "-", dir=self.tmp))
        for rel, text in files.items():
            (folder / rel).parent.mkdir(parents=True, exist_ok=True)
            (folder / rel).write_text(text, encoding="utf-8")
        return folder

    def missing(self, node: Node) -> list[str]:
        names = (node.get("data-requires") or "").split()
        for name in names:
            if name not in self.missing_cache:
                self.missing_cache[name] = importlib.util.find_spec(name) is None
        return [n for n in names if self.missing_cache[n]]

    def problem(self, page, node, message):
        self.report.problems.append(Problem(page, node, message))

    # ------------------------------------------------------------------ checks
    def compile_all(self, page: Page):
        for node in page.scripts("text/x-python"):
            if self.too_new(node):
                continue
            code = page.code(node)
            if "</script" in page.raw(node).lower():
                self.problem(page, node, "code contains '</script' (the page would break)")
            expect = node.get("data-expect")
            try:
                compile(code, f"{page.path.name}:{node.line}", "exec", dont_inherit=True)
                if expect == "SyntaxError":
                    self.problem(page, node, 'marked data-expect="SyntaxError" but compiles')
            except SyntaxError as err:
                if expect != "SyntaxError":
                    self.problem(page, node, f"does not compile: {err.msg} (code line {err.lineno})")
            self.report.counts["compiled"] += 1

    def example(self, page: Page, figure: Node):
        scripts = [n for n in figure.iter() if n.tag == "script"]
        code = next((n for n in scripts if n.get("type") == "text/x-python"), None)
        out = next((n for n in scripts if n.get("type") == "text/x-output"), None)
        if code is None or out is None or self.too_new(figure):
            return  # display-only figure (check_site enforces the structure rules) or needs a newer Python
        if (missing := self.missing(figure)):
            if self.skip_missing:
                self.report.counts["skipped"] += 1
                return
            self.problem(page, figure, f"needs {', '.join(missing)} (install it, or pass --skip-missing)")
            return
        files = {n.get("data-name"): page.code(n) + "\n" for n in scripts if n.get("type") == "text/x-file"}
        name = code.get("data-file") or "example.py"
        files[name] = page.code(code) + "\n"
        stdin = next((page.code(n) + "\n" for n in scripts if n.get("type") == "text/x-stdin"), "")
        args = (figure.get("data-args") or "").split()
        want_exit = int(figure.get("data-exit") or (1 if figure.get("data-raises") else 0))
        timeout = int(figure.get("data-timeout") or 60)
        runs = []
        for seed in SEEDS:
            folder = self.workdir(f"{page.path.stem}-{figure.get('id', figure.line)}", files)
            status, text = self.run([str(self.tmp / "harness.py"), "script", name, *args], folder, seed, stdin, timeout)
            runs.append((status, normalize(text)))
        status, got = runs[0]
        self.report.counts["examples"] += 1
        label = f"example {figure.get('id') or ''}".strip()
        if status != want_exit:
            self.problem(page, figure, f"{label} exited with status {status} (expected {want_exit}):\n{indent(got)}")
            return
        if raises := figure.get("data-raises"):
            last = got.rsplit("\n", 1)[-1]
            if not last.startswith(raises):
                self.problem(page, figure, f"{label} should raise {raises}, last line was: {last}")
                return
        if figure.get("data-output") == "sample":
            return
        want = normalize(page.code(out))
        ellipsis = figure.get("data-match") == "ellipsis"
        if all(matches(want, text, ellipsis) for _, text in runs):
            return
        if not ellipsis and runs[0][1] != runs[1][1]:
            self.problem(page, figure, f"{label} prints different output under different hash seeds "
                                       "(set iteration order?):\n" + diff(runs[0][1], runs[1][1]))
        elif self.update and not ellipsis:
            self.report.updates.setdefault(page, {})[out] = got
        else:
            self.problem(page, figure, f"{label} output differs from the page"
                         + ("" if ellipsis else " (run with --update-outputs to accept)") + ":\n" + diff(want, got))

    def session(self, page: Page, node: Node):
        holder = node.closest(lambda a: a.get("data-requires")) or node
        if self.too_new(node):
            return
        if self.missing(holder) and self.skip_missing:
            self.report.counts["skipped"] += 1
            return
        files = {"session.txt": page.code(node) + "\n"}
        owner = node.closest(lambda a: a.has_class("exercise"))
        if owner is not None:  # a session in an exercise statement runs against the solution
            ex = next((e for e in exercises(page) if e.node is owner), None)
            if ex is not None and "solution" in ex.roles:
                files.update(ex.files("solution"))
        folder = self.workdir(f"{page.path.stem}-pycon", files)
        flag = "ellipsis" if (node.get("data-match") or (holder.get("data-match"))) == "ellipsis" else "-"
        for seed in SEEDS:
            status, text = self.run([str(self.tmp / "harness.py"), "pycon", "session.txt", flag], folder, seed)
            if status != 0:
                self.problem(page, node, f"interactive session does not match real Python (seed {seed}):\n{indent(text)}")
                break
        self.report.counts["sessions"] += 1

    def exercise(self, page: Page, ex):
        prefix = f"exercise {ex.id}"
        need = {"starter", "solution"} | ({"target"} if ex.kind == "write_tests" else {"tests"})
        if (absent := need - ex.roles.keys()):
            self.problem(page, ex.node, f"{prefix} is missing: {', '.join(sorted(absent))}")
            return
        if (missing := self.missing(ex.node)):
            if self.skip_missing:
                self.report.counts["skipped"] += 1
                return
            self.problem(page, ex.node, f"{prefix} needs {', '.join(missing)}")
            return
        shared = {name: (LEARNER / name).read_text(encoding="utf-8") for name in SHARED_FILES if name != "conftest.py"}
        for variant, should_pass in (("solution", True), ("starter", False)):
            folder = self.workdir(f"{ex.id}-{variant}", {**shared, **ex.files(variant)})
            status, text = self.run(["-m", "pytest", "-q", "-p", "no:cacheprovider", ex.test_file], folder, timeout=180)
            if should_pass and status != 0:
                self.problem(page, ex.node, f"{prefix}: tests fail on the solution:\n{indent(tail(text))}")
                return
            if not should_pass and status == 0:
                self.problem(page, ex.node, f"{prefix}: tests already pass on the starter code")
            if not should_pass and status == 5:
                self.problem(page, ex.node, f"{prefix}: pytest collected no tests")
        self.report.counts["exercises"] += 1

    def quiz(self, page: Page, section: Node):
        spec_node = next((n for n in section.iter() if n.tag == "script" and n.has_class("quiz-spec")), None)
        if spec_node is None:
            self.problem(page, section, "quiz without <script type=\"application/json\" class=\"quiz-spec\">")
            return
        try:
            spec = json.loads(page.raw(spec_node))
        except ValueError as err:
            self.problem(page, spec_node, f"quiz spec is not valid JSON: {err}")
            return
        for message in validate_quiz(spec, section.get("id")):
            self.problem(page, spec_node, message)
        for i, q in enumerate(spec.get("questions", []), 1):
            if q.get("type") == "predict" and isinstance(q.get("code"), str):
                folder = self.workdir(f"{spec.get('id')}-q{i}", {"predict.py": dedent(q["code"]) + "\n"})
                _, text = self.run([str(self.tmp / "harness.py"), "script", "predict.py"], folder)
                if normalize(text) != normalize(str(q.get("answer", ""))):
                    self.problem(page, spec_node, f"quiz question {i}: answer does not match real output:\n"
                                 + diff(normalize(str(q.get('answer', ''))), normalize(text)))
        self.report.counts["quizzes"] += 1

    # ------------------------------------------------------------------ driver
    def check(self, pages: list[Page], only: set[str]):
        tasks = []
        for page in pages:
            if "compile" in only:
                self.compile_all(page)
            if "examples" in only:
                tasks += [(self.example, page, f) for f in page.all("figure", cls="example")]
                tasks += [(self.session, page, n) for n in page.scripts("text/x-pycon")]
            if "exercises" in only:
                tasks += [(self.exercise, page, ex) for ex in exercises(page)]
            if "quizzes" in only:
                tasks += [(self.quiz, page, s) for s in page.all("section", cls="quiz")]
        with ThreadPoolExecutor(max_workers=self.jobs) as pool:
            for future in [pool.submit(fn, page, item) for fn, page, item in tasks]:
                future.result()


QUESTION_TYPES = {"mcq", "multi", "predict", "short", "order"}


def validate_quiz(spec: dict, section_id: str | None) -> list[str]:
    errors = []
    if spec.get("id") != section_id:
        errors.append(f"quiz id {spec.get('id')!r} must equal the section id {section_id!r}")
    questions = spec.get("questions")
    if not isinstance(questions, list) or not questions:
        return errors + ["quiz needs a non-empty questions list"]
    for i, q in enumerate(questions, 1):
        kind = q.get("type")
        where = f"question {i} ({kind})"
        if kind not in QUESTION_TYPES:
            errors.append(f"question {i}: type must be one of {sorted(QUESTION_TYPES)}")
            continue
        if not str(q.get("prompt", "")).strip():
            errors.append(f"{where}: empty prompt")
        if not str(q.get("explanation", "")).strip() and not q.get("explanations"):
            errors.append(f"{where}: add an explanation (shown after checking)")
        options = q.get("options", [])
        if kind in ("mcq", "multi"):
            if len(options) < 2 or len(set(options)) != len(options):
                errors.append(f"{where}: needs 2+ distinct options")
            answer = q.get("answer")
            picks = [answer] if kind == "mcq" else answer
            if not isinstance(picks, list) or not picks or any(not isinstance(a, int) or not 0 <= a < len(options) for a in picks):
                errors.append(f"{where}: answer must be {'an option index' if kind == 'mcq' else 'a list of option indexes'}")
            elif kind == "multi" and len(set(picks)) != len(picks):
                errors.append(f"{where}: duplicate answer indexes")
            if "explanations" in q and len(q["explanations"]) != len(options):
                errors.append(f"{where}: explanations must have one entry per option")
        elif kind == "predict":
            if not isinstance(q.get("code"), str) or "answer" not in q:
                errors.append(f"{where}: needs code and answer")
        elif kind == "short":
            accept, pattern = q.get("accept", []), q.get("accept_regex")
            if not accept and not pattern:
                errors.append(f"{where}: needs accept and/or accept_regex")
            if pattern:
                try:
                    re.compile(pattern)
                except re.error as err:
                    errors.append(f"{where}: bad accept_regex: {err}")
                if re.search(r"\(\?P<|\(\?[aiLmsux]+\)|\\[AZ]", pattern):
                    errors.append(f"{where}: accept_regex must also work in JavaScript (no (?P<, inline flags, \\A, \\Z)")
        elif kind == "order":
            items = q.get("items", [])
            if len(items) < 3 or len(set(items)) != len(items):
                errors.append(f"{where}: needs 3+ distinct items (in the correct order)")
    return errors


def matches(want: str, got: str, ellipsis: bool) -> bool:
    if not ellipsis:
        return want == got
    return doctest.OutputChecker().check_output(want + "\n", got + "\n", doctest.ELLIPSIS)


def diff(want: str, got: str) -> str:
    lines = difflib.unified_diff(want.split("\n"), got.split("\n"), "page", "real Python", lineterm="", n=2)
    return indent("\n".join(lines))


def indent(text: str) -> str:
    return "\n".join("    " + line for line in text.split("\n"))


def tail(text: str, n: int = 30) -> str:
    return "\n".join(text.strip().split("\n")[-n:])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", type=Path)
    ap.add_argument("--update-outputs", action="store_true", help="rewrite x-output blocks that differ")
    ap.add_argument("--skip-missing", action="store_true", help="skip code whose data-requires libraries are absent")
    ap.add_argument("--only", default="compile,examples,exercises,quizzes")
    ap.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--python", default=sys.executable, help="interpreter used to run the code")
    args = ap.parse_args(argv)
    paths = args.pages or site_pages(SITE)
    pages = [Page(p) for p in paths]
    pages = [p for p in pages if p.kind in ("lesson", "reference", "project", "exam", "setup", "home")]
    checker = Checker(args.python, args.jobs, args.skip_missing, args.update_outputs)
    checker.check(pages, set(args.only.split(",")))
    report = checker.report
    for page, replacements in report.updates.items():
        page.path.write_text(replace_scripts(page, replacements), encoding="utf-8")
        print(f"updated {len(replacements)} output block(s) in {page.path.name}")
    for problem in sorted(report.problems, key=str):
        print(f"FAIL {problem}")
    c = report.counts
    print(f"check_content: {len(pages)} page(s), {c['compiled']} blocks compiled, {c['examples']} examples, "
          f"{c['sessions']} sessions, {c['exercises']} exercises, {c['quizzes']} quizzes, {c['skipped']} skipped, "
          f"{len(report.problems)} problem(s)")
    return 1 if report.problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 11. `tools/check_coverage.py`

````python
"""Prove the course covers "everything available": every public name of every declared target has a row.

  python tools/check_coverage.py             # whole course (CI)
  python tools/check_coverage.py --partial   # while the course is being built: unbuilt items are "pending"
  python tools/check_coverage.py --show class:dict   # print the required names of one target

Targets are declared on reference sections: <section class="api-reference" data-api-targets="class:dict
expr:dict_keys=type({}.keys()) module:json">. Rows name what they document: <tr data-api="dict.get">.
Coverage of a target is the union of rows on every page that declares it. Course-wide checks add every
keyword, every AST node type (in verified code), and every public standard-library module (kw:..., module:...
rows). Exclusions, each with a reason, live in tools/coverage.json.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import doctest
import fnmatch
import importlib
import importlib.util
import inspect
import io
import json
import keyword
import sys
import tokenize
import warnings
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pagekit import Page, site_pages

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CONFIG = Path(__file__).resolve().parent / "coverage.json"
FREE_NAMESPACES = ("syntax:", "concept:")


@dataclass
class Target:
    spec: str
    kind: str
    alias: str
    obj: object

    def full(self) -> set[str]:
        return {f"{self.alias}.{n}" for n in dir(self.obj)} | {self.alias}

    def required(self, ignore: set[str], documented_classes: frozenset = frozenset()) -> set[str]:
        """Module: __all__ (or public non-module names). Class: its own attributes plus those it inherits
        from helper bases (pandas NDFrame, matplotlib _AxesBase...), but not from builtins or from
        classes that are targets themselves (Counter doesn't repeat dict; Path doesn't repeat PurePath)."""
        if self.kind == "module":
            names = getattr(self.obj, "__all__", None)
            if names is None:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    names = [n for n in dir(self.obj) if not n.startswith("_")
                             and not inspect.ismodule(getattr(self.obj, n, None))]
            return {f"{self.alias}.{n}" for n in names}
        names = set()
        for cls in self.obj.__mro__:
            if cls is not self.obj and (cls.__module__ == "builtins" or cls in documented_classes):
                continue
            own = vars(cls)
            names |= {n for n in own if not n.startswith("_")}
            names |= {n for n in own if n.startswith("__") and n.endswith("__") and n not in ignore}
        return {self.alias} | {f"{self.alias}.{n}" for n in names}


def resolve(spec: str) -> Target:
    """class:dict | class:Counter=collections.Counter | module:json | expr:dict_keys=type({}.keys())"""
    kind, _, rest = spec.partition(":")
    alias, eq, path = rest.partition("=")
    if not eq:
        path = alias
        alias = path.rsplit(".", 1)[-1] if kind == "class" else path
    if kind == "module":
        obj = importlib.import_module(path)
    elif kind == "class":
        obj = _dotted(path)
        if not isinstance(obj, type):
            raise ValueError(f"{spec}: {path} is not a class")
    elif kind == "expr":
        obj = eval(path, {"__builtins__": builtins, "importlib": importlib})  # course-authored text only
        if not isinstance(obj, type):
            obj = type(obj)
    else:
        raise ValueError(f"{spec}: target kind must be class:, module: or expr:")
    return Target(spec, kind, alias, obj)


def _dotted(path: str):
    if "." not in path:
        return getattr(builtins, path)
    parts = path.split(".")
    for cut in range(len(parts) - 1, 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue
        for part in parts[cut:]:
            obj = getattr(obj, part)
        return obj
    raise ImportError(path)


# ---------------------------------------------------------------------- code inventory
def code_blocks(page: Page):
    """Every piece of Python on a page that the content checker verifies (compiled, run or tested)."""
    for node in page.scripts("text/x-python"):
        if node.get("data-expect") != "SyntaxError":
            yield node, page.code(node)
    for node in page.scripts("text/x-pycon"):
        examples = doctest.DocTestParser().get_examples(page.code(node))
        yield node, "\n".join(ex.source for ex in examples)


def syntax_used(blocks) -> tuple[set[str], set[str]]:
    nodes, words = set(), set()
    for _, code in blocks:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            nodes.add(type(node).__name__)
            if isinstance(node, ast.Match):
                words |= {"match", "case"}
            elif isinstance(node, ast.TypeAlias):
                words.add("type")
            elif isinstance(node, ast.MatchAs) and node.pattern is None and node.name is None:
                words.add("_")
            elif isinstance(node, (ast.Import, ast.ImportFrom)) and getattr(node, "is_lazy", 0):
                words.add("lazy")
        try:
            for tok in tokenize.generate_tokens(io.StringIO(code).readline):
                if tok.type == tokenize.NAME and keyword.iskeyword(tok.string):
                    words.add(tok.string)
        except (tokenize.TokenError, SyntaxError):
            pass
    return nodes, words


# ---------------------------------------------------------------------- checker
@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def excluded(name: str, rules: dict) -> bool:
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in rules)


def check(pages: list[Page], config: dict, partial: bool) -> Result:
    res = Result()
    ignore = set(config["ignore_dunders"])
    targets: dict[str, Target] = {}
    declared_on: dict[str, list[Page]] = {}
    rows: dict[str, list[tuple[Page, object]]] = {}
    version = sys.version_info[:2]

    for page in pages:
        for section in page.all("section", cls="api-reference"):
            for spec in (section.get("data-api-targets") or "").split():
                try:
                    target = targets.get(spec) or resolve(spec)
                except Exception as err:  # noqa: BLE001 - report any resolution failure
                    res.errors.append(f"{page.path.name}:{section.line}: cannot resolve target {spec}: {err}")
                    continue
                targets[spec] = target
                declared_on.setdefault(spec, []).append(page)
        for node in page.root.iter():
            for name in (node.get("data-api") or "").split():
                rows.setdefault(name, []).append((page, node))

    aliases = sorted({t.alias: t for t in targets.values()}.items(), key=lambda kv: -len(kv[0]))

    def owner(name: str):
        """The declared target a row name belongs to (longest alias wins: os.path before os)."""
        return next((t for alias, t in aliases if name == alias or name.startswith(alias + ".")), None)

    documented = set(rows)
    stdlib = {m for m in sys.stdlib_module_names if not m.startswith("_")} | set(config["stdlib"]["include"])

    # every row must name something real
    for name, places in sorted(rows.items()):
        page, node = places[0]
        where = f"{page.path.name}:{node.line}"
        newer = node.get("data-version") and tuple(map(int, node.get("data-version").split("."))) > version
        if name.startswith(FREE_NAMESPACES):
            continue
        if name.startswith("kw:"):
            if name[3:] not in keyword.kwlist + keyword.softkwlist:
                res.errors.append(f"{where}: {name} is not a Python keyword")
        elif name.startswith("module:"):
            top = name[7:].split(".")[0]
            if top not in stdlib and importlib.util.find_spec(top) is None and not newer:
                res.errors.append(f"{where}: {name} is not a module")
        else:
            target = owner(name)
            if target is None:
                res.errors.append(f"{where}: data-api {name!r} does not belong to any declared target")
            elif name not in target.full() and not newer:
                res.errors.append(f"{where}: {name} does not exist in this Python ({sys.version.split()[0]})")

    # every required name of every declared target needs a row (or an exclusion with a reason)
    exclusions = config["exclude"]
    classes = frozenset(t.obj for t in targets.values() if t.kind != "module")
    for spec, target in sorted(targets.items()):
        rules = exclusions.get(target.alias, {})
        for name, reason in rules.items():
            if not str(reason).strip():
                res.errors.append(f"coverage.json: exclusion {target.alias}.{name} needs a reason")
            full_name = f"{target.alias}.{name}"
            if not any(fnmatch.fnmatchcase(n, full_name) for n in target.full()):
                res.errors.append(f"coverage.json: stale exclusion {full_name} (no such attribute)")
        required = target.required(ignore, classes)
        missing = sorted(n for n in required - documented
                         if not excluded(n[len(target.alias) + 1:], rules))
        pages_ = ", ".join(sorted({p.path.name for p in declared_on[spec]}))
        if missing:
            res.errors.append(f"{spec} ({pages_}): {len(missing)} name(s) without a row: {', '.join(missing)}")
        else:
            res.notes.append(f"{spec}: complete ({len(required)} names)")

    def course_item(label: str, missing: list[str]):
        if not missing:
            res.notes.append(f"{label}: complete")
        elif partial:
            res.pending.append(f"{label}: {len(missing)} pending: {', '.join(missing)}")
        else:
            res.errors.append(f"{label}: {len(missing)} missing: {', '.join(missing)}")

    declared_specs = set(targets)
    course_item("required targets", sorted(set(config["required_targets"]) - declared_specs))
    nodes, words = syntax_used(b for page in pages for b in code_blocks(page))
    every_kw = keyword.kwlist + keyword.softkwlist
    course_item("keywords used in verified code", sorted(set(every_kw) - words))
    course_item("keyword reference rows", sorted(k for k in every_kw if f"kw:{k}" not in documented))
    leaf = {c.__name__ for c in vars(ast).values()
            if isinstance(c, type) and issubclass(c, ast.AST) and c is not ast.AST and not c.__subclasses__()}
    course_item("AST node types in verified code",
                sorted(n for n in leaf - nodes if n not in config["ast"]["exclude"]))
    stdlib_rules = config["stdlib"]["exclude"]
    course_item("standard-library atlas rows",
                sorted(m for m in stdlib if not excluded(m, stdlib_rules) and f"module:{m}" not in documented))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", type=Path)
    ap.add_argument("--partial", action="store_true", help="report unbuilt course-wide items as pending")
    ap.add_argument("--show", metavar="TARGET", help="print the required names of one target and exit")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if args.show:
        target = resolve(args.show)
        others = set()
        for spec in config["required_targets"]:
            if not spec.startswith("module:") and spec != args.show:
                with contextlib.suppress(Exception):  # a library that isn't installed
                    others.add(resolve(spec).obj)
        others = frozenset(others)
        print("\n".join(sorted(target.required(set(config["ignore_dunders"]), others))))
        return 0
    pages = [Page(p) for p in (args.pages or site_pages(SITE))]
    res = check(pages, config, args.partial)
    for line in res.errors:
        print(f"MISSING {line}" if "without a row" in line or "missing:" in line else f"ERROR {line}")
    for line in res.pending:
        print(f"pending {line[:300]}{'...' if len(line) > 300 else ''}")
    if args.verbose:
        for line in res.notes:
            print(f"ok {line}")
    print(f"check_coverage: {len(pages)} page(s), {len(res.errors)} error(s), {len(res.pending)} pending")
    return 1 if res.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 12. `tools/coverage.json`

The `required_targets` list mirrors the coverage map in `spec/02` §4. Add an entry to `exclude` only with a reason (`{"dict": {"__name__": "reason"}}`; glob patterns allowed); stale exclusions fail the check.

````json
{
  "about": "Coverage commitments checked by tools/check_coverage.py. Every exclusion needs a reason.",
  "python": "3.15",
  "required_targets": [
    "module:builtins", "class:object", "class:type", "class:int", "class:bool", "class:float", "class:complex",
    "class:str", "class:bytes", "class:bytearray", "class:memoryview", "class:list", "class:tuple", "class:range",
    "class:slice", "class:dict", "expr:dict_keys=type({}.keys())", "expr:dict_values=type({}.values())",
    "expr:dict_items=type({}.items())", "class:frozendict", "class:set", "class:frozenset", "class:BaseException", "class:property", "class:sentinel",
    "expr:function=type(lambda: None)", "expr:generator=type((x for x in ()))", "class:types.MappingProxyType",
    "module:math", "module:math.integer", "module:statistics", "module:random", "module:decimal", "module:fractions", "module:string",
    "module:string.templatelib", "module:re", "class:re.Pattern", "class:re.Match", "module:textwrap",
    "module:datetime", "class:datetime.date", "class:datetime.datetime", "class:datetime.time",
    "class:datetime.timedelta", "class:datetime.timezone", "module:zoneinfo", "module:time",
    "module:collections", "class:collections.Counter", "class:collections.deque", "class:collections.defaultdict",
    "class:collections.OrderedDict", "class:collections.ChainMap", "module:collections.abc", "module:heapq",
    "module:bisect", "module:enum", "module:dataclasses", "module:typing", "module:types", "module:annotationlib",
    "module:copy", "module:itertools", "module:functools", "module:operator", "module:contextlib", "module:abc",
    "module:pathlib", "class:pathlib.PurePath", "class:pathlib.Path", "module:os.path", "module:shutil",
    "module:glob", "module:tempfile", "module:io", "module:json", "module:csv", "module:pickle", "module:sqlite3",
    "module:tomllib", "module:zipfile", "module:gzip", "module:hashlib", "module:secrets", "module:uuid",
    "module:base64", "module:sys", "module:argparse", "module:logging", "module:subprocess", "module:warnings",
    "module:traceback", "module:timeit", "module:cProfile", "module:profiling.tracing", "module:profiling.sampling", "module:pprint", "module:unittest",
    "class:unittest.TestCase", "module:asyncio", "module:threading", "module:concurrent.futures", "module:queue",
    "module:urllib.parse", "module:urllib.request", "module:graphlib",
    "module:numpy", "class:numpy.ndarray", "class:numpy.random.Generator", "module:numpy.linalg",
    "module:pandas", "class:pandas.DataFrame", "class:pandas.Series", "class:pandas.Index",
    "expr:StringMethods=type(importlib.import_module('pandas').Series(['a']).str)",
    "expr:DatetimeProperties=type(importlib.import_module('pandas').Series(importlib.import_module('pandas').to_datetime(['2026-01-01'])).dt)",
    "expr:DataFrameGroupBy=type(importlib.import_module('pandas').DataFrame({'a': [1]}).groupby('a'))",
    "module:matplotlib.pyplot", "class:matplotlib.axes.Axes", "class:matplotlib.figure.Figure",
    "class:sklearn.base.BaseEstimator", "module:sklearn.preprocessing", "module:sklearn.model_selection",
    "module:sklearn.metrics", "module:sklearn.pipeline", "module:sklearn.compose", "module:sklearn.impute",
    "module:sklearn.linear_model", "module:sklearn.ensemble", "module:sklearn.tree", "module:sklearn.neighbors",
    "module:sklearn.svm", "module:sklearn.cluster", "module:sklearn.decomposition",
    "class:torch.Tensor", "module:torch.nn", "module:torch.optim", "module:torch.utils.data"
  ],
  "ignore_dunders": [
    "__doc__", "__new__", "__init__", "__getattribute__", "__module__", "__dict__", "__weakref__", "__slots__",
    "__init_subclass__", "__subclasshook__", "__reduce__", "__reduce_ex__", "__getstate__", "__setstate__",
    "__getnewargs__", "__getnewargs_ex__", "__sizeof__", "__annotations__", "__annotate__", "__annotate_func__",
    "__annotations_cache__", "__qualname__", "__firstlineno__", "__static_attributes__", "__abstractmethods__",
    "__orig_bases__", "__parameters__", "__type_params__", "__dataclass_fields__", "__dataclass_params__",
    "__match_args__", "__text_signature__", "__objclass__", "__classcell__", "__classdictcell__"
  ],
  "ast": {
    "exclude": {
      "AugLoad": "deprecated, never produced by the parser", "AugStore": "deprecated, never produced",
      "Param": "deprecated, never produced", "Suite": "deprecated, never produced",
      "Index": "deprecated, never produced", "ExtSlice": "deprecated, never produced",
      "Interactive": "parse mode root (mode='single'), not syntax", "Expression": "parse mode root (mode='eval')",
      "FunctionType": "parse mode root (mode='func_type')", "TypeIgnore": "only with type_comments=True"
    }
  },
  "stdlib": {
    "include": ["__future__", "__main__"],
    "exclude": {
      "genericpath": "private helper of os.path", "nturl2path": "private helper of urllib",
      "encodings": "codec implementations behind codecs",
      "pydoc_data": "data files for pydoc", "turtledemo": "demo scripts for turtle",
      "nt": "low-level module behind os (Windows)", "posix": "low-level module behind os (Unix)",
      "pyexpat": "C accelerator behind xml.parsers.expat"
    }
  },
  "exclude": {}
}
````

## 13. `tools/api_skeleton.py`

````python
"""Print draft reference-table rows for a coverage target, one per required name.

  python tools/api_skeleton.py class:dict
  python tools/api_skeleton.py "expr:dict_keys=type({}.keys())" --var keys

Each row carries the real signature and the first docstring line as a TODO description. Rewrite every
description in course voice, set data-level, group related names into one row (data-api takes several
names), then remove the TODO markers: check_site.py rejects pages that still contain them.
"""
from __future__ import annotations

import argparse
import html
import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_coverage import CONFIG, resolve
from pagekit import api_id

SYNTAX = {
    "__getitem__": "{x}[key]", "__setitem__": "{x}[key] = value", "__delitem__": "del {x}[key]",
    "__contains__": "item in {x}", "__len__": "len({x})", "__iter__": "iter({x})", "__reversed__": "reversed({x})",
    "__repr__": "repr({x})", "__str__": "str({x})", "__hash__": "hash({x})", "__bool__": "bool({x})",
    "__format__": "format({x}, spec)", "__call__": "{x}(...)", "__eq__": "{x} == other", "__ne__": "{x} != other",
    "__lt__": "{x} < other", "__le__": "{x} <= other", "__gt__": "{x} > other", "__ge__": "{x} >= other",
    "__add__": "{x} + other", "__radd__": "other + {x}", "__iadd__": "{x} += other",
    "__sub__": "{x} - other", "__rsub__": "other - {x}", "__isub__": "{x} -= other",
    "__mul__": "{x} * other", "__rmul__": "other * {x}", "__imul__": "{x} *= other",
    "__truediv__": "{x} / other", "__rtruediv__": "other / {x}", "__itruediv__": "{x} /= other",
    "__floordiv__": "{x} // other", "__rfloordiv__": "other // {x}", "__ifloordiv__": "{x} //= other",
    "__mod__": "{x} % other", "__rmod__": "other % {x}", "__imod__": "{x} %= other",
    "__divmod__": "divmod({x}, other)", "__rdivmod__": "divmod(other, {x})",
    "__pow__": "{x} ** other", "__rpow__": "other ** {x}", "__ipow__": "{x} **= other",
    "__matmul__": "{x} @ other", "__rmatmul__": "other @ {x}", "__imatmul__": "{x} @= other",
    "__and__": "{x} &amp; other", "__rand__": "other &amp; {x}", "__iand__": "{x} &amp;= other",
    "__or__": "{x} | other", "__ror__": "other | {x}", "__ior__": "{x} |= other",
    "__xor__": "{x} ^ other", "__rxor__": "other ^ {x}", "__ixor__": "{x} ^= other",
    "__lshift__": "{x} &lt;&lt; n", "__rlshift__": "n &lt;&lt; {x}", "__ilshift__": "{x} &lt;&lt;= n",
    "__rshift__": "{x} &gt;&gt; n", "__rrshift__": "n &gt;&gt; {x}", "__irshift__": "{x} &gt;&gt;= n",
    "__neg__": "-{x}", "__pos__": "+{x}", "__abs__": "abs({x})", "__invert__": "~{x}",
    "__int__": "int({x})", "__float__": "float({x})", "__complex__": "complex({x})", "__index__": "operator.index({x})",
    "__round__": "round({x}, ndigits)", "__trunc__": "math.trunc({x})", "__floor__": "math.floor({x})",
    "__ceil__": "math.ceil({x})", "__bytes__": "bytes({x})", "__enter__": "with {x}:", "__exit__": "with {x}: (exit)",
    "__class_getitem__": "{cls}[T]", "__missing__": "subclass hook: called for a missing key",
    "__getattr__": "{x}.name (fallback)", "__setattr__": "{x}.name = value", "__delattr__": "del {x}.name",
    "__dir__": "dir({x})", "__copy__": "copy.copy({x})", "__deepcopy__": "copy.deepcopy({x})",
    "__buffer__": "memoryview({x})", "__release_buffer__": "(buffer protocol)", "__fspath__": "os.fspath({x})",
    "__await__": "await {x}", "__aiter__": "async for ... in {x}", "__anext__": "anext({x})",
    "__aenter__": "async with {x}:", "__aexit__": "async with {x}: (exit)", "__set_name__": "(descriptor setup)",
    "__get__": "(descriptor get)", "__set__": "(descriptor set)", "__delete__": "(descriptor delete)",
    "__instancecheck__": "isinstance(obj, {x})", "__subclasscheck__": "issubclass(cls, {x})",
    "__length_hint__": "operator.length_hint({x})", "__next__": "next({x})",
}


def signature(obj, name: str, var: str, cls_name: str) -> str:
    if name in SYNTAX:
        return SYNTAX[name].format(x=var, cls=cls_name)
    member = getattr(obj, name, None)
    try:
        sig = str(inspect.signature(member))
        sig = sig.replace("(self, ", "(").replace("(self)", "()").replace("(cls, ", "(")
        return html.escape(f"{var}.{name}{sig}") if callable(member) else html.escape(f"{var}.{name}")
    except (TypeError, ValueError):
        return html.escape(f"{var}.{name}" + ("(...)" if callable(member) else ""))


def first_line(obj) -> str:
    doc = inspect.getdoc(obj) or ""
    return html.escape(doc.strip().split("\n\n")[0].replace("\n", " ")[:160])


def rows(spec: str, var: str | None) -> list[str]:
    target = resolve(spec)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    names = sorted(target.required(set(config["ignore_dunders"])), key=lambda n: (n.count("__") > 0, n))
    var = var or (target.alias if target.kind == "module" else target.alias[0].lower())
    out = []
    for full in names:
        member = full[len(target.alias) + 1:] if full != target.alias else ""
        if not member:
            code, doc = html.escape(f"{target.alias}(...)"), first_line(target.obj)
        elif target.kind == "module":
            code, doc = html.escape(full), first_line(getattr(target.obj, member, None))
        else:
            code, doc = signature(target.obj, member, var, target.alias), first_line(getattr(target.obj, member, None))
        out.append(f'<tr id="{api_id(full)}" data-api="{full}" data-level="TODO">'
                   f'<td><code>{code}</code></td><td>TODO {doc}</td></tr>')
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--var", help="variable name used in examples (default: first letter of the class)")
    args = ap.parse_args(argv)
    print("\n".join(rows(args.target, args.var)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 14. `tools/export_exercises.py`

````python
"""Build the downloadable exercise packs: site/downloads/<lesson-id>.zip and all-exercises.zip.

  python tools/export_exercises.py           # write the zips
  python tools/export_exercises.py --check   # fail if a zip is missing or out of date (CI)

Zips are deterministic (sorted names, fixed timestamps), so --check can compare bytes.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packs import exercises, pack_files
from pagekit import Page

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
STAMP = (2026, 1, 1, 0, 0, 0)


def zip_bytes(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, STAMP)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, files[name].encode("utf-8"))
    return buffer.getvalue()


def lesson_pages(course: dict, site: Path):
    for module in course["modules"]:
        for lesson in module["lessons"]:
            path = site / module["path"] / lesson["file"]
            if not lesson.get("planned") and path.exists():
                yield module, lesson, Page(path)


def packs(course: dict, site: Path = SITE) -> dict[str, bytes]:
    """Relative output path -> zip bytes, for every lesson that has exercises."""
    out, everything = {}, {}
    base = course.get("base_url", "")
    for module, lesson, page in lesson_pages(course, site):
        if not exercises(page):
            continue
        url = f"{base}{module['path']}{lesson['file']}" if base else f"site/{module['path']}{lesson['file']}"
        files = {f"{lesson['id']}/{name}": text for name, text in pack_files(page, lesson["title"], url).items()}
        out[f"downloads/{lesson['id']}.zip"] = zip_bytes(files)
        everything.update(files)
    if everything:
        out["downloads/all-exercises.zip"] = zip_bytes(everything)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    course = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
    stale = 0
    for rel, data in packs(course).items():
        path = SITE / rel
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                print(f"out of date: site/{rel} (run python tools/build.py)")
                stale += 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(f"wrote site/{rel} ({len(data) // 1024 + 1} KB)")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 15. `tools/build.py`

````python
"""Regenerate every derived file from course.json and the pages. Commit the results (the site must work
from file:// with no build step on the learner's side).

  python tools/build.py           # write manifest.js, search-index.js, api-index.html, exercise packs
  python tools/build.py --check   # fail if any generated file is out of date (CI)

Derived files:
  site/assets/js/manifest.js      window.COURSE = {course.json + exercises/quiz/pack per lesson}
  site/assets/js/search-index.js  window.SEARCH_INDEX = [lessons, sections, reference rows, terms, exercises]
  site/api-index.html             A-Z index of every reference row, grouped by target
  site/downloads/*.zip            exercise packs (tools/export_exercises.py)
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_exercises import lesson_pages, packs
from packs import exercises
from pagekit import Page, site_pages

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SHELL = ROOT / "templates" / "page-shell.html"


def manifest(course: dict, site: Path) -> dict:
    data = json.loads(json.dumps(course))
    found = {lesson["id"]: page for _, lesson, page in lesson_pages(course, site)}
    for module in data["modules"]:
        for lesson in module["lessons"]:
            page = found.get(lesson["id"])
            if page is None:
                continue
            desc = page.first("meta", name="description")
            lesson["description"] = desc.get("content", "") if desc else ""
            items = exercises(page)
            lesson["exercises"] = [{"id": e.id, "title": e.title, "optional": e.optional} for e in items]
            quizzes = [q.get("id") for q in page.all("section", cls="quiz")]
            lesson["quiz"] = next((q for q in quizzes if q.endswith("-quiz")), None)
            lesson["pack"] = f"downloads/{lesson['id']}.zip" if items else None
    return data


def search_entries(site: Path, course: dict) -> list[dict]:
    labels = {f"{m['path']}{l['file']}": f"{l['id'].upper()} {l['title']}" for m in course["modules"] for l in m["lessons"]}
    out = []
    for path in site_pages(site):
        page = Page(path)
        if page.body is None or page.body.get("data-generated") is not None:
            continue
        rel = path.relative_to(site).as_posix()
        h1 = page.first("h1")
        where = labels.get(rel, h1.text() if h1 else rel)
        desc = page.first("meta", name="description")
        out.append({"t": h1.text() if h1 else rel, "u": rel, "k": page.kind,
                    "s": desc.get("content", "") if desc else "", "m": where})
        for node in page.root.iter():
            ident = node.get("id")
            if not ident:
                continue
            level = Page.level_of(node) or ""
            if node.tag in ("h2", "h3"):
                out.append({"t": node.text(), "u": f"{rel}#{ident}", "k": "section", "l": level, "m": where})
            elif node.get("data-api"):
                cells = [n for n in node.elements() if n.tag in ("td", "th")]
                code = next((n.text() for n in node.iter() if n.tag == "code"), node.get("data-api"))
                out.append({"t": code, "a": node.get("data-api"), "u": f"{rel}#{ident}", "k": "api", "l": level,
                            "s": cells[1].text()[:140] if len(cells) > 1 else "", "m": where})
            elif node.tag == "dfn":
                out.append({"t": node.text(), "u": f"{rel}#{ident}", "k": "term", "l": level, "m": where})
            elif node.tag == "article" and node.has_class("exercise"):
                title = next((n.text() for n in node.iter() if n.tag in ("h3", "h4")), ident)
                out.append({"t": title, "u": f"{rel}#{ident}", "k": "exercise", "m": where})
    return out


def api_index(entries: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        if entry["k"] != "api":
            continue
        for name in entry["a"].split():
            key = name.split(":")[0] + ":" if ":" in name else name.split(".")[0]
            groups.setdefault(key, []).append({**entry, "name": name})
    nice = {"kw:": "Keywords", "module:": "Standard-library atlas", "syntax:": "Syntax", "concept:": "Concepts"}
    parts = [('<p class="lead">Every name documented in a reference table, with a link to its row. '
              'Use the search box (press <kbd>/</kbd>) to jump straight to one.</p>')]
    toc = []
    for key in sorted(groups, key=str.lower):
        anchor = "idx-" + "".join(ch if ch.isalnum() or ch in "_-" else "-" for ch in key).strip("-")
        title = nice.get(key, key)
        toc.append(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>')
        items = "".join(
            f'<li><a href="{html.escape(e["u"])}"><code>{html.escape(e["name"])}</code></a>'
            f' <span class="muted">{html.escape(e["m"])}</span></li>'
            for e in sorted(groups[key], key=lambda e: e["name"].lower()))
        parts.append(f'<section id="{anchor}"><h2>{html.escape(title)}</h2><ul class="api-index">{items}</ul></section>')
    if not groups:
        parts.append("<p>No reference tables yet.</p>")
    body = f'<nav aria-label="Index sections"><ul class="chips">{"".join(toc)}</ul></nav>' + "".join(parts)
    shell = SHELL.read_text(encoding="utf-8")
    return (shell.replace("{{title}}", "API index").replace("{{description}}", "A-Z index of every documented name")
            .replace("{{root}}", "").replace("{{page}}", "reference").replace("{{content}}", body))


def outputs(site: Path = SITE) -> dict[str, bytes]:
    course = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
    files = {
        "assets/js/manifest.js": ("window.COURSE = " + json.dumps(manifest(course, site), ensure_ascii=False,
                                                                    separators=(",", ":")) + ";\n").encode(),
    }
    entries = search_entries(site, course)
    files["assets/js/search-index.js"] = ("window.SEARCH_INDEX = " + json.dumps(
        entries, ensure_ascii=False, separators=(",", ":")) + ";\n").encode()
    files["api-index.html"] = api_index(entries).encode()
    files.update(packs(course, site))
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    stale = 0
    for rel, data in outputs().items():
        path = SITE / rel
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                print(f"out of date: site/{rel}")
                stale += 1
        elif not path.exists() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(f"wrote site/{rel}")
    if args.check:
        print(f"build --check: {'all generated files up to date' if not stale else f'{stale} stale file(s): run python tools/build.py'}")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 16. `tools/ci.py`

````python
"""Run every check the way CI does. Stops at the first failing step.

  python tools/ci.py                # full course: everything must be complete
  python tools/ci.py --partial      # while building: unbuilt course-wide coverage is "pending"
  python tools/ci.py --no-browser   # skip the headless-Chrome smoke test
  python tools/ci.py --skip-missing # skip examples and library checks whose libraries are absent
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--partial", action="store_true")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--skip-missing", action="store_true", help="skip examples and library checks whose libraries are not installed")
    args = ap.parse_args(argv)
    py = sys.executable
    steps = [
        ("unit tests for the tools", [py, "-m", "pytest", "tools/tests", "-q", "-p", "no:cacheprovider"]),
        ("pinned libraries import and work", [py, "tools/check_libraries.py", "-j", "4"]
         + (["--skip-missing"] if args.skip_missing else [])),
        ("course code passes ruff", [py, "-m", "ruff", "check", "--no-cache", "tools"]),
        ("generated files are up to date", [py, "tools/build.py", "--check"]),
        ("site structure, links, markers", [py, "tools/check_site.py"]),
        ("reference coverage", [py, "tools/check_coverage.py"] + (["--partial"] if args.partial else [])),
        ("every example, session, exercise, quiz", [py, "tools/check_content.py"] + (["--skip-missing"] if args.skip_missing else [])),
        ("validated exercise patterns (spec/05 §11)", [py, "tools/check_content.py", "examples/spec05-examples.html"]
         + (["--skip-missing"] if args.skip_missing else [])),
    ]
    if not args.no_browser:
        if shutil.which("node") and (ROOT / "node_modules/puppeteer-core").exists():
            steps.append(("pages in headless Chrome", ["node", "tools/smoke_pages.mjs"]))
        else:
            print("note: skipping the browser smoke test (needs node and npm install puppeteer-core axe-core)")
    for title, cmd in steps:
        print(f"\n== {title}: {' '.join(cmd[1:] if cmd[0] == py else cmd)}", flush=True)
        if subprocess.run(cmd, cwd=ROOT, env={**os.environ, "PYTHON": py}, check=False).returncode:
            print(f"\nCI FAILED at: {title}")
            return 1
    print("\nCI passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 17. `tools/learner/conftest.py`

````python
"""Course plugin for pytest. You don't need to edit (or understand) this file.

It does two things:
1. lets the tests import your exercise files from any working directory;
2. after a run, prints a completion code for every exercise whose tests ALL passed.
   Paste the code into the exercise on the lesson page to record it as passed.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    PACK = json.loads((HERE / "pack.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    PACK = {"lesson": "?", "exercises": []}
BY_FILE = {ex["tests"]: ex for ex in PACK.get("exercises", [])}
TESTED_ON = PACK.get("python", "3.15")


def completion_code(exercise_id: str) -> str:
    """FNV-1a (32-bit) of the exercise id: the lesson page computes the same value."""
    value = 0x811C9DC5
    for byte in ("pyai:" + exercise_id).encode("utf-8"):
        value = ((value ^ byte) * 0x01000193) & 0xFFFFFFFF
    text = f"{value:08X}"
    return f"{text[:4]}-{text[4:]}"


_collected: Counter = Counter()
_passed: Counter = Counter()
_problems: Counter = Counter()
_deselected: set = set()


def _file(nodeid: str) -> str:
    return Path(nodeid.split("::", 1)[0]).name


def pytest_report_header(config):
    version = ".".join(map(str, sys.version_info[:3]))
    lines = [f"course pack {PACK.get('lesson')}: Python {version} (course tested on {TESTED_ON})"]
    if sys.version_info < (3, 15):
        lines.append(f"WARNING: the course is verified on Python {TESTED_ON}; some exercises use features "
                     "your version lacks. See the setup page.")
    return lines


def pytest_deselected(items):
    _deselected.update(item.path.name for item in items)


def pytest_collection_finish(session):
    _collected.update(item.path.name for item in session.items)


def pytest_runtest_logreport(report):
    name = _file(report.nodeid)
    if report.when == "call" and report.passed:
        _passed[name] += 1
    elif report.failed or report.skipped:
        _problems[name] += 1


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not BY_FILE:
        return
    write = terminalreporter.write_line
    terminalreporter.section("course: completion codes")
    for tests, ex in BY_FILE.items():
        label = f"{ex['id']:<12} {ex['title'][:40]:<40}"
        total = _collected[tests]
        if total == 0:
            write(f"{label}  - not run")
        elif tests in _deselected:
            write(f"{label}  - only some tests ran; run the whole file to get a code")
        elif _passed[tests] == total and not _problems[tests]:
            write(f"{label}  PASSED  code {completion_code(ex['id'])}")
        else:
            write(f"{label}  {total - _passed[tests]} of {total} tests not passing yet")
    write("Paste a code into the matching exercise on the lesson page to record it as passed.")
````

## 18. `tools/learner/course_helpers.py`

````python
"""Helpers the exercise tests use. Read it if you are curious; you don't need to edit it."""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

__all__ = ["assert_fast_enough", "assert_no_syntax", "check_tests", "run_program"]


def run_program(path, stdin: str = "", args=(), timeout: float = 10) -> str:
    """Run a Python script like you would in a terminal and return everything it printed."""
    path = Path(path).resolve()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "NO_COLOR": "1"}
    try:
        result = subprocess.run([sys.executable, str(path), *map(str, args)], input=stdin, text=True,
                                capture_output=True, timeout=timeout, cwd=path.parent, env=env, check=False)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{path.name} was still running after {timeout} s "
                             "(is it waiting for more input, or stuck in a loop?)") from None
    if result.returncode != 0:
        raise AssertionError(f"{path.name} stopped with exit status {result.returncode}.\n"
                             f"--- it printed ---\n{result.stdout}\n--- errors ---\n{result.stderr}")
    return result.stdout


def _best_time(func, args, repeat: int) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best


def assert_fast_enough(func, baseline, *args, factor: float = 10.0, repeat: int = 3) -> None:
    """Fail if func(*args) is more than `factor` times slower than baseline(*args).

    Speed is compared with a reference solution on the same machine, so a slow laptop
    doesn't fail a good solution (fixed time limits do).
    """
    mine = _best_time(func, args, repeat)
    reference = max(_best_time(baseline, args, repeat), 1e-4)
    assert mine <= factor * reference, (
        f"{func.__name__} took {mine * 1000:.1f} ms; the reference takes {reference * 1000:.1f} ms. "
        f"Look for repeated work inside a loop (allowed: up to {factor:g}x slower).")


def assert_no_syntax(path, nodes=(), calls=()) -> None:
    """Fail if the file uses any of the given AST node types (e.g. ast.For) or calls (e.g. "sorted", ".sort")."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if nodes and isinstance(node, tuple(nodes)):
            raise AssertionError(f"line {node.lineno}: this exercise asks you not to use {type(node).__name__}")
        if calls and isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else "." + func.attr if isinstance(func, ast.Attribute) else None
            if name in calls:
                raise AssertionError(f"line {node.lineno}: this exercise asks you not to call {name.lstrip('.')}()")


def _pytest(folder: Path, test_file: str) -> int:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", test_file],
                          cwd=folder, capture_output=True, text=True, env=env, timeout=60, check=False).returncode


def check_tests(test_file, module: str, mutants) -> None:
    """Check *your* tests: they must pass on the correct code and fail on every buggy version.

    mutants: {"description of the bug": "buggy source of the module", ...} or a JSON file name.
    """
    test_path = Path(test_file).resolve()
    here = test_path.parent
    if isinstance(mutants, (str, Path)):
        mutants = json.loads((here / mutants).read_text(encoding="utf-8"))
    correct = (here / f"{module}.py").read_text(encoding="utf-8")

    def run_with(source: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copy(test_path, folder / test_path.name)
            (folder / f"{module}.py").write_text(source, encoding="utf-8")
            return _pytest(folder, test_path.name)

    status = run_with(correct)
    assert status != 5, f"{test_path.name} has no tests yet: write functions whose names start with test_"
    assert status == 0, f"{test_path.name} fails on the CORRECT code; fix the tests first (run pytest {test_path.name})"
    missed = [bug for bug, source in mutants.items() if run_with(source) == 0]
    assert not missed, "Your tests did not catch these bugs:\n" + "\n".join(f"  - {bug}" for bug in missed)
````

## 19. `tools/learner/course_mocks.py`

````python
"""Offline stand-ins for paid or online services, so AI-integration exercises run free and deterministically.

MockLLM      behaves like a chat-completion client: scripted replies, every request recorded.
HashEmbedder turns text into fixed-size vectors by hashing words: lexical, not semantic, but deterministic.
fake_get     answers HTTP GET requests from a dictionary of canned responses.
Real clients appear in the lessons too; tests always use these, so they never need a key or a network.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field

__all__ = ["FakeResponse", "HashEmbedder", "MockLLM", "fake_get"]


@dataclass
class MockLLM:
    """replies: a list used in order (the last one repeats) or a function(messages) -> str."""
    replies: list[str] | Callable[[list[dict]], str]
    calls: list[dict] = field(default_factory=list)

    def complete(self, messages: list[dict], **options) -> str:
        if not messages or any({"role", "content"} - set(m) for m in messages):
            raise ValueError("messages must be a non-empty list of {'role': ..., 'content': ...} dicts")
        self.calls.append({"messages": messages, **options})
        if callable(self.replies):
            return self.replies(messages)
        return self.replies[min(len(self.calls), len(self.replies)) - 1]


@dataclass
class HashEmbedder:
    """Bag-of-words vectors: each lower-case word adds +1 or -1 to one of `dim` slots; vectors have length 1."""
    dim: int = 64

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.blake2b(word.encode(), digest_size=8).digest()
            slot = int.from_bytes(digest[:4], "big") % self.dim
            vec[slot] += 1.0 if digest[4] % 2 == 0 else -1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]


@dataclass
class FakeResponse:
    """The parts of requests.Response / httpx.Response that the course uses."""
    status_code: int = 200
    payload: object = None

    @property
    def text(self) -> str:
        return json.dumps(self.payload)

    def json(self):
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def fake_get(routes: dict[str, FakeResponse]) -> Callable[..., FakeResponse]:
    """Return a get(url, **kwargs) function that answers from `routes` (404 for anything else)."""
    def get(url: str, **kwargs) -> FakeResponse:
        return routes.get(url, FakeResponse(404, {"error": "not found"}))
    return get
````

## 20. `tools/smoke_pages.mjs`

Needs Node 22.12 or later, `npm install --no-save puppeteer-core@25 axe-core@4.14.1` and Google Chrome, which it finds where it is usually installed on macOS, Windows and Linux (`CHROME_PATH` overrides that; GitHub's Ubuntu runners have it at `/usr/bin/google-chrome`). Without Chrome it fails with one line saying so. `ci.py` skips it with a note when Node or puppeteer-core is missing; when axe-core is missing, its checks fail with the install command. Besides driving every widget, it checks the fonts load, the on-this-page rail follows the reading position, the reading position is saved for "continue where you left off", the reading settings and the shortcut switch work, controls are at least 24 × 24 px, and axe-core finds no WCAG 2.2 A/AA problem on nine page states (lesson, home, setup and API index in both themes; the lesson at phone width).

````javascript
// Browser smoke test: opens the built pages from file:// in headless Chrome, drives every widget and runs
// axe-core's WCAG 2.2 A/AA rules on each page in both themes.
//   npm install --no-save puppeteer-core@25 axe-core@4.14.1 && node tools/smoke_pages.mjs
// Finds Chrome where it is usually installed on macOS, Windows and Linux; CHROME_PATH overrides that.
// Exit code 0 = all checks passed.
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import puppeteer from "puppeteer-core";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SITE = join(ROOT, "site");
const url = (rel) => pathToFileURL(join(SITE, rel)).href;
const PY = process.env.PYTHON || "python3";
const results = [];
const check = (name, ok, detail = "") => { results.push({ name, ok }); console.log(`${ok ? "ok  " : "FAIL"} ${name}${!ok && detail ? ` (${detail})` : ""}`); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let AXE = null;
try { AXE = createRequire(import.meta.url).resolve("axe-core/axe.min.js"); } catch { /* reported by the check */ }
const WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
async function accessible(page, label) {
  if (!AXE) return check(`axe-core WCAG 2.2 A/AA: ${label}`, false, "npm install --no-save axe-core@4.14.1");
  await page.addScriptTag({ path: AXE });
  const found = await page.evaluate(async (tags) => (await window.axe.run(document, { runOnly: { type: "tag", values: tags } }))
    .violations.map((v) => `${v.id} x${v.nodes.length}: ${v.nodes[0].target.join(" ")}`), WCAG);
  check(`axe-core finds no WCAG 2.2 A/AA problems: ${label}`, found.length === 0, found.join(" | "));
}
async function accessibleInBothThemes(page, label) {
  for (const theme of ["light", "dark"]) {
    await page.evaluate((t) => { document.documentElement.dataset.theme = t; }, theme);
    await accessible(page, `${label}, ${theme} theme`);
  }
}

// Python's own answers, to prove the JS implementations agree (dedent rule + completion codes).
const CASES = ["\n    a\n      b\n    ", "  x\n  y", "\n      two\n      lines\n    ", "\n\n    keep\n\n    blank\n  ", "  ragged\nleft\n"];
const pyAnswers = JSON.parse(execFileSync(PY, ["-c", `
import json, sys
sys.path.insert(0, ${JSON.stringify(join(ROOT, "tools"))})
sys.path.insert(0, ${JSON.stringify(join(ROOT, "tools", "learner"))})
from pagekit import dedent
from conftest import completion_code
cases = json.loads(sys.argv[1])
print(json.dumps({"dedent": [dedent(c) for c in cases], "code": completion_code("m03-l04-e1")}))
`, JSON.stringify(CASES)]).toString());

function findChrome(env = process.env) {
  if (env.CHROME_PATH) return env.CHROME_PATH;
  const places = {
    darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
      join(env.HOME || "/", "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
      "/Applications/Chromium.app/Contents/MacOS/Chromium"],
    win32: [env.PROGRAMFILES, env["PROGRAMFILES(X86)"], env.LOCALAPPDATA].filter(Boolean)
      .map((dir) => join(dir, "Google", "Chrome", "Application", "chrome.exe")),
    linux: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser", "/snap/bin/chromium"],
  }[process.platform] || [];
  return places.find((place) => existsSync(place));
}
const CHROME = findChrome();
if (!CHROME) {
  console.log("FAIL Chrome not found: install Google Chrome, or set CHROME_PATH to the browser's executable");
  process.exit(1);
}
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--no-sandbox", "--allow-file-access-from-files"] });
const page = await browser.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
await page.setViewport({ width: 1280, height: 900 });

// ------------------------------------------------------------------ lesson page
await page.goto(url("modules/m03-data-structures/l04-dictionaries.html"), { waitUntil: "load" });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: "load" });
await page.waitForSelector("html.js-ready");
const stats = await page.evaluate(() => ({
  panels: document.querySelectorAll(".code-panel").length,
  tokens: document.querySelectorAll(".code-panel .token.keyword").length,
  badges: document.querySelectorAll(".badge--level").length,
  callouts: document.querySelectorAll(".callout .callout-kind").length,
  versions: [...document.querySelectorAll("span.version")].map((s) => s.textContent),
  toc: document.querySelectorAll("nav.toc li").length,
  legend: Boolean(document.querySelector("details.legend")),
  rawTokens: document.querySelector("main").innerText.includes("{python}") || document.querySelector("main").innerText.includes("{pytest}"),
  rowsWithBadge: document.querySelectorAll("tr[data-api] .badge--level").length,
  anchors: document.querySelectorAll("a.anchor").length,
}));
check("code panels rendered and highlighted", stats.panels > 40 && stats.tokens > 50, JSON.stringify(stats));
check("level badges, legend and table of contents", stats.badges > 60 && stats.legend && stats.toc >= 15, JSON.stringify(stats));
check("callouts labelled by kind", stats.callouts >= 15, String(stats.callouts));
check("version markers filled in", stats.versions.includes("New in 3.9") && stats.versions.includes("Changed in 3.7"), stats.versions.join("|"));
check("command tokens replaced for the learner's runner", !stats.rawTokens);
check("every reference row shows its level", stats.rowsWithBadge === (await page.$$("tr[data-api]")).length);
check("headings and rows have anchor links", stats.anchors > 60, String(stats.anchors));

const jsAnswers = await page.evaluate((cases) => ({ dedent: cases.map(window.CourseUI.dedent), code: window.CourseUI.completionCode("m03-l04-e1") }), CASES);
check("dedent: JavaScript matches Python", JSON.stringify(jsAnswers.dedent) === JSON.stringify(pyAnswers.dedent), JSON.stringify([jsAnswers.dedent, pyAnswers.dedent]));
check("completion code: JavaScript matches the pytest plugin", jsAnswers.code === pyAnswers.code, `${jsAnswers.code} vs ${pyAnswers.code}`);

// fonts, layout and reading aids
const fonts = await page.evaluate(async () => {
  await document.fonts.ready;
  const loaded = (family) => [...document.fonts].some((f) => f.family.replace(/"/g, "") === family && f.status === "loaded");
  return { text: loaded("Atkinson Hyperlegible Next"), code: loaded("Atkinson Hyperlegible Mono") };
});
check("course fonts load (Atkinson Hyperlegible Next and Mono)", fonts.text && fonts.code, JSON.stringify(fonts));
check("on-this-page rail sits beside the lesson on wide screens", Boolean(await page.$(".toc-rail nav.toc")) && !(await page.$("details.toc-inline")));
await accessible(page, "lesson, light theme");

// depth filter (the Show switch in the header)
const visible = (sel) => page.$eval(sel, (el) => getComputedStyle(el).display !== "none" && el.getClientRects().length > 0);
const show = (depth) => page.click(`header .depth-switch input[value="${depth}"]`);
await show("essential");
check("Show → Essentials hides extra and advanced parts", !(await visible("#merge")) && !(await visible("#hood")) && (await visible("#read")));
check("...including non-essential reference rows", !(await visible("#api-dict-setdefault")) && (await visible("#api-dict-get")));
check("...and says how much is hidden", Boolean(await page.$(".depth-note")));
await show("core");
check("Core hides only advanced parts", (await visible("#merge")) && !(await visible("#hood")));
await show("all");
check("Everything shows everything", (await visible("#hood")) && !(await page.$(".depth-note")));

// reading position: the rail follows the section in view, the progress line moves, the place is saved
await page.evaluate(() => document.querySelector("#merge").scrollIntoView());
await sleep(1200);
const reading = await page.evaluate(() => ({
  current: document.querySelector('.toc a[aria-current="location"]')?.getAttribute("href"),
  bar: document.querySelector(".reading-progress span")?.style.transform,
  resume: JSON.parse(localStorage.getItem("pyai.progress.v1")).settings.resume,
}));
check("the on-this-page rail marks the section being read", reading.current === "#merge", JSON.stringify(reading));
check("the reading-progress line moves with the page", /scaleX\(0\.\d+\)/.test(reading.bar || ""), reading.bar);
check("the reading position is saved for 'continue where you left off'", reading.resume && reading.resume.section === "merge", JSON.stringify(reading.resume));

// reading settings panel and keyboard shortcuts (single-key shortcuts can be turned off: WCAG 2.1.4)
await page.click(".display-btn");
const panelOpen = await visible("#display-panel");
await page.click('#display-panel .text-group input[value="l"]');
const large = await page.evaluate(() => document.documentElement.dataset.text);
await page.click('#display-panel .text-group input[value="m"]');
await page.keyboard.press("Escape");
check("reading settings: text size changes and the panel closes with Escape", panelOpen && large === "l" && !(await page.evaluate(() => document.documentElement.dataset.text)) && !(await visible("#display-panel")));
await page.evaluate(() => document.activeElement.blur());
await page.keyboard.press("/");
const slashOn = await page.evaluate(() => document.activeElement.classList.contains("search-input"));
await page.evaluate(() => { document.activeElement.blur(); window.CourseUI.store.setSetting("shortcuts", false); });
await page.keyboard.press("/");
const slashOff = await page.evaluate(() => document.activeElement.classList.contains("search-input"));
await page.evaluate(() => { document.activeElement.blur(); window.CourseUI.store.setSetting("shortcuts", true); });
check("'/' focuses search, and single-key shortcuts can be turned off", slashOn && !slashOff);

// a link into hidden content reveals it
await show("essential");
await page.evaluate(() => { location.hash = "#ex-proxy"; });
await page.waitForFunction(() => document.documentElement.dataset.depth === "all");
check("following a link into hidden content switches to Everything", await visible("#ex-proxy"));

// predict-then-reveal
const predictHidden = await page.$eval("#ex-why-dicts .output-panel", (el) => el.hidden);
await page.click("#ex-why-dicts .predict-btn");
check("predict examples hide the output until revealed", predictHidden && !(await page.$eval("#ex-why-dicts .output-panel", (el) => el.hidden)));

// exercises: hints, solution gate, completion codes
await page.click("#m03-l04-e1 .hints-box button");
check("hints are revealed one at a time", (await page.$$eval("#m03-l04-e1 .hints-shown li", (l) => l.length)) === 1);
await page.click("#m03-l04-e1 details.solution > summary");
const gated = Boolean(await page.$("#m03-l04-e1 .solution-gate"));
await page.click("#m03-l04-e1 .solution-gate button");
check("solution is gated, then shown on request", gated && (await page.$eval("#m03-l04-e1 details.solution", (d) => d.textContent.includes("counts.get(word, 0) + 1"))));
await page.type("#m03-l04-e1 .ex-code-input", "ABCD-1234");
await page.click("#m03-l04-e1 .toolbar .btn--primary");
const wrong = await page.$eval("#m03-l04-e1 .ex-feedback", (el) => el.textContent);
await page.$eval("#m03-l04-e1 .ex-code-input", (el) => { el.value = ""; });
await page.type("#m03-l04-e1 .ex-code-input", pyAnswers.code.toLowerCase());
await page.keyboard.press("Enter");
const status = await page.$eval("#m03-l04-e1 .ex-status", (el) => el.textContent);
check("a wrong completion code is rejected", wrong.includes("doesn't match"), wrong);
check("the code printed by pytest records a pass", status.includes("Passed"), status);
check("lesson summary counts required exercises", (await page.$eval(".lesson-summary", (el) => el.textContent)) === "Exercises passed: 1 of 3");
await page.click("#m03-l04-e2 .toolbar .btn--ghost");
check("'mark as done' records an unverified completion", (await page.$eval("#m03-l04-e2 .ex-status", (el) => el.textContent)).includes("not verified"));

// quiz: answer everything correctly
const quiz = "#m03-l04-quiz";
const spec = await page.evaluate(() => JSON.parse(document.querySelector("#m03-l04-quiz script.quiz-spec").textContent));
await page.click(`${quiz} fieldset:nth-of-type(1) input[value="${spec.questions[0].answer}"]`);
await page.type(`${quiz} fieldset:nth-of-type(2) textarea`, spec.questions[1].answer);
for (const i of spec.questions[2].answer) await page.click(`${quiz} fieldset:nth-of-type(3) input[value="${i}"]`);
await page.type(`${quiz} fieldset:nth-of-type(4) input`, spec.questions[3].accept[0]);
const wanted = await page.evaluate((items) => items.map((h) => { const s = document.createElement("span"); s.innerHTML = h; return s.textContent; }), spec.questions[4].items);
for (let guard = 0; guard < 30; guard++) {
  const order = await page.$$eval(`${quiz} fieldset:nth-of-type(5) .q-order-text`, (els) => els.map((e) => e.textContent));
  const i = order.findIndex((t, k) => t !== wanted[k]);
  if (i < 0) break;
  const j = order.indexOf(wanted[i]);
  await page.click(`${quiz} fieldset:nth-of-type(5) li:nth-child(${j + 1}) .q-up`);
}
await page.click(`${quiz} fieldset:nth-of-type(6) input[value="${spec.questions[5].answer}"]`);
await page.type(`${quiz} fieldset:nth-of-type(7) textarea`, spec.questions[6].answer);
await page.click(`${quiz} button[type=submit]`);
const score = await page.$eval(`${quiz} .quiz-score`, (el) => el.textContent);
check("quiz: all five question types can be answered correctly", score.startsWith("7 of 7"), score);

// search
await page.focus(".search-input");
await page.waitForFunction(() => Array.isArray(window.SEARCH_INDEX));
await page.type(".search-input", "setdefault");
await page.waitForSelector(".search-hit");
const first = await page.$eval(".search-hit .hit-title", (el) => el.textContent);
await page.keyboard.press("Enter");
await page.waitForFunction(() => location.hash === "#api-dict-setdefault");
check("search finds an API row and jumps to it", first.includes("setdefault"), first);

// theme
await page.click(".theme-toggle");
const theme = await page.evaluate(() => document.documentElement.dataset.theme);
check("theme toggle switches and remembers", ["dark", "light"].includes(theme) && (await page.evaluate(() => JSON.parse(localStorage.getItem("pyai.progress.v1")).settings.theme)) === theme);
await page.evaluate(() => { document.documentElement.dataset.theme = "dark"; window.scrollTo(0, 0); });
await accessible(page, "lesson, dark theme");
const small = await page.evaluate(() => [...document.querySelectorAll("button, a.btn, select, input[type=text], input[type=search], .seg label, .q-option, summary, .nav-lessons a, .toc a")]
  .filter((el) => el.getClientRects().length && getComputedStyle(el).visibility !== "hidden")
  .map((el) => { const r = el.getBoundingClientRect(); return { el: el.className || el.tagName, w: Math.round(r.width), h: Math.round(r.height) }; })
  .filter((r) => r.w < 24 || r.h < 24));
check("controls are at least 24 x 24 px (WCAG 2.5.8)", small.length === 0, JSON.stringify(small.slice(0, 5)));
await page.evaluate(() => { document.documentElement.dataset.theme = "light"; });

// ------------------------------------------------------------------ home page: dashboard + settings
await page.goto(url("index.html"), { waitUntil: "load" });
await page.waitForSelector(".module-card");
const dash = await page.$eval(".dash-total", (el) => el.textContent);
check("dashboard totals progress", dash.includes("2 of 3 exercises"), dash);
const resumeLink = await page.$eval(".continue-card a", (a) => a.getAttribute("href"));
const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("pyai.progress.v1")).settings.resume.section);
check("home offers to continue where you left off", resumeLink.endsWith(`l04-dictionaries.html#${saved}`), `${resumeLink} vs #${saved}`);
await accessibleInBothThemes(page, "home");
await page.select("#set-runner", "uv");
const preview = await page.$eval(".settings .fill-cmd", (el) => el.textContent);
check("runner setting changes every command", preview.startsWith("uv run python example.py") && preview.includes("uv run --with pytest pytest"), preview);
await page.goto(url("setup.html"), { waitUntil: "load" });
await page.waitForSelector("html.js-ready");
check("setup page renders commands in the chosen runner", (await page.$eval("#check pre", (el) => el.textContent)).trim() === "uv run python --version");
await accessibleInBothThemes(page, "setup");
await page.goto(url("api-index.html"), { waitUntil: "load" });
await page.waitForSelector("html.js-ready");
check("API index links to reference rows", (await page.$$("ul.api-index a")).length > 80);
await accessibleInBothThemes(page, "API index");

// ------------------------------------------------------------------ small screens
await page.setViewport({ width: 390, height: 800 });
await page.goto(url("modules/m03-data-structures/l04-dictionaries.html"), { waitUntil: "load" });
await page.waitForSelector("html.js-ready");
const navHidden = !(await visible("#sidebar"));
await page.click(".nav-toggle");
check("mobile: contents are behind the menu button", navHidden && (await visible("#sidebar")));
const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
check("mobile: the page doesn't scroll sideways", overflow <= 1, `${overflow}px`);
check("mobile: on-this-page is a collapsible list above the lesson", Boolean(await page.$("details.toc-inline nav.toc")) && !(await page.$(".toc-rail")));
await page.keyboard.press("Escape");
await accessible(page, "lesson on a phone");

check("no JavaScript errors on any page", errors.length === 0, errors.join(" | "));
await browser.close();
const failed = results.filter((r) => !r.ok).length;
console.log(`smoke_pages: ${results.length - failed} of ${results.length} checks passed`);
process.exit(failed ? 1 : 0);
````

## 21. Vendored assets

Both scripts copy from pinned npm packages, so these binary or generated files never need printing. Run them once, commit the results (CI and the deployed site use the committed files), and again only when upgrading. In one go: `npm install --no-save prismjs@1.30.0 @fontsource-variable/atkinson-hyperlegible-next@5.3.0 @fontsource-variable/atkinson-hyperlegible-mono@5.3.0`, then both scripts.

### 21.1 `tools/vendor/build_prism.py`

Writes `site/assets/vendor/prism.bundle.js` (about 33 KB; core + clike, markup, css, javascript, python, bash, sql, json, yaml, toml, docker, ini) in manual mode, with the MIT licence header kept.

````python
"""Build site/assets/vendor/prism.bundle.js: Prism core + the languages the course uses.

Run once (and when upgrading Prism):  npm install prismjs@1.30.0 && python tools/vendor/build_prism.py
Prism is MIT-licensed; the licence header is kept at the top of the bundle.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "node_modules/prismjs/components"
# Order matters: dependencies first (clike before javascript; markup before docker/xml-based ones).
LANGUAGES = ["clike", "markup", "css", "javascript", "python", "bash", "sql", "json", "yaml", "toml", "docker", "ini"]

parts = [
    "/*! Prism 1.30.0 | MIT License | https://prismjs.com | bundled for this course: core + "
    + ", ".join(LANGUAGES) + " */",
    # manual mode: the course highlights code itself (no automatic pass over the page)
    "window.Prism = window.Prism || {}; window.Prism.manual = true;",
    (COMPONENTS / "prism-core.min.js").read_text(encoding="utf-8"),
]
parts += [(COMPONENTS / f"prism-{lang}.min.js").read_text(encoding="utf-8") for lang in LANGUAGES]
out = ROOT / "site/assets/vendor/prism.bundle.js"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
````

### 21.2 `tools/vendor/build_fonts.py`

Copies five woff2 files (116 KB in all; a lesson loads three of them, 87 KB) and the two licences into `site/assets/fonts/`. Chrome loads them from `file://` too; a browser that refuses fonts from a parent folder of a `file://` page falls back to system fonts, and over http (GitHub Pages, `python -m http.server`) every browser loads them.

````python
"""Copy the course fonts into site/assets/fonts/: Atkinson Hyperlegible Next (text) and Mono (code).

Run once (and when upgrading the fonts):
  npm install --no-save @fontsource-variable/atkinson-hyperlegible-next@5.3.0 \\
      @fontsource-variable/atkinson-hyperlegible-mono@5.3.0
  python tools/vendor/build_fonts.py
Both are variable fonts (weights 200-800) from the Braille Institute, under the SIL Open Font License 1.1;
the licence is copied next to the files. course.css declares them with @font-face and unicode-range, so a
browser downloads only the subsets and styles a page uses. Without these files the pages fall back to
system fonts.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "node_modules/@fontsource-variable"
OUT = ROOT / "site/assets/fonts"
FILES = {
    "atkinson-hyperlegible-next": ["latin-wght-normal", "latin-ext-wght-normal", "latin-wght-italic"],
    "atkinson-hyperlegible-mono": ["latin-wght-normal", "latin-ext-wght-normal"],
}

OUT.mkdir(parents=True, exist_ok=True)
total = 0
for family, variants in FILES.items():
    for variant in variants:
        src = PACKAGES / family / "files" / f"{family}-{variant}.woff2"
        shutil.copyfile(src, OUT / src.name)
        total += src.stat().st_size
    shutil.copyfile(PACKAGES / family / "LICENSE", OUT / f"{family}-LICENSE.txt")
print(f"wrote {sum(map(len, FILES.values()))} fonts to {OUT.relative_to(ROOT)} ({total // 1024} KB)")
````

## 22. `tools/tests/`

### 22.1 `tools/tests/test_tools.py`

````python
"""Tests for the build and check tools. Run: python -m pytest tools/tests -q"""
from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
FIX = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "learner"))

import api_skeleton
import build
import check_content
import check_coverage
import check_libraries
import check_pins
import check_site
import course_helpers
import export_exercises
import pagekit

spec = importlib.util.spec_from_file_location("learner_conftest", TOOLS / "learner" / "conftest.py")
learner_conftest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(learner_conftest)
SAMPLE = ROOT / "site/modules/m03-data-structures/l04-dictionaries.html"


# ---------------------------------------------------------------------- pagekit
@pytest.mark.parametrize("raw, expected", [
    ("\n    a\n      b\n    ", "a\n  b"),                   # closing line sets the base indent
    ("\n      two\n      lines\n    ", "  two\n  lines"),    # ...so all-indented output survives
    ("  x\n  y", "x\ny"),                                    # no closing line: common indent
    ("\n\n    keep\n\n    blank\n  ", "  keep\n\n  blank"),   # inner blank lines stay, edges go
    ("  ragged\nleft\n", "  ragged\nleft"),                  # never cuts into text
    ("one line", "one line"),
])
def test_dedent(raw, expected):
    assert pagekit.dedent(raw) == expected


def test_parser_reports_structure_errors():
    page = pagekit.Page("x.html", "<html><body><p>open<div></div></body></html>")
    assert any("closes <p>" in e for e in page.errors)
    assert any("never closed" in e for e in pagekit.Page("y.html", "<main><section>").errors)


def test_replace_scripts_round_trip():
    page = pagekit.Page(FIX / "bad-lesson.html")
    out = next(n for n in page.scripts("text/x-output"))
    new_source = pagekit.replace_scripts(page, {out: "['a', 'b']\n  indented"})
    again = pagekit.Page("z.html", new_source)
    assert again.code(next(iter(again.scripts("text/x-output")))) == "['a', 'b']\n  indented"
    assert new_source.count("\n") == page.source.count("\n") + 1


def test_api_id():
    assert pagekit.api_id("dict.get") == "api-dict-get"
    assert pagekit.api_id("dict_keys.__and__") == "api-dict_keys-__and__"
    assert pagekit.api_id("syntax:dict-display") == "api-syntax-dict-display"


# ---------------------------------------------------------------------- check_content
def run_checker(paths, update=False):
    checker = check_content.Checker(sys.executable, 4, skip_missing=True, update=update)
    checker.check([pagekit.Page(p) for p in paths], {"compile", "examples", "exercises", "quizzes"})
    return checker.report


def test_good_fixture_passes():
    report = run_checker([FIX / "good-lesson.html"])
    assert [str(p) for p in report.problems] == []
    assert report.counts["examples"] == 7 and report.counts["exercises"] == 2 and report.counts["sessions"] == 1


def test_bad_fixture_problems_are_reported():
    text = "\n".join(str(p) for p in run_checker([FIX / "bad-lesson.html"]).problems)
    for expected in ["output differs", "different output under different hash seeds", "exited with status 1",
                     "does not compile", "already pass on the starter", "answer does not match",
                     "answer must be an option index"]:
        assert expected in text, expected


def test_update_outputs_rewrites_only_wrong_outputs(tmp_path):
    page_path = tmp_path / "bad.html"
    shutil.copy(FIX / "bad-lesson.html", page_path)
    report = run_checker([page_path], update=True)
    for page, replacements in report.updates.items():
        page.path.write_text(pagekit.replace_scripts(page, replacements), encoding="utf-8")
    assert "['a', 'b']" in page_path.read_text()
    remaining = "\n".join(str(p) for p in run_checker([page_path]).problems)
    assert "ex-wrong" not in remaining and "hash seeds" in remaining  # nondeterminism is never "accepted"


def test_quiz_validation():
    bad = {"id": "q", "questions": [
        {"type": "short", "prompt": "?", "accept_regex": "(?P<x>a)", "explanation": "e"},
        {"type": "multi", "prompt": "?", "options": ["a", "b"], "answer": [0, 0], "explanation": "e"},
        {"type": "order", "prompt": "?", "items": ["a", "b"], "explanation": "e"},
        {"type": "essay", "prompt": "?"}]}
    errors = "\n".join(check_content.validate_quiz(bad, "q"))
    assert "JavaScript" in errors and "duplicate" in errors and "3+ distinct items" in errors and "type must be" in errors


# ---------------------------------------------------------------------- coverage
CONFIG = json.loads(check_coverage.CONFIG.read_text())
IGNORE = set(CONFIG["ignore_dunders"])


def test_dict_surface():
    required = check_coverage.resolve("class:dict").required(IGNORE)
    assert {"dict", "dict.get", "dict.__or__", "dict.__class_getitem__", "dict.__hash__"} <= required
    assert "dict.__init__" not in required and "dict.__sizeof__" not in required


def test_subclasses_skip_builtin_and_target_bases():
    counter = check_coverage.resolve("class:collections.Counter")
    names = counter.required(IGNORE)
    assert "Counter.most_common" in names and "Counter.get" not in names  # dict's get belongs to dict


def test_helper_bases_are_included():
    pytest.importorskip("pandas")
    names = check_coverage.resolve("class:pandas.DataFrame").required(IGNORE)
    assert {"DataFrame.head", "DataFrame.loc", "DataFrame.groupby"} <= names


def test_module_alias_lookup_prefers_longest():
    page = pagekit.Page("p.html", """<main><section class="api-reference" data-api-targets="module:os.path">
    <table><tr id="api-os-path-join" data-api="os.path.join" data-level="essential"><td>x</td></tr></table></section></main>""")
    res = check_coverage.check([page], CONFIG, partial=True)
    assert not [e for e in res.errors if "does not belong" in e or "does not exist" in e]
    assert any("os.path" in e and "without a row" in e for e in res.errors)


def test_coverage_flags_missing_unknown_and_stale():
    page = pagekit.Page("p.html", """<main><section class="api-reference" data-api-targets="class:dict">
    <table><tr data-api="dict.gett"><td>x</td></tr><tr data-api="list.append"><td>y</td></tr></table></section></main>""")
    config = {**CONFIG, "exclude": {"dict": {"__nope__": "stale"}}}
    text = "\n".join(check_coverage.check([page], config, partial=True).errors)
    assert "dict.gett does not exist" in text and "list.append' does not belong" in text
    assert "stale exclusion dict.__nope__" in text and "without a row" in text


def test_soft_keywords_are_found_in_code():
    _, words = check_coverage.syntax_used([(None, "match x:\n    case _:\n        pass\ntype Pair = tuple[int, int]\n")])
    assert {"match", "case", "_", "type"} <= words
    if sys.version_info >= (3, 15):
        assert "lazy" in check_coverage.syntax_used([(None, "lazy import json\n")])[1]


def test_sample_lesson_targets_are_complete():
    res = check_coverage.check([pagekit.Page(SAMPLE)], CONFIG, partial=True)
    assert res.errors == []
    assert sum("complete" in n for n in res.notes) >= 5


def test_api_skeleton_covers_every_required_name():
    rows = api_skeleton.rows("class:dict", None)
    names = {r.split('data-api="')[1].split('"')[0] for r in rows}
    assert names == check_coverage.resolve("class:dict").required(IGNORE)
    assert all('data-level="TODO"' in r for r in rows)


# ---------------------------------------------------------------------- packs and the learner side
def test_completion_code_format_and_stability():
    code = learner_conftest.completion_code("m03-l04-e1")
    assert len(code) == 9 and code[4] == "-" and code == learner_conftest.completion_code("m03-l04-e1")
    assert code != learner_conftest.completion_code("m03-l04-e2")


def test_exports_are_deterministic():
    course = json.loads((ROOT / "course.json").read_text())
    first, second = export_exercises.packs(course), export_exercises.packs(course)
    assert first == second and "downloads/m03-l04.zip" in first
    names = zipfile.ZipFile(io.BytesIO(first["downloads/m03-l04.zip"])).namelist()
    assert {"m03-l04/conftest.py", "m03-l04/pack.json", "m03-l04/e1_word_freq.py", "m03-l04/test_e4_first_unique.py",
            "m03-l04/README.md", "m03-l04/course_helpers.py"} <= set(names)
    assert not any("solution" in n for n in names)


def test_learner_pack_prints_codes_only_for_fully_passing_files(tmp_path):
    course = json.loads((ROOT / "course.json").read_text())
    data = export_exercises.packs(course)["downloads/m03-l04.zip"]
    zipfile.ZipFile(io.BytesIO(data)).extractall(tmp_path)
    pack = tmp_path / "m03-l04"
    page = pagekit.Page(SAMPLE)
    solution = next(e for e in check_content.exercises(page) if e.id == "m03-l04-e1").roles["solution"]
    (pack / "e1_word_freq.py").write_text(solution + "\n")
    run = lambda *args: subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
                                       cwd=pack, capture_output=True, text=True, check=False).stdout
    out = run()
    assert f"PASSED  code {learner_conftest.completion_code('m03-l04-e1')}" in out
    assert "m03-l04-e2" in out and "not passing yet" in out
    partial = run("-k", "counts_repeated")
    assert "only some tests ran" in partial and "PASSED  code" not in partial


def test_course_helpers(tmp_path):
    script = tmp_path / "echo.py"
    script.write_text("name = input('Name? ')\nprint('Hi', name)\n")
    assert course_helpers.run_program(script, stdin="Ada\n").endswith("Hi Ada\n")
    slow = lambda n: sum(1 for i in range(n) for j in range(n))
    fast = lambda n: n * n
    with pytest.raises(AssertionError, match="took"):
        course_helpers.assert_fast_enough(slow, fast, 400, factor=5)
    code = tmp_path / "loops.py"
    code.write_text("total = 0\nfor x in range(3):\n    total += x\nprint(sorted([2, 1]))\n")
    with pytest.raises(AssertionError, match="For"):
        course_helpers.assert_no_syntax(code, nodes=(__import__("ast").For,))
    with pytest.raises(AssertionError, match="sorted"):
        course_helpers.assert_no_syntax(code, calls=("sorted",))


def test_check_tests_catches_weak_tests(tmp_path):
    (tmp_path / "leap.py").write_text("def is_leap(y):\n    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)\n")
    mutants = {"every 4th year": "def is_leap(y):\n    return y % 4 == 0\n"}
    weak = tmp_path / "test_weak.py"
    weak.write_text("from leap import is_leap\n\ndef test_basic():\n    assert is_leap(2024)\n")
    with pytest.raises(AssertionError, match="every 4th year"):
        course_helpers.check_tests(weak, "leap", mutants)
    strong = tmp_path / "test_strong.py"
    strong.write_text("from leap import is_leap\n\ndef test_rules():\n    assert is_leap(2024) and not is_leap(1900)\n")
    course_helpers.check_tests(strong, "leap", mutants)


# ---------------------------------------------------------------------- check_site and build
def make_site(tmp_path: Path, lesson_html: str) -> Path:
    site = tmp_path / "site"
    (site / "assets/js").mkdir(parents=True)
    (site / "m").mkdir()
    manifest = {"modules": [{"id": "m99", "path": "m/", "lessons": [{"id": "m99-l01", "file": "l01.html"}]}]}
    (site / "assets/js/manifest.js").write_text("window.COURSE = " + json.dumps(manifest) + ";\n")
    (site / "m/l01.html").write_text(lesson_html)
    return site


def test_check_site_catches_authoring_mistakes(tmp_path):
    shell = SAMPLE.read_text()
    head, rest = shell.split('<main id="main" class="content">', 1)
    tail = rest.split("</main>", 1)[1]
    head = head.replace('data-lesson-id="m03-l04" data-root="../../"', 'data-lesson-id="m99-l01" data-root="../"').replace("../../", "../")
    body = """<main id="main" class="content"><h1>T</h1>
      <section id="s1"><h2>No level</h2><h4>skipped h3</h4></section>
      <section id="s2" data-level="extra"><p data-level="essential">too essential</p><a href="missing.html">x</a></section>
      <section class="api-reference" id="ref" data-api-targets="class:dict"><table><caption>c</caption>
      <thead><tr><th scope="col">a</th></tr></thead><tbody><tr id="wrong" data-api="dict.get"><td>TODO later</td></tr></tbody></table></section>
      <aside class="callout" data-kind="shout"><p>?</p></aside>
    </main>"""
    site = make_site(tmp_path, head + body + tail)
    page = pagekit.Page(site / "m/l01.html")
    errors = "\n".join(check_site.check_page(page, site, check_site.load_manifest(site), {}))
    for expected in ["content sections need data-level", "skips from h2 to h4", "a child can't be more essential",
                     "broken link missing.html", "id must be 'api-dict-get'", "unfinished row", "callout data-kind",
                     "lesson pages need section.outcomes"]:
        assert expected in errors, expected


def test_sample_site_is_clean_and_built():
    site = ROOT / "site"
    manifest = check_site.load_manifest(site)
    for path in pagekit.site_pages(site):
        assert check_site.check_page(pagekit.Page(path), site, manifest, {}) == [], path.name
    stale = [rel for rel, data in build.outputs().items() if (site / rel).read_bytes() != data]
    assert stale == [], "run python tools/build.py"


# ------------------------------------------------------------- pins and libraries
def test_read_pins_follows_includes_and_rejects_ranges(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("pytest==9.2.0\n", encoding="utf-8")
    (tmp_path / "a.txt").write_text("# tools\n-r sub/b.txt\nNumPy==2.5.5  # arrays\npsycopg[binary]==3.3.9\n",
                                    encoding="utf-8")
    pins = check_pins.read_pins(tmp_path / "a.txt")
    assert {name: version for name, (version, _) in pins.items()} == {
        "pytest": "9.2.0", "numpy": "2.5.5", "psycopg": "3.3.9"}
    (tmp_path / "c.txt").write_text("pandas>=3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exact pin"):
        check_pins.read_pins(tmp_path / "c.txt")


@pytest.mark.parametrize("filename, ok", [
    ("x-1.0-cp315-cp315-manylinux_2_28_x86_64.whl", True),
    ("x-1.0-cp314-cp314-win_amd64.whl", False),
    ("x-1.0-cp315-cp315t-macosx_11_0_arm64.whl", False),     # free-threaded build only
    ("x-1.0-cp310-abi3-manylinux_2_28_x86_64.whl", True),     # stable ABI: 3.10 and later
    ("x-1.0-cp316-abi3-manylinux_2_28_x86_64.whl", False),
    ("x-1.0-py3-none-any.whl", True),
    ("x-1.0-py2.py3-none-any.whl", True),
    ("x-1.0-py3-none-manylinux_2_17_x86_64.whl", True),       # platform wheel for any Python 3
    ("x-1.0.tar.gz", True),                                    # source only (pure Python)
])
def test_installs_on(filename, ok):
    assert check_pins.installs_on([{"filename": filename}], "3.15") is ok


def test_newest_usable_release_skips_prereleases_and_missing_wheels():
    def wheel(tag):
        return [{"filename": f"a-0-{tag}-{tag}-linux_x86_64.whl"}]

    releases = {"0.9": wheel("cp315"), "1.0": wheel("cp315"), "1.1": wheel("cp315"),
                "1.2rc1": wheel("cp315"), "1.3": wheel("cp314")}

    def fetch(name):
        if name == "b":
            raise OSError("offline")
        return {"releases": releases}

    pins = {"a": ("1.0", Path("requirements-x.txt")), "b": ("2.0", Path("requirements-x.txt"))}
    a, b = check_pins.check(pins, "3.15", fetch)
    assert (a.status, a.newest, a.skipped) == ("update", "1.1", ["1.3"])
    assert b.status == "error" and "offline" in b.error


def test_every_pin_has_a_library_check_and_one_download():
    pins = check_pins.read_pins(check_libraries.DEV_REQUIREMENTS)
    assert sorted(pins) == sorted(check_libraries.IMPORTS)
    files = sorted((ROOT / "site/downloads").glob("requirements-*.txt"))
    names = [name for f in files for name in check_pins.read_pins(f)]
    assert len(names) == len(set(names)) == len(pins)      # each library in exactly one learner file
    setup = (ROOT / "site/setup.html").read_text(encoding="utf-8")
    assert all(f'href="downloads/{f.name}"' in setup for f in files)
````

### 22.2 `tools/tests/fixtures/good-lesson.html`

````html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Fixture</title></head>
<body data-page="lesson" data-lesson-id="m99-l01" data-root="../../">
  <main id="main">
    <section id="basics" data-level="essential">
      <h2>Basics</h2>
      <figure class="example" id="ex-dict">
        <script type="text/x-python">
        ages = {"Ada": 36, "Alan": 41}
        ages["Grace"] = 85
        for name, age in ages.items():
            print(f"{name:<6}{age:>3}")
        </script>
        <script type="text/x-output">
        Ada    36
        Alan   41
        Grace  85
        </script>
      </figure>
      <figure class="example" id="ex-keyerror" data-raises="KeyError">
        <script type="text/x-python">
        ages = {"Ada": 36}
        print("before")
        print(ages["Bob"])
        </script>
        <script type="text/x-output">
        before
        Traceback (most recent call last):
          ...
        KeyError: 'Bob'
        </script>
      </figure>
      <figure class="example" id="ex-input">
        <script type="text/x-python">
        name = input("Name: ")
        print(f"Hello, {name}!")
        </script>
        <script type="text/x-stdin">
        Ada
        </script>
        <script type="text/x-output">
        Name: Ada
        Hello, Ada!
        </script>
      </figure>
      <figure class="example" id="ex-ellipsis" data-match="ellipsis">
        <script type="text/x-python">
        print(object())
        </script>
        <script type="text/x-output">
        <object object at 0x...>
        </script>
      </figure>
      <figure class="example" id="ex-indented-output">
        <script type="text/x-python">
        print("  two leading spaces\n  on every line")
        </script>
        <script type="text/x-output">
          two leading spaces
          on every line
        </script>
      </figure>
      <figure class="example" id="ex-file">
        <script type="text/x-file" data-name="scores.csv">
        name,score
        Ada,90
        </script>
        <script type="text/x-python" data-file="read_scores.py">
        import csv
        with open("scores.csv", newline="") as f:
            print(list(csv.DictReader(f)))
        </script>
        <script type="text/x-output">
        [{'name': 'Ada', 'score': '90'}]
        </script>
      </figure>
      <figure class="example" id="ex-sample" data-output="sample">
        <script type="text/x-python">
        import random
        print(random.random())
        </script>
        <script type="text/x-output">
        0.6394267984578837
        </script>
      </figure>
      <figure class="session">
        <script type="text/x-pycon">
        >>> d = {"a": 1}
        >>> d.get("b", 0)
        0
        >>> d["b"]
        Traceback (most recent call last):
          ...
        KeyError: 'b'
        </script>
      </figure>
    </section>
    <section class="exercises" id="exercises">
      <h2>Exercises</h2>
      <article class="exercise" id="m99-l01-e1" data-kind="function" data-file="e1_double.py">
        <h3>Double every value</h3>
        <script type="text/x-python" data-role="starter">
        def double_values(d):
            """Return a new dict with every value doubled."""
            raise NotImplementedError
        </script>
        <script type="text/x-python" data-role="tests">
        from e1_double import double_values

        def test_doubles():
            assert double_values({"a": 1, "b": 2}) == {"a": 2, "b": 4}

        def test_does_not_mutate():
            d = {"a": 1}
            double_values(d)
            assert d == {"a": 1}
        </script>
        <script type="text/x-python" data-role="solution">
        def double_values(d):
            """Return a new dict with every value doubled."""
            return {k: v * 2 for k, v in d.items()}
        </script>
      </article>
      <article class="exercise" id="m99-l01-e2" data-kind="write_tests" data-file="e2_leap.py">
        <h3>Test a leap-year function</h3>
        <script type="text/x-python" data-role="target">
        def is_leap(year):
            return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        </script>
        <script type="text/x-python" data-role="starter">
        from e2_leap import is_leap

        def test_typical_leap_year():
            ...  # replace with real asserts
        </script>
        <script type="text/x-python" data-role="solution">
        from e2_leap import is_leap

        def test_rules():
            assert is_leap(2024) and not is_leap(2023)
            assert not is_leap(1900) and is_leap(2000)
        </script>
        <script type="application/json" data-role="mutants">
        {"every century is a leap year": "def is_leap(year):\n    return year % 4 == 0\n",
         "no century is a leap year": "def is_leap(year):\n    return year % 4 == 0 and year % 100 != 0\n"}
        </script>
      </article>
    </section>
    <section class="quiz" id="m99-l01-quiz">
      <h2>Quiz</h2>
      <script type="application/json" class="quiz-spec">
      {"id": "m99-l01-quiz", "questions": [
        {"type": "mcq", "prompt": "Which call never raises?", "options": ["d[k]", "d.get(k)"], "answer": 1,
         "explanation": "get returns None (or your default) for a missing key."},
        {"type": "predict", "prompt": "What prints?", "code": "d = {'a': 1}\nd['a'] += 1\nprint(d)", "answer": "{'a': 2}",
         "explanation": "Augmented assignment reads, adds and stores."},
        {"type": "order", "prompt": "Order the steps", "items": ["read", "update", "write"], "explanation": "Read first."}
      ]}
      </script>
    </section>
  </main>
</body>
</html>
````

### 22.3 `tools/tests/fixtures/bad-lesson.html`

````html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Bad fixture</title></head>
<body data-page="lesson" data-lesson-id="m99-l02" data-root="../../">
  <main id="main">
    <figure class="example" id="ex-wrong">
      <script type="text/x-python">
      print(sorted({"b": 2, "a": 1}))
      </script>
      <script type="text/x-output">
      ['b', 'a']
      </script>
    </figure>
    <figure class="example" id="ex-seed">
      <script type="text/x-python">
      print({"apple", "banana", "cherry", "date", "elderberry", "fig"})
      </script>
      <script type="text/x-output">
      {'apple'}
      </script>
    </figure>
    <figure class="example" id="ex-crash">
      <script type="text/x-python">
      print(1 / 0)
      </script>
      <script type="text/x-output">
      inf
      </script>
    </figure>
    <script type="text/x-python">
    def broken(:
        pass
    </script>
    <section class="exercises" id="exercises">
      <article class="exercise" id="m99-l02-e1" data-kind="function" data-file="e1_same.py">
        <h3>Already solved</h3>
        <script type="text/x-python" data-role="starter">
        def one():
            return 1
        </script>
        <script type="text/x-python" data-role="tests">
        from e1_same import one

        def test_one():
            assert one() == 1
        </script>
        <script type="text/x-python" data-role="solution">
        def one():
            return 1
        </script>
      </article>
    </section>
    <section class="quiz" id="m99-l02-quiz">
      <script type="application/json" class="quiz-spec">
      {"id": "m99-l02-quiz", "questions": [
        {"type": "predict", "prompt": "What prints?", "code": "print(len({'a': 1, 'a': 2}))", "answer": "2", "explanation": "x"},
        {"type": "mcq", "prompt": "?", "options": ["a", "a"], "answer": 3, "explanation": "x"}
      ]}
      </script>
    </section>
  </main>
</body>
</html>
````

### 22.4 `examples/spec05-examples.html`

The validated exercise patterns of `spec/05` §11 as one page; `ci.py` re-checks it on every run.

````html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>spec/05 validated examples</title></head>
<body data-page="lesson" data-lesson-id="spec05" data-root="../">
<main id="main">

<section id="program-exercise">
<article class="exercise" id="m01-l03-e1" data-kind="program" data-file="e1_split_bill.py">
  <h3>Exercise 1 · Split the bill</h3>
  <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
  <div class="exercise-task">
    <p>Read three lines: the total bill, the number of people and the tip percentage. Print each person's share with two decimals, exactly like this: <code>Each person pays 23.10</code></p>
  </div>
  <script type="text/x-python" data-role="starter">
  total = float(input("Total bill: "))
  # read the number of people and the tip percentage the same way
  # work out each person's share, then print it
  </script>
  <script type="text/x-python" data-role="tests">
  import pytest
  from course_helpers import run_program

  CASES = [
      ("63\n3\n10\n", "Each person pays 23.10"),
      ("50\n1\n0\n", "Each person pays 50.00"),
      ("100\n3\n0\n", "Each person pays 33.33"),
      ("45.5\n2\n15\n", "Each person pays 26.16"),
      ("0\n4\n20\n", "Each person pays 0.00"),
  ]


  @pytest.mark.parametrize("typed, expected", CASES)
  def test_prints_each_share(typed, expected):
      printed = run_program("e1_split_bill.py", stdin=typed)
      last_line = printed.strip().splitlines()[-1]
      assert last_line.endswith(expected), f"typed {typed!r}: expected a line ending {expected!r}, got {last_line!r}"
  </script>
  <script type="text/x-python" data-role="solution">
  total = float(input("Total bill: "))
  people = int(input("People: "))
  tip = float(input("Tip %: "))
  share = total * (1 + tip / 100) / people
  print(f"Each person pays {share:.2f}")
  </script>
  <ol class="hints">
    <li>Read each line with <code>input()</code> and convert it: <code>float</code> for money and percentages, <code>int</code> for people.</li>
    <li>The total including the tip is <code>total * (1 + tip / 100)</code>.</li>
    <li>Print with two decimals: <code>print(f"Each person pays {share:.2f}")</code>.</li>
  </ol>
</article>
</section>

<section id="data-exercise">
<article class="exercise" id="m12-l06-e1" data-kind="function" data-file="e1_revenue.py" data-requires="pandas">
  <h3>Exercise 1 · Revenue by category</h3>
  <p class="ex-meta">★★☆ · 15 points · AI help: explain only</p>
  <div class="exercise-task">
    <p>Write <code>revenue_by_category(df)</code> that returns a Series of total revenue (<code>units × unit_price</code>) per category, largest first, named <code>"revenue"</code>. Don't change <code>df</code>.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  import pandas as pd


  def revenue_by_category(df: pd.DataFrame) -> pd.Series:
      """Total revenue (units x unit_price) per category, largest first."""
      ...
  </script>
  <script type="text/x-python" data-role="tests">
  import pandas as pd
  import pytest
  from pandas.testing import assert_frame_equal

  from e1_revenue import revenue_by_category


  @pytest.fixture
  def orders():
      return pd.DataFrame({
          "category": ["books", "games", "books", "music", "games", "books"],
          "units": [2, 1, 1, 3, 2, 5],
          "unit_price": [12.5, 60.0, 8.0, 9.99, 55.0, 10.0],
      })


  def test_correct_totals(orders):
      assert revenue_by_category(orders).to_dict() == pytest.approx({"games": 170.0, "books": 83.0, "music": 29.97})


  def test_largest_first(orders):
      assert list(revenue_by_category(orders).index) == ["games", "books", "music"], "finish with sort_values(ascending=False)"


  def test_named_revenue(orders):
      assert revenue_by_category(orders).name == "revenue"


  def test_leaves_the_input_unchanged(orders):
      before = orders.copy()
      revenue_by_category(orders)
      assert_frame_equal(orders, before)


  def test_zero_units_and_one_category():
      df = pd.DataFrame({"category": ["x", "x"], "units": [0, 3], "unit_price": [9.0, 1.5]})
      assert revenue_by_category(df).to_dict() == pytest.approx({"x": 4.5})
  </script>
  <script type="text/x-python" data-role="solution">
  import pandas as pd


  def revenue_by_category(df: pd.DataFrame) -> pd.Series:
      """Total revenue (units x unit_price) per category, largest first."""
      revenue = df["units"] * df["unit_price"]
      return revenue.groupby(df["category"]).sum().sort_values(ascending=False).rename("revenue")
  </script>
  <ol class="hints">
    <li>Multiply the two columns to get a revenue Series: <code>df["units"] * df["unit_price"]</code>.</li>
    <li>Group that Series by the category column and sum: <code>revenue.groupby(df["category"]).sum()</code>.</li>
    <li>Chain <code>.sort_values(ascending=False).rename("revenue")</code>.</li>
  </ol>
</article>
</section>

<section id="model-exercise">
<article class="exercise" id="m16-l02-e1" data-kind="function" data-file="e1_knn.py" data-requires="sklearn">
  <h3>Exercise 1 · A k-NN pipeline that generalises</h3>
  <p class="ex-meta">★★☆ · 15 points · AI help: explain only</p>
  <div class="exercise-task">
    <p>Write <code>make_knn(k)</code> returning an <em>unfitted</em> scikit-learn <code>Pipeline</code> that scales the features, then classifies with k-NN. The tests train it on the wine data and score it on a split you never see.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  from sklearn.neighbors import KNeighborsClassifier
  from sklearn.pipeline import Pipeline


  def make_knn(k: int) -> Pipeline:
      """Scale the features, then classify with k-NN. Return it unfitted."""
      return Pipeline([("knn", KNeighborsClassifier(n_neighbors=k))])
  </script>
  <script type="text/x-python" data-role="tests">
  from sklearn.datasets import load_wine
  from sklearn.dummy import DummyClassifier
  from sklearn.model_selection import train_test_split
  from sklearn.pipeline import Pipeline
  from sklearn.preprocessing import MinMaxScaler, StandardScaler

  from e1_knn import make_knn


  def split(seed):
      X, y = load_wine(return_X_y=True)
      return train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)


  def test_returns_an_unfitted_pipeline():
      model = make_knn(5)
      assert isinstance(model, Pipeline)
      assert not hasattr(model[-1], "classes_"), "return the pipeline without calling fit"


  def test_uses_k():
      assert make_knn(7)[-1].n_neighbors == 7


  def test_scales_the_features_first():
      assert isinstance(make_knn(5)[0], (StandardScaler, MinMaxScaler)), "k-NN compares distances: put a scaler first"


  def test_beats_the_majority_baseline_by_20_points():
      Xtr, Xte, ytr, yte = split(7)
      baseline = DummyClassifier().fit(Xtr, ytr).score(Xte, yte)
      assert make_knn(5).fit(Xtr, ytr).score(Xte, yte) >= baseline + 0.20


  def test_generalises_to_a_split_you_never_saw():
      Xtr, Xte, ytr, yte = split(11)
      accuracy = make_knn(5).fit(Xtr, ytr).score(Xte, yte)
      assert accuracy >= 0.90, f"accuracy on unseen data is {accuracy:.2f}; did you scale the features?"
  </script>
  <script type="text/x-python" data-role="solution">
  from sklearn.neighbors import KNeighborsClassifier
  from sklearn.pipeline import Pipeline
  from sklearn.preprocessing import StandardScaler


  def make_knn(k: int) -> Pipeline:
      """Scale the features, then classify with k-NN. Return it unfitted."""
      return Pipeline([("scale", StandardScaler()), ("knn", KNeighborsClassifier(n_neighbors=k))])
  </script>
  <ol class="hints">
    <li>A Pipeline is a list of named steps: <code>Pipeline([("scale", ...), ("knn", ...)])</code>.</li>
    <li>Use <code>StandardScaler()</code> for the first step.</li>
    <li>Return the pipeline without calling <code>fit</code>: the tests fit it.</li>
  </ol>
</article>
</section>

<section id="sql-exercise">
<article class="exercise" id="m15-l01-e1" data-kind="function" data-file="e1_top_customers.py">
  <h3>Exercise 1 · Top customers (SQL)</h3>
  <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
  <div class="exercise-task">
    <p>Set <code>QUERY</code> to SQL that returns the 3 customers who spent the most: columns <code>customer</code> and <code>total</code> (rounded to 2 decimals), highest first.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  QUERY = """
  SELECT customer
  FROM orders
  """
  </script>
  <script type="text/x-python" data-role="tests">
  import sqlite3

  import pytest

  from e1_top_customers import QUERY

  ROWS = [("Aisyah", 120.0), ("Ben", 35.5), ("Aisyah", 60.0), ("Chen", 99.9), ("Ben", 10.0), ("Dev", 250.0)]


  def database(rows):
      conn = sqlite3.connect(":memory:")
      conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT, amount REAL)")
      conn.executemany("INSERT INTO orders (customer, amount) VALUES (?, ?)", rows)
      return conn


  @pytest.fixture
  def conn():
      return database(ROWS)


  def test_returns_the_top_three(conn):
      assert conn.execute(QUERY).fetchall() == [("Dev", 250.0), ("Aisyah", 180.0), ("Chen", 99.9)]


  def test_column_names(conn):
      assert [d[0] for d in conn.execute(QUERY).description] == ["customer", "total"], "name the sum with AS total"


  def test_does_not_change_the_data(conn):
      conn.execute(QUERY).fetchall()
      assert conn.execute("SELECT COUNT(*) FROM orders").fetchall() == [(6,)]


  def test_works_on_other_data():
      other = database([("Eve", 5), ("Eve", 5), ("Fay", 7), ("Gus", 1), ("Hal", 2)])
      assert other.execute(QUERY).fetchall() == [("Eve", 10.0), ("Fay", 7.0), ("Hal", 2.0)]
  </script>
  <script type="text/x-python" data-role="solution">
  QUERY = """
  SELECT customer, ROUND(SUM(amount), 2) AS total
  FROM orders
  GROUP BY customer
  ORDER BY total DESC
  LIMIT 3
  """
  </script>
  <ol class="hints">
    <li>Group the rows by customer and add up the amounts: <code>GROUP BY customer</code> with <code>SUM(amount)</code>.</li>
    <li>Sort with <code>ORDER BY total DESC</code> and keep three rows with <code>LIMIT 3</code>.</li>
    <li>Round in SQL: <code>ROUND(SUM(amount), 2) AS total</code>.</li>
  </ol>
</article>
</section>

<section id="plot-exercise">
<article class="exercise" id="m13-l01-e1" data-kind="function" data-file="e1_monthly_chart.py" data-requires="matplotlib pandas">
  <h3>Exercise 1 · Monthly sales chart</h3>
  <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
  <div class="exercise-task">
    <p>Write <code>plot_monthly_sales(df)</code>: a line chart of <code>sales</code> by <code>month</code> titled "Monthly sales", with axis labels "Month" and "Sales (units)". Return the <code>Axes</code>.</p>
  </div>
  <script type="text/x-python" data-role="starter">
  import matplotlib.pyplot as plt


  def plot_monthly_sales(df):
      """Line chart of sales by month with a title and axis labels. Return the Axes."""
      fig, ax = plt.subplots()
      # your code here
      return ax
  </script>
  <script type="text/x-python" data-role="tests">
  import matplotlib

  matplotlib.use("Agg")  # draw off-screen: no windows pop up during the tests
  import matplotlib.axes  # noqa: E402
  import matplotlib.pyplot as plt  # noqa: E402
  import pandas as pd  # noqa: E402
  import pytest  # noqa: E402

  from e1_monthly_chart import plot_monthly_sales  # noqa: E402

  SALES = [12, 15, 14, 18, 21, 25, 24, 22, 20, 19, 23, 30]


  @pytest.fixture
  def ax():
      axes = plot_monthly_sales(pd.DataFrame({"month": range(1, 13), "sales": SALES}))
      yield axes
      plt.close("all")


  def test_returns_an_axes(ax):
      assert isinstance(ax, matplotlib.axes.Axes), "create it with fig, ax = plt.subplots() and return ax"


  def test_title_and_labels(ax):
      assert ax.get_title() == "Monthly sales"
      assert (ax.get_xlabel(), ax.get_ylabel()) == ("Month", "Sales (units)")


  def test_one_line_with_twelve_points(ax):
      assert len(ax.get_lines()) == 1
      assert len(ax.get_lines()[0].get_xdata()) == 12


  def test_plots_the_sales_column(ax):
      assert list(ax.get_lines()[0].get_ydata()) == SALES, "plot the sales column on the y-axis"
  </script>
  <script type="text/x-python" data-role="solution">
  import matplotlib.pyplot as plt


  def plot_monthly_sales(df):
      """Line chart of sales by month with a title and axis labels. Return the Axes."""
      fig, ax = plt.subplots(figsize=(7, 3.5))
      ax.plot(df["month"], df["sales"], marker="o")
      ax.set_title("Monthly sales")
      ax.set_xlabel("Month")
      ax.set_ylabel("Sales (units)")
      ax.set_xticks(range(1, 13))
      return ax
  </script>
  <ol class="hints">
    <li>Start with <code>fig, ax = plt.subplots()</code> and draw with <code>ax.plot(x, y)</code>.</li>
    <li>Use <code>ax.set_title</code>, <code>ax.set_xlabel</code> and <code>ax.set_ylabel</code>.</li>
    <li><code>ax.plot(df["month"], df["sales"], marker="o")</code> draws one line with a dot per month.</li>
  </ol>
</article>
</section>

<section id="write-tests-exercise">
<article class="exercise" id="m04-l07-e1" data-kind="write_tests" data-file="e1_leap.py">
  <h3>Exercise 1 · Write tests that catch bugs</h3>
  <p class="ex-meta">★★☆ · 15 points · AI help: hints only</p>
  <div class="exercise-task">
    <p><code>e1_leap.py</code> contains a correct <code>is_leap_year(year)</code>. Write tests in <code>test_e1_leap.py</code> that pass on it and fail on each of three buggy versions we hide behind the scenes.</p>
  </div>
  <script type="text/x-python" data-role="target">
  def is_leap_year(year: int) -> bool:
      """Gregorian rule: every 4th year, except centuries, except every 400th year."""
      return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
  </script>
  <script type="text/x-python" data-role="starter">
  from e1_leap import is_leap_year


  def test_a_typical_leap_year():
      ...  # replace with an assert
  </script>
  <script type="text/x-python" data-role="solution">
  import pytest

  from e1_leap import is_leap_year


  @pytest.mark.parametrize("year, expected", [
      (2024, True),    # divisible by 4
      (2023, False),   # not divisible by 4
      (1900, False),   # century: not a leap year
      (2000, True),    # every 400th year is
  ])
  def test_gregorian_rule(year, expected):
      assert is_leap_year(year) is expected
  </script>
  <script type="application/json" data-role="mutants">
  {"treats every 4th year as a leap year (forgets centuries)": "def is_leap_year(year):\n    return year % 4 == 0\n",
   "forgets the 400-year exception": "def is_leap_year(year):\n    return year % 4 == 0 and year % 100 != 0\n",
   "says every year is a leap year": "def is_leap_year(year):\n    return True\n"}
  </script>
  <ol class="hints">
    <li>Each bug is wrong for one kind of year. Which years does each rule of the definition talk about?</li>
    <li>You need at least: an ordinary leap year, an ordinary non-leap year, a century, and a 400th year.</li>
    <li>Try 2024, 2023, 1900 and 2000.</li>
  </ol>
</article>
</section>

<section class="quiz" id="spec05-quiz">
  <h2>A quiz with every question type</h2>
  <script type="application/json" class="quiz-spec">
  {"id": "spec05-quiz", "questions": [
    {"type": "mcq", "prompt": "Which call reads a whole text file as one string?",
     "options": ["<code>Path('a.txt').read_text()</code>", "<code>Path('a.txt').read()</code>", "<code>open('a.txt').readlines()</code>"],
     "answer": 0, "explanations": ["Right.", "<code>Path</code> has no <code>read()</code> method.", "<code>readlines()</code> returns a list of lines."]},
    {"type": "multi", "prompt": "Which of these are immutable?", "options": ["<code>tuple</code>", "<code>list</code>", "<code>str</code>", "<code>dict</code>"],
     "answer": [0, 2], "explanation": "Tuples and strings can't be changed in place; lists and dicts can."},
    {"type": "predict", "prompt": "What does this print?", "code": "nums = [3, 1, 2]\nnums.sort()\nprint(nums[-1], len(nums))",
     "answer": "3 3", "explanation": "<code>sort()</code> sorts in place; the last item is now the largest."},
    {"type": "short", "prompt": "Which built-in returns the number of items in a list?", "accept": ["len", "len()"],
     "accept_regex": "^len(\\(\\))?$", "explanation": "<code>len(items)</code>."},
    {"type": "order", "prompt": "Put the debugging loop in order.", "items": ["Reproduce the bug", "Isolate where it happens", "Form a hypothesis", "Test the fix"],
     "explanation": "Reproduce, isolate, hypothesise, test."}
  ]}
  </script>
</section>

</main>
</body>
</html>
````

## 23. Requirements

Every library the course uses is pinned with `==` to its newest release that installs on Python 3.15, checked on 2026-11-23: each learner file was resolved for Python 3.15 (`uv pip compile`), and the union was installed into a fresh 3.15.2 environment and passed `check_libraries.py`. Everything resolves to wheels on Linux (x86-64, glibc 2.39), on macOS 15 or later on Apple Silicon, and on Windows (x64), except two pure-Python packages that install from source anywhere without a compiler: PySpark (electives) and ANTLR's Python runtime (`antlr4-python3-runtime`, which DVC needs through Hydra). faiss-cpu has no Windows wheels, so its pin carries the marker `sys_platform != "win32"` (`spec/02` §5). Each library appears in exactly one learner file; learners install the files in order as they reach each phase (`site/setup.html` §6). The builder's file includes all six. Libraries that do not install on 3.15 yet are in `spec/02` §5 (not pinned, taught as overview).

### 23.1 `tools/requirements-dev.txt`

````text
# Everything a course builder needs: every library the pages use, so CI can run every
# example, session, exercise and notebook check (Python 3.15). From the repository root:
#   python -m pip install -r tools/requirements-dev.txt
-r ../site/downloads/requirements-tools.txt
-r ../site/downloads/requirements-core.txt
-r ../site/downloads/requirements-ml.txt
-r ../site/downloads/requirements-deep-learning.txt
-r ../site/downloads/requirements-production.txt
-r ../site/downloads/requirements-electives.txt
````

### 23.2 `site/downloads/requirements-tools.txt`

````text
# Testing and code-quality tools, used from the first lesson (Phases 0-2). Python 3.15.
# Install into your course virtual environment:
#   python -m pip install -r requirements-tools.txt
pytest==9.2.0
pytest-cov==7.1.0
hypothesis==6.170.17
ruff==0.17.6
mypy==2.4.1
pre-commit==4.7.0
````

### 23.3 `site/downloads/requirements-core.txt`

````text
# Data-science libraries for Phases 3-4 (Python 3.15). Install after requirements-tools.txt:
#   python -m pip install -r requirements-core.txt
# Arrays and tables (M11, M12, M15)
numpy==2.5.5
pandas==3.1.1
pyarrow==26.0.1
polars==2.1.0
duckdb==2.0.1
# Charts (M11, M13)
matplotlib==3.11.2
seaborn==0.13.2
plotly==7.1.0
altair==6.3.0
# Statistics and machine learning (M14, M16-M19)
scipy==1.18.1
statsmodels==0.15.0
scikit-learn==1.9.1
# Notebooks (from M11)
jupyterlab==4.6.6
# Files, web APIs, scraping, databases, validation (M15)
requests==2.34.2
httpx==0.28.1
beautifulsoup4==4.15.0
lxml==6.1.3
pydantic==2.14.4
sqlalchemy==2.1.9
pandera==0.36.0
pyyaml==6.0.4
python-dotenv==1.2.4
rich==15.0.0
````

### 23.4 `site/downloads/requirements-ml.txt`

````text
# Machine-learning extras for Phase 4 (Python 3.15). Install after requirements-core.txt:
#   python -m pip install -r requirements-ml.txt
xgboost==3.4.1
lightgbm==4.7.0
shap==0.54.1
optuna==5.1.0
imbalanced-learn==0.14.2
umap-learn==0.6.0
mlflow==3.18.0
````

### 23.5 `site/downloads/requirements-deep-learning.txt`

````text
# Deep learning, NLP and LLM apps for Phase 5 (Python 3.15). Install after requirements-ml.txt:
#   python -m pip install -r requirements-deep-learning.txt
# Every graded exercise runs on the CPU. On Linux the default torch build also downloads the
# NVIDIA CUDA libraries (about 4 GB); without an NVIDIA GPU, install torch first with the
# CPU-only command from https://pytorch.org/get-started/locally/ and then run this file.
torch==2.15.0
torchvision==0.29.2
transformers==5.24.0
datasets==5.2.0
tokenizers==0.23.3
tiktoken==0.14.0
sentence-transformers==6.3.0
faiss-cpu==1.16.0; sys_platform != "win32"  # no Windows wheels: Windows learners use WSL 2 for M23-L05 (spec/02 section 5)
bm25s==0.3.16
anthropic==2.12.0
openai==3.57.0
mcp==2.3.0
````

### 23.6 `site/downloads/requirements-production.txt`

````text
# Deployment and MLOps for Phase 6 (Python 3.15). Install after requirements-deep-learning.txt:
#   python -m pip install -r requirements-production.txt
fastapi==0.165.0
uvicorn==0.54.0
streamlit==1.67.0
gradio==6.32.0
skops==0.16.0
onnx==1.23.2
skl2onnx==1.20.0
river==0.27.0
locust==2.47.0
dvc==3.67.1
````

### 23.7 `site/downloads/requirements-electives.txt`

````text
# Elective modules E1-E7 (Python 3.15). Install after requirements-core.txt:
#   python -m pip install -r requirements-electives.txt
prophet==1.5.0
opencv-python==5.1.0.95
gymnasium==1.4.0
networkx==3.7
geopandas==1.2.0
shapely==2.2.0
# E4: PySpark installs from source (pure Python, no compiler needed) and needs Java 17 or later.
pyspark==4.3.0
````

## 24. Workflows

### 24.1 `.github/workflows/site.yml`

Runs on GitHub only. A push to `main` (or a pull request) runs `python tools/ci.py --partial`, so the site publishes while the course is being built: every page that exists is checked in full, and course-wide coverage that isn't built yet is reported as pending. Running the workflow by hand with `release` ticked runs the full `python tools/ci.py` (`spec/11` Stage 9). The deploy job runs only for `main`. Its steps match what was run locally before assembly, except the first install step: it fetches the CPU build of the pinned PyTorch from PyTorch's own index (the default Linux build adds about 4 GB of CUDA libraries), which the verifying sandbox could not reach. If that step fails, delete it: the next step installs the default build from PyPI, which was verified.

````yaml
name: Check and publish the course
on:
  push: { branches: [main] }
  pull_request:
  workflow_dispatch:
    inputs:
      release:
        description: "Release check: every course-wide coverage target must be complete"
        type: boolean
        default: false
permissions: { contents: read, pages: write, id-token: write }
concurrency: { group: pages, cancel-in-progress: false }
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.15"
          cache: pip
          cache-dependency-path: |
            tools/requirements-dev.txt
            site/downloads/requirements-*.txt
      # The CPU build of the pinned PyTorch first (the default Linux build adds about 4 GB of
      # CUDA libraries), then every other pinned library. PySpark uses the runner's Java 17.
      - run: >-
          grep -E '^torch(vision)?==' site/downloads/requirements-deep-learning.txt
          | xargs python -m pip install --index-url https://download.pytorch.org/whl/cpu
      - run: python -m pip install -r tools/requirements-dev.txt
      - uses: actions/setup-node@v7
        with: { node-version: 22 }
      - run: npm install --no-save puppeteer-core@25 axe-core@4.14.1
      # Pushes publish whatever is built so far: --partial reports course-wide coverage that isn't
      # built yet as "pending", and checks every page that exists in full. Run the workflow by hand
      # with "release" ticked for the full release check (spec/11 Stage 9).
      - run: python tools/ci.py ${{ !inputs.release && '--partial' || '' }}
        env: { CHROME_PATH: /usr/bin/google-chrome }
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: check
    runs-on: ubuntu-latest
    environment: { name: github-pages, url: "${{ steps.deployment.outputs.page_url }}" }
    steps:
      - uses: actions/checkout@v7
      - uses: actions/configure-pages@v6
      - uses: actions/upload-pages-artifact@v5
        with: { path: site }
      - id: deployment
        uses: actions/deploy-pages@v5
````

### 24.2 `.github/workflows/pins.yml`

Every Monday, and on demand: fails when `check_pins.py --strict` finds a pin that can move up. Move the pin, run `tools/check_libraries.py` and `tools/ci.py`, read every changed output (`check_content.py --update-outputs` shows them), and log the bump in `DECISIONS.md`.

````yaml
name: Check for newer library releases
on:
  schedule: [{ cron: "23 5 * * 1" }]  # Mondays: fails when a pin can move up
  workflow_dispatch:
permissions: { contents: read }
jobs:
  pins:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with: { python-version: "3.15" }
      - run: python -m pip install packaging
      - run: python tools/check_pins.py --strict
````

## 25. `tools/check_pins.py`

Needs network access to pypi.org (nothing else does). On 2026-11-23 it reported all 65 pins current.

````python
"""Find pinned libraries whose newer releases on PyPI can install on the course's Python.

  python tools/check_pins.py            # every requirements file in site/downloads
  python tools/check_pins.py --strict   # exit 1 if any pin can move up (the weekly workflow)
  python tools/check_pins.py FILE...    # only these files (-r includes are followed)

A release counts as usable when it has a wheel for the course's Python ("python" in
course.json) on any platform: a wheel for that version, an abi3 wheel for an older one, a
pure-Python wheel, or no wheels at all (a source-only release such as PySpark). Pre-releases
and yanked files are ignored. Newer releases that are not usable are listed, and the pin stays.
Needs network access to pypi.org; nothing else in CI does. After moving a pin, run
tools/check_libraries.py and tools/ci.py: a new release can change outputs on the pages.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "site" / "downloads"
PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)(\[[^\]]*\])?==([^\s;]+)")
WHEEL_TAG = re.compile(r"(cp|py)(\d)(\d*)")


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def read_pins(path: Path, seen: set[Path] | None = None) -> dict[str, tuple[str, Path]]:
    """name -> (pinned version, file) for every `name==version` line, following -r includes."""
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return {}
    seen.add(path)
    pins: dict[str, tuple[str, Path]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith(("-r ", "--requirement ")):
            pins.update(read_pins(path.parent / line.split(maxsplit=1)[1], seen))
        elif m := PIN.fullmatch(line.split(";", 1)[0].strip()):
            pins[canonical(m[1])] = (m[3], path)
        else:
            raise ValueError(f"{path.name}: not an exact pin (name==version): {line!r}")
    return pins


def installs_on(files: list[dict], python: str) -> bool:
    """True if this release can install on CPython `python` ("3.15") on some platform."""
    major, minor = (int(part) for part in python.split(".")[:2])
    files = [f for f in files if not f.get("yanked")]
    wheels = [f["filename"] for f in files if f["filename"].endswith(".whl")]
    if not wheels:  # source only: pure-Python projects such as PySpark build anywhere
        return any(f["filename"].endswith((".tar.gz", ".zip")) for f in files)
    for name in wheels:
        py_tags, abi, _platform = name[:-4].split("-")[-3:]
        for tag in py_tags.split("."):
            m = WHEEL_TAG.fullmatch(tag)
            if not m or int(m[2]) != major:
                continue
            kind, tag_minor = m[1], int(m[3]) if m[3] else None
            if kind == "py" and tag_minor in (None, minor) and abi == "none":
                return True
            if kind == "cp" and tag_minor == minor and abi in (f"cp{major}{minor}", "abi3", "none"):
                return True
            if kind == "cp" and abi == "abi3" and tag_minor is not None and tag_minor <= minor:
                return True
    return False


@dataclass
class Result:
    name: str
    pinned: str
    file: Path
    newest: str = ""                                  # newest usable release
    skipped: list[str] = field(default_factory=list)  # newer, but no wheel for the course's Python
    error: str = ""

    @property
    def status(self) -> str:
        if self.error:
            return "error"
        return "update" if Version(self.newest) > Version(self.pinned) else "current"


def fetch_pypi(name: str) -> dict:
    request = urllib.request.Request(f"https://pypi.org/pypi/{name}/json",
                                     headers={"User-Agent": "python-ai-course check_pins"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def check_one(name: str, pinned: str, file: Path, python: str, fetch) -> Result:
    result = Result(name, pinned, file, newest=pinned)
    try:
        releases = fetch(name)["releases"]
    except (OSError, ValueError, KeyError) as err:  # network, 404, bad JSON: report, carry on
        result.error = f"{type(err).__name__}: {err}"
        return result
    versions = []
    for text, files in releases.items():
        try:
            version = Version(text)
        except InvalidVersion:
            continue
        if not version.is_prerelease and files and version > Version(pinned):
            versions.append((version, text, files))
    for version, text, files in sorted(versions, reverse=True):
        if installs_on(files, python):
            result.newest = text
            break
        result.skipped.append(text)
    return result


def check(pins: dict[str, tuple[str, Path]], python: str, fetch=fetch_pypi, jobs: int = 8) -> list[Result]:
    with cf.ThreadPoolExecutor(jobs) as pool:
        futures = [pool.submit(check_one, name, version, file, python, fetch)
                   for name, (version, file) in sorted(pins.items())]
        return [f.result() for f in futures]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--strict", action="store_true", help="exit 1 when a pin can move up")
    ap.add_argument("--python", help="target Python (default: course.json)")
    args = ap.parse_args(argv)
    python = args.python or json.loads((ROOT / "course.json").read_text(encoding="utf-8"))["python"]
    pins: dict[str, tuple[str, Path]] = {}
    for file in args.files or sorted(DOWNLOADS.glob("requirements-*.txt")):
        pins.update(read_pins(file))
    results = check(pins, python)
    width = max(len(r.name) for r in results)
    for r in results:
        note = {"current": "current", "update": f"update to {r.newest}", "error": r.error}[r.status]
        if r.skipped:
            note += f" (skipped, no wheel for Python {python}: {', '.join(r.skipped[:3])}"
            note += "...)" if len(r.skipped) > 3 else ")"
        print(f"{r.name:<{width}}  {r.pinned:<12} {note}  [{r.file.name}]")
    updates = sum(r.status == "update" for r in results)
    errors = sum(r.status == "error" for r in results)
    print(f"\n{len(results)} pins for Python {python}: {updates} can move up, {errors} errors")
    if errors:
        return 2
    return 1 if args.strict and updates else 0


if __name__ == "__main__":
    raise SystemExit(main())
````

## 26. `tools/check_libraries.py`

Runs each check in its own process (about a minute with `-j 4`). Its functional checks double as the list of API generations the lessons must use: pandas 3 (Copy-on-Write, `str` dtype), DuckDB 2 (relations have no `fetchone()`), MCP 2 (`MCPServer`), transformers 5 (`dtype=`), MLflow 3 (`name=`), `torch.load` with `weights_only=True`, FastAPI lifespan, Gymnasium's 5-tuple `step()`, pytest 9's `[tool.pytest]` table. `spec/06` §9 lists them for authors.

````python
"""Check that every pinned library imports and works on this Python.

  python tools/check_libraries.py                 # all pins in tools/requirements-dev.txt
  python tools/check_libraries.py --skip-missing  # while building: skip libraries not installed
  python tools/check_libraries.py -j 8 torch      # only checks whose title contains "torch"

Each check runs in its own process, so one broken library cannot hide another. The checks
also pin down the API generation the lessons must use (pandas 3, DuckDB 2, MCP 2, ...):
if a check fails after a version bump, the matching lessons need the same change.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pins import ROOT, read_pins

DEV_REQUIREMENTS = ROOT / "tools" / "requirements-dev.txt"

IMPORTS = {  # distribution -> import name
    "pytest": "pytest", "pytest-cov": "pytest_cov", "hypothesis": "hypothesis", "ruff": "ruff",
    "mypy": "mypy", "pre-commit": "pre_commit",
    "numpy": "numpy", "pandas": "pandas", "pyarrow": "pyarrow", "polars": "polars", "duckdb": "duckdb",
    "matplotlib": "matplotlib", "seaborn": "seaborn", "plotly": "plotly", "altair": "altair",
    "scipy": "scipy", "statsmodels": "statsmodels", "scikit-learn": "sklearn", "jupyterlab": "jupyterlab",
    "requests": "requests", "httpx": "httpx", "beautifulsoup4": "bs4", "lxml": "lxml",
    "pydantic": "pydantic", "sqlalchemy": "sqlalchemy", "pandera": "pandera", "pyyaml": "yaml",
    "python-dotenv": "dotenv", "rich": "rich",
    "xgboost": "xgboost", "lightgbm": "lightgbm", "shap": "shap", "optuna": "optuna",
    "imbalanced-learn": "imblearn", "umap-learn": "umap", "mlflow": "mlflow",
    "torch": "torch", "torchvision": "torchvision", "transformers": "transformers", "datasets": "datasets",
    "tokenizers": "tokenizers", "tiktoken": "tiktoken", "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss", "bm25s": "bm25s", "anthropic": "anthropic", "openai": "openai", "mcp": "mcp",
    "fastapi": "fastapi", "uvicorn": "uvicorn", "streamlit": "streamlit", "gradio": "gradio",
    "skops": "skops", "onnx": "onnx", "skl2onnx": "skl2onnx", "river": "river", "locust": "locust",
    "dvc": "dvc",
    "prophet": "prophet", "opencv-python": "cv2", "gymnasium": "gymnasium", "networkx": "networkx",
    "geopandas": "geopandas", "shapely": "shapely", "pyspark": "pyspark",
}
CLI_ONLY = {"ruff", "locust"}  # checked by running them: ruff is a binary, locust patches sockets on import

CHECKS: dict[str, tuple[list[str], str]] = {}


def check(title: str, needs: str):
    def register(fn):
        CHECKS[title] = (needs.split(), textwrap.dedent(fn.__doc__))
        return fn
    return register


@check("pandas 3 and NumPy 2 semantics", "pandas numpy")
def _():
    """
    import numpy as np, pandas as pd
    s = pd.Series(["a", "b"])
    assert str(s.dtype) == "str", s.dtype                    # strings get the str dtype by default
    assert not hasattr(pd.DataFrame, "applymap") and not hasattr(pd.DataFrame, "append")
    df = pd.DataFrame({"k": ["x", "y", "x"], "v": [1, 2, 3]})
    column = df["v"]; column.iloc[0] = 99                    # Copy-on-Write: df itself is unchanged
    assert df.loc[0, "v"] == 1
    assert df.groupby("k")["v"].sum().to_dict() == {"x": 4, "y": 2}
    assert np.random.default_rng(0).integers(0, 10, 3).shape == (3,)
    assert not hasattr(np, "float_")                         # NumPy 2 removed the old aliases
    """


@check("Polars, DuckDB 2 and PyArrow", "polars duckdb pyarrow pandas")
def _():
    """
    import pathlib, tempfile
    import duckdb, pandas as pd, polars as pl, pyarrow as pa
    out = (pl.LazyFrame({"k": ["a", "b", "a"], "v": [1, 2, 3]})
           .group_by("k").agg(pl.col("v").sum()).sort("k").collect())
    assert out["v"].to_list() == [4, 2]
    path = pathlib.Path(tempfile.mkdtemp()) / "t.parquet"; out.write_parquet(path)
    assert duckdb.sql(f"select sum(v) from read_parquet('{path}')").fetchall() == [(6,)]
    df = pd.DataFrame({"v": [1, 2]})
    assert duckdb.sql("select sum(v) as s from df").df()["s"].tolist() == [3]
    assert not hasattr(duckdb.sql("select 1"), "fetchone")  # DuckDB 2: relations re-run, no fetchone()
    assert duckdb.connect().execute("select 2").fetchone() == (2,)
    assert pa.table({"a": [1]}).num_rows == 1
    """


@check("charts: Matplotlib, seaborn, Plotly, Altair", "matplotlib seaborn plotly altair")
def _():
    """
    import io, matplotlib
    matplotlib.use("Agg")
    import altair as alt, matplotlib.pyplot as plt, pandas as pd, plotly.express as px, seaborn as sns
    df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 3], "g": ["a", "b", "a"]})
    fig, ax = plt.subplots(); sns.barplot(df, x="g", y="y", ax=ax)
    buf = io.BytesIO(); fig.savefig(buf, format="png"); assert buf.getvalue()[:4] == b"\\x89PNG"
    assert "<div" in px.line(df, x="x", y="y").to_html(include_plotlyjs=False)
    assert '"mark"' in alt.Chart(df).mark_line().encode(x="x", y="y").to_json()
    """


@check("SciPy and statsmodels", "scipy statsmodels")
def _():
    """
    import numpy as np, pandas as pd, scipy.stats as st, statsmodels.formula.api as smf
    rng = np.random.default_rng(1)
    assert st.ks_2samp(rng.normal(size=200), rng.normal(size=200)).pvalue > 0.01
    df = pd.DataFrame({"x": np.arange(50.0)}); df["y"] = 2 * df.x + 1 + rng.normal(scale=0.1, size=50)
    assert abs(smf.ols("y ~ x", data=df).fit().params["x"] - 2) < 0.01
    """


@check("scikit-learn, skops, ONNX export and the ONNX reference runtime", "sklearn skops skl2onnx onnx")
def _():
    """
    import pathlib, tempfile
    import numpy as np, onnx, skops.io as sio
    from onnx.reference import ReferenceEvaluator
    from skl2onnx import to_onnx
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X, y = load_iris(return_X_y=True); X = X.astype(np.float32)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X, y)
    path = pathlib.Path(tempfile.mkdtemp()) / "model.skops"
    sio.dump(model, path)                                    # no pickle: types are checked on load
    back = sio.load(path, trusted=sio.get_untrusted_types(file=path))
    assert (back.predict(X) == model.predict(X)).all()
    onx = to_onnx(model, X[:1], options={"zipmap": False}); onnx.checker.check_model(onx)
    labels = ReferenceEvaluator(onx).run(None, {"X": X})[0]
    assert (labels == model.predict(X)).mean() > 0.99
    """


@check("XGBoost, LightGBM, SHAP, Optuna, imbalanced-learn, UMAP", "xgboost lightgbm shap optuna imblearn umap")
def _():
    """
    import lightgbm as lgb, optuna, shap, umap, xgboost as xgb
    from imblearn.over_sampling import SMOTE
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=300, n_features=8, weights=[0.85], random_state=0)
    m = xgb.XGBClassifier(n_estimators=20, max_depth=3, early_stopping_rounds=5, eval_metric="logloss")
    m.fit(X[:200], y[:200], eval_set=[(X[200:], y[200:])], verbose=False)
    lgb.LGBMClassifier(n_estimators=20, verbose=-1).fit(X, y, callbacks=[lgb.log_evaluation(0)])
    assert shap.TreeExplainer(m)(X[:10]).values.shape == (10, 8)
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(); study.optimize(lambda t: (t.suggest_float("x", -2, 2) - 1) ** 2, n_trials=15)
    Xr, yr = SMOTE(random_state=0).fit_resample(X, y); assert (yr == 1).sum() == (yr == 0).sum()
    assert umap.UMAP(n_neighbors=10, random_state=0).fit_transform(X[:100]).shape == (100, 2)
    """


@check("MLflow 3 tracking and model logging", "mlflow sklearn")
def _():
    """
    import inspect, tempfile, mlflow, mlflow.sklearn
    from sklearn.linear_model import LinearRegression
    mlflow.set_tracking_uri(f"sqlite:///{tempfile.mkdtemp()}/mlflow.db")
    assert "name" in inspect.signature(mlflow.sklearn.log_model).parameters   # MLflow 3: name=, not artifact_path=
    with mlflow.start_run():
        mlflow.log_param("alpha", 0.1); mlflow.log_metric("rmse", 1.5)
        info = mlflow.sklearn.log_model(LinearRegression().fit([[0], [1]], [0, 1]), name="model")
    assert round(float(mlflow.sklearn.load_model(info.model_uri).predict([[2]])[0]), 6) == 2.0
    """


@check("PyTorch and torchvision on the CPU", "torch torchvision")
def _():
    """
    import pickle, tempfile, torch
    from torchvision.transforms import v2
    torch.manual_seed(0)
    net = torch.nn.Sequential(torch.nn.Linear(4, 8), torch.nn.ReLU(), torch.nn.Linear(8, 1))
    opt = torch.optim.AdamW(net.parameters(), lr=0.01)
    x, y = torch.randn(64, 4), torch.randn(64, 1)
    for _ in range(5):
        opt.zero_grad(); torch.nn.functional.mse_loss(net(x), y).backward(); opt.step()
    img = torch.randint(0, 256, (3, 32, 32), dtype=torch.uint8)
    out = v2.Compose([v2.RandomResizedCrop(16), v2.ToDtype(torch.float32, scale=True)])(img)
    assert out.shape == (3, 16, 16) and out.dtype == torch.float32
    class Box: pass
    path = tempfile.mktemp(suffix=".pt"); torch.save({"box": Box()}, path)
    try:
        torch.load(path)                                     # weights_only=True is the default
        raise SystemExit("torch.load accepted an arbitrary object")
    except pickle.UnpicklingError:
        pass
    torch.save(net.state_dict(), path); net.load_state_dict(torch.load(path))
    """


@check("transformers 5, tokenizers, datasets, sentence-transformers (offline)",
       "transformers tokenizers datasets sentence_transformers torch")
def _():
    """
    import pathlib, tempfile, torch, transformers
    from datasets import Dataset
    from sentence_transformers import SentenceTransformer, models as st_models
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers
    from transformers import AutoModel, BertConfig, BertModel, PreTrainedTokenizerFast
    assert not hasattr(transformers, "TFAutoModel")          # transformers 5 is PyTorch-only
    folder = pathlib.Path(tempfile.mkdtemp())
    tok = Tokenizer(models.WordPiece(unk_token="[UNK]")); tok.pre_tokenizer = pre_tokenizers.Whitespace()
    special = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
    tok.train_from_iterator(["the cat sat", "the dog ran", "a cat ran"] * 20,
                            trainers.WordPieceTrainer(vocab_size=60, special_tokens=special))
    fast = PreTrainedTokenizerFast(tokenizer_object=tok, unk_token="[UNK]", pad_token="[PAD]",
                                   cls_token="[CLS]", sep_token="[SEP]", mask_token="[MASK]")
    config = BertConfig(vocab_size=fast.vocab_size, hidden_size=32, num_hidden_layers=1,
                        num_attention_heads=2, intermediate_size=37)
    BertModel(config).save_pretrained(folder); fast.save_pretrained(folder)
    model = AutoModel.from_pretrained(folder, dtype=torch.float16)   # dtype=, not torch_dtype=
    assert next(model.parameters()).dtype == torch.float16
    ds = Dataset.from_dict({"text": ["the cat", "a dog"]}).map(lambda b: fast(b["text"]), batched=True)
    assert "input_ids" in ds.column_names
    st = SentenceTransformer(modules=[st_models.Transformer(str(folder)), st_models.Pooling(32, "mean")])
    assert st.encode(["the cat sat"]).shape == (1, 32)
    """


@check("FAISS and bm25s retrieval", "faiss bm25s")
def _():
    """
    import bm25s, faiss, numpy as np
    xb = np.random.default_rng(0).random((100, 16), dtype=np.float32)
    index = faiss.IndexFlatL2(16); index.add(xb)
    _, ids = index.search(xb[:3], 2); assert (ids[:, 0] == [0, 1, 2]).all()
    corpus = ["the cat sat on the mat", "dogs chase cats", "python is a language"]
    retriever = bm25s.BM25(); retriever.index(bm25s.tokenize(corpus, show_progress=False), show_progress=False)
    docs, _ = retriever.retrieve(bm25s.tokenize(["python language"], show_progress=False), k=1, show_progress=False)
    assert int(docs[0, 0]) == 2
    """


@check("Anthropic and OpenAI SDKs, MCP 2 server", "anthropic openai mcp")
def _():
    """
    import asyncio, anthropic, openai
    from mcp.server.mcpserver import MCPServer               # MCP 2: FastMCP was renamed MCPServer
    a, o = anthropic.Anthropic(api_key="test"), openai.OpenAI(api_key="test")
    assert callable(a.messages.create) and callable(o.responses.create)
    server = MCPServer("demo")
    @server.tool()
    def add(a: int, b: int) -> int:
        "Add two integers."
        return a + b
    tools = asyncio.run(server.list_tools())
    assert [t.name for t in tools] == ["add"] and tools[0].input_schema["required"] == ["a", "b"]
    """


@check("FastAPI lifespan and TestClient", "fastapi httpx pydantic")
def _():
    """
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel
    state = {}
    @asynccontextmanager
    async def lifespan(app):
        state["model"] = "loaded"; yield; state.clear()
    app = FastAPI(lifespan=lifespan)
    class Item(BaseModel):
        x: float
    @app.post("/predict")
    def predict(item: Item):
        return {"y": item.x * 2, "model": state["model"]}
    with TestClient(app) as client:
        assert client.post("/predict", json={"x": 2}).json() == {"y": 4.0, "model": "loaded"}
        assert client.post("/predict", json={"x": "a"}).status_code == 422
    """


@check("Streamlit AppTest and Gradio Blocks", "streamlit gradio")
def _():
    """
    import gradio as gr
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_string("import streamlit as st\\nn = st.number_input('n', value=2)\\nst.write(n * 2)").run()
    assert not at.exception and "4" in at.markdown[0].value
    with gr.Blocks():
        box, out = gr.Textbox(), gr.Textbox(); box.submit(lambda s: s.upper(), box, out)
    """


@check("pydantic 2, SQLAlchemy 2, pandera, httpx, Beautiful Soup, PyYAML, dotenv, rich",
       "pydantic sqlalchemy pandera httpx bs4 lxml yaml dotenv rich")
def _():
    """
    import io, pathlib, tempfile
    import httpx, pandas as pd, pandera.pandas as pa, yaml
    from bs4 import BeautifulSoup
    from dotenv import dotenv_values
    from pydantic import BaseModel, field_validator
    from rich.console import Console
    from sqlalchemy import String, create_engine, select
    from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
    class User(BaseModel):
        name: str
        @field_validator("name")
        @classmethod
        def strip(cls, v): return v.strip()
    assert User.model_validate({"name": " ada "}).model_dump() == {"name": "ada"}
    class Base(DeclarativeBase): pass
    class Row(Base):
        __tablename__ = "rows"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(20))
    engine = create_engine("sqlite://"); Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Row(name="a")); session.commit()
        assert session.scalars(select(Row.name)).all() == ["a"]
    pa.DataFrameSchema({"x": pa.Column(int, pa.Check.ge(0))}).validate(pd.DataFrame({"x": [1]}))
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"ok": True})))
    assert client.get("https://example.test").json() == {"ok": True}
    assert BeautifulSoup("<p class='a'>hi</p>", "lxml").select_one("p.a").text == "hi"
    assert yaml.safe_load("a: 1") == {"a": 1}
    env = pathlib.Path(tempfile.mkdtemp()) / ".env"; env.write_text("KEY=value\\n")
    assert dotenv_values(env) == {"KEY": "value"}
    Console(file=io.StringIO()).print("[bold]ok[/]")
    """


@check("pytest 9 (native TOML config), pytest-cov, Hypothesis, mypy, ruff, pre-commit",
       "pytest pytest_cov hypothesis mypy pre_commit")
def _():
    """
    import pathlib, subprocess, sys, tempfile
    folder = pathlib.Path(tempfile.mkdtemp())
    (folder / "calc.py").write_text("def add(a: int, b: int) -> int:\\n    return a + b\\n")
    (folder / "check_calc.py").write_text(
        "from hypothesis import given, strategies as st\\nfrom calc import add\\n\\n\\n"
        "@given(st.integers(), st.integers())\\ndef check_add(a: int, b: int) -> None:\\n"
        "    assert add(a, b) == add(b, a)\\n")
    (folder / "pyproject.toml").write_text(  # [tool.pytest] is read only if it finds check_*.py
        '[tool.pytest]\\npython_files = ["check_*.py"]\\npython_functions = ["check_*"]\\n')
    def run(*args):
        done = subprocess.run([sys.executable, "-m", *args], cwd=folder, capture_output=True, text=True)
        assert done.returncode == 0, " ".join(args) + "\\n" + done.stdout + done.stderr
        return done.stdout
    assert "1 passed" in run("pytest", "-p", "no:cacheprovider", "--cov=calc")
    run("mypy", "--strict", "calc.py", "check_calc.py")
    run("ruff", "check", "calc.py"); run("ruff", "format", "--check", "calc.py")
    run("pre_commit", "--version")
    """


@check("Jupyter runs a notebook on this Python", "nbformat nbclient ipykernel")
def _():
    """
    import sys, nbformat
    from nbclient import NotebookClient
    nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("import sys; print(sys.version_info[:2])")])
    NotebookClient(nb, timeout=120, kernel_name="python3").execute()
    assert str(tuple(sys.version_info[:2])) in nb.cells[0].outputs[0]["text"]
    """


@check("DVC and Locust command lines", "dvc locust")
def _():
    """
    import subprocess, sys
    for module in ("dvc", "locust"):
        done = subprocess.run([sys.executable, "-m", module, "--version"], capture_output=True, text=True)
        assert done.returncode == 0, module + done.stdout + done.stderr
    """


@check("River streaming drift detection", "river numpy")
def _():
    """
    import numpy as np
    from river import drift
    rng = np.random.default_rng(0)
    stream = np.concatenate([rng.normal(0, 1, 1000), rng.normal(2, 1, 1000)])
    detector, first = drift.ADWIN(), None
    for i, x in enumerate(stream):
        detector.update(float(x))
        if detector.drift_detected and first is None:
            first = i
    assert first is not None and 1000 <= first < 1100, first
    """


@check("OpenCV, Gymnasium, NetworkX, GeoPandas and Shapely", "cv2 gymnasium networkx geopandas shapely")
def _():
    """
    import cv2, geopandas as gpd, gymnasium as gym, networkx as nx, numpy as np
    from shapely.geometry import Point
    img = np.zeros((32, 32, 3), np.uint8); cv2.circle(img, (16, 16), 8, (255, 255, 255), -1)
    assert cv2.imencode(".png", cv2.GaussianBlur(img, (5, 5), 0))[0]
    env = gym.make("CartPole-v1"); obs, info = env.reset(seed=0)
    assert len(env.step(env.action_space.sample())) == 5     # obs, reward, terminated, truncated, info
    assert nx.shortest_path(nx.Graph([(1, 2), (2, 3), (1, 3), (3, 4)]), 1, 4) == [1, 3, 4]
    gdf = gpd.GeoDataFrame({"n": [1, 2]}, geometry=[Point(0, 0), Point(1, 1)], crs="EPSG:4326")
    assert gdf.to_crs("EPSG:3857").buffer(10).area.gt(0).all()
    """


@check("Prophet fit and forecast", "prophet")
def _():
    """
    import logging, numpy as np, pandas as pd
    logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
    from prophet import Prophet
    ds = pd.date_range("2026-01-01", periods=90, freq="D")
    y = 10 + 0.1 * np.arange(90) + np.sin(np.arange(90) * 2 * np.pi / 7)
    model = Prophet(daily_seasonality=False).fit(pd.DataFrame({"ds": ds, "y": y}))
    assert len(model.predict(model.make_future_dataframe(periods=7))) == 97
    """


@check("PySpark local session with a Python UDF", "pyspark java")
def _():
    """
    import os, sys
    os.environ["PYSPARK_PYTHON"] = sys.executable            # workers must run the same Python
    from pyspark.sql import SparkSession, functions as F
    spark = (SparkSession.builder.master("local[1]").appName("check")
             .config("spark.ui.enabled", "false").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    df = spark.createDataFrame([("a", 1), ("b", 2), ("a", 3)], ["k", "v"])
    assert sorted(tuple(r) for r in df.groupBy("k").agg(F.sum("v")).collect()) == [("a", 4), ("b", 2)]
    plus_one = F.udf(lambda x: x + 1, "int")
    assert [r[0] for r in df.select(plus_one("v")).collect()] == [2, 3, 4]
    spark.stop()
    """


def available(name: str) -> bool:
    return shutil.which(name) is not None if name == "java" else importlib.util.find_spec(name) is not None


def import_script(dists: list[str]) -> str:
    lines = ["import importlib, importlib.metadata as md, subprocess, sys", "bad = []"]
    for dist in dists:
        if dist in CLI_ONLY:
            lines.append(f"r = subprocess.run([sys.executable, '-m', {IMPORTS[dist]!r}, '--version'], capture_output=True)\n"
                         f"bad += [] if r.returncode == 0 else [{dist!r}]")
        else:
            lines.append(f"try:\n    importlib.import_module({IMPORTS[dist]!r})\n"
                         f"except Exception as err:\n    bad.append(f'{dist} ({{type(err).__name__}}: {{err}})')")
    lines.append("assert not bad, 'failed: ' + ', '.join(bad)")
    return "\n".join(lines)


def run(title: str, code: str, timeout: int) -> tuple[str, bool, str, float]:
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as cwd:
        try:
            done = subprocess.run([sys.executable, "-c", code], cwd=cwd, capture_output=True,
                                  text=True, timeout=timeout, check=False)
            ok, out = done.returncode == 0, done.stdout + done.stderr
        except subprocess.TimeoutExpired:
            ok, out = False, f"timed out after {timeout} s"
    return title, ok, out.strip(), time.perf_counter() - start


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("only", nargs="*", help="run only checks whose title contains one of these words")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--skip-missing", action="store_true", help="skip checks whose libraries are absent")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args(argv)

    pinned = sorted(read_pins(DEV_REQUIREMENTS))
    unknown = [d for d in pinned if d not in IMPORTS]
    stale = [d for d in IMPORTS if d not in pinned]
    if unknown or stale:
        print(f"IMPORTS is out of step with {DEV_REQUIREMENTS.name}: add {unknown}, remove {stale}")
        return 1
    present = [d for d in pinned if available(IMPORTS[d])]  # find_spec does not import
    missing = sorted(set(pinned) - set(present))
    if missing and not args.skip_missing:
        print(f"not installed: {', '.join(missing)} (install {DEV_REQUIREMENTS.relative_to(ROOT)}, "
              "or pass --skip-missing)")
        return 1
    tasks = {f"import {len(present)} pinned libraries": import_script(present)}
    skipped = []
    for title, (needs, code) in CHECKS.items():
        if all(available(n) for n in needs):
            tasks[title] = code
        elif args.skip_missing:
            skipped.append(title)
        else:
            tasks[title] = f"raise SystemExit('needs: {' '.join(n for n in needs if not available(n))}')"
    if args.only:
        tasks = {t: c for t, c in tasks.items() if any(w.lower() in t.lower() for w in args.only)}

    print(f"Python {sys.version.split()[0]}: {len(tasks)} checks"
          + (f", {len(skipped)} skipped (libraries not installed)" if skipped else ""), flush=True)
    failed = 0
    with cf.ThreadPoolExecutor(args.jobs) as pool:
        for title, ok, out, secs in pool.map(lambda kv: run(*kv, args.timeout), tasks.items()):
            failed += not ok
            print(f"[{'PASS' if ok else 'FAIL'}] {title} ({secs:.0f} s)", flush=True)
            if not ok:
                print(textwrap.indent(out[-3000:], "    "))
    print("all checks passed" if not failed else f"{failed} checks failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
````
