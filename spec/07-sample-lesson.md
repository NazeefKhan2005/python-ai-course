# 07 · Sample lesson: M03-L04 Dictionaries (the quality bar)

This is a finished lesson, built exactly as `spec/06` asks. Match its depth, structure, tone and level marking in every lesson. The file goes to `site/modules/m03-data-structures/l04-dictionaries.html`.

## 1. What it demonstrates

| Requirement (`spec/06`) | Where in the page |
|---|---|
| Anatomy in order | outcomes → run-locally → warm-up → teaching sections → reference → exercises → quiz → summary → completion + pager |
| Levels, honest and monotonic | 7 essential sections (why, create, keys, read, change, loop, patterns), 7 extra (merge, views, order, copying, typing, performance, frozendict), 4 advanced (matching, hood, readonly, missing); extra and advanced subsections, paragraphs, figures and callouts inside essential and extra sections; every reference row levelled (19 essential, 26 extra, 18 advanced) |
| Essentials-only path stands alone | With Show set to "Essentials", the page still teaches everything Exercises 1–3 need; Exercise 4 (optional) uses the counting pattern plus the performance idea |
| Complete coverage | 6 targets, 130 required names, all with rows: `class:dict` (31), `dict_keys` (23), `dict_values` (6), `dict_items` (23), `frozendict` (23), `types.MappingProxyType` (24); 63 rows in six task-grouped tables, plus `syntax:` rows |
| Current Python | Python 3.15 features taught as normal content with "New in 3.15" markers: `frozendict` (its own section and reference table) and merging with `{**d for d in dicts}`; older changes marked too (3.7 ordering, 3.8 `reversed`, 3.9 `\|`, 3.10 `match` and `view.mapping`) |
| Kind markers | 6 pitfalls (`{}` is not a set; 1/1.0/True; `in` checks keys; changing keys while looping; JSON keys; frozen is shallow), tips, a version note (3.7 ordering), under the hood, on the job, interview, performance |
| Verified output | 28 examples (each run twice with different hash seeds), 9 interactive sessions (doctest), 5 examples that end in a real error on purpose (`data-raises`), 3 predict-first examples (`data-predict`). (Data-file examples, `x-file`, are shown in `spec/05` §11 and the tools' test fixtures.) |
| Exercises | 4 pytest exercises (E4 optional, with a relative speed test that fails the `s.count` approach); sessions in each task run against the solution |
| Quizzes | Warm-up (2 questions on earlier lessons) and an end quiz of 7 questions covering all five types, one marked "Advanced" |

## 2. Check results when the kit was assembled (Python 3.15.2)

```text
check_site: 0 problem(s)
check_coverage: class:dict complete (31) · dict_keys complete (23) · dict_values complete (6) ·
                dict_items complete (23) · frozendict complete (23) · types.MappingProxyType complete (24)
check_content: 40 blocks compiled, 28 examples, 9 sessions, 4 exercises, 2 quizzes, 0 problem(s)
smoke_pages: 51 of 51 checks passed (headless Chrome, file://; axe-core WCAG 2.2 A/AA: 0 problems)
```

## 3. How it was built (repeat this for every lesson)

1. Read the M03-L04 row in `spec/curriculum/phase-1-foundations.md`: Essential, Extra & advanced, `Ref:` targets, exercises.
2. `python tools/api_skeleton.py class:dict` (and each other target) → draft rows with real signatures. Grouped them by task, wrote every description, set levels, removed every `TODO`.
3. Planned the teaching sections so the reference is the natural end point; ordered them essential → extra → advanced.
4. Wrote each example's code, then `python tools/check_content.py <page> --update-outputs` and read every output it wrote (Python's real message "cannot use 'list' as a dict key (unhashable type: 'list')" went straight into the text).
5. Wrote the exercises from the curriculum signatures; the checker proved each solution passes and each starter fails.
6. `python tools/build.py`, then `python tools/ci.py --partial`; read the page with Show set to "Essentials", "Core" and "Everything", in light and dark themes, at phone width.

## 4. The page

