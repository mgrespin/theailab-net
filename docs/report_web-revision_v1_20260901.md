# Web Revision Report — IPHS 400 Course Site

**Repository:** `theailab-net`
**Reviewed commit:** `4184aa1` (Migrate IPHS 400 course site from ai-swe-best-practices)
**Date:** 2026-09-01
**Reviewer:** Claude (Sonnet 5), automated code/content review
**Scope:** Full static site — 22 HTML pages, one stylesheet, pytest suite, Netlify config, GitHub Actions deploy workflow, repo docs.

---

## 1. Executive Summary

The site is small, fast, dependency-free, and structurally consistent. The pytest
suite (25 tests, all passing) is a genuine strength and already enforces things
most course sites get wrong: DOCTYPE, title convention, nav-label consistency,
internal-link resolution, page reachability, and "no leftover template branding."

However, the review found **one theme that dominates everything else**: the site
is 22 hand-maintained HTML files with no templating, and it carries the skeleton
(and stylesheet) of the WordPress theme it was ported from. This produces three
recurring problems — duplicated markup, duplicated *content*, and ~55% dead CSS —
and the test suite currently *locks the duplication in place* by asserting exact
equality of the copied navigation across 21 pages.

Beyond that, the most actionable gaps are:

| # | Area | Severity |
|---|------|----------|
| F-1 | No external links anywhere — GitHub repo, Moodle, `digital.kenyon.edu`, SASS email, poster template are all plain text | **High** |
| F-2 | Content duplicated across pages (About ≈ Syllabus, assignments table ×2, secrets policy ×2) with no single source of truth | **High** |
| F-3 | Schedule link text disagrees with the target page's own `<title>`/`<h1>` for Weeks 10, 13, 15 | **Medium** |
| F-4 | No `<meta name="description">`, canonical URL, Open Graph, favicon, `robots.txt`, or `sitemap.xml` on any page | **Medium** |
| F-5 | ~55% of `css/style.css` targets classes that appear in zero pages (blog, featured-image, badges, WP blocks) | **Medium** |
| F-6 | GitHub Actions uses a third-party action pinned to a mutable tag (`nwtgck/actions-netlify@v3`); test deps unpinned | **Medium** |
| F-7 | Accessibility: no skip link, no `aria-current`, tables missing `scope`/`<caption>`, no `<caption>`, borderline contrast on muted text | **Medium** |
| F-8 | `netlify.toml` publishes the repo root, so `tests/*.py`, `.github/`, `netlify.toml` are served on the CDN | **Low** |
| F-9 | No security headers beyond two (`CSP`, `Referrer-Policy`, `HSTS`, `Permissions-Policy` absent) | **Low** |
| F-10 | README placeholder ("_add Netlify URL here_"), vague provenance link, brittle hard-coded page count in tests | **Low** |

Nothing here is a functional defect that breaks the site for a visitor today. The
recommendations are about making the site cheaper to maintain over a semester of
weekly edits, more accessible, more discoverable, and better aligned with the
software-engineering practices the course itself teaches.

---

## 2. What the Site Does Well

- **Zero build step, zero runtime JS, one stylesheet.** Loads instantly, trivial to host, nothing to break.
- **Consistent page skeleton.** Every page has DOCTYPE, `lang="en"`, charset, viewport, a titled hero `<h1>`, shared header/nav/footer.
- **A real test suite.** `tests/` validates structure, internal links, nav consistency, reachability from `index.html`, exact page inventory, and absence of stub/placeholder text. This is well above the norm for a course site.
- **CI gates deploy on tests.** `deploy` job `needs: test`, so a broken build won't publish.
- **Sensible viewport meta** — `width=device-width, initial-scale=1.0` with no `maximum-scale`, so pinch-zoom is preserved (an accessibility positive).
- **Least-privilege workflow token** — `permissions: contents: read` at workflow level.
- **`concurrency` group** on the deploy workflow prevents overlapping production deploys.
- **Breadcrumbs** on every interior page, with a correct Home » Schedule » Week trail on week pages.
- **Content is substantive and accurate-looking** — the syllabus, policies, and assignments read as a real, carefully written course, not filler.

---

## 3. Findings

Severity key: **High** = fix before the semester relies on it · **Medium** = fix
this month · **Low** = cleanup / nice-to-have.

### A. Links and Navigation

