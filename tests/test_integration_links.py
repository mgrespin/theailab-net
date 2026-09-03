"""Integration tests: internal links resolve, nav is consistent, schedule links all weeks."""
import pytest
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import unquote

SITE_ROOT = Path(__file__).parent.parent

EXPECTED_NAV_LABELS = {"Home", "Syllabus", "Schedule", "Assignments", "Policies", "About"}


def _rel(path):
    return str(path.relative_to(SITE_ROOT))


def _resolve_href(href, page_path):
    """Resolve a relative href to an absolute Path, or None for external/anchor/mailto links."""
    if not href or href.startswith(("http://", "https://", "mailto:", "#", "javascript:")):
        return None
    href = href.split("#")[0]
    if not href:
        return None
    href = unquote(href)
    return (page_path.parent / href).resolve()


def _collect_broken_links(page_path, soup, selector="a"):
    broken = []
    for tag in soup.select(selector):
        href = tag.get("href", "")
        target = _resolve_href(href, page_path)
        if target is not None and not target.exists():
            broken.append(href)
    return broken


class TestAllInternalLinks:
    def test_all_internal_links_resolve(self, site_root, parsed_pages):
        """Every internal <a href> across all pages must resolve to an existing file."""
        broken = []
        for path, _, soup in parsed_pages:
            for bad in _collect_broken_links(path, soup):
                broken.append(f"{_rel(path)} -> {bad}")
        assert not broken, f"{len(broken)} broken internal links. First 15: {broken[:15]}"


class TestNavConsistency:
    def test_all_nav_pages_have_identical_nav_labels(self, site_root, nav_pages):
        """Every page (except 404.html) must have the exact same set of nav link labels."""
        failures = []
        for f in nav_pages:
            soup = BeautifulSoup(f.read_text(encoding="utf-8"), "lxml")
            nav = soup.select_one("nav.main-nav")
            if not nav:
                failures.append(f"{_rel(f)}: missing nav.main-nav")
                continue
            labels = {a.get_text(strip=True) for a in nav.find_all("a")}
            if labels != EXPECTED_NAV_LABELS:
                failures.append(f"{_rel(f)}: {sorted(labels)}")
        assert not failures, f"Pages with inconsistent nav labels: {failures[:15]}"

    def test_nav_links_resolve(self, site_root, nav_pages):
        """Nav links on every non-404 page must resolve to existing files."""
        broken = []
        for f in nav_pages:
            soup = BeautifulSoup(f.read_text(encoding="utf-8"), "lxml")
            nav = soup.select_one("nav.main-nav")
            if not nav:
                continue
            for link in _collect_broken_links(f, nav, "a"):
                broken.append(f"{_rel(f)} -> {link}")
        assert not broken, f"Broken nav links: {broken[:15]}"


class TestExternalLinks:
    """External resources named in the copy must be real <a> links (T-01)."""

    # (page relative to core/, resource substring, expected href)
    EXPECTED = [
        ("syllabus.html", "github.com/jon-chun/theailab-net", "https://github.com/jon-chun/theailab-net"),
        ("syllabus.html", "Moodle", "https://moodle.kenyon.edu"),
        ("syllabus.html", "digital.kenyon.edu/dh", "https://digital.kenyon.edu/dh"),
        ("syllabus.html", "OpenRouter", "https://openrouter.ai"),
        ("syllabus.html", "Anthropic", "https://www.anthropic.com"),
        ("about.html", "github.com/jon-chun/theailab-net", "https://github.com/jon-chun/theailab-net"),
        ("about.html", "Moodle", "https://moodle.kenyon.edu"),
        ("policies.html", "digital.kenyon.edu/dh", "https://digital.kenyon.edu/dh"),
        ("policies.html", "sass@kenyon.edu", "mailto:sass@kenyon.edu"),
        ("assignments.html", "Moodle", "https://moodle.kenyon.edu"),
        ("assignments.html", "digital.kenyon.edu/dh", "https://digital.kenyon.edu/dh"),
        ("assignments.html", "course repository", "https://github.com/jon-chun/theailab-net"),
    ]

    def test_known_external_resources_are_linked(self, site_root):
        missing = []
        for page, _substr, href in self.EXPECTED:
            html = (site_root / "core" / page).read_text(encoding="utf-8")
            soup = BeautifulSoup(html, "lxml")
            if not soup.find("a", href=href):
                missing.append(f"{page}: no <a href='{href}'>")
        assert not missing, f"Unlinked external resources: {missing}"

    def test_external_links_with_blank_target_have_noopener(self, parsed_pages):
        bad = []
        for path, _, soup in parsed_pages:
            for a in soup.find_all("a", target="_blank"):
                rel = " ".join(a.get("rel", []))
                if "noopener" not in rel:
                    bad.append(f"{_rel(path)}: {a.get('href')}")
        assert not bad, f"target=_blank links missing rel=noopener: {bad}"


