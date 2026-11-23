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