````html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dictionaries · M03 Core Data Structures · Python for AI</title>
  <meta name="description" content="Everything a Python dictionary can do: create, read, update and loop; counting and grouping; views, merging, copying, JSON, frozendict, type hints, pattern matching and how hash tables work.">
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
<body data-page="lesson" data-lesson-id="m03-l04" data-root="../../">
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
      <p class="breadcrumb">Phase 1 · M03 Core Data Structures · Lesson 4 of 7</p>
      <h1>Dictionaries: look things up by key</h1>
      <ul class="lesson-meta" aria-label="Lesson details">
        <li>⏱ Essentials 60 min · whole page about 2 h</li>
        <li>Level: Beginner, with advanced reference</li>
        <li>Needs: <a href="l01-lists.html">Lists</a>, <a href="l03-tuples.html">Tuples</a></li>
        <li>Python 3.15</li>
      </ul>

      <section class="outcomes" id="outcomes">
        <h2>What you'll be able to do</h2>
        <ul>
          <li>Create a dictionary in five ways and say which keys are allowed.</li>
          <li>Read, add, change and remove entries without surprise <code>KeyError</code>s.</li>
          <li>Loop over keys, values and pairs, and sort a dictionary by its values.</li>
          <li>Use the three everyday patterns: counting, grouping and lookup tables.</li>
          <li>Merge, copy, freeze and nest dictionaries, and move them to and from JSON.</li>
          <li>Explain why lookups are fast (hash tables) and look up any dictionary method in the reference.</li>
        </ul>
      </section>

      <section class="run-locally" id="run">
        <h2>Run the code yourself</h2>
        <p>Nothing on this page runs in your browser. Every example shows the exact output that Python 3.15 printed when the course was built, so you can trust it, and then check it yourself. New to running Python? Follow the <a href="../../setup.html">setup guide</a> first.</p>
        <ol>
          <li>Copy an example into a file (the <strong>Copy</strong> button), or click <strong>Download</strong> to save it with its file name.</li>
          <li>Run it in a terminal opened in the same folder:
            <script type="text/x-shell">
            {python} why_dicts.py
            </script>
          </li>
          <li>For the exercises, <a class="btn btn--small" data-pack href="../../downloads/m03-l04.zip" download>download the exercise pack</a>, unzip it, and run the tests:
            <script type="text/x-shell">
            cd m03-l04
            {pytest}
            </script>
          </li>
        </ol>
        <p>Blocks that start with <code>&gt;&gt;&gt;</code> are interactive sessions: start <code>python</code> with no file name and type the lines after the prompt. The lines without a prompt are what Python answers.</p>
      </section>

      <section class="quiz" id="m03-l04-warmup">
        <h2>Warm-up: remember the last lessons?</h2>
        <script type="application/json" class="quiz-spec">
        {"id": "m03-l04-warmup", "questions": [
          {"type": "mcq", "prompt": "Which list method adds one item to the end of a list?",
           "options": ["<code>append</code>", "<code>extend</code>", "<code>insert</code>", "<code>add</code>"], "answer": 0,
           "explanations": ["Right: <code>items.append(x)</code>.", "<code>extend</code> adds every item of another iterable.", "<code>insert(i, x)</code> adds at a position you choose.", "Lists have no <code>add</code>; sets do."]},
          {"type": "predict", "prompt": "What does this print?", "code": "first, *rest = (1, 2, 3)\nprint(rest)",
           "answer": "[2, 3]", "explanation": "Starred unpacking always collects the remaining items into a <em>list</em>, even from a tuple."}
        ]}
        </script>
      </section>

      <section id="why" data-level="essential">
        <h2>Why dictionaries?</h2>
        <p>A <dfn id="term-dictionary">dictionary</dfn> (<code>dict</code>) stores <em>key → value</em> pairs and finds a value from its key in one step. A list makes you search from the start; a dictionary jumps straight to the answer, however many entries it holds.</p>
        <figure class="example" id="ex-why-dicts" data-predict="">
          <script type="text/x-python" data-file="why_dicts.py">
          # A list of (name, phone) pairs: to find Grace we must search from the start.
          contacts = [("Ada", "555-0100"), ("Alan", "555-0199"), ("Grace", "555-0142")]
          for name, phone in contacts:
              if name == "Grace":
                  print("list search:", phone)
                  break

          # A dictionary jumps straight to the value stored under a key.
          phone_book = {"Ada": "555-0100", "Alan": "555-0199", "Grace": "555-0142"}
          print("dict lookup:", phone_book["Grace"])
          </script>
          <script type="text/x-output">
          list search: 555-0142
          dict lookup: 555-0142
          </script>
          <figcaption>Same answer, but the dictionary didn't look at Ada or Alan at all.</figcaption>
        </figure>
        <p>You will meet dictionaries everywhere: JSON from web APIs, configuration files, word counts, caches, rows of a dataset before they become a DataFrame, and the <code>{"role": ..., "content": ...}</code> messages sent to large language models.</p>
      </section>

      <section id="create" data-level="essential">
        <h2>Create a dictionary</h2>
        <p>Write pairs as <code>key: value</code> inside braces, separated by commas. <code>dict()</code> builds the same thing from keyword arguments, from a list of pairs, or from two lists zipped together.</p>
        <figure class="example" id="ex-create">
          <script type="text/x-python" data-file="create.py">
          empty = {}
          ages = {"Ada": 36, "Alan": 41}
          same = dict(Ada=36, Alan=41)              # keyword arguments become str keys
          from_pairs = dict([("Ada", 36), ("Alan", 41)])
          from_zip = dict(zip(["Ada", "Alan"], [36, 41]))
          squares = {n: n * n for n in range(4)}    # a dict comprehension (lesson 6)

          print(empty, len(empty))
          print(ages)
          print(ages == same == from_pairs == from_zip)
          print(squares)
          </script>
          <script type="text/x-output">
          {} 0
          {'Ada': 36, 'Alan': 41}
          True
          {0: 0, 1: 1, 2: 4, 3: 9}
          </script>
        </figure>
        <aside class="callout" data-kind="pitfall">
          <p><code>{}</code> is an empty <em>dictionary</em>, not an empty set. Write <code>set()</code> for an empty set (lesson 5).</p>
        </aside>
        <section id="create-fromkeys" data-level="extra">
          <h3>Same value for many keys: <code>dict.fromkeys</code></h3>
          <p><code>dict.fromkeys(keys, value)</code> gives every key the same starting value. It is safe for numbers, strings and <code>None</code>, but not for lists or other mutable values: all keys share <em>one</em> object.</p>
          <figure class="example" id="ex-fromkeys">
            <script type="text/x-python" data-file="fromkeys.py">
            flags = dict.fromkeys(["read", "write", "run"], False)
            print(flags)

            # Pitfall: every key shares the SAME list object.
            shared = dict.fromkeys(["a", "b"], [])
            shared["a"].append(1)
            print(shared)

            # Fix: build a new list for each key.
            separate = {key: [] for key in ["a", "b"]}
            separate["a"].append(1)
            print(separate)
            </script>
            <script type="text/x-output">
            {'read': False, 'write': False, 'run': False}
            {'a': [1], 'b': [1]}
            {'a': [1], 'b': []}
            </script>
          </figure>
          <p>A key that appears twice in one literal keeps its first position and its last value:</p>
          <figure class="session">
            <script type="text/x-pycon">
            >>> {"a": 1, "b": 2, "a": 3}
            {'a': 3, 'b': 2}
            >>> dict([("a", 1), ("a", 2)])
            {'a': 2}
            </script>
          </figure>
        </section>
      </section>

      <section id="keys" data-level="essential">
        <h2>What can be a key?</h2>
        <p>Keys must be <dfn id="term-hashable">hashable</dfn>: values that never change, such as numbers, strings, <code>True</code>/<code>False</code>, <code>None</code>, and tuples that contain only hashable values. Lists, sets and dictionaries can change, so they can't be keys. Values can be anything at all.</p>
        <figure class="example" id="ex-keys" data-raises="TypeError">
          <script type="text/x-python" data-file="keys.py">
          point_names = {(0, 0): "origin", (1, 0): "east"}   # tuples of immutable values work
          print(point_names[(0, 0)])

          grid = {}
          grid[[0, 0]] = "origin"   # a list can change, so it can't be a key
          </script>
          <script type="text/x-output">
          origin
          Traceback (most recent call last):
            ...
          TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
          </script>
          <figcaption>The error names the type that can't be a key. Convert it: <code>tuple([0, 0])</code> works.</figcaption>
        </figure>
        <aside class="callout" data-kind="pitfall" data-level="advanced">
          <p class="callout-title">1, 1.0 and True are the same key</p>
          <p>Keys are compared with <code>==</code>, and <code>1 == 1.0 == True</code>. Mixing them silently merges entries: the first key object stays, the last value wins. Keep keys of one type.</p>
          <script type="text/x-pycon">
          >>> {1: "int", 1.0: "float", True: "bool"}
          {1: 'bool'}
          >>> hash(1) == hash(1.0) == hash(True)
          True
          </script>
        </aside>
      </section>

      <section id="read" data-level="essential">
        <h2>Read values safely</h2>
        <p><code>d[key]</code> returns the value or raises <code>KeyError</code> if the key is missing. <code>key in d</code> tests whether a key exists, and <code>d.get(key, default)</code> returns a default instead of failing.</p>
        <figure class="example" id="ex-read" data-raises="KeyError" data-predict="">
          <script type="text/x-python" data-file="read.py">
          stock = {"apples": 12, "pears": 0}
          print(stock["apples"])          # the key must exist
          print("kiwis" in stock)         # membership tests keys, not values
          print(stock.get("kiwis"))       # missing: None
          print(stock.get("kiwis", 0))    # missing: your default
          print(len(stock))               # number of pairs
          print(stock["kiwis"])
          </script>
          <script type="text/x-output">
          12
          False
          None
          0
          2
          Traceback (most recent call last):
            ...
          KeyError: 'kiwis'
          </script>
        </figure>
        <aside class="callout" data-kind="tip">
          <p>Use <code>d[key]</code> when the key <em>must</em> be there: a missing key is a bug, and the error tells you at once. Use <code>d.get(key, default)</code> when a missing key is normal, such as an optional setting.</p>
        </aside>
        <aside class="callout" data-kind="pitfall">
          <p><code>in</code> looks at keys only. To search the values, ask the values view, which is slow on big dictionaries because it checks every value:</p>
          <script type="text/x-pycon">
          >>> stock = {"apples": 12, "pears": 0}
          >>> 0 in stock
          False
          >>> 0 in stock.values()
          True
          </script>
        </aside>
      </section>

      <section id="change" data-level="essential">
        <h2>Add, change and remove</h2>
        <p>Assigning to <code>d[key]</code> adds the key if it is new and replaces the value if it exists. There is no separate "add" method.</p>
        <figure class="example" id="ex-change">
          <script type="text/x-python" data-file="change.py">
          cart = {"apple": 2}
          cart["pear"] = 1                       # add a new key
          cart["apple"] = 5                      # replace the value of an existing key
          cart.update({"kiwi": 3, "pear": 2})    # add or replace many at once
          print(cart)

          del cart["kiwi"]                       # remove (KeyError if missing)
          removed = cart.pop("pear")             # remove and return the value
          missing = cart.pop("plum", 0)          # a default instead of KeyError
          print(cart, removed, missing)

          cart.clear()                           # remove everything
          print(cart)
          </script>
          <script type="text/x-output">
          {'apple': 5, 'pear': 2, 'kiwi': 3}
          {'apple': 5} 2 0
          {}
          </script>
        </figure>
        <section id="change-setdefault" data-level="extra">
          <h3><code>setdefault</code>, <code>popitem</code> and the forms of <code>update</code></h3>
          <p><code>d.setdefault(key, default)</code> returns the value if the key exists; otherwise it inserts the default and returns it. <code>d.popitem()</code> removes the most recently inserted pair (last in, first out), which makes a dictionary usable as a stack of pairs.</p>
          <figure class="example" id="ex-setdefault">
            <script type="text/x-python" data-file="setdefault.py">
            settings = {"theme": "dark"}
            print(settings.setdefault("theme", "light"))   # exists: returned, unchanged
            print(settings.setdefault("font", "mono"))     # missing: inserted
            print(settings)
            print(settings.popitem())                      # the LAST inserted pair
            print(settings)

            settings.update([("size", 12)], lang="en")     # pairs and keywords work too
            print(settings)
            </script>
            <script type="text/x-output">
            dark
            mono
            {'theme': 'dark', 'font': 'mono'}
            ('font', 'mono')
            {'theme': 'dark'}
            {'theme': 'dark', 'size': 12, 'lang': 'en'}
            </script>
          </figure>
          <p data-level="advanced"><code>popitem()</code> on an empty dictionary raises <code>KeyError: 'popitem(): dictionary is empty'</code>; <code>d.update(other)</code> accepts anything with a <code>keys()</code> method, or an iterable of two-item pairs.</p>
        </section>
      </section>

      <section id="loop" data-level="essential">
        <h2>Loop over a dictionary</h2>
        <p>Looping over a dictionary gives its keys. Ask for <code>.values()</code> or <code>.items()</code> to get the values or the <code>(key, value)</code> pairs. Order is the order the keys were first inserted, guaranteed by the language <span class="version" data-version="3.7" data-change="changed"></span>.</p>
        <figure class="example" id="ex-loop">
          <script type="text/x-python" data-file="loop.py">
          prices = {"apple": 0.5, "pear": 0.75, "kiwi": 0.6}

          for fruit in prices:                 # same as: for fruit in prices.keys()
              print(fruit, end=" ")
          print()

          for price in prices.values():
              print(price, end=" ")
          print()

          for fruit, price in prices.items():  # unpack each (key, value) pair
              print(f"{fruit:<6}{price:>5.2f}")
          </script>
          <script type="text/x-output">
          apple pear kiwi
          0.5 0.75 0.6
          apple  0.50
          pear   0.75
          kiwi   0.60
          </script>
        </figure>
        <section id="loop-sort" data-level="extra">
          <h3>Sort by key or by value</h3>
          <p>Dictionaries keep insertion order but have no <code>sort()</code> method. <code>sorted()</code> returns a sorted <em>list</em>; wrap it in <code>dict()</code> if you want a dictionary in that order.</p>
          <figure class="example" id="ex-sort">
            <script type="text/x-python" data-file="sort.py">
            scores = {"Ada": 91, "Alan": 78, "Grace": 95}
            print(sorted(scores))                                  # keys, alphabetically
            by_score = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
            print(by_score)
            print(dict(by_score))                                  # back to a dict, in that order
            print(max(scores, key=scores.get))                     # the key with the largest value
            </script>
            <script type="text/x-output">
            ['Ada', 'Alan', 'Grace']
            [('Grace', 95), ('Ada', 91), ('Alan', 78)]
            {'Grace': 95, 'Ada': 91, 'Alan': 78}
            Grace
            </script>
          </figure>
        </section>
        <aside class="callout" data-kind="pitfall">
          <p class="callout-title">Changing the keys while you loop</p>
          <p>Adding or deleting keys while looping over the same dictionary raises <code>RuntimeError</code>. Loop over a copy of the keys, <code>list(d)</code>, when you need to delete. Changing the <em>values</em> of existing keys is fine.</p>
          <figure class="example" id="ex-mutate" data-raises="RuntimeError">
            <script type="text/x-python" data-file="mutate.py">
            stock = {"apples": 12, "pears": 0, "kiwis": 0}
            for fruit in list(stock):        # loop over a COPY of the keys...
                if stock[fruit] == 0:
                    del stock[fruit]         # ...so deleting is safe
            print(stock)

            for fruit in stock:              # looping over the dict itself
                stock[fruit.upper()] = 1     # adding keys while looping
            </script>
            <script type="text/x-output">
            {'apples': 12}
            Traceback (most recent call last):
              ...
            RuntimeError: dictionary changed size during iteration
            </script>
          </figure>
        </aside>
      </section>

      <section id="patterns" data-level="essential">
        <h2>Three patterns you'll use every week</h2>
        <h3 id="pattern-count">Counting</h3>
        <p>Read the current count with a default of 0, add one, store it back:</p>
        <figure class="example" id="ex-count">
          <script type="text/x-python" data-file="count.py">
          votes = ["red", "blue", "red", "green", "red", "blue"]
          counts = {}
          for colour in votes:
              counts[colour] = counts.get(colour, 0) + 1
          print(counts)
          </script>
          <script type="text/x-output">
          {'red': 3, 'blue': 2, 'green': 1}
          </script>
        </figure>
        <h3 id="pattern-group">Grouping</h3>
        <p>A dictionary whose values are lists. <code>setdefault</code> creates each list the first time a key appears:</p>
        <figure class="example" id="ex-group">
          <script type="text/x-python" data-file="group.py">
          names = ["Ada", "Alan", "Grace", "Guido", "Barbara"]
          by_letter = {}
          for name in names:
              by_letter.setdefault(name[0], []).append(name)
          print(by_letter)
          </script>
          <script type="text/x-output">
          {'A': ['Ada', 'Alan'], 'G': ['Grace', 'Guido'], 'B': ['Barbara']}
          </script>
        </figure>
        <h3 id="pattern-index">Lookup tables</h3>
        <p>Turn a list of records into a dictionary keyed by an id once, and every later lookup is a single step instead of a search:</p>
        <figure class="example" id="ex-index">
          <script type="text/x-python" data-file="index_records.py">
          users = [
              {"id": 7, "name": "Ada"},
              {"id": 3, "name": "Alan"},
          ]
          by_id = {user["id"]: user for user in users}   # build once...
          print(by_id[3]["name"])                         # ...then look up instantly
          </script>
          <script type="text/x-output">
          Alan
          </script>
        </figure>
        <aside class="callout" data-kind="tip" data-level="extra">
          <p>The standard library packages the first two patterns: <code>collections.Counter</code> counts, <code>collections.defaultdict(list)</code> groups. Both are dictionaries underneath, taught in full later in the course.</p>
          <figure class="example" id="ex-collections">
            <script type="text/x-python" data-file="collections_preview.py">
            from collections import Counter, defaultdict

            print(Counter(["red", "blue", "red"]).most_common(1))
            groups = defaultdict(list)
            groups["A"].append("Ada")         # no KeyError: the list is created for you
            print(dict(groups))
            </script>
            <script type="text/x-output">
            [('red', 2)]
            {'A': ['Ada']}
            </script>
          </figure>
        </aside>
      </section>

      <section id="merge" data-level="extra">
        <h2>Merge dictionaries</h2>
        <p>The <code>|</code> operator <span class="version" data-version="3.9" data-change="added"></span> builds a new dictionary from two; when both have a key, the value from the <strong>right</strong> side wins. <code>|=</code> updates the left dictionary in place, like <code>update()</code>.</p>
        <figure class="example" id="ex-merge">
          <script type="text/x-python" data-file="merge.py">
          defaults = {"theme": "light", "font": "sans", "size": 12}
          user = {"theme": "dark", "size": 14}

          print(defaults | user)          # a new dict; the RIGHT side wins on clashes
          print({**defaults, **user})     # the same with unpacking (any Python 3)
          merged = dict(defaults)
          merged.update(user)             # in place
          print(merged == defaults | user)
          defaults |= user                # in place, like update()
          print(defaults)
          </script>
          <script type="text/x-output">
          {'theme': 'dark', 'font': 'sans', 'size': 14}
          {'theme': 'dark', 'font': 'sans', 'size': 14}
          True
          {'theme': 'dark', 'font': 'sans', 'size': 14}
          </script>
        </figure>
        <p>To merge a whole list of dictionaries, unpack each one inside a dictionary comprehension <span class="version" data-version="3.15" data-change="added"></span>. As with <code>|</code>, later dictionaries win.</p>
        <figure class="example" id="ex-merge-many">
          <script type="text/x-python" data-file="merge_many.py">
          layers = [{"theme": "light", "size": 12}, {"theme": "dark"}, {"size": 14}]
          print({**layer for layer in layers})     # unpacking in a comprehension
          </script>
          <script type="text/x-output">
          {'theme': 'dark', 'size': 14}
          </script>
          <figcaption>Before Python 3.15 you would write <code>{k: v for layer in layers for k, v in layer.items()}</code>.</figcaption>
        </figure>
        <aside class="callout" data-kind="job">
          <p>Layered configuration is exactly this: <code>settings = defaults | file_settings | command_line_settings</code>, so each later source overrides the earlier ones.</p>
        </aside>
      </section>

      <section id="views" data-level="extra">
        <h2>Views: <code>keys()</code>, <code>values()</code> and <code>items()</code></h2>
        <p>These methods return <dfn id="term-view">views</dfn>, not copies. A view is a live window onto the dictionary: change the dictionary and the view shows the change. Turn a view into a list with <code>list(view)</code> when you need a snapshot.</p>
        <figure class="example" id="ex-views">
          <script type="text/x-python" data-file="views.py">
          inventory = {"apples": 3, "pears": 5}
          keys = inventory.keys()
          print(keys)
          inventory["kiwis"] = 2          # change the dict...
          print(keys)                     # ...and the view shows it
          print(len(keys), "pears" in keys)
          print(list(inventory.values()))
          </script>
          <script type="text/x-output">
          dict_keys(['apples', 'pears'])
          dict_keys(['apples', 'pears', 'kiwis'])
          3 True
          [3, 5, 2]
          </script>
        </figure>
        <p>Keys views and items views behave like sets, so you can compare two dictionaries with set operators: <code>&amp;</code> (in both), <code>|</code> (in either), <code>-</code> (in the left only) and <code>^</code> (in exactly one).</p>
        <figure class="example" id="ex-view-sets">
          <script type="text/x-python" data-file="view_sets.py">
          monday = {"Ada": 3, "Alan": 1, "Grace": 2}
          tuesday = {"Grace": 4, "Guido": 1}

          print(monday.keys() & tuesday.keys())                     # in both
          print(sorted(monday.keys() | tuesday.keys()))             # in either
          print(sorted(monday.keys() - tuesday.keys()))             # Monday only
          print(monday.keys() ^ {"Ada", "Alan", "Grace", "Linus"})  # in exactly one
          print(monday.keys().isdisjoint({"Linus"}))                # nothing in common?
          print(monday.items() & {("Ada", 3), ("Ada", 9)})          # matching pairs
          </script>
          <script type="text/x-output">
          {'Grace'}
          ['Ada', 'Alan', 'Grace', 'Guido']
          ['Ada', 'Alan']
          {'Linus'}
          True
          {('Ada', 3)}
          </script>
          <figcaption>Set results print in an order that can change from one run to the next, so the example sorts any set with more than one item.</figcaption>
        </figure>
        <aside class="callout" data-kind="hood" data-level="advanced">
          <p>A values view is <em>not</em> set-like (values can repeat and needn't be hashable), so it has no set operators and compares by identity: two views are equal only if they are the same object. Every view has a <code>mapping</code> attribute <span class="version" data-version="3.10" data-change="added"></span>: a read-only proxy of the dictionary it belongs to.</p>
          <script type="text/x-pycon">
          >>> d = {"a": 1}
          >>> d.values() == d.values()
          False
          >>> list(d.values()) == list(d.values())
          True
          >>> d.keys().mapping
          mappingproxy({'a': 1})
          </script>
        </aside>
      </section>

      <section id="order" data-level="extra">
        <h2>Order: what is kept, and what isn't</h2>
        <ul>
          <li>Keys stay in the order they were <strong>first</strong> inserted. Replacing a value keeps the key's place.</li>
          <li>Deleting a key and adding it again moves it to the end.</li>
          <li><code>reversed(d)</code> walks the keys newest first <span class="version" data-version="3.8" data-change="added"></span>.</li>
          <li>Equality ignores order: two dictionaries are equal when they hold the same pairs.</li>
        </ul>
        <figure class="example" id="ex-order">
          <script type="text/x-python" data-file="order.py">
          d = {}
          d["b"] = 1
          d["a"] = 2
          d["b"] = 3                  # replacing a value keeps the key's position
          print(list(d))
          del d["b"]
          d["b"] = 4                  # deleting and re-adding moves it to the end
          print(list(d))
          print(list(reversed(d)))    # newest first
          print({"x": 1, "y": 2} == {"y": 2, "x": 1})
          </script>
          <script type="text/x-output">
          ['b', 'a']
          ['a', 'b']
          ['b', 'a']
          True
          </script>
        </figure>
        <aside class="callout" data-kind="version" data-version="3.7">
          <p>Python 3.6 kept insertion order as an implementation detail; since 3.7 the language guarantees it. Older tutorials that say "dictionaries are unordered", or that reach for <code>collections.OrderedDict</code> just to keep order, are out of date. <code>OrderedDict</code> is still useful for its order-aware equality and <code>move_to_end()</code>.</p>
        </aside>
      </section>

      <section id="copying" data-level="extra">
        <h2>Copy and nest dictionaries</h2>
        <p><code>b = a</code> doesn't copy anything: both names refer to one dictionary. <code>a.copy()</code> (or <code>dict(a)</code>, or <code>{**a}</code>) makes a <em>shallow</em> copy: a new dictionary holding the same value objects. <code>copy.deepcopy(a)</code> copies the values too, all the way down.</p>
        <figure class="example" id="ex-copy" data-predict="">
          <script type="text/x-python" data-file="copying.py">
          import copy

          original = {"name": "Ada", "langs": ["Python"]}
          alias = original                 # NOT a copy: two names, one dict
          shallow = original.copy()        # a new dict, but the SAME inner list
          deep = copy.deepcopy(original)   # a new dict and a new inner list

          original["langs"].append("SQL")
          print(alias is original, shallow is original)
          print(shallow["langs"])
          print(deep["langs"])
          </script>
          <script type="text/x-output">
          True False
          ['Python', 'SQL']
          ['Python']
          </script>
        </figure>
        <section id="nested-json" data-level="extra">
          <h3>Nested data and JSON</h3>
          <p>Real data nests: dictionaries of lists of dictionaries. This is exactly the shape of JSON, the text format web APIs use, and <code>json.dumps</code> / <code>json.loads</code> convert between the two.</p>
          <figure class="example" id="ex-json">
            <script type="text/x-python" data-file="nested_json.py">
            import json

            order = {
                "id": 1042,
                "customer": {"name": "Ada", "city": "London"},
                "items": [{"sku": "A1", "qty": 2}, {"sku": "B7", "qty": 1}],
            }
            print(order["customer"]["city"])
            print(sum(item["qty"] for item in order["items"]))
            print(order.get("shipping", {}).get("method", "standard"))   # safe chained lookup

            text = json.dumps(order)              # dict -> JSON text (what APIs send)
            print(text[:40])
            back = json.loads(text)               # JSON text -> dict
            print(back == order)
            print(json.loads(json.dumps({1: "one"})))   # JSON keys are always strings
            </script>
            <script type="text/x-output">
            London
            3
            standard
            {"id": 1042, "customer": {"name": "Ada",
            True
            {'1': 'one'}
            </script>
          </figure>
          <aside class="callout" data-kind="pitfall">
            <p>JSON object keys are always text, so integer keys come back as strings after a round trip: <code>{1: "one"}</code> returns as <code>{'1': 'one'}</code>. Convert them back yourself, or keep string keys in data you'll save as JSON.</p>
          </aside>
        </section>
      </section>

      <section id="typing" data-level="extra">
        <h2>Type hints for dictionaries</h2>
        <p>Hints document what a dictionary holds; tools such as mypy check them, Python itself ignores them at run time. Write <code>dict[str, int]</code> for "string keys, integer values". For a parameter you only read, <code>Mapping[str, int]</code> also accepts read-only mappings. When each key has its own type, as in a JSON record, describe it with a <code>TypedDict</code>.</p>
        <figure class="example" id="ex-typing">
          <script type="text/x-python" data-file="dict_hints.py">
          from collections.abc import Mapping
          from typing import TypedDict


          def total(prices: Mapping[str, float]) -> float:   # read-only parameter
              return sum(prices.values())


          class Book(TypedDict):          # a dict with known keys and value types
              title: str
              year: int


          stock: dict[str, int] = {"apples": 3}
          book: Book = {"title": "SICP", "year": 1985}
          print(total({"tea": 2.5, "cake": 3.0}))
          print(book["year"], type(book).__name__)
          </script>
          <script type="text/x-output">
          5.5
          1985 dict
          </script>
          <figcaption>A <code>TypedDict</code> is an ordinary <code>dict</code> at run time; only the type checker knows about its keys.</figcaption>
        </figure>
      </section>

      <section id="performance" data-level="extra">
        <h2>Performance cheat sheet</h2>
        <div class="table-wrap">
          <table>
            <caption>Cost of dictionary operations (n = number of entries)</caption>
            <thead><tr><th scope="col">Operation</th><th scope="col">Average</th><th scope="col">Worst case</th><th scope="col">Note</th></tr></thead>
            <tbody>
              <tr><td><code>d[k]</code>, <code>d[k] = v</code>, <code>del d[k]</code>, <code>k in d</code>, <code>d.get(k)</code></td><td>O(1)</td><td>O(n)</td><td>The worst case needs many colliding hashes: rare in practice.</td></tr>
              <tr><td><code>len(d)</code></td><td>O(1)</td><td>O(1)</td><td>The size is stored, never counted.</td></tr>
              <tr><td>loop over <code>d</code>, <code>.keys()</code>, <code>.values()</code>, <code>.items()</code></td><td>O(n)</td><td>O(n)</td><td>Views cost nothing to create; the loop does the work.</td></tr>
              <tr><td><code>v in d.values()</code></td><td>O(n)</td><td>O(n)</td><td>Checks every value. Keep a reverse dictionary if you do this often.</td></tr>
              <tr><td><code>d.copy()</code>, <code>a | b</code>, <code>d.update(other)</code></td><td>O(n)</td><td>O(n)</td><td>Proportional to the number of entries copied.</td></tr>
              <tr><td><code>sorted(d)</code></td><td>O(n log n)</td><td>O(n log n)</td><td>Sorting dominates.</td></tr>
            </tbody>
          </table>
        </div>
        <aside class="callout" data-kind="performance">
          <p>Swapping a list search for a dictionary lookup is the most common way to turn an O(n²) program into an O(n) one. Exercise 4 measures exactly that.</p>
        </aside>
      </section>

      <section id="frozendict" data-level="extra">
        <h2>Immutable dictionaries: <code>frozendict</code></h2>
        <p><code>frozendict</code> <span class="version" data-version="3.15" data-change="added"></span> is a built-in dictionary that can't change after it is created. It has the reading half of the <code>dict</code> API (<code>[]</code>, <code>get</code>, <code>in</code>, the views, iteration in insertion order) and none of the writing half. Because it can't change, it is <strong>hashable</strong> when all its keys and values are: it can be a dictionary key, a set member or a cache key, and it is safe to share between functions and threads.</p>
        <figure class="example" id="ex-frozendict" data-raises="TypeError">
          <script type="text/x-python" data-file="frozen.py">
          config = frozendict(host="localhost", port=8000)
          print(config)
          print(config["port"], config.get("debug", False))

          updated = config | {"port": 9000}         # a NEW frozendict; config is unchanged
          print(updated, config["port"])
          print(hash(config) == hash(frozendict(port=8000, host="localhost")))   # order doesn't matter
          connections = {config: "open"}            # hashable, so it can be a key
          print(connections[frozendict(port=8000, host="localhost")])

          editable = dict(config)                   # "thaw" into a normal dict...
          editable["debug"] = True
          print(frozendict(editable))               # ...and freeze it again
          config["port"] = 9000                     # no changes allowed
          </script>
          <script type="text/x-output">
          frozendict({'host': 'localhost', 'port': 8000})
          8000 False
          frozendict({'host': 'localhost', 'port': 9000}) 8000
          True
          open
          frozendict({'host': 'localhost', 'port': 8000, 'debug': True})
          Traceback (most recent call last):
            ...
          TypeError: 'frozendict' object does not support item assignment
          </script>
        </figure>
        <aside class="callout" data-kind="pitfall">
          <p class="callout-title">Frozen is shallow</p>
          <p>A <code>frozendict</code> stops you replacing its values, not changing them. A list stored inside can still grow, and then the <code>frozendict</code> is no longer hashable. Store tuples, frozensets and frozendicts inside when you need it frozen all the way down.</p>
          <script type="text/x-pycon">
          >>> team = frozendict(name="core", members=["Ada"])
          >>> team["members"].append("Alan")
          >>> team
          frozendict({'name': 'core', 'members': ['Ada', 'Alan']})
          >>> hash(team)
          Traceback (most recent call last):
            ...
          TypeError: unhashable type: 'list'
          </script>
        </aside>
        <ul>
          <li><code>frozendict</code> is <em>not</em> a subclass of <code>dict</code>: <code>isinstance(fd, dict)</code> is <code>False</code>. Accept both with <code>isinstance(x, (dict, frozendict))</code>, or any mapping with <code>collections.abc.Mapping</code>.</li>
          <li><code>fd | other</code> returns a new <code>frozendict</code>, but <code>d | fd</code> returns a <code>dict</code>: the left side decides. <code>fd |= other</code> makes the name point to a new <code>frozendict</code>.</li>
          <li>Compare it with <code>types.MappingProxyType</code> (below): a proxy is a live read-only <em>window</em> onto a dict that its owner can still change; a <code>frozendict</code> is an independent value that nobody can change.</li>
        </ul>
        <p data-level="advanced">To freeze JSON all the way down while loading it, pass <code>object_pairs_hook=frozendict</code> and <code>array_hook=tuple</code> to <code>json.loads</code> (<code>array_hook</code> is also new in 3.15).</p>
        <figure class="example" id="ex-frozen-json" data-level="advanced">
          <script type="text/x-python" data-file="frozen_json.py">
          import json

          text = '{"model": "knn", "params": {"k": 5}, "tags": ["a", "b"]}'
          settings = json.loads(text, object_pairs_hook=frozendict, array_hook=tuple)
          print(settings)
          cache = {settings: "model-v1"}      # hashable all the way down: a valid cache key
          print(cache[settings])
          </script>
          <script type="text/x-output">
          frozendict({'model': 'knn', 'params': frozendict({'k': 5}), 'tags': ('a', 'b')})
          model-v1
          </script>
        </figure>
      </section>

      <section id="matching" data-level="advanced">
        <h2>Pattern matching on dictionaries</h2>
        <p>A <code>match</code> statement <span class="version" data-version="3.10" data-change="added"></span> can check that a dictionary has certain keys and pull their values out in one step. Mapping patterns ignore extra keys unless you capture them with <code>**rest</code>.</p>
        <figure class="example" id="ex-match">
          <script type="text/x-python" data-file="match_events.py">
          def describe(event: dict) -> str:
              match event:
                  case {"type": "click", "x": x, "y": y}:
                      return f"click at ({x}, {y})"
                  case {"type": "key", "key": key, **rest}:
                      return f"key {key!r}, extra fields: {sorted(rest)}"
                  case {"type": kind}:
                      return f"unknown event {kind!r}"
                  case _:
                      return "not an event"


          print(describe({"type": "click", "x": 3, "y": 4, "button": "left"}))
          print(describe({"type": "key", "key": "q", "shift": True, "ctrl": False}))
          print(describe({"type": "scroll"}))
          print(describe({}))
          </script>
          <script type="text/x-output">
          click at (3, 4)
          key 'q', extra fields: ['ctrl', 'shift']
          unknown event 'scroll'
          not an event
          </script>
        </figure>
      </section>

      <section id="hood" data-level="advanced">
        <h2>Under the hood: hash tables</h2>
        <p>A dictionary is a <strong>hash table</strong>. To store a key, Python calls <code>hash(key)</code>, turns the number into a slot position, and puts the pair there. To find a key it computes the same hash, jumps to that slot, and confirms the match with <code>==</code>. That is why a lookup takes about the same time for ten entries or ten million (O(1) on average), and why keys must not change: a changed key would no longer hash to the slot it was stored in.</p>
        <ul>
          <li>Equal objects must have equal hashes. If you define <code>__eq__</code> on your own class, define <code>__hash__</code> too (or Python makes instances unhashable).</li>
          <li>Different keys can share a slot (a <em>collision</em>); Python then probes other slots. Collisions are rare enough that the average stays O(1); the worst case is O(n).</li>
          <li>The hash of a string changes every time Python starts (hash randomisation, a defence against attacks that force collisions). That is why the <em>order</em> of a set of strings can change between runs, while dictionaries keep insertion order regardless.</li>
          <li>CPython stores entries compactly in insertion order and keeps a separate small table of slot indexes; the table grows (and is rebuilt) as the dictionary fills, so memory grows in steps.</li>
        </ul>
        <figure class="example" id="ex-hash">
          <script type="text/x-python" data-file="hashing.py">
          class Point:
              def __init__(self, x, y):
                  self.x, self.y = x, y

              def __eq__(self, other):
                  return (self.x, self.y) == (other.x, other.y)

              def __hash__(self):               # equal objects MUST have equal hashes
                  return hash((self.x, self.y))


          labels = {Point(0, 0): "origin"}
          print(labels[Point(0, 0)])           # a different object, but equal: found
          print(hash(42), hash(42.0), hash(True))
          </script>
          <script type="text/x-output">
          origin
          42 42 1
          </script>
        </figure>
        <aside class="callout" data-kind="interview">
          <p>"What is the time complexity of a dictionary lookup, and why?" Answer: O(1) on average, because the key's hash gives the slot directly; O(n) in the worst case, when many keys collide. Then mention that keys must be hashable, and why.</p>
        </aside>
      </section>

      <section id="readonly" data-level="advanced">
        <h2>Read-only dictionaries</h2>
        <p><code>types.MappingProxyType(d)</code> wraps a dictionary in a read-only view. Code that receives the proxy can read but not write; the owner keeps the real dictionary and can still change it, and the proxy sees those changes.</p>
        <figure class="example" id="ex-proxy" data-raises="TypeError">
          <script type="text/x-python" data-file="readonly.py">
          from types import MappingProxyType

          _settings = {"debug": False}
          settings = MappingProxyType(_settings)     # a read-only window onto the dict
          print(settings["debug"], settings.get("missing", "n/a"))
          _settings["debug"] = True                  # the owner can still change it...
          print(settings["debug"])                   # ...and the proxy sees the change
          print(settings | {"level": 3})             # | returns a plain new dict
          settings["debug"] = False                  # nobody can write through the proxy
          </script>
          <script type="text/x-output">
          False n/a
          True
          {'debug': True, 'level': 3}
          Traceback (most recent call last):
            ...
          TypeError: 'mappingproxy' object does not support item assignment
          </script>
        </figure>
      </section>

      <section id="missing" data-level="advanced">
        <h2>Custom behaviour for missing keys: <code>__missing__</code></h2>
        <p>When <code>d[key]</code> fails in a <em>subclass</em> of <code>dict</code>, Python calls the subclass's <code>__missing__(key)</code> method before raising <code>KeyError</code>. This is how <code>collections.defaultdict</code> and <code>Counter</code> work. Only <code>d[key]</code> uses it: <code>get()</code> and <code>in</code> don't.</p>
        <figure class="example" id="ex-missing">
          <script type="text/x-python" data-file="missing_hook.py">
          class ZeroDict(dict):
              """A dict that answers 0 for missing keys (like defaultdict(int))."""

              def __missing__(self, key):
                  return 0


          counts = ZeroDict()
          counts["a"] += 1          # reads 0 via __missing__, then stores 1
          print(counts, counts["zzz"], "zzz" in counts, counts.get("zzz"))
          </script>
          <script type="text/x-output">
          {'a': 1} 0 False None
          </script>
        </figure>
      </section>

      <section class="api-reference" id="reference" data-api-targets="class:dict expr:dict_keys=type({}.keys()) expr:dict_values=type({}.values()) expr:dict_items=type({}.items()) class:frozendict class:types.MappingProxyType">
        <h2>Reference: everything a dictionary can do</h2>
        <p>Every public method and operator of <code>dict</code>, its three view types, <code>frozendict</code> and <code>types.MappingProxyType</code> in Python 3.15, checked against the real objects by <code>tools/check_coverage.py</code>. Set <strong>Show → Essentials</strong> to turn these tables into a cheat sheet. In the code column, <code>d</code> is a dictionary and <code>k</code> a key.</p>

        <div class="table-wrap">
          <table class="api-table">
            <caption>Creating dictionaries</caption>
            <thead><tr><th scope="col">Code</th><th scope="col">What it does</th><th scope="col">Notes</th></tr></thead>
            <tbody>
              <tr id="api-syntax-dict-display" data-api="syntax:dict-display" data-level="essential"><td><code>{k1: v1, k2: v2}</code></td><td>Dictionary literal ("display"); <code>{}</code> is empty.</td><td>A repeated key keeps its first position and last value.</td></tr>
              <tr id="api-dict" data-api="dict" data-level="essential"><td><code>dict(...)</code></td><td><code>dict()</code> empty; <code>dict(mapping)</code> copy; <code>dict(pairs)</code> from (key, value) pairs; <code>dict(a=1)</code> keyword keys; forms combine: <code>dict(pairs, z=3)</code>.</td><td>Keyword form only makes <code>str</code> keys that are valid names.</td></tr>
              <tr id="api-syntax-dict-comprehension" data-api="syntax:dict-comprehension" data-level="essential"><td><code>{k: v for x in it}</code></td><td>Dictionary comprehension.</td><td>Lesson 6 covers filters and nesting.</td></tr>
              <tr id="api-syntax-dict-unpacking" data-api="syntax:dict-unpacking" data-level="extra"><td><code>{**a, **b, k: v}</code></td><td>Unpack mappings into a new literal; later entries win.</td><td>Also <code>f(**d)</code> passes keys as keyword arguments.</td></tr>
              <tr id="api-dict-fromkeys" data-api="dict.fromkeys" data-level="extra"><td><code>dict.fromkeys(iterable, value=None)</code></td><td>New dict with the given keys, all set to <code>value</code>.</td><td>Class method. All keys share one value object: don't use a list.</td></tr>
              <tr id="api-dict-__class_getitem__" data-api="dict.__class_getitem__" data-level="extra"><td><code>dict[str, int]</code></td><td>The type "dict with str keys and int values", for type hints.</td><td>A <code>types.GenericAlias</code>; does nothing at run time.</td></tr>
            </tbody>
          </table>
        </div>

        <div class="table-wrap">
          <table class="api-table">
            <caption>Reading, testing and comparing</caption>
            <thead><tr><th scope="col">Code</th><th scope="col">What it does</th><th scope="col">Notes</th></tr></thead>
            <tbody>
              <tr id="api-dict-__getitem__" data-api="dict.__getitem__" data-level="essential"><td><code>d[k]</code></td><td>The value stored under <code>k</code>.</td><td><code>KeyError</code> if missing (subclasses: <code>__missing__</code> is tried first).</td></tr>
              <tr id="api-dict-get" data-api="dict.get" data-level="essential"><td><code>d.get(k, default=None)</code></td><td>The value, or <code>default</code> if <code>k</code> is missing.</td><td>Never raises <code>KeyError</code>; never inserts.</td></tr>
              <tr id="api-dict-__contains__" data-api="dict.__contains__" data-level="essential"><td><code>k in d</code>, <code>k not in d</code></td><td>Is <code>k</code> a key?</td><td>Keys only; use <code>v in d.values()</code> for values (slow).</td></tr>
              <tr id="api-dict-__len__" data-api="dict.__len__" data-level="essential"><td><code>len(d)</code></td><td>Number of pairs.</td><td>O(1). An empty dict is falsy: <code>if not d:</code>.</td></tr>
              <tr id="api-dict-__iter__" data-api="dict.__iter__" data-level="essential"><td><code>for k in d</code>, <code>iter(d)</code>, <code>list(d)</code></td><td>The keys in insertion order.</td><td>Adding or removing keys during the loop raises <code>RuntimeError</code>.</td></tr>
              <tr id="api-dict-keys" data-api="dict.keys" data-level="essential"><td><code>d.keys()</code></td><td>A live, set-like view of the keys.</td><td>See the views table.</td></tr>
              <tr id="api-dict-values" data-api="dict.values" data-level="essential"><td><code>d.values()</code></td><td>A live view of the values.</td><td>Not set-like.</td></tr>
              <tr id="api-dict-items" data-api="dict.items" data-level="essential"><td><code>d.items()</code></td><td>A live, set-like view of <code>(key, value)</code> pairs.</td><td><code>for k, v in d.items():</code> is the standard loop.</td></tr>
              <tr id="api-dict-__reversed__" data-api="dict.__reversed__" data-level="extra"><td><code>reversed(d)</code></td><td>The keys, newest first.</td><td>New in 3.8 (views too).</td></tr>
              <tr id="api-dict-__repr__" data-api="dict.__repr__" data-level="extra"><td><code>repr(d)</code>, <code>str(d)</code>, <code>print(d)</code></td><td>Text like <code>{'a': 1}</code> using each key's and value's <code>repr</code>.</td><td>Use <code>json.dumps(d, indent=2)</code> or <code>pprint</code> for big nested data.</td></tr>
              <tr id="api-dict-__eq__" data-api="dict.__eq__ dict.__ne__" data-level="essential"><td><code>d1 == d2</code>, <code>d1 != d2</code></td><td>Equal when they hold the same pairs, in any order.</td><td>Values compared with <code>==</code>: <code>{'a': 1} == {'a': 1.0}</code>.</td></tr>
              <tr id="api-dict-__lt__" data-api="dict.__lt__ dict.__le__ dict.__gt__ dict.__ge__" data-level="advanced"><td><code>d1 &lt; d2</code> (and <code>&lt;=</code>, <code>&gt;</code>, <code>&gt;=</code>)</td><td>Not supported: <code>TypeError</code>.</td><td>Compare <code>d1.keys() &lt; d2.keys()</code> for "subset of keys".</td></tr>
              <tr id="api-dict-__hash__" data-api="dict.__hash__" data-level="extra"><td><code>hash(d)</code></td><td><code>TypeError: unhashable type: 'dict'</code>.</td><td>A dict can't be a key or a set member; freeze it with <code>frozendict(d)</code>.</td></tr>
            </tbody>
          </table>
        </div>

        <div class="table-wrap">
          <table class="api-table">
            <caption>Changing a dictionary</caption>
            <thead><tr><th scope="col">Code</th><th scope="col">What it does</th><th scope="col">Notes</th></tr></thead>
            <tbody>
              <tr id="api-dict-__setitem__" data-api="dict.__setitem__" data-level="essential"><td><code>d[k] = v</code></td><td>Add <code>k</code>, or replace its value.</td><td>Replacing keeps the key's position.</td></tr>
              <tr id="api-dict-__delitem__" data-api="dict.__delitem__" data-level="essential"><td><code>del d[k]</code></td><td>Remove <code>k</code>.</td><td><code>KeyError</code> if missing.</td></tr>
              <tr id="api-dict-pop" data-api="dict.pop" data-level="essential"><td><code>d.pop(k[, default])</code></td><td>Remove <code>k</code> and return its value.</td><td>With a default: returns it instead of raising <code>KeyError</code>.</td></tr>
              <tr id="api-dict-update" data-api="dict.update" data-level="essential"><td><code>d.update(other, **kw)</code></td><td>Add or replace many pairs from a mapping, an iterable of pairs, and/or keywords.</td><td>Returns <code>None</code> (changes <code>d</code> in place).</td></tr>
              <tr id="api-dict-setdefault" data-api="dict.setdefault" data-level="extra"><td><code>d.setdefault(k, default=None)</code></td><td>Return <code>d[k]</code>; if missing, insert <code>default</code> first.</td><td>The grouping idiom: <code>d.setdefault(k, []).append(x)</code>.</td></tr>
              <tr id="api-dict-popitem" data-api="dict.popitem" data-level="extra"><td><code>d.popitem()</code></td><td>Remove and return the last inserted <code>(key, value)</code>.</td><td>LIFO since 3.7. <code>KeyError</code> when empty.</td></tr>
              <tr id="api-dict-clear" data-api="dict.clear" data-level="essential"><td><code>d.clear()</code></td><td>Remove every pair.</td><td>Other names for the same dict see it empty too.</td></tr>
              <tr id="api-dict-copy" data-api="dict.copy" data-level="essential"><td><code>d.copy()</code></td><td>A shallow copy.</td><td>Values are shared; use <code>copy.deepcopy(d)</code> for nested data.</td></tr>
              <tr id="api-dict-__or__" data-api="dict.__or__ dict.__ror__" data-level="extra"><td><code>d | other</code></td><td>A new dict: <code>d</code>'s pairs, then <code>other</code>'s (right side wins).</td><td>New in 3.9. Both operands must be dicts (<code>__ror__</code> is the reflected form).</td></tr>
              <tr id="api-dict-__ior__" data-api="dict.__ior__" data-level="extra"><td><code>d |= other</code></td><td>Update <code>d</code> in place.</td><td>Like <code>update()</code>; <code>other</code> may be any mapping or iterable of pairs.</td></tr>
            </tbody>
          </table>
        </div>

        <div class="table-wrap">
          <table class="api-table">
            <caption>Views: dict_keys, dict_values, dict_items</caption>
            <thead><tr><th scope="col">Code</th><th scope="col">What it does</th><th scope="col">Notes</th></tr></thead>
            <tbody>
              <tr id="api-dict_keys" data-api="dict_keys dict_values dict_items" data-level="extra"><td><code>d.keys()</code>, <code>d.values()</code>, <code>d.items()</code></td><td>The three view types. You never create them directly.</td><td>Live: they reflect later changes to <code>d</code>.</td></tr>
              <tr id="api-dict_keys-__len__" data-api="dict_keys.__len__ dict_values.__len__ dict_items.__len__ dict_keys.__iter__ dict_values.__iter__ dict_items.__iter__" data-level="essential"><td><code>len(view)</code>, <code>for x in view</code></td><td>Size and iteration, in insertion order.</td><td>Iterating while the dict changes size raises <code>RuntimeError</code>.</td></tr>
              <tr id="api-dict_keys-__contains__" data-api="dict_keys.__contains__ dict_items.__contains__" data-level="extra"><td><code>k in d.keys()</code>, <code>(k, v) in d.items()</code></td><td>Fast membership (hash lookup).</td><td><code>v in d.values()</code> is a slow scan (no row of its own: plain iteration).</td></tr>
              <tr id="api-dict_keys-__reversed__" data-api="dict_keys.__reversed__ dict_values.__reversed__ dict_items.__reversed__" data-level="extra"><td><code>reversed(view)</code></td><td>Newest first.</td><td>New in 3.8.</td></tr>
              <tr id="api-dict_keys-__repr__" data-api="dict_keys.__repr__ dict_values.__repr__ dict_items.__repr__" data-level="extra"><td><code>print(d.keys())</code></td><td>Text like <code>dict_keys(['a', 'b'])</code>.</td><td>Use <code>list(view)</code> for plain list output.</td></tr>
              <tr id="api-dict_keys-__and__" data-api="dict_keys.__and__ dict_keys.__rand__ dict_items.__and__ dict_items.__rand__" data-level="extra"><td><code>view &amp; other</code></td><td>Intersection, as a new <code>set</code>.</td><td><code>other</code> can be any iterable on the right; reflected form for <code>set &amp; view</code>.</td></tr>
              <tr id="api-dict_keys-__or__" data-api="dict_keys.__or__ dict_keys.__ror__ dict_items.__or__ dict_items.__ror__" data-level="extra"><td><code>view | other</code></td><td>Union, as a new <code>set</code>.</td><td>Sort the result before printing if order matters.</td></tr>
              <tr id="api-dict_keys-__sub__" data-api="dict_keys.__sub__ dict_keys.__rsub__ dict_items.__sub__ dict_items.__rsub__" data-level="extra"><td><code>view - other</code></td><td>Difference, as a new <code>set</code>.</td><td>"Keys in <code>d</code> but not in <code>other</code>".</td></tr>
              <tr id="api-dict_keys-__xor__" data-api="dict_keys.__xor__ dict_keys.__rxor__ dict_items.__xor__ dict_items.__rxor__" data-level="extra"><td><code>view ^ other</code></td><td>Symmetric difference, as a new <code>set</code>.</td><td>In exactly one of the two.</td></tr>
              <tr id="api-dict_keys-isdisjoint" data-api="dict_keys.isdisjoint dict_items.isdisjoint" data-level="extra"><td><code>view.isdisjoint(other)</code></td><td><code>True</code> if nothing is in common.</td><td>Stops at the first shared item.</td></tr>
              <tr id="api-dict_keys-__eq__" data-api="dict_keys.__eq__ dict_keys.__ne__ dict_keys.__lt__ dict_keys.__le__ dict_keys.__gt__ dict_keys.__ge__ dict_items.__eq__ dict_items.__ne__ dict_items.__lt__ dict_items.__le__ dict_items.__gt__ dict_items.__ge__" data-level="advanced"><td><code>d1.keys() == d2.keys()</code>, <code>&lt;</code>, <code>&lt;=</code>, <code>&gt;</code>, <code>&gt;=</code></td><td>Set comparisons: equality, proper subset/superset.</td><td>Also against sets: <code>d.keys() == {'a', 'b'}</code>.</td></tr>
              <tr id="api-dict_keys-__hash__" data-api="dict_keys.__hash__ dict_items.__hash__" data-level="advanced"><td><code>hash(d.keys())</code></td><td><code>TypeError</code>: views are unhashable.</td><td>Use <code>frozenset(d)</code> for a hashable snapshot of the keys.</td></tr>
              <tr id="api-dict_keys-mapping" data-api="dict_keys.mapping dict_values.mapping dict_items.mapping" data-level="advanced"><td><code>view.mapping</code></td><td>A read-only <code>mappingproxy</code> of the original dict.</td><td>New in 3.10.</td></tr>
            </tbody>
          </table>
        </div>

        <div class="table-wrap">
          <table class="api-table">
            <caption>frozendict (immutable dictionary, new in 3.15)</caption>
            <thead><tr><th scope="col">Code</th><th scope="col">What it does</th><th scope="col">Notes</th></tr></thead>
            <tbody>
              <tr id="api-frozendict" data-api="frozendict" data-level="extra"><td><code>frozendict(...)</code></td><td>An immutable dictionary: <code>frozendict()</code>, <code>frozendict(mapping)</code>, <code>frozendict(pairs)</code>, <code>frozendict(a=1)</code>, or combined, exactly like <code>dict()</code>.</td><td>Not a <code>dict</code> subclass; inherits from <code>object</code>.</td></tr>
              <tr id="api-frozendict-fromkeys" data-api="frozendict.fromkeys" data-level="advanced"><td><code>frozendict.fromkeys(iterable, value=None)</code></td><td>New frozendict with the given keys, all set to <code>value</code>.</td><td>Class method, as for <code>dict</code>.</td></tr>
              <tr id="api-frozendict-__getitem__" data-api="frozendict.__getitem__ frozendict.get frozendict.__contains__ frozendict.__len__ frozendict.__iter__ frozendict.__reversed__" data-level="extra"><td><code>fd[k]</code>, <code>fd.get(k)</code>, <code>k in fd</code>, <code>len(fd)</code>, <code>iter(fd)</code>, <code>reversed(fd)</code></td><td>Read exactly like a dict, in insertion order.</td><td>Same costs as <code>dict</code> (O(1) lookups).</td></tr>
              <tr id="api-frozendict-keys" data-api="frozendict.keys frozendict.values frozendict.items" data-level="extra"><td><code>fd.keys()</code>, <code>fd.values()</code>, <code>fd.items()</code></td><td>The usual <code>dict_keys</code>, <code>dict_values</code> and <code>dict_items</code> views.</td><td>Set operations work as for dict views.</td></tr>
              <tr id="api-frozendict-copy" data-api="frozendict.copy" data-level="advanced"><td><code>fd.copy()</code></td><td>Returns the same object.</td><td>Nothing can change, so there is nothing to copy; use <code>dict(fd)</code> for a mutable copy.</td></tr>
              <tr id="api-frozendict-__or__" data-api="frozendict.__or__ frozendict.__ror__" data-level="extra"><td><code>fd | other</code>, <code>other | fd</code></td><td>A new mapping with the merged pairs (right side wins); its type is the left operand's.</td><td><code>fd |= other</code> rebinds the name to a new frozendict.</td></tr>
              <tr id="api-frozendict-__hash__" data-api="frozendict.__hash__" data-level="extra"><td><code>hash(fd)</code></td><td>A hash that ignores order, so equal frozendicts hash equally.</td><td><code>TypeError</code> if any key or value is unhashable (a list inside, say).</td></tr>
              <tr id="api-frozendict-__eq__" data-api="frozendict.__eq__ frozendict.__ne__" data-level="extra"><td><code>fd == other</code>, <code>fd != other</code></td><td>Equal to any <code>dict</code> or <code>frozendict</code> holding the same pairs, in any order.</td><td><code>frozendict(a=1) == {'a': 1}</code> is <code>True</code>.</td></tr>
              <tr id="api-frozendict-__lt__" data-api="frozendict.__lt__ frozendict.__le__ frozendict.__gt__ frozendict.__ge__" data-level="advanced"><td><code>fd1 &lt; fd2</code> (and <code>&lt;=</code>, <code>&gt;</code>, <code>&gt;=</code>)</td><td>Not supported: <code>TypeError</code>.</td><td>As for <code>dict</code>.</td></tr>
              <tr id="api-frozendict-__repr__" data-api="frozendict.__repr__" data-level="extra"><td><code>repr(fd)</code>, <code>print(fd)</code></td><td>Text like <code>frozendict({'a': 1})</code>.</td><td>Paste it back into Python to rebuild the value.</td></tr>
              <tr id="api-frozendict-__class_getitem__" data-api="frozendict.__class_getitem__" data-level="advanced"><td><code>frozendict[str, int]</code></td><td>The type for hints.</td><td>Or accept any read-only mapping with <code>Mapping[str, int]</code>.</td></tr>
            </tbody>
          </table>
        </div>

        <div class="table-wrap">
          <table class="api-table">
            <caption>types.MappingProxyType (read-only view of a mapping)</caption>
            <thead><tr><th scope="col">Code</th><th scope="col">What it does</th><th scope="col">Notes</th></tr></thead>
            <tbody>
              <tr id="api-MappingProxyType" data-api="MappingProxyType" data-level="advanced"><td><code>MappingProxyType(d)</code></td><td>A read-only, live view of <code>d</code>.</td><td>Writes through the proxy raise <code>TypeError</code>.</td></tr>
              <tr id="api-MappingProxyType-__getitem__" data-api="MappingProxyType.__getitem__ MappingProxyType.get MappingProxyType.__contains__ MappingProxyType.__len__ MappingProxyType.__iter__ MappingProxyType.__reversed__" data-level="advanced"><td><code>p[k]</code>, <code>p.get(k)</code>, <code>k in p</code>, <code>len(p)</code>, <code>iter(p)</code>, <code>reversed(p)</code></td><td>Read exactly like the dict.</td><td>Delegated to the wrapped mapping.</td></tr>
              <tr id="api-MappingProxyType-keys" data-api="MappingProxyType.keys MappingProxyType.values MappingProxyType.items" data-level="advanced"><td><code>p.keys()</code>, <code>p.values()</code>, <code>p.items()</code></td><td>The wrapped dict's views.</td><td>Still live.</td></tr>
              <tr id="api-MappingProxyType-copy" data-api="MappingProxyType.copy" data-level="advanced"><td><code>p.copy()</code></td><td>A shallow copy of the wrapped mapping (a normal, writable dict).</td><td>The copy is independent of the proxy.</td></tr>
              <tr id="api-MappingProxyType-__or__" data-api="MappingProxyType.__or__ MappingProxyType.__ror__" data-level="advanced"><td><code>p | other</code>, <code>other | p</code></td><td>A new plain dict with the merged pairs.</td><td>New in 3.9.</td></tr>
              <tr id="api-MappingProxyType-__ior__" data-api="MappingProxyType.__ior__" data-level="advanced"><td><code>p |= other</code></td><td><code>TypeError</code>: "'|=' is not supported by mappingproxy; use '|' instead".</td><td>Defined only to give that clear message.</td></tr>
              <tr id="api-MappingProxyType-__eq__" data-api="MappingProxyType.__eq__ MappingProxyType.__ne__ MappingProxyType.__lt__ MappingProxyType.__le__ MappingProxyType.__gt__ MappingProxyType.__ge__" data-level="advanced"><td><code>p == d</code> (and the other comparisons)</td><td>Compares the wrapped mapping with <code>d</code>.</td><td>Ordering comparisons fail for dicts, as above.</td></tr>
              <tr id="api-MappingProxyType-__hash__" data-api="MappingProxyType.__hash__" data-level="advanced"><td><code>hash(p)</code></td><td>The hash of the wrapped mapping: <code>TypeError</code> for a dict.</td><td>Read-only is not the same as hashable.</td></tr>
              <tr id="api-MappingProxyType-__repr__" data-api="MappingProxyType.__repr__ MappingProxyType.__str__" data-level="advanced"><td><code>repr(p)</code>, <code>str(p)</code></td><td><code>mappingproxy({'a': 1})</code> and <code>{'a': 1}</code>.</td><td><code>str</code> shows the wrapped dict.</td></tr>
              <tr id="api-MappingProxyType-__class_getitem__" data-api="MappingProxyType.__class_getitem__" data-level="advanced"><td><code>MappingProxyType[str, int]</code></td><td>Generic alias for type hints.</td><td>Usually you'd annotate with <code>Mapping[str, int]</code>.</td></tr>
            </tbody>
          </table>
        </div>
        <p>Related types taught elsewhere: <code>collections.Counter</code>, <code>defaultdict</code>, <code>OrderedDict</code> and <code>ChainMap</code> (all dictionaries with extra behaviour), and <code>json</code> for saving dictionaries as text.</p>
      </section>

      <section class="exercises" id="exercises">
        <h2>Exercises</h2>
        <p>Download the <a data-pack href="../../downloads/m03-l04.zip" download>exercise pack</a> once; it contains every exercise's starter file and tests. Exercise 4 is an optional interview-style challenge.</p>

        <article class="exercise" id="m03-l04-e1" data-kind="function" data-file="e1_word_freq.py">
          <h3>Exercise 1 · Word frequencies</h3>
          <p class="ex-meta">★☆☆ · 10 points · AI help: hints only</p>
          <div class="exercise-task">
            <p>Write <code>word_freq(text)</code> that returns a dictionary mapping each word to the number of times it appears. Treat upper and lower case as the same word, and split on any whitespace.</p>
            <script type="text/x-pycon">
            >>> from e1_word_freq import word_freq
            >>> word_freq("the cat the hat")
            {'the': 2, 'cat': 1, 'hat': 1}
            </script>
          </div>
          <script type="text/x-python" data-role="starter">
          def word_freq(text):
              """Return a dict mapping each lower-case word in text to its count."""
              counts = {}
              # your code here
              return counts


          if __name__ == "__main__":
              print(word_freq("the cat the hat"))
          </script>
          <script type="text/x-python" data-role="tests">
          from e1_word_freq import word_freq


          def test_counts_repeated_words():
              assert word_freq("the cat the hat") == {"the": 2, "cat": 1, "hat": 1}


          def test_treats_upper_and_lower_case_as_one_word():
              assert word_freq("Data data DATA") == {"data": 3}


          def test_empty_text_gives_an_empty_dict():
              assert word_freq("") == {}


          def test_returns_a_dict_instead_of_printing():
              assert isinstance(word_freq("a b"), dict), "end with: return counts"


          def test_splits_on_any_whitespace():
              assert word_freq("  spaced   out\nwords  ") == {"spaced": 1, "out": 1, "words": 1}
          </script>
          <script type="text/x-python" data-role="solution">
          def word_freq(text):
              """Return a dict mapping each lower-case word in text to its count."""
              counts = {}
              for word in text.lower().split():
                  counts[word] = counts.get(word, 0) + 1
              return counts


          if __name__ == "__main__":
              print(word_freq("the cat the hat"))
          </script>
          <ol class="hints">
            <li>Loop over the words one at a time: <code>text.lower().split()</code> gives you a list of lower-case words.</li>
            <li><code>split()</code> with no arguments splits on any run of spaces, tabs or newlines.</li>
            <li>For each word: <code>counts[word] = counts.get(word, 0) + 1</code>.</li>
          </ol>
        </article>

        <article class="exercise" id="m03-l04-e2" data-kind="function" data-file="e2_invert.py">
          <h3>Exercise 2 · Flip a dictionary</h3>
          <p class="ex-meta">★★☆ · 10 points · AI help: hints only</p>
          <div class="exercise-task">
            <p>Write <code>invert(d)</code> that returns a <em>new</em> dictionary with keys and values swapped. Every value is different. Don't change the dictionary you were given.</p>
            <script type="text/x-pycon">
            >>> from e2_invert import invert
            >>> invert({"MY": "Malaysia", "JP": "Japan"})
            {'Malaysia': 'MY', 'Japan': 'JP'}
            </script>
          </div>
          <script type="text/x-python" data-role="starter">
          def invert(d):
              """Return a NEW dict with keys and values swapped (values are unique)."""
              pass
          </script>
          <script type="text/x-python" data-role="tests">
          from e2_invert import invert


          def test_swaps_keys_and_values():
              assert invert({"a": 1, "b": 2}) == {1: "a", 2: "b"}


          def test_works_with_string_values():
              assert invert({"MY": "Malaysia", "JP": "Japan"}) == {"Malaysia": "MY", "Japan": "JP"}


          def test_empty_dict():
              assert invert({}) == {}


          def test_does_not_change_the_original():
              d = {"x": 10}
              result = invert(d)
              assert d == {"x": 10}
              assert result is not d, "build a brand-new dictionary"


          def test_many_pairs():
              codes = {i: str(i) for i in range(100)}
              assert invert(codes) == {str(i): i for i in range(100)}
          </script>
          <script type="text/x-python" data-role="solution">
          def invert(d):
              """Return a NEW dict with keys and values swapped (values are unique)."""
              return {value: key for key, value in d.items()}
          </script>
          <ol class="hints">
            <li>Create an empty result dictionary and loop with <code>for key, value in d.items():</code>.</li>
            <li>Inside the loop, store the pair the other way round: <code>result[value] = key</code>.</li>
            <li>A dict comprehension does it in one line: <code>{value: key for key, value in d.items()}</code>.</li>
          </ol>
        </article>

        <article class="exercise" id="m03-l04-e3" data-kind="function" data-file="e3_group_words.py">
          <h3>Exercise 3 · Group words by first letter</h3>
          <p class="ex-meta">★★☆ · 15 points · AI help: hints only</p>
          <div class="exercise-task">
            <p>Write <code>group_by_first_letter(words)</code> that returns a dictionary mapping each <strong>lower-case</strong> first letter to the list of words that start with it, in their original order. Keep each word exactly as given, skip empty strings, and don't change the input list.</p>
            <script type="text/x-pycon">
            >>> from e3_group_words import group_by_first_letter
            >>> group_by_first_letter(["apple", "Avocado", "banana"])
            {'a': ['apple', 'Avocado'], 'b': ['banana']}
            </script>
          </div>
          <script type="text/x-python" data-role="starter">
          def group_by_first_letter(words):
              """Group words by lower-case first letter, keeping their order."""
              groups = {}
              for word in words:
                  ...  # your code here
              return groups
          </script>
          <script type="text/x-python" data-role="tests">
          from e3_group_words import group_by_first_letter


          def test_groups_words():
              assert group_by_first_letter(["apple", "avocado", "banana"]) == {"a": ["apple", "avocado"], "b": ["banana"]}


          def test_keeps_the_original_order_inside_a_group():
              assert group_by_first_letter(["bee", "ant", "bat"])["b"] == ["bee", "bat"]


          def test_keys_are_lower_case_and_words_unchanged():
              assert group_by_first_letter(["Python", "pandas"]) == {"p": ["Python", "pandas"]}


          def test_empty_list():
              assert group_by_first_letter([]) == {}


          def test_skips_empty_strings_and_leaves_the_input_alone():
              words = ["", "x-ray", "", "Xylo"]
              assert group_by_first_letter(words) == {"x": ["x-ray", "Xylo"]}
              assert words == ["", "x-ray", "", "Xylo"]
          </script>
          <script type="text/x-python" data-role="solution">
          def group_by_first_letter(words):
              """Group words by lower-case first letter, keeping their order."""
              groups = {}
              for word in words:
                  if not word:
                      continue
                  groups.setdefault(word[0].lower(), []).append(word)
              return groups
          </script>
          <ol class="hints">
            <li>For each word, the key is <code>word[0].lower()</code>; append the original <code>word</code>.</li>
            <li>A key's list must exist before you append to it: check <code>if key not in groups</code>, or use <code>setdefault</code>.</li>
            <li><code>''[0]</code> raises <code>IndexError</code>: skip empty strings with <code>if not word: continue</code>.</li>
          </ol>
        </article>

        <article class="exercise" id="m03-l04-e4" data-kind="function" data-file="e4_first_unique.py" data-optional="">
          <h3>Exercise 4 · First unique character (interview challenge)</h3>
          <p class="ex-meta">★★★ · 20 points · AI help: none (practise like it's an interview)</p>
          <div class="exercise-task">
            <p>Write <code>first_unique_index(s)</code> that returns the index of the first character that appears <strong>exactly once</strong> in <code>s</code>, or <code>-1</code> if there is none. Upper- and lower-case letters are different characters. Your function must stay fast on long strings: a test compares its speed with a linear-time reference on 40,001 characters.</p>
            <script type="text/x-pycon">
            >>> from e4_first_unique import first_unique_index
            >>> first_unique_index("loveleetcode")
            2
            >>> first_unique_index("aabb")
            -1
            </script>
          </div>
          <script type="text/x-python" data-role="starter">
          def first_unique_index(s):
              """Index of the first character that appears exactly once in s, else -1."""
              return -1
          </script>
          <script type="text/x-python" data-role="tests">
          from course_helpers import assert_fast_enough
          from e4_first_unique import first_unique_index


          def linear_reference(s):
              counts = {}
              for ch in s:
                  counts[ch] = counts.get(ch, 0) + 1
              return next((i for i, ch in enumerate(s) if counts[ch] == 1), -1)


          def test_first_character_is_unique():
              assert first_unique_index("leetcode") == 0


          def test_skips_repeated_characters():
              assert first_unique_index("loveleetcode") == 2


          def test_no_unique_character():
              assert first_unique_index("aabb") == -1


          def test_empty_string():
              assert first_unique_index("") == -1


          def test_case_matters():
              assert first_unique_index("Aa") == 0


          def test_fast_on_40_001_characters():
              s = "ab" * 20_000 + "c"
              assert first_unique_index(s) == 40_000
              assert_fast_enough(first_unique_index, linear_reference, s, factor=10)
          </script>
          <script type="text/x-python" data-role="solution" data-notes="Two linear passes make this O(n). Calling s.count(ch) inside the loop rescans the whole string for every character: O(n²), about 50 times slower on the speed test.">
          def first_unique_index(s):
              """Index of the first character that appears exactly once in s, else -1."""
              counts = {}
              for ch in s:
                  counts[ch] = counts.get(ch, 0) + 1
              for i, ch in enumerate(s):
                  if counts[ch] == 1:
                      return i
              return -1
          </script>
          <ol class="hints">
            <li>Two passes: first count how often every character appears, then find the first one whose count is 1.</li>
            <li>The first pass is Exercise 1 again: <code>counts[ch] = counts.get(ch, 0) + 1</code>.</li>
            <li>Second pass: <code>for i, ch in enumerate(s):</code> and return <code>i</code> when <code>counts[ch] == 1</code>. Avoid <code>s.count(ch)</code> inside a loop.</li>
          </ol>
        </article>
      </section>

      <section class="quiz" id="m03-l04-quiz">
        <h2>Check your understanding</h2>
        <script type="application/json" class="quiz-spec">
        {"id": "m03-l04-quiz", "questions": [
          {"type": "mcq", "prompt": "<code>stock = {'apples': 12}</code>. Which expression gives <code>0</code> instead of raising <code>KeyError</code>?",
           "options": ["<code>stock['kiwis']</code>", "<code>stock.get('kiwis', 0)</code>", "<code>stock.pop('kiwis')</code>", "<code>stock.kiwis</code>"],
           "answer": 1,
           "explanations": ["<code>[]</code> raises <code>KeyError</code> for a missing key.", "Right: <code>get</code> returns the default for a missing key.", "<code>pop</code> without a default raises <code>KeyError</code>.", "Dictionaries don't expose keys as attributes: <code>AttributeError</code>."]},
          {"type": "predict", "prompt": "What does this print?",
           "code": "d = {'x': 1, 'y': 2}\nd['x'] = 10\nd['z'] = 3\nprint(list(d))",
           "answer": "['x', 'y', 'z']",
           "explanation": "Replacing a value keeps the key's position; new keys go at the end."},
          {"type": "multi", "prompt": "Which of these can be dictionary <strong>keys</strong>? Select all that apply.",
           "options": ["<code>(1, 2)</code>", "<code>[1, 2]</code>", "<code>'name'</code>", "<code>frozenset({1})</code>", "<code>{'a': 1}</code>", "<code>frozendict(a=1)</code>"],
           "answer": [0, 2, 3, 5],
           "explanation": "Keys must be hashable: tuples of hashable values, strings, frozensets and frozendicts are; lists and dicts can change, so they aren't."},
          {"type": "short", "prompt": "Which <code>dict</code> method returns a key's value, inserting a default first if the key is missing?",
           "accept": ["setdefault", "dict.setdefault", "d.setdefault", "setdefault()"],
           "accept_regex": "^(d\\.|dict\\.)?setdefault(\\(\\))?$",
           "explanation": "<code>d.setdefault(k, default)</code>, the heart of the grouping pattern."},
          {"type": "order", "prompt": "Put the steps of the counting pattern in order.",
           "items": ["Create an empty dict: <code>counts = {}</code>", "Loop over the items", "Read the current count: <code>counts.get(item, 0)</code>", "Store that count plus one in <code>counts[item]</code>"],
           "explanation": "Start empty, then for each item read-with-default and write back."},
          {"type": "mcq", "prompt": "<code>a = {'k': 1}</code> and <code>b = {'k': 2}</code>. What is <code>a | b</code>?",
           "options": ["<code>{'k': 1}</code>", "<code>{'k': 2}</code>", "<code>{'k': [1, 2]}</code>", "<code>TypeError</code>"],
           "answer": 1,
           "explanation": "The right-hand side wins when both dictionaries have the key."},
          {"type": "predict", "prompt": "Advanced: what does this print?",
           "code": "print({1: 'a', True: 'b', 1.0: 'c'})",
           "answer": "{1: 'c'}",
           "explanation": "<code>1 == True == 1.0</code>, so they are one key: the first key object stays and the last value wins."}
        ]}
        </script>
      </section>

      <section class="summary" id="summary">
        <h2>Summary</h2>
        <ul>
          <li data-level="essential">A dictionary maps hashable keys to any values and finds a value from its key in one step.</li>
          <li data-level="essential"><code>d[k]</code> when the key must exist, <code>d.get(k, default)</code> when it may not; <code>k in d</code> tests keys.</li>
          <li data-level="essential">Loop with <code>for k, v in d.items():</code>; order is insertion order.</li>
          <li data-level="essential">Counting: <code>d[k] = d.get(k, 0) + 1</code>. Grouping: <code>d.setdefault(k, []).append(x)</code>.</li>
          <li data-level="extra"><code>a | b</code> merges (right wins); views are live and keys/items views support set operations.</li>
          <li data-level="extra"><code>copy()</code> is shallow; use <code>copy.deepcopy</code> for nested data. JSON keys are always strings.</li>
          <li data-level="extra"><code>frozendict</code> (3.15) is the immutable, hashable dictionary; <code>MappingProxyType</code> is a read-only window onto a dict.</li>
          <li data-level="advanced">Lookups are O(1) on average because dictionaries are hash tables; equal keys must have equal hashes.</li>
        </ul>
        <aside class="callout" data-kind="job">
          <p>Where this shows up at work: API payloads and responses (JSON), configuration, caches and memoisation, feature dictionaries before vectorising (<code>sklearn.feature_extraction.DictVectorizer</code>), and the message lists sent to LLM APIs.</p>
        </aside>
        <aside class="callout" data-kind="interview">
          <p>Classic questions that are really dictionary questions: two-sum (store each number's index, look up <code>target - x</code>), first unique character (Exercise 4), group anagrams (key: <code>"".join(sorted(word))</code>), and "is this string a permutation of that one?" (compare counts).</p>
        </aside>
        <p>Go further: <a href="https://docs.python.org/3/library/stdtypes.html#mapping-types-dict">Python docs: mapping types</a> · <a href="https://docs.python.org/3/glossary.html#term-hashable">glossary: hashable</a> · <a href="https://docs.python.org/3/library/types.html#types.MappingProxyType">types.MappingProxyType</a>.</p>
      </section>

      <div class="lesson-complete"></div>
      <nav class="pager" aria-label="Previous and next lesson"></nav>
    </main>
  </div>
</body>
</html>
````