class TestWeekTitleConsistency:
    """Each week's title must be identical in schedule link, <title>, <h1>, breadcrumb (T-03)."""

    def test_week_titles_agree_everywhere(self, site_root):
        schedule = site_root / "core" / "schedule.html"
        s_soup = BeautifulSoup(schedule.read_text(encoding="utf-8"), "lxml")
        link_text = {}
        for a in s_soup.find_all("a", href=True):
            if "week-" in a["href"]:
                n = int(a["href"].split("week-")[1].split(".")[0])
                link_text[n] = a.get_text(strip=True)

        mismatches = []
        for n in range(1, 16):
            page = site_root / "weeks" / f"week-{n:02d}.html"
            soup = BeautifulSoup(page.read_text(encoding="utf-8"), "lxml")
            title = soup.title.string.split("–")[0].strip()
            h1 = soup.select_one(".hero h1").get_text(strip=True)
            crumb = soup.select_one(".breadcrumbs").find_all("span")[-1].get_text(strip=True)
            want = link_text.get(n)
            for label, got in (("<title>", title), ("<h1>", h1), ("breadcrumb", crumb)):
                if got != want:
                    mismatches.append(f"week-{n:02d} {label}: {got!r} != schedule {want!r}")
        assert not mismatches, "Week title mismatches:\n" + "\n".join(mismatches)


class TestNoDuplicateBlocks:
    """Large content blocks must not be copied verbatim across pages (T-02)."""

    def test_no_identical_large_blocks_across_pages(self, parsed_pages):
        import re

        seen = {}  # normalized text -> page
        collisions = []
        for path, _, soup in parsed_pages:
            content = soup.select_one(".page-content")
            if not content:
                continue
            for el in content.find_all(["ul", "ol", "table"]):
                text = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
                if len(text) < 200:
                    continue
                if text in seen and seen[text] != path.name:
                    collisions.append(f"{seen[text]} <-> {path.name}: {text[:70]}...")
                else:
                    seen.setdefault(text, path.name)
        assert not collisions, f"Verbatim duplicated blocks: {collisions}"


class TestScheduleLinksAllWeeks:
    def test_schedule_links_to_all_15_weeks(self, site_root):
        """core/schedule.html must link to weeks/week-01.html through weeks/week-15.html."""
        schedule = site_root / "core" / "schedule.html"
        soup = BeautifulSoup(schedule.read_text(encoding="utf-8"), "lxml")
        hrefs = {a.get("href", "") for a in soup.find_all("a")}
        missing = []
        for n in range(1, 16):
            expected = f"../weeks/week-{n:02d}.html"
            alt = f"weeks/week-{n:02d}.html"
            if expected not in hrefs and alt not in hrefs and not any(
                h.endswith(f"week-{n:02d}.html") for h in hrefs
            ):
                missing.append(f"week-{n:02d}.html")
        assert not missing, f"core/schedule.html missing links to: {missing}"
