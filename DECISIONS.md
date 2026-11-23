# Decisions

Each line: date, decision, reason. The settings in force are the table in `CLAUDE.md` §2; every change to that table is also logged here.

| Date | Decision | Reason |
|---|---|---|
| 2026-11-23 | Build the course from kit v5 with the defaults in `CLAUDE.md` §2: Python 3.15, 65 libraries pinned in six phase files, a static site on GitHub Pages | The owner's starting point; the kit was verified with these settings |
| 2026-11-23 | Finder's `.DS_Store` files are not in the first commit, and `.gitignore` ignores them | macOS created them after the kit was unzipped; they are not part of the kit |
| 2026-11-23 | `.gitignore` also ignores `.pytest_cache/`, `.hypothesis/` and `.ipynb_checkpoints/` | Local caches of pytest, Hypothesis and Jupyter, never course content |
| 2026-11-23 | Empty layout folders hold an empty `.gitkeep` file. `site/assets/vendor/`, `site/assets/fonts/` and `.github/workflows/` are created empty instead | Git does not store empty folders. The permission rules guard those three folders (generated assets, workflows), and Stage 1 fills them |
| 2026-11-23 | The course is published from the public GitHub repository `python-ai-course`. GitHub Pages builds from GitHub Actions (`site.yml`) | Pages needs a public repository on GitHub Free, and Actions minutes are free for public repositories. The name follows `BUILD-AND-DEPLOY.md` |
