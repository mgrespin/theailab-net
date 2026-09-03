"""Unit tests for css/style.css: no dead selectors, no template cruft (T-09)."""
import re
from pathlib import Path

SITE_ROOT = Path(__file__).parent.parent
CSS = (SITE_ROOT / "css" / "style.css").read_text(encoding="utf-8")

# Classes applied by CSS state or reserved, not present as a literal class="" token.
ALLOWLIST = set()


def _class_selectors():
    # strip declaration blocks so we only scan selector text
    selectors = re.sub(r"\{[^}]*\}", "", CSS)
    selectors = re.sub(r"/\*.*?\*/", "", selectors, flags=re.S)
    return set(re.findall(r"\.([A-Za-z_][\w-]*)", selectors))


def test_no_dead_class_selectors():
    html_blob = "\n".join(
        p.read_text(encoding="utf-8")
        for p in SITE_ROOT.rglob("*.html")
        if ".venv" not in p.parts
    )
    used = set(re.findall(r'class="([^"]*)"', html_blob))
    used_classes = {c for group in used for c in group.split()}
    dead = sorted(
        cls for cls in _class_selectors()
        if cls not in used_classes and cls not in ALLOWLIST
    )
    assert not dead, f"CSS class selectors used by no HTML page: {dead}"


def test_no_wordpress_font_override():
    assert "NonBreakingSpaceOverride" not in CSS


def test_header_comment_describes_this_site():
    assert "Programming Humanity" not in CSS
    assert "programminghumanity" not in CSS


def test_has_print_stylesheet():
    assert "@media print" in CSS