**A-1 · High · No external links exist on the entire site.**
`grep` for `href="http` across all HTML returns nothing. The only hrefs on the
site are internal `.html` links and `css/style.css`. Yet the content refers a
student to, at minimum:

- the course GitHub repo — `core/syllabus.html:39`, `core/about.html:60` (shown in `<code>`, not linked)
- Moodle — many pages
- `digital.kenyon.edu/dh` — `core/assignments.html`, `core/policies.html`
- `sass@kenyon.edu` — `core/policies.html:101` (not a `mailto:`)
- the Final Project **poster template** — "link on the course repository" (`core/assignments.html:81`) — there is no link
- OpenRouter, Anthropic, GitHub Spec-Kit, OpenSpec — `core/syllabus.html`, `weeks/week-10.html`

For a course whose stated model is "readings and the authoritative schedule live
in the GitHub repo; submissions go through Moodle," making students copy-paste
URLs from rendered text is a real usability regression. **Add real `<a>` elements**
(with `rel="noopener"` for `target="_blank"` if used) for every external
reference, and a `mailto:` for the SASS address.

**A-2 · Medium · Schedule link text ≠ destination page title.**

| Schedule link text (`core/schedule.html`) | Week page `<title>` / `<h1>` / breadcrumb |
|---|---|
| Week 10: MP3 Demos and the Spec-Driven **Development** Landscape | Week 10: MP3 Demos and the Spec-Driven Landscape |
| Week 13: Full-Cycle Capstone Work Session **and MP4 Presentations** | Week 13: Full-Cycle Capstone Work Session |
| Week 15: Final Project **Poster** Presentations | Week 15: Final Project Presentations |

Pick one canonical title per week and use it in all four places (`schedule.html`
link, `<title>`, hero `<h1>`, breadcrumb `<span>`). Then add a test that asserts
they match (see I-2).

**A-3 · Low · `index.html` nav uses a different attribute order** (`href` before
`class="active"`) than every other page (`class="active"` before `href`). Cosmetic,
but a tell that pages were edited by hand rather than generated from a template.
A formatter or generator would normalize this.

**A-4 · Low · Redundant Quick Links block.** `index.html` lists Syllabus /
Schedule / Assignments / Policies / About in the main content (`index.html:37-45`)
— the same five links already in the nav directly above. Not wrong, but it is
duplicated maintenance surface.

### B. Accessibility (WCAG 2.1 AA)

**B-1 · Medium · No "skip to content" link.** Keyboard and screen-reader users
tab through the full 6-item nav on every page before reaching `<main>`. Add
`<a class="skip-link" href="#main">Skip to content</a>` as the first body child
and `id="main"` on `<main>`.

**B-2 · Medium · Current page not exposed to assistive tech.** The active nav item
gets `class="active"` (visual only). Add `aria-current="page"` to the active link.

**B-3 · Medium · Data tables lack semantics.**
- No `<caption>` on any table (`index.html:30`, `core/syllabus.html:30,74,104,121`, etc.).
- Row-header tables (`<th>Instructor</th><td>Jon Chun</td>`) don't mark the `<th>` as `scope="row"`; column-header tables don't use `scope="col"`.
- Screen readers cannot announce header/data relationships correctly as written.

**B-4 · Medium · `<nav>` has no accessible name.** With one `<nav class="main-nav">`
today it's tolerable, but `aria-label="Primary"` on the nav and `aria-label` on
the breadcrumb `<div>` (better: make breadcrumbs a `<nav aria-label="Breadcrumb">`
with an `<ol>`) is the standard pattern.

**B-5 · Low · Muted-text contrast is at the AA floor.** `--text-lt: #767676` on
white is ≈4.5:1 — it passes AA for normal text with essentially no margin, and is
used at 15–16px for the footer, breadcrumbs, and site description. Darkening to
`#6b6b6b` or `#666` buys a comfortable margin. Link color `#0073aa` on white is
≈5:1 (passes AA, fails AAA).

**B-6 · Low · No visible focus styling is defined.** The CSS heavily restyles link
`text-decoration` but never defines `:focus-visible`. Browsers still draw a
default outline, but given the custom link treatment you should define an explicit
`:focus-visible` outline so it's unmistakable.

