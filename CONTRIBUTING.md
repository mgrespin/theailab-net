# Contributing

This is a static site: flat HTML + one stylesheet (`css/style.css`), served by
a local web server. **No build step, no JavaScript, no external runtime
dependencies.** Keep it that way.

## Editing

- Page content lives in `index.html`, `404.html`, `core/*.html`, and
  `weeks/*.html`.
- The shared skeleton (`<head>` metadata, header, nav, footer) is copied into
  every page. If you change it in one place, change it in all of them — the
  test suite enforces an identical nav across pages.
- Each week's title must be **identical** in four places: the `core/schedule.html`
  link text, the page `<title>`, the hero `<h1>`, and the breadcrumb.
- Add a `<meta name="description">` (50–160 chars) and the canonical / Open
  Graph tags for any new page. The canonical origin is `https://theailab.net`.
- Don't reintroduce content that already lives on another page — link to the
  canonical copy instead (see the Syllabus / Assignments / Policies split).

## Testing

```bash
uv venv --python=3.12
source .venv/bin/activate
uv pip install -r tests/requirements.txt
pytest tests/ -v
```

Run the tests before opening a PR. Every change should keep the suite green;
new behavior should come with a new or extended test.

## Serving locally

```bash
python3 -m http.server 8080
# http://localhost:8080/
```

View pages through the server, not by opening the file directly (relative and
root-absolute asset paths depend on it).
