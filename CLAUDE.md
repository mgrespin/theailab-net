# CLAUDE.md

Guidance for AI coding agents working in this repository.

## What this is

The course website for **IPHS 400: Frontiers in AI** (Kenyon College). Static
HTML + one CSS file. It is served locally; there is no deployment.

## Hard constraints

1. **No build step.** No SSG, templating engine, bundler, or Node toolchain.
2. **No JavaScript** on any page.
3. **No external runtime dependencies** — no CDN links, web fonts, analytics,
   or third-party embeds. Everything is served from the repo.
4. **Page content is the instructor's.** Fix inconsistencies between pages, add
   links, restructure duplicated blocks — do not rewrite course policy, dates,
   or assignment substance.

## Layout

- `index.html`, `404.html` — root pages
- `core/` — syllabus, schedule, assignments, policies, about
- `weeks/` — `week-01.html` … `week-15.html`
- `css/style.css` — the only stylesheet
- `tests/` — pytest suite (structure, links, metadata, a11y, calendar, CSS)
- `docs/` — internal review reports and specs (not part of the site)

## Rules the tests enforce

- Every page: `<!DOCTYPE html>`, `<title>` ending `– IPHS 400: Frontiers in AI`,
  a `<meta name="description">` (50–160 chars), favicon link, canonical +
  Open Graph tags, the shared header / identical nav / footer, a skip link,
  and a `.hero` `<h1>`.
- Each week's title is identical in four places: `schedule.html` link text,
  `<title>`, hero `<h1>`, breadcrumb.
- No large content block is duplicated verbatim across two pages.
- No dead CSS class selectors; no leftover template branding.
- The canonical origin for absolute URLs is `https://theailab.net`.

## Workflow

```bash
uv venv --python=3.12 && source .venv/bin/activate
uv pip install -r tests/requirements.txt
pytest tests/ -v            # must stay green
python3 -m http.server 8080 # to view
```

Work on a branch, keep the suite green, add a test for any new behavior.