**B-7 · Low · `<section class="hero">` inside `<header>`.** A `<section>` should
have an accessible name; here it wraps only the `<h1>`. It also sits *inside*
`<header>`, which is unusual. A plain `<div>` (or just the `<h1>`) would be more
correct. Low impact because the `<h1>` is present.

**B-8 · Low · `index.html` hero is `<h1>Home</h1>`.** "Home" is a poor document
heading and page identity. Use the course name or "IPHS 400: Frontiers in AI".

**Recommendation:** add `pa11y-ci` or `axe-core` (via `@axe-core/cli` +
Playwright, or `pytest` + `axe-selenium-python`) to CI so these regress-proof.

### C. SEO, Metadata, and Discoverability

**C-1 · Medium · No `<meta name="description">` on any of the 22 pages.** Search
and link-preview snippets will be auto-generated and poor. Add a one-sentence
description per page.

**C-2 · Medium · No favicon.** Every page load produces a `GET /favicon.ico` 404.
Add `favicon.ico` / `favicon.svg` and a `<link rel="icon">`.

**C-3 · Medium · No canonical URL and no Open Graph / Twitter Card tags.** When
the syllabus URL is shared in Slack/email/Moodle it renders as a bare link. Add
`<link rel="canonical">` and `og:title` / `og:description` / `og:type` /
`og:url` (an `og:image` is optional but improves shares).

**C-4 · Low · No `robots.txt` and no `sitemap.xml`.** For 22 pages a static
`sitemap.xml` is cheap and improves crawlability; `robots.txt` can point at it.

**C-5 · Low · No `<html>`-level or `<meta>` theme-color, no `prefers-color-scheme`
support.** Optional, but a dark-mode-friendly palette is a low-cost polish item.

**C-6 · Low · Titles use an en dash separator** (`Syllabus – IPHS 400…`). Fine
and internally consistent (the test enforces it), just noting that ` — ` or ` | `
are the more common separators; not a defect.

### D. Content Consistency and Accuracy

**D-1 · High · Verbatim content duplication across pages.**
- `core/about.html:29-48` reproduces the entire "Course Description" + "Course Goals and Learning Outcomes" from `core/syllabus.html:42-61` word-for-word.
- The "Summary of Assignments and Weights" table appears in full on both `core/syllabus.html:104-116` and `core/assignments.html:32-44`.
- "Secrets Hygiene and Agent Safety" appears in full on both `core/syllabus.html:85-92` and `core/policies.html:85-92`.

Every future edit to any of these must be applied in two places or the site
silently contradicts itself. Choose one authoritative location and replace the
copies with a short summary + link, or generate the shared block from one source
file at build time (see E-1).

**D-2 · Medium · Calendar cross-checks are unverified and fragile.** Dates are
spread across `core/schedule.html:29`, `core/syllabus.html`, `core/assignments.html`,
and all 15 week pages, entered by hand. Examples worth auditing:
- `week-15.html` says "Tuesday & Thursday, December 8 & 10"; `schedule.html:29` says last day of classes is Friday, December 11 and final exams Dec 14–18 — check that Week 15 sessions and the presentation dates in `assignments.html` line up.
- `assignments.html` MP4 "presentations Nov 17/19" vs. `schedule.html` Thanksgiving recess starting Nov 21 — plausible but should be verified against the Kenyon academic calendar.

Consider a single `data/schedule.(yml|json)` as the source of truth and render
week pages + the schedule table from it.

**D-3 · Low · Repo/site name mismatch may confuse students.** Site title and all
headings say "IPHS 400: Frontiers in AI"; the repo, and presumably the domain, is
`theailab-net` ("the AI Lab"). If the deployed URL is `theailab.net`, add a line
somewhere ("This course site lives at theailab.net") so students who hear one name
find the other.

**D-4 · Low · `README.md` provenance link is vague.** `README.md:103-104` links
"programminghumanity-org" to `https://github.com/jon-chun` (the user profile, not
a repo). Link the actual source repo or drop the link.

### E. Architecture and Maintainability

**E-1 · High · No templating for a 22-page hand-edited site.** The header, nav
(6 links), hero wrapper, and footer are copied into all 22 files. A nav change is
a 22-file edit — and the test suite (`test_all_nav_pages_have_identical_nav_labels`)
will fail the build until all 21 non-404 copies match, so the tests actively
enforce the copy-paste rather than catch drift in a generated artifact.

