# Tech-Spec — IPHS 400 Course Site Revision

**Repository:** `theailab-net`
**Base commit:** `dfe40a6` (after H.0: Netlify/CI stripped)
**Date:** 2026-09-03
**Source:** synthesized from `docs/report_web-revision_v1_20260901.md`
**Author:** Claude (Sonnet 5), for Mini-Project #1

---

## 0. How to read this

Every task below has: an **ID**, a **criticality** (`high` / `medium` / `low`),
a one-line **description**, a **justification**, and **step-by-step
instructions**. Tasks are ordered by criticality, then by dependency.

Each task is written so that "done" is testable: where a task adds or changes
behavior the site can assert, it names the test to add or extend (all in
`tests/`). The implementation loop is: **write/extend the test → make the
change → run `pytest tests/` → fix until green → commit.**

### Design constraints (do not violate)

1. **No build step.** The site is flat HTML + one stylesheet, served directly by
   `python3 -m http.server`. No SSG, no templating engine, no bundler, no
   Node. This is a deliberate course-design choice; see §4.
2. **No JavaScript.** No runtime JS on any page.
3. **No external runtime dependencies.** No CDN links, web fonts, analytics, or
   third-party embeds. Everything is served from the repo.
4. **Page *content* is authoritative.** Wording of course policy, dates, and
   assignment descriptions is the instructor's. Revisions may fix
   inconsistencies *between* pages, add links, and restructure duplicated
   blocks — they may not rewrite policy substance.

---

## 1. HIGH criticality

### T-01 · high · Add real hyperlinks and `mailto:` for every external reference

**Justification.** `grep 'href="http'` across the site returns nothing. Every
external resource a student needs — the course GitHub repo, Moodle,
`digital.kenyon.edu/dh`, the SASS email, OpenRouter, Anthropic — is plain text
or wrapped in `<code>`. For a course whose model is "materials in the repo,
submissions on Moodle," making students hand-copy URLs is a real regression.

**Scope of links to add** (exhaustive list — do not invent URLs beyond these):

| Location(s) | Current text | Becomes |
|---|---|---|
| `syllabus.html`, `about.html` | `https://github.com/jon-chun/theailab-net` in `<code>` | `<a href="https://github.com/jon-chun/theailab-net">` (keep `<code>` inside the `<a>` or drop it — pick one and be consistent) |
| all pages that say "Moodle" | plain text | link to `https://moodle.kenyon.edu` on first mention per page only |
| `syllabus.html`, `about.html`, `policies.html`, `assignments.html` | `digital.kenyon.edu/dh` | `<a href="https://digital.kenyon.edu/dh">` on first mention per page |
| `policies.html` | `sass@kenyon.edu` | `<a href="mailto:sass@kenyon.edu">sass@kenyon.edu</a>` |
| `syllabus.html` | "OpenRouter.com" | `<a href="https://openrouter.ai">` |
| `syllabus.html` | "Anthropic.com (Claude) subscription" | `<a href="https://www.anthropic.com">` |
| `assignments.html` | "course poster template (link on the course repository)" | link the phrase "course repository" to the repo URL; leave the template's own path as text (the file may not exist yet) |

**Rules.**
- External `<a>` get `rel="noopener"` only if they also get `target="_blank"`.
  Default: **no** `target="_blank"` (same-tab is fine and simpler).
- Link the **first** occurrence of a given resource on each page, not every
  occurrence, to avoid a wall of links.
- Do not add links to resources not already named in the copy.

**Steps.**
1. Extend `tests/test_integration_links.py` with a class `TestExternalLinks`:
   - `test_known_external_resources_are_linked`: for a fixed map of
     `(page, substring) -> expected_href`, assert the page contains an `<a>`
     with that `href`. (Encodes the table above.)
   - `test_all_external_links_have_safe_rel`: any `<a target="_blank">` must
     have `rel` containing `noopener`.
   - `test_no_bare_urls_in_code_or_text`: no `http(s)://` substring appears
     outside an `<a href>` (allowing a documented exception list if needed).
2. Run the suite — the new tests fail.
3. Edit the HTML pages to add the anchors.
4. `pytest tests/` green. Commit.

---

### T-02 · high · De-duplicate verbatim content across pages

**Justification.** Three blocks are copied word-for-word between pages, so every
future edit must be made twice or the site contradicts itself:

