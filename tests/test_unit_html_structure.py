"""Unit tests: every HTML page has valid structure and required elements."""
from pathlib import Path

from bs4 import BeautifulSoup

SITE_ROOT = Path(__file__).parent.parent

TITLE_SUFFIX = "– IPHS 400: Frontiers in AI"  # en dash
FOOTER_TEXT = "IPHS 400: Frontiers in AI · Kenyon College"
ORIGIN = "https://theailab.net"


def _rel(path):
    return str(path.relative_to(SITE_ROOT))


class TestDoctype:
    def test_all_pages_have_doctype(self, parsed_pages):
        """Every HTML page must begin with <!DOCTYPE html>."""
        failures = []
        for path, text, _ in parsed_pages:
            if not text.strip().lower().startswith("<!doctype html"):
                failures.append(_rel(path))
        assert not failures, f"Pages missing <!DOCTYPE html>: {failures[:15]}"


class TestTitle:
    def test_all_titles_end_with_course_suffix(self, parsed_pages):
        """Every <title> must end with '{TITLE_SUFFIX}'."""
        failures = []
        for path, _, soup in parsed_pages:
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            if not title.endswith(TITLE_SUFFIX):
                failures.append(f"{_rel(path)}: '{title}'")
        assert not failures, f"Titles not ending with course suffix: {failures[:15]}"


class TestCSSLink:
    def test_all_pages_link_to_resolvable_style_css(self, parsed_pages):
        """Every page must have a <link rel='stylesheet'> to a resolvable css/style.css."""
        failures = []
        for path, _, soup in parsed_pages:
            links = [
                tag for tag in soup.find_all("link", rel="stylesheet")
                if "style.css" in tag.get("href", "")
            ]
            if not links:
                failures.append(f"{_rel(path)}: no stylesheet link")
                continue
            href = links[0]["href"]
            target = (path.parent / href).resolve()
            if not target.exists():
                failures.append(f"{_rel(path)}: href '{href}' does not resolve")
        assert not failures, f"CSS link issues: {failures[:15]}"


class TestHeaderFooterHero:
    def test_all_pages_have_site_header(self, parsed_pages):
        """Every page must contain a <header class="site-header">."""
        failures = [_rel(p) for p, _, s in parsed_pages if not s.select_one("header.site-header")]
        assert not failures, f"Pages missing header.site-header: {failures[:15]}"

    def test_all_pages_have_site_footer_with_text(self, parsed_pages):
        """Every page must contain a <footer class="site-footer"> with the course footer text."""
        failures = []
        for path, _, soup in parsed_pages:
            footer = soup.select_one("footer.site-footer")
            if not footer:
                failures.append(f"{_rel(path)}: missing footer.site-footer")
                continue
            if FOOTER_TEXT not in footer.get_text():
                failures.append(f"{_rel(path)}: footer text mismatch")
        assert not failures, f"Footer issues: {failures[:15]}"

    def test_all_pages_have_hero_with_h1(self, parsed_pages):
        """Every page must have a .hero container with an <h1>."""
        failures = []
        for path, _, soup in parsed_pages:
            hero = soup.select_one(".hero")
            if not hero:
                failures.append(f"{_rel(path)}: missing .hero")
                continue
            if not hero.find("h1"):
                failures.append(f"{_rel(path)}: hero has no h1")
        assert not failures, f"Hero issues: {failures[:15]}"


class TestNoLeftoverBranding:
    def test_no_programming_humanity_text(self, parsed_pages):
        """No page should contain leftover 'Programming Humanity' template branding."""
        failures = [
            _rel(path) for path, text, _ in parsed_pages
            if "Programming Humanity" in text
        ]
        assert not failures, f"Pages with leftover 'Programming Humanity' text: {failures[:15]}"

    def test_no_placeholder_notice(self, parsed_pages):
        """No page should contain a .placeholder-notice element."""
        failures = [
            _rel(path) for path, _, soup in parsed_pages
            if soup.select_one(".placeholder-notice")
        ]
        assert not failures, f"Pages with .placeholder-notice: {failures[:15]}"

    def test_no_stub_or_placeholder_strings(self, parsed_pages):
        """No page should contain literal 'Lorem ipsum', 'TBD', or 'TODO' text."""
        failures = []
        for path, text, _ in parsed_pages:
            hits = [s for s in ("Lorem ipsum", "TBD", "TODO") if s in text]
            if hits:
                failures.append(f"{_rel(path)}: {hits}")
        assert not failures, f"Pages with stub/placeholder strings: {failures[:15]}"


class TestMetaDescription:
    def test_every_page_has_one_meta_description(self, parsed_pages):
        """Every page has exactly one <meta name="description"> of 50-160 chars (T-04)."""
        failures = []
        for path, _, soup in parsed_pages:
            tags = soup.find_all("meta", attrs={"name": "description"})
            if len(tags) != 1:
                failures.append(f"{_rel(path)}: {len(tags)} description tags")
                continue
            content = (tags[0].get("content") or "").strip()
            if not (50 <= len(content) <= 160):
                failures.append(f"{_rel(path)}: description is {len(content)} chars")
        assert not failures, f"meta description issues: {failures}"


