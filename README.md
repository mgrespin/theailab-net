# IPHS 400: Frontiers in AI

**Kenyon College — Integrated Program for Humane Studies (IPHS) — Fall 2026**

Course website for IPHS 400, a hands-on study of AI software engineering (AI-SWE):
configuring, extending, and orchestrating AI coding agents through a professional
software development lifecycle. This repository contains the site's source and
its test suite; course submissions, quizzes, and grades are handled separately
on Moodle.

- **Instructor:** Jon Chun
- **Schedule:** Tu/Th, 2:40–4:00 PM · Timberlake #5 (Evans Conference Room)

This is a self-contained static site: it runs from a local web server with no
build step, no deploy pipeline, and no external hosting configuration.

## Repository Structure

```
.
├── index.html              # Home page
├── 404.html                 # Not-found page
├── core/                    # Syllabus, schedule, assignments, policies, about
│   ├── syllabus.html
│   ├── schedule.html
│   ├── assignments.html
│   ├── policies.html
│   └── about.html
├── weeks/                   # One page per week, week-01.html … week-15.html
├── css/
│   └── style.css            # Single shared stylesheet, no build step
└── tests/                   # pytest suite validating the site
    ├── conftest.py
    ├── test_unit_html_structure.py
    ├── test_integration_links.py
    ├── test_e2e_site.py
    └── requirements.txt
```

The site is static HTML/CSS with no build step or JS framework. Every page
shares one stylesheet and a common header/nav/hero/footer skeleton.

## Local Development

Serve the site locally with Python's built-in HTTP server:

```bash
python3 -m http.server 8080
# then open http://localhost:8080/
```

No install step is required to view the site — only the test suite has
dependencies.

## Running the Tests

The test suite (pytest + BeautifulSoup/lxml) validates structural and content
integrity of every page:

- `test_unit_html_structure.py` — every page has a DOCTYPE, title, stylesheet
  link, header, footer, and hero `<h1>`; no leftover template branding; no
  placeholder or stub content
- `test_integration_links.py` — every internal link resolves; navigation is
  identical across all pages; the schedule links to all 15 week pages
- `test_e2e_site.py` — required files/directories exist; exact page count;
  every page is reachable from `index.html` (no orphaned pages)

```bash
uv venv --python=3.12          # or: python3 -m venv .venv
source .venv/bin/activate
uv pip install -r tests/requirements.txt   # or: pip install -r tests/requirements.txt
pytest tests/ -v
```

Re-run `source .venv/bin/activate` in each new terminal session before running
the tests.

Run a single test file or test:

```bash
pytest tests/test_unit_html_structure.py -v
pytest tests/test_integration_links.py::TestNavConsistency::test_nav_links_resolve -v
```

## Deployment

None. This is a standalone static site with no deploy pipeline — serve it
locally with the command in [Local Development](#local-development). To host it
elsewhere, any static file host will serve the repository root as-is.

## Content Source and Provenance

All course content (syllabus text, schedule, assignments, policies) is
sourced from the official Fall 2026 syllabus. The page layout, navigation
pattern, and stylesheet are adapted from a prior Kenyon course site (a
"Twenty Nineteen"-style layout used across Jon Chun's Kenyon course sites)
for visual consistency; no course content from that site is reused here.

The site is also reachable at **theailab.net**.

## Mini-Project 1 — Revision Notes

*Submitted by [your name], IPHS 400, Fall 2026.*

### Generative AI Use Statement

I used **Claude Code (Sonnet 5, thinking effort medium)** for this project.
The agent did the critique, wrote the tech-spec, made every code and content
edit, wrote the tests, and drafted the supporting docs. I directed the work
and made the judgment calls described below. No other AI tools were used.
Artifacts of the AI work: `docs/report_web-revision_v1_20260901.md` (critique),
`docs/tech-spec_website-revision_v1_20260903.md` (plan), `CHANGELOG.md`
(result), and the per-task commit history on the `web-revision-v1` branch.

### Decisions I made

*(Reword this section in your own words — this is what I'll be asked to
explain.)*

- **Reused the in-class critique** (`report_web-revision_v1_20260901.md`)
  instead of regenerating it, then stripped the Netlify/CI config first so the
  tech-spec wouldn't carry findings about a deploy pipeline we'd removed.
- **Reviewed and approved the tech-spec** before implementation, including its
  five judgment calls: leaving a build step / templating system out of scope
  (it contradicts the site's no-build-step design), assuming `theailab.net` as
  the canonical URL, the direction of each de-duplication, using the longer
  week-title wording, and not rewriting any policy text.
- **Weights table:** chose to group it into *Ongoing / Mini-Projects / Final
  Project* rather than force one strict date-ordered list, because the two
  assignment tracks run in parallel (the Final Project proposal is genuinely
  due before Mini-Project 4).
- **"What is Mini-Project 1?"** The assignment email calls this exercise
  Mini-Project 1, but the site says Mini-Project 1 is Development Environment
  Configuration. I left the site as-is and logged the contradiction in
  `docs/open-questions-for-instructor_20260903.md` rather than rewrite the
  assignment based on one ambiguous sentence.
- **Home page:** added an Office Hours row to the Course Details table (value
  taken from the syllabus); did **not** add an email row because no instructor
  address is published anywhere on the site and I wasn't going to invent one.
- **Reviewed the rendered site** page by page in Chrome before finalizing, then
  merged to `main` and pushed to my fork.

### What changed

See `CHANGELOG.md`. Test suite went from 25 to 51 checks; run `pytest tests/`.

## License

See [LICENSE](LICENSE).
