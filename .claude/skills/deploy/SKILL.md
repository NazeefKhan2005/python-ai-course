---
name: deploy
description: Publish the course to GitHub Pages - preflight checks, create the GitHub repository and turn on Pages the first time, push, watch the workflow and report the site's address. Use when the owner types /deploy.
disable-model-invocation: true
---

Publish the `main` branch with `.github/workflows/site.yml`. Every push to `main` runs `python tools/ci.py --partial` on GitHub and, if it passes, deploys `site/` to GitHub Pages. The full release check is for Stage 9.

1. **Preflight.** The branch must be `main` and `git status` clean (otherwise ask me whether to commit first). Run `python tools/build.py --check` and `python tools/ci.py --partial`; stop on anything red and suggest `/fix-ci`. Run `gh auth status`; if `gh` is missing or signed out, tell me to run `brew install gh` and `gh auth login`, and stop.
2. **Repository, first time only.** If `git remote get-url origin` fails, ask me for the repository name, then run `gh repo create <name> --public --source . --remote origin`. It must be public on GitHub Free: Pages needs a public repository on that plan, and Actions minutes are free for public repositories.
3. **Pages, first time only.** Run `gh api repos/{owner}/{repo}/pages`. If it answers 404 (Not Found), turn Pages on with GitHub Actions as the source: `gh api --method POST repos/{owner}/{repo}/pages -f build_type=workflow`. If that fails, give me the manual steps: the repository's **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. **Push.** Ask me first, then `git push -u origin main`.
5. **Watch.** Find the run with `gh run list --workflow site.yml --branch main --limit 1` and follow it with `gh run watch <id> --exit-status`. The first run installs every pinned library and takes longest.
6. **Report.** On success: the site's address (`https://<owner>.github.io/<repository>/`) and the run's link, after checking that the home page, the setup page and one lesson load. On failure: the failing step, then follow `/fix-ci` with the run id.

For the release (Stage 9): `gh workflow run site.yml -f release=true` (ask me first), then watch that run the same way.
