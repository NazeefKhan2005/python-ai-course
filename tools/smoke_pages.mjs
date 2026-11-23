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