Given this is *a course about software-engineering best practices with AI agents*,
the site not eating its own dog food is worth addressing. Options, cheapest first:
1. A ~30-line Python build script that injects `partials/{head,header,footer}.html` into `pages/*.html` → `dist/`. Keeps "no framework," makes the shared skeleton single-source, and the existing pytest suite runs against `dist/`.
2. A minimal SSG (Eleventy, Zola, or `staticjinja`) with a `base.html` layout and a `schedule.yml` data file (also fixes D-2).
3. If "literally zero tooling" is a hard constraint, at least add a `Makefile`/script that regenerates the copied blocks and a CI check that they're in sync.

**E-2 · Medium · Content and presentation both duplicated.** See D-1. A build
step (E-1) plus content includes removes both the markup duplication and the
prose duplication in one move.

**E-3 · Low · No `CLAUDE.md` in the repo.** The course teaches `CLAUDE.md`
authoring; the course's own repo would be a natural teaching example (how to run
the tests, the "one canonical week title" rule, the no-JS constraint, the build
step if added).

### F. CSS Quality

**F-1 · Medium · ~55% of `css/style.css` is dead code.** Confirmed by grep — the
following classes appear in **zero** HTML files:

`has-featured-image`, `featured-media` (+ `::after` duotone), `social-nav`,
`entry-meta`, `entry-footer`, `post-nav`, `share-links`, `post-preview`,
`other-blog-pages`, `page-meta`, `badge` / `badge-draft` / `badge-private` /
`badge-placeholder`, `placeholder-notice`, `columns`, `wp-block-image`,
`wp-block-separator`.

That's roughly `style.css:69-100`, `188-199`, `265-334`, `431-500`, `527-545`,
plus the `--draft` / `--priv` custom properties. Removing it makes the one file a
new maintainer can actually read. Keep only what the 22 pages use
(`site-header.no-featured-image`, `hero`, `breadcrumbs`, `page-content`, `section`,
`item-list`, `site-footer`, tables, code, blockquote).

**F-2 · Low · Leftover WordPress cruft in the font stacks.**
`style.css:17-18` — `"NonBreakingSpaceOverride"` is the first family in both
`--fh` and `--fb`. It's a WordPress-specific trick with no purpose here; it just
forces one failed font lookup. Remove it.

**F-3 · Low · Stale provenance comments.** `style.css:1-4` still describes the
site as "Twenty Nineteen-faithful theme for Programming Humanity" with tokens
"measured from programminghumanity.wordpress.com." Harmless, but misleading to a
new reader. Rewrite the header comment for this site.

**F-4 · Low · Only two breakpoints, content pinned left on wide screens.**
`--col-left: calc(8.33vw + 28px)` with a 640px measure means very wide viewports
show a narrow column hugging the left with a large empty right margin. This may be
the intended "Twenty Nineteen" look; flag it as a deliberate design decision to
confirm, not necessarily a bug.

**F-5 · Low · No print stylesheet.** A syllabus / policies / schedule page is a
prime candidate for printing or "Save as PDF" (students, accommodations offices,
advisors). Add an `@media print` block: hide the nav, un-pin the left column, use
black text, show link URLs after link text.

### G. Security

**G-1 · Low · Minimal security headers.** `netlify.toml:4-8` sets `X-Frame-Options: DENY`
and `X-Content-Type-Options: nosniff` — good. Missing, and all cheap for a static
site with no inline JS:
- `Content-Security-Policy: default-src 'self'; style-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'` (tighten to taste)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (Netlify can also be told to force HTTPS)
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

**G-2 · Low · The redirect rule is redundant.** `netlify.toml:10-13` maps
`/*` → `/404.html` with `status = 404`. Netlify already serves `/404.html` with a
404 for unmatched paths. Since `force` defaults to `false`, real files still win,
so this isn't harmful — just delete it or keep it as an explicit statement of
intent.

**G-3 · Low · Deploy publishes non-site files.** `netlify.toml:2` `publish = "."`
uploads `tests/*.py`, `tests/requirements.txt`, `conftest.py`, `.github/`,
`netlify.toml`, `README.md`, and `LICENSE` to the public CDN. Not a vulnerability
(nothing secret is there), but `/tests/conftest.py` being fetchable is untidy.
Fix by moving the site into `public/` (or `src/` → build → `dist/`) and pointing
`publish` at that, or add a `.netlifyignore` / `build.ignore`.

### H. CI/CD and Deployment