| Block | Copies | Canonical home (this spec's decision) |
|---|---|---|
| "Course Description" + "Course Goals and Learning Outcomes" | `syllabus.html` ↔ `about.html` | **Syllabus** |
| "Summary of Assignments and Weights" table | `syllabus.html` ↔ `assignments.html` | **Syllabus** (grading contract) |
| "Secrets Hygiene and Agent Safety" list | `syllabus.html` ↔ `policies.html` | **Policies** |

**Steps.**
1. `about.html`: replace the two duplicated `<h2>` sections with a 2–3 sentence
   summary of the course and a sentence: *"See the [Syllabus](../core/syllabus.html)
   for the full course description and the nine learning outcomes."* Keep the
   Instructor table and Course Site list (those are About-specific).
2. `assignments.html`: replace the full weights `<table>` with one sentence
   linking to `syllabus.html#assignments-weights` (add that `id` to the table's
   heading on the syllabus). Keep the intro paragraph and all the per-project
   `<h2>` sections — that detail is the Assignments page's job.
3. `syllabus.html`: replace the full "Secrets Hygiene and Agent Safety" `<ul>`
   with a 1–2 sentence summary linking to `policies.html#secrets-hygiene` (add
   that `id`).
4. Verify no remaining block > ~40 words is byte-identical between two pages
   (add `tests/test_integration_links.py::TestNoDuplicateBlocks` — hash each
   `<h2>`/`<h3>` section's text, assert no hash collision across different
   pages, with a short allowlist for headings/boilerplate).
5. `.page-content` min-text test still passes (About stays well over 20 chars).
6. Reachability test still passes (new links keep every page reachable).
7. `pytest tests/` green. Commit.

**Reviewer note.** The canonical-home choices above are judgment calls. If the
instructor wants the weights table to live on the Assignments page instead,
swap the direction — the de-dup principle is the point, not the specific home.

---

## 2. MEDIUM criticality

### T-03 · medium · Make each week's title identical in all four places

**Justification.** For 5 of 15 weeks the `schedule.html` link text disagrees with
the destination page's `<title>`, `<h1>`, and breadcrumb:

| Week | `schedule.html` link text | Week page `<title>` / `<h1>` / breadcrumb |
|---|---|---|
| 6 | Hooks Architecture **and Guardrails** | Hooks Architecture |
| 10 | ...Spec-Driven **Development** Landscape | ...Spec-Driven Landscape |
| 13 | ...Work Session **and MP4 Presentations** | ...Work Session |
| 14 | ...Work Session **and Poster Development** | ...Work Session |
| 15 | Final Project **Poster** Presentations | Final Project Presentations |

**Steps.**
1. Add `tests/test_integration_links.py::TestWeekTitleConsistency`:
   for each `week-NN.html`, assert that
   `schedule.html` link text == page `<title>` prefix (before ` – IPHS 400…`)
   == hero `<h1>` text == breadcrumb final `<span>` text.
2. Run — it fails for weeks 6, 10, 13, 14, 15.
3. Pick one canonical title per week. **Default: adopt the longer, more
   descriptive `schedule.html` phrasing** and propagate it into the four
   locations on each week page. (Reviewer may prefer the shorter form — either
   is fine as long as all four agree.)
4. `pytest tests/` green. Commit.

---

### T-04 · medium · Add a `<meta name="description">` to every page

**Justification.** 0 of 22 pages has one; search and link-preview snippets are
auto-generated and poor.

**Steps.**
1. Add `tests/test_unit_html_structure.py::TestMetaDescription`:
   every page has exactly one `<meta name="description">` with 50–160 chars of
   non-empty content.
2. Write a one-sentence description per page (22 total): index, 404, 5 core, 15
   weeks. Week descriptions can follow a template: *"IPHS 400 Week N: {topic}.
   {one clause on what happens that week}."*
3. `pytest tests/` green. Commit.

---

### T-05 · medium · Add a favicon

**Justification.** Every page load 404s on `/favicon.ico`.

**Steps.**
1. Add `favicon.svg` at repo root — a tiny, dependency-free mark (e.g. a
   monogram "AI" or a lab-flask glyph in `--accent` `#0073aa`). Inline SVG text,
   no raster.
2. Add `<link rel="icon" href="/favicon.svg" type="image/svg+xml">` to every
   page's `<head>` (path is root-absolute so it works from `core/` and `weeks/`).
3. Add `tests/test_e2e_site.py` check: `favicon.svg` exists; every page links to
   it.
4. `pytest tests/` green. Commit.

---

### T-06 · medium · Add canonical URL + Open Graph / Twitter Card tags

**Justification.** Shared links render as bare URLs. A canonical tag also
disambiguates `index.html` vs `/`.

**Steps.**
1. Decide the production origin. **Default assumption: `https://theailab.net`.**
   Put it in one place — a comment in the spec and a constant in the test — so
   it is easy to change.
2. Per page add to `<head>`:
   - `<link rel="canonical" href="{origin}/{path}">`
   - `<meta property="og:title" content="{page title}">`
   - `<meta property="og:description" content="{same as meta description}">`
   - `<meta property="og:type" content="website">`
   - `<meta property="og:url" content="{canonical}">`
   - `<meta name="twitter:card" content="summary">`
3. Add `tests/test_unit_html_structure.py::TestSocialMeta`: every page has a
   canonical link whose href ends with the page's own path, and the five OG/
   twitter tags, with `og:description` == the `meta name="description"` content.
4. `pytest tests/` green. Commit.

**Reviewer note.** If the real origin is not `theailab.net`, it is a one-line
change to the test constant + a find/replace.

---

### T-07 · medium · Add `robots.txt` and `sitemap.xml`

**Justification.** 22 stable pages; a sitemap is cheap crawlability. `robots.txt`
should also exclude `/tests/` and `/docs/` from indexing.

**Steps.**
1. Add `robots.txt` at repo root: `User-agent: *` / `Allow: /` /
   `Disallow: /tests/` / `Disallow: /docs/` / `Sitemap: {origin}/sitemap.xml`.
2. Add `sitemap.xml` at repo root listing all 21 linked pages (exclude
   `404.html`), each `<url><loc>` using the canonical origin.
3. Add `tests/test_e2e_site.py::TestSitemap`: both files exist; every non-404
   HTML page appears exactly once in `sitemap.xml`; no stale entries.
4. `pytest tests/` green. Commit.

**Note.** If T-06's origin changes, `sitemap.xml` and `robots.txt` must change
with it — the test in step 3 should key off the same constant.

---

### T-08 · medium · Accessibility batch (WCAG 2.1 AA structural gaps)

**Justification.** Report findings B-1…B-8: no skip link, current page not
exposed to AT, tables without `<caption>`/`scope`, unnamed landmarks, no
explicit focus style, `index.html` `<h1>` is just "Home".

**Steps.**
1. Add `tests/test_unit_html_structure.py::TestAccessibility` with one method
   per check below; run — all fail.
2. Implement across all pages:
   - **Skip link:** first child of `<body>`:
     `<a class="skip-link" href="#main">Skip to content</a>`; add `id="main"`
     to `<main>`; add a `.skip-link` rule to `style.css` (visually hidden until
     `:focus`).
   - **Current page:** the active nav `<a>` gets `aria-current="page"` (keep the
     `class="active"` too).
   - **Nav name:** `<nav class="main-nav" aria-label="Primary">`.
   - **Breadcrumbs:** convert `<div class="breadcrumbs">` to
     `<nav class="breadcrumbs" aria-label="Breadcrumb">` containing an `<ol>`
     with `<li>` items (update `style.css` selector; the ` » ` separators become
     CSS `::before` on `li + li` or stay as literal text — pick one).
   - **Tables:** every `<table>` gets a `<caption>` (may be visually hidden via
     a `.sr-only` class); row-header cells get `scope="row"`, column-header
     cells `scope="col"`.
   - **Focus:** add `:focus-visible { outline: 2px solid var(--accent);
     outline-offset: 2px; }` to `style.css`.
   - **Hero element:** change `<section class="hero">` to `<div class="hero">`
     (the `<h1>` provides the heading; a nameless `<section>` is an a11y
     anti-pattern). **Update `tests/test_unit_html_structure.py`
     `test_all_pages_have_hero_with_h1`** to select `.hero` rather than
     `section.hero`.
   - **Index heading:** `index.html` `<h1>Home</h1>` →
     `<h1>IPHS 400: Frontiers in AI</h1>`; update its `<title>` from
     `Home – …` to `Home – …` is fine, but the `<h1>` and breadcrumb/label
     stay "Home" in the nav. (Nav label test still expects "Home" — leave nav
     text alone; only the hero `<h1>` changes.)
3. Keep existing tests green — note the two deliberate test edits above
   (`.hero` selector; hero `<h1>` text is no longer asserted to equal the nav
   label anywhere).
4. `pytest tests/` green. Commit.

---

### T-09 · medium · Delete dead CSS; clean font stacks and header comment

**Justification.** ~55% of `style.css` targets classes (`has-featured-image`,
`featured-media`, `social-nav`, `entry-meta`, `entry-footer`, `post-nav`,
`share-links`, `post-preview`, `other-blog-pages`, `page-meta`, `badge*`,
`placeholder-notice`, `columns`, `wp-block-*`) that appear in **zero** pages —
leftovers from the WordPress theme this was ported from.

**Steps.**
1. Add `tests/test_unit_html_structure.py::TestNoDeadCSS` (or put it in a new
   `tests/test_unit_css.py`): parse `style.css` for class selectors; for each,
   assert at least one HTML page uses that class. Allow a small explicit
   allowlist (`.sr-only`, `.skip-link`, `.active`, `print-only` helpers, etc.).
2. Run — it lists the dead selectors.
3. Delete the dead rule blocks. Cross-check that nothing remaining references a
   deleted custom property (`--draft`, `--priv`, `--primary` if now unused).
4. `style.css:17-18`: remove `"NonBreakingSpaceOverride"` from `--fh` and
   `--fb` (WordPress hack, forces a failed font lookup).
5. `style.css:1-4`: rewrite the header comment to describe *this* site, not
   "Twenty Nineteen-faithful theme for Programming Humanity".
6. Manually diff-check the rendered site before/after (Part I.2 visual pass) —
   pixel output should be unchanged.
7. `pytest tests/` green. Commit.

---

### T-10 · medium · Pin test dependencies to exact versions

**Justification.** `tests/requirements.txt` is `pytest>=7` / `beautifulsoup4>=4`
/ `lxml>=4`. An `lxml`/`bs4` release can change parsing behavior and break — or
silently change — results.

**Steps.**
1. Freeze the currently-installed, known-good versions:
   `pytest==9.1.1`, `beautifulsoup4==<installed>`, `lxml==<installed>`,
   plus their pinned transitive deps (`soupsieve`, etc.) — generate with
   `uv pip freeze`.
2. Split: `tests/requirements.in` (the three direct deps, still loosely ranged
   for humans) + `tests/requirements.txt` (fully pinned, machine-generated,
   with a header comment saying how to regenerate).
3. Update `README.md` test instructions if the filename split changes the
   command.
4. `pytest tests/` green in a fresh venv. Commit.

---

### T-11 · medium · Cross-check all calendar dates for internal consistency

**Justification.** Dates are hand-entered across `schedule.html`,
`syllabus.html`, `assignments.html`, and 15 week pages. The report flags
possible drift (Week 15 sessions vs. last-day-of-classes; MP4 presentation
dates vs. Thanksgiving recess).

**Steps.**
1. Add `tests/test_integration_links.py::TestCalendarConsistency` — a
   data-driven check, not a live-calendar check:
   - every "Week N" page states a session date that falls in the Mon–Fri range
     implied by `schedule.html`'s "classes begin Aug 27 / breaks / last day
     Dec 11";
   - assignment due dates mentioned on `assignments.html` match the same dates
     on `syllabus.html`'s weights table (string-equal).
2. Run — record every mismatch.
3. Fix mismatches by making the pages agree. **Where a date cannot be resolved
   from the pages alone (needs the real Kenyon 2026–27 academic calendar),
   list it in a `docs/` note for the instructor rather than guessing.**
4. `pytest tests/` green (or xfail-with-note for instructor-only items). Commit.

---

### T-12 · medium · Harden and extend the test suite

**Justification.** Report section I. The suite parses leniently (malformed HTML
passes) and does not check titles, a11y, or metadata. Several of the checks
above (T-01…T-08) add tests; this task adds the general-purpose ones and
tidies `conftest.py`.

**Steps.**
1. `tests/test_unit_html_structure.py::TestHTMLValidity`:
   - no duplicate `id` attribute within a page;
   - every `<a href>` that is not external/anchor/mailto resolves (already
     covered — keep);
   - every `<img>` has `alt` (currently no images, so this is a guard);
   - `<html lang>` present and non-empty.
   *(Full Nu-validator/`html5validator` needs a JRE and is out of scope; this
   is the lint subset that catches the common breakages.)*
2. `conftest.py`: wrap the `lxml` parse in a clear error if `lxml` is missing
   ("run `uv pip install -r tests/requirements.txt`").
3. `tests/test_e2e_site.py`: keep `EXPECTED_TOTAL_PAGES == 22` but also assert
   the **shape** (`1 index + 1 404 + 5 core + N weeks`, N derived from the
   directory) so an intentional new week page gives a clear message.
4. `pytest tests/` green. Commit.

---

## 3. LOW criticality

### T-13 · low · Normalize nav markup

`index.html` writes `href` before `class="active"`; every other page writes
`class` first. Some pages use `../core/x.html` from within `core/`, others use
`x.html`. Pick one form each and make all 22 pages match. Add a test:
nav `<a>` on each page use the shortest correct relative path and a consistent
attribute order (attribute-order check optional — a string-normalise compare is
enough). Commit.

### T-14 · low · Contrast + Quick Links

- `style.css`: `--text-lt: #767676` → `#6b6b6b` (comfortable AA margin at the
  15–16px sizes it is used at). Verify the footer/breadcrumb still look right in
  the visual pass.
- `index.html`: the "Quick Links" list duplicates the nav directly above it.
  **Decision: keep it** (it is a reasonable landing-page affordance) but drop
  "About" from it so it is "things you do" not "every nav item". Reviewer may
  prefer to delete the block entirely.
Commit.

### T-15 · low · Print stylesheet

Add `@media print` to `style.css`: hide `.main-nav` and `.skip-link`, un-pin the
left column (`--col-left: 0`), force black text, show external link hrefs after
the link text (`a[href^="http"]::after { content: " (" attr(href) ")"; }`).
Add a test that the string `@media print` appears in `style.css`. Commit.

### T-16 · low · `.gitignore` trim

Replace the 218-line GitHub Python template with ~20 relevant lines:
`.venv/`, `__pycache__/`, `.pytest_cache/`, `*.pyc`, `.DS_Store`, `.vscode/`,
`.idea/`, `.ruff_cache/`. Nothing the site generates is currently ignored that
matters. Commit.

### T-17 · low · `CONTRIBUTING.md` + `CHANGELOG.md`

- `CONTRIBUTING.md`: ~15 lines — "edit the HTML in `core/`/`weeks/`, keep the
  shared header/nav/footer identical across pages, run `pytest tests/`, open a
  PR." Note the "one canonical week title" and "no build step / no JS" rules.
- `CHANGELOG.md`: seed with a `[Unreleased]` section summarising this revision
  pass (Keep-a-Changelog format).
Commit.

### T-18 · low · Add `CLAUDE.md` for the repo

The course teaches `CLAUDE.md` authoring; the course's own repo should model it.
~30 lines: how to run the tests, the design constraints from §0 of this spec,
the "no leftover template branding" rule, "week titles must match in four
places", where docs go. Commit.

### T-19 · low · README provenance + site-name note

- `README.md:105-107`: the provenance link points at
  `https://github.com/jon-chun` (a profile, not a repo). Link the actual source
  repo or drop the link.
- Add one line somewhere on `index.html` or `about.html`: *"This site is also
  reachable at theailab.net"* (resolves the repo-name vs. course-name gap).
Commit.

### T-20 · low · `prefers-color-scheme` (optional, may skip)

A dark palette via `@media (prefers-color-scheme: dark)` reassigning the
`:root` custom properties. Low value for a text site, non-trivial to get right
(duotone tokens, table borders). **Recommend skipping** unless the visual pass
shows time to spare.

---

## 4. Explicitly OUT of scope (documented, not implemented)

| Report item | Why deferred |
|---|---|
| **E-1 — introduce a build step / templating / SSG** | Directly contradicts design constraint §0.1 and the project manual's framing ("plain HTML/CSS with no build step"). It is a large, invasive change: all 22 files restructure, the test suite re-points at a build output, and a new toolchain (Python build script or Node SSG) enters a course that deliberately has none. This is a real improvement worth doing — but as a **separate, instructor-approved decision**, not folded into a revision pass. The de-dup in T-02 removes the worst *content* duplication without it. |
| **Full `axe-core` / `pa11y` a11y automation in CI** | Needs Node + a headless browser, and there is no CI after H.0. Replaced by the structural a11y assertions in T-08 / T-12. |
| **CSP / HSTS / `Permissions-Policy` response headers (G-1)** | These are hosting-layer config; H.0 removed the hosting layer. `<meta http-equiv>` CSP is brittle and partial. Revisit if/when a host is chosen. |
| **Scheduled external-link liveness check (I-4)** | Needs CI. Could be a local `make linkcheck` target later. |
| **`nwtgck/actions-netlify` SHA pin (H-1) and other CI hardening (H-3…H-7)** | The workflow was deleted in H.0. Moot. |

---

## 5. Suggested commit / execution order

1. T-01, T-02 (high)
2. T-03 (unblocks the title-consistency test other tasks rely on)
3. T-04 → T-05 → T-06 → T-07 (metadata chain — share the origin constant)
4. T-08, T-09 (a11y + CSS — both touch `style.css`; do together, one visual pass)
5. T-10, T-11, T-12 (test/infra)
6. T-13 … T-19 (low — can be batched into 2–3 commits)
7. T-20 only if time remains
8. Part I.2 — serve the site, click every page in Chrome, confirm the visual
   pass for T-08/T-09/T-14.