class TestFavicon:
    def test_every_page_links_favicon(self, parsed_pages):
        failures = [
            _rel(p) for p, _, s in parsed_pages
            if not s.find("link", rel="icon", href="/favicon.svg")
        ]
        assert not failures, f"Pages not linking /favicon.svg: {failures}"


class TestSocialMeta:
    """Canonical + Open Graph/Twitter tags on every indexable page (T-06)."""

    def test_canonical_and_og_tags(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            rel = _rel(path)
            is_404 = path.name == "404.html"
            desc_tag = soup.find("meta", attrs={"name": "description"})
            desc = desc_tag.get("content") if desc_tag else None
            og_desc = soup.find("meta", property="og:description")
            if not og_desc or og_desc.get("content") != desc:
                failures.append(f"{rel}: og:description missing or != meta description")
            for prop in ("og:title", "og:type"):
                if not soup.find("meta", property=prop):
                    failures.append(f"{rel}: missing {prop}")
            if not soup.find("meta", attrs={"name": "twitter:card"}):
                failures.append(f"{rel}: missing twitter:card")
            canon = soup.find("link", rel="canonical")
            if is_404:
                if canon:
                    failures.append(f"{rel}: 404 should not be canonical")
                if not soup.find("meta", attrs={"name": "robots", "content": "noindex"}):
                    failures.append(f"{rel}: 404 missing noindex")
            else:
                if not canon or not canon.get("href", "").startswith(ORIGIN):
                    failures.append(f"{rel}: canonical missing/!=origin")
                og_url = soup.find("meta", property="og:url")
                if not og_url or og_url.get("content") != canon.get("href"):
                    failures.append(f"{rel}: og:url != canonical")
        assert not failures, "Social meta issues:\n" + "\n".join(failures)


class TestAccessibility:
    """Structural WCAG 2.1 AA gaps from report section B (T-08)."""

    def test_skip_link_first_and_target_exists(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            body = soup.body
            first = body.find(True) if body else None
            if not first or first.name != "a" or "skip-link" not in first.get("class", []):
                failures.append(f"{_rel(path)}: first body child is not .skip-link")
            elif first.get("href") != "#main" or not soup.find(id="main"):
                failures.append(f"{_rel(path)}: skip-link target #main missing")
        assert not failures, f"skip link: {failures}"

    def test_active_nav_has_aria_current(self, nav_pages):
        failures = []
        for f in nav_pages:
            soup = BeautifulSoup(f.read_text(encoding="utf-8"), "lxml")
            active = soup.select_one("nav.main-nav a.active")
            if not active or active.get("aria-current") != "page":
                failures.append(_rel(f))
        assert not failures, f"active nav link missing aria-current=page: {failures}"

    def test_landmarks_are_named(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            nav = soup.select_one("nav.main-nav")
            if not nav or not nav.get("aria-label"):
                failures.append(f"{_rel(path)}: main-nav unnamed")
            crumb = soup.select_one(".breadcrumbs")
            if crumb:
                if crumb.name != "nav" or not crumb.get("aria-label"):
                    failures.append(f"{_rel(path)}: breadcrumbs not a named nav")
                elif not crumb.find("ol"):
                    failures.append(f"{_rel(path)}: breadcrumbs has no <ol>")
        assert not failures, f"landmark naming: {failures}"

    def test_tables_have_caption_and_scoped_headers(self, parsed_pages):
        failures = []
        for path, _, soup in parsed_pages:
            for i, table in enumerate(soup.find_all("table")):
                if not table.find("caption"):
                    failures.append(f"{_rel(path)} table#{i}: no <caption>")
                for th in table.find_all("th"):
                    if not th.get("scope"):
                        failures.append(f"{_rel(path)} table#{i}: <th> without scope")
                        break
        assert not failures, f"table a11y: {failures}"

    def test_hero_is_not_a_section(self, parsed_pages):
        failures = [_rel(p) for p, _, s in parsed_pages if s.find("section", class_="hero")]
        assert not failures, f"pages still using <section class=hero>: {failures}"


class TestContentNotEmpty:
    def test_page_content_has_minimum_text(self, parsed_pages):
        """Every page's .page-content div must have at least 20 characters of stripped text."""
        failures = []
        for path, _, soup in parsed_pages:
            content_div = soup.select_one(".page-content")
            if not content_div:
                failures.append(f"{_rel(path)}: missing .page-content")
                continue
            text = content_div.get_text(strip=True)
            if len(text) < 20:
                failures.append(f"{_rel(path)}: only {len(text)} chars")
        assert not failures, f"Pages with near-empty .page-content: {failures[:15]}"