**H-1 · Medium · Third-party action pinned to a mutable tag.**
`.github/workflows/deploy-netlify.yml:48` — `nwtgck/actions-netlify@v3`. A
compromised or force-pushed `v3` tag would run with your `NETLIFY_AUTH_TOKEN`.
Pin to a full commit SHA (`nwtgck/actions-netlify@<sha>  # v3.x.y`) and let
Dependabot bump it. This is exactly the supply-chain hygiene the course teaches
in Week 8 / Week 12.

**H-2 · Medium · Test dependencies are unpinned.** `tests/requirements.txt` —
`pytest>=7`, `beautifulsoup4>=4`, `lxml>=4`. A future `lxml` or `bs4` release can
change parsing behavior and break CI (or, worse, change results silently). Pin
exact versions (`pytest==8.3.3`), ideally with hashes (`pip-compile` →
`requirements.txt` with `--generate-hashes`), and add a `constraints` file or use
`uv`/`pip-tools`.

**H-3 · Low · No dependency caching in CI.** `actions/setup-python@v5` supports
`cache: pip`; add it plus `cache-dependency-path: tests/requirements.txt` to
speed runs.

**H-4 · Low · `pip` not upgraded before install.** Add
`python -m pip install --upgrade pip` or use `uv pip` for reproducibility and
speed.

**H-5 · Low · No PR / preview builds.** The workflow only runs on `push` to
`main` and `workflow_dispatch`. Running the test job on `pull_request` (and a
Netlify deploy-preview) would catch breakage before it hits `main`. Right now the
first signal that a change broke the site is a failed production deploy.

**H-6 · Low · No CodeQL / actions-hardening / `permissions` on the job level.**
Workflow-level `permissions: contents: read` is good; consider also
`persist-credentials: false` on checkout for the deploy job.

**H-7 · Low · README deployment note vs. reality.** `README.md:92-95` says "Until
those secrets are configured, the workflow run will fail at the deploy step."
True, but the `test` job also runs on every push and will pass — worth stating
that tests still gate `main` even before Netlify is wired up (it does say checkout
succeeds; just be explicit that the test job is meaningful on its own).

### I. Testing Gaps

The suite is good. What it does **not** check:

**I-1 · Medium · HTML validity.** `lxml`/BeautifulSoup parse leniently, so
malformed markup (unclosed tags, invalid nesting, duplicate `id`s) passes. Add
`html5validator` (wraps the Nu validator) or `vnu` in CI against the built site.

**I-2 · Medium · Schedule link text vs. week-page title.** The existing
`test_schedule_links_to_all_15_weeks` only checks that hrefs exist. Add a test:
for each week, the `schedule.html` link text == that page's `<title>` prefix ==
its hero `<h1>` == its breadcrumb `<span>`. (Would have caught D-1 / A-2.)

**I-3 · Medium · Accessibility.** No axe/pa11y. See B.

**I-4 · Low · External link liveness.** Once A-1 is fixed, a *scheduled* (weekly)
workflow running `lychee` or `linkchecker` against external URLs will catch link
rot over the semester without failing normal CI.

**I-5 · Low · Duplicated-content drift.** If D-1 duplication is kept rather than
removed, add a test that the duplicated blocks are byte-identical between their
two locations, so they can't silently diverge.

**I-6 · Low · Brittle hard-coded inventory.** `EXPECTED_TOTAL_PAGES = 22`
(`test_e2e_site.py:8`) and `EXPECTED_WEEK_FILES = {week-01..15}` mean any
intentional new page is a test failure first. That's a defensible design choice
for a fixed-shape site — just be aware it's a "change detector," not only a
correctness check. Consider deriving the count from the directory structure and
asserting the *shape* (index + 404 + 5 core + N weeks) instead of a magic number.

**I-7 · Low · `parsed_pages` fixture parses with `lxml`** but conftest never
asserts the parser is installed with a helpful message; a missing `lxml` gives a
cryptic `bs4` error. Minor DX.

### J. Repository Hygiene and Docs

**J-1 · Low · README placeholder shipped.** `README.md:13` — "Live site: _add
Netlify URL here once deployed_". Fill it in or remove the line.

