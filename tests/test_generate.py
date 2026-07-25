"""generate_doksam.py 의 클래스 계약 검증기 단위 테스트 (stdlib only)."""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import generate_doksam as gd


class TestExtractStyle(unittest.TestCase):
    def test_returns_css_between_style_tags(self):
        html = "<head><style>\n.a { color: red; }\n</style></head>"
        self.assertIn(".a { color: red; }", gd.extract_style(html))

    def test_raises_when_no_style_block(self):
        with self.assertRaises(ValueError):
            gd.extract_style("<head></head>")


class TestDefinedClasses(unittest.TestCase):
    def test_extracts_simple_class_selectors(self):
        css = ".ppt-slide { color: red; }\n.mock-tab { color: blue; }"
        self.assertEqual(gd.defined_classes(css), {"ppt-slide", "mock-tab"})

    def test_extracts_compound_and_descendant_selectors(self):
        css = ".mock-tab.active { color: red; }\n.desc-list li { margin: 0; }"
        self.assertEqual(gd.defined_classes(css), {"mock-tab", "active", "desc-list"})

    def test_ignores_element_and_pseudo_selectors(self):
        css = "body { margin: 0; }\n* { box-sizing: border-box; }\ncode { color: red; }"
        self.assertEqual(gd.defined_classes(css), set())

    def test_ignores_decimal_values_in_declarations(self):
        css = ".a { transform: scale(0.9); box-shadow: 0 2px 4px rgba(0,0,0,0.3); }"
        self.assertEqual(gd.defined_classes(css), {"a"})

    def test_ignores_at_import_url_extension(self):
        css = "@import url('https://cdn.example.com/pretendard.css');\n.a { color: red; }"
        self.assertEqual(gd.defined_classes(css), {"a"})


class TestUsedClasses(unittest.TestCase):
    def test_extracts_single_and_multiple_classes(self):
        html = '<div class="ppt-slide"><span class="mock-tab active"></span></div>'
        self.assertEqual(gd.used_classes(html), {"ppt-slide", "mock-tab", "active"})

    def test_collapses_extra_whitespace(self):
        html = '<div class="  a   b  "></div>'
        self.assertEqual(gd.used_classes(html), {"a", "b"})

    def test_returns_empty_when_no_class_attribute(self):
        self.assertEqual(gd.used_classes("<div></div>"), set())


class TestUndefinedClasses(unittest.TestCase):
    CSS = ".ppt-slide { color: red; }\n.mock-tab { color: blue; }"

    def test_returns_empty_when_all_defined(self):
        html = '<div class="ppt-slide"><span class="mock-tab"></span></div>'
        self.assertEqual(gd.undefined_classes(html, self.CSS), [])

    def test_reports_undefined_sorted(self):
        html = '<div class="storyboard"><span class="dochead"></span></div>'
        self.assertEqual(gd.undefined_classes(html, self.CSS), ["dochead", "storyboard"])

    def test_mermaid_is_whitelisted(self):
        html = '<div class="mermaid">mindmap</div>'
        self.assertEqual(gd.undefined_classes(html, self.CSS), [])

    def test_whitelist_contains_mermaid(self):
        self.assertIn("mermaid", gd.WHITELIST)


class TestAgainstRealTemplate(unittest.TestCase):
    """실제 template.html 로 계약이 성립하는지 확인한다."""

    def setUp(self):
        path = REPO_ROOT / "skills" / "mobile-web-planner" / "resources" / "template.html"
        self.css = gd.extract_style(path.read_text(encoding="utf-8"))

    def test_core_classes_are_defined(self):
        for name in ("docwrap", "ppt-slide", "ppt-top-no", "ppt-body-full",
                     "ppt-wireframe", "ppt-desc-panel", "desc-num",
                     "pointer-badge", "mock", "mock-tab", "ppt-footer", "icon"):
            with self.subTest(name=name):
                self.assertIn(name, gd.defined_classes(self.css))


if __name__ == "__main__":
    unittest.main()