**J-2 · Low · `.gitignore` is the full GitHub Python template (~220 lines) for a
site with three `.py` files.** Not harmful, but it's noise, and it's missing the
things this repo will actually generate: `.DS_Store`, editor dirs (`.vscode/`,
`.idea/` are commented out), `dist/` or `_site/` if a build is added, `.netlify/`,
`node_modules/` (if an SSG is adopted). Trim it to what's relevant.

**J-3 · Low · No `CHANGELOG.md` / `CONTRIBUTING.md`.** For a site that will be
edited weekly by (possibly) more than one person, a one-paragraph CONTRIBUTING
("edit `pages/`, run `pytest`, push to a branch, open a PR") and a changelog would
help. Low priority for a solo maintainer.

**J-4 · Low · `docs/` did not exist before this report.** Created it here. If
`docs/` is going to hold internal reports, add it to `.netlifyignore` (see G-3)
so review docs aren't published with the site.

---

## 4. Prioritized Remediation Checklist

### Do first (before students rely on the site)
1. **A-1 / F-2 (High):** Add real `<a>` links + `mailto:` for every external reference (GitHub repo, Moodle, `digital.kenyon.edu`, SASS, poster template, tool docs).
2. **D-1 (High):** De-duplicate content — one authoritative location for the Course Description, the assignments table, and the secrets policy; replace copies with a summary + link.
3. **A-2 / D-2 (Medium):** Reconcile Week 10/13/15 titles across `schedule.html` + `<title>` + `<h1>` + breadcrumb; audit all dates against the Kenyon 2026–27 calendar.
4. **J-1 (Low, trivial):** Put the real production URL in `README.md`.

### Do this month
5. **E-1 (High):** Introduce a minimal build step (partials + a `schedule.yml`); run the test suite against the built output. Removes E-2, most of D-1/D-2, A-3.
6. **C-1..C-4 (Medium):** Add per-page `<meta name="description">`, a favicon, `<link rel="canonical">`, Open Graph tags, `robots.txt`, `sitemap.xml`.
7. **F-1 (Medium):** Delete the dead CSS (~55% of `style.css`); clean the font stacks (F-2) and header comment (F-3).
8. **B-1..B-4 (Medium):** Skip link, `aria-current="page"`, table `<caption>` + `scope`, `nav` / breadcrumb labels.
9. **H-1 / H-2 (Medium):** Pin `nwtgck/actions-netlify` to a SHA; pin test deps (ideally hashed). Add Dependabot.
10. **I-1 / I-2 / I-3 (Medium):** Add HTML validation, a title-consistency test, and pa11y/axe to CI.

### Cleanup / polish
11. **G-1 / G-3 (Low):** Add CSP + `Referrer-Policy` + HSTS + `Permissions-Policy`; move the site into `public/`/`dist/` so `tests/` and `.github/` aren't published.
12. **G-2 (Low):** Delete the redundant `/* → /404.html` redirect.
13. **H-3..H-6 (Low):** pip cache, pip upgrade, run tests on `pull_request`, Netlify deploy previews, `persist-credentials: false`.
14. **F-5 (Low):** Add an `@media print` stylesheet.
15. **B-5 / B-6 (Low):** Darken `--text-lt`; add an explicit `:focus-visible` style.
16. **J-2 / J-3 / J-4 (Low):** Trim `.gitignore`; add `CONTRIBUTING.md`; `.netlifyignore` the `docs/` dir; add a `CLAUDE.md` (E-3).

---

## 5. Appendix — Verification Performed

- Read all 22 HTML pages (spot-read weeks 1, 5, 8, 10, 13, 15 in full; verified skeleton on the rest).
- Read `css/style.css`, `netlify.toml`, `.github/workflows/deploy-netlify.yml`, `README.md`, `LICENSE`, `.gitignore`, and all four test files + `conftest.py`.
- Ran the test suite: **25 passed in 0.46s** (`pytest tests/ -q`).
- `grep` verification:
  - external links: none present (`href="http…"` → 0 matches; only 2 bare URLs, both in `<code>`).
  - dead CSS: 16 class names from `style.css` confirmed absent from every HTML file.
  - schedule vs. week-page titles: mismatches confirmed for weeks 10, 13, 15.
  - `<meta name="description">`: 0 of 22 pages.
- Contrast ratios computed for `--text-lt` (#767676 ≈ 4.5:1 on white) and `--accent` (#0073aa ≈ 5:1 on white).

---

_Report generated with [Claude Code](https://claude.com/claude-code)._
