"""generate_doksam.py 의 클래스 계약 검증기 단위 테스트 (stdlib only)."""
import re
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


class TestBuiltExample(unittest.TestCase):
    """생성 결과가 계약과 번호 체계를 지키는지 확인한다."""

    def setUp(self):
        template = gd.TEMPLATE_PATH.read_text(encoding="utf-8")
        self.css = gd.extract_style(template)
        self.html = gd.build_html(self.css)

    def test_has_seven_slides(self):
        self.assertEqual(self.html.count('class="ppt-slide"'), 7)

    def test_slide_numbers_follow_scheme(self):
        numbers = re.findall(r'class="ppt-top-no">NO\. ([\d.]+)<', self.html)
        self.assertEqual(numbers, ["01", "02", "03", "04", "05", "06.1", "06.2"])

    def test_no_undefined_classes(self):
        self.assertEqual(gd.undefined_classes(self.html, self.css), [])

    def test_no_stale_branding(self):
        # 외부 블로그 브랜딩(레포와 무관한 인물명 + "'s blog 기획이야기 |
        # Ver.1.0.0" 형태의 푸터 문구)의 인물명 자체는 목록에서 뺐다.
        # "기획이야기" 가 그 문구의 부분 문자열이라 재발 시 이 테스트가
        # 여전히 잡는다. 그 인물명을 다시 넣지 말 것.
        for banned in ("기획이야기", "덕삼이"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, self.html)

    def test_project_name_is_present(self):
        self.assertIn(gd.PROJECT_NAME, self.html)

    def test_no_emoji(self):
        found = re.findall(
            r"[\U0001F300-\U0001FAFF☀-➿⬀-⯿]", self.html
        )
        self.assertEqual(found, [])

    def test_styles_are_inlined(self):
        self.assertIn(".ppt-slide", self.html)

    def test_committed_example_matches_generated_output(self):
        """예시는 생성 산출물이다 — 손으로 편집하면 이 테스트가 잡는다."""
        self.assertEqual(
            gd.OUTPUT_PATH.read_text(encoding="utf-8"),
            self.html,
            "examples/ 의 커밋된 내용이 generate_doksam.py 출력과 다르다. "
            "python3 generate_doksam.py 로 재생성할 것.",
        )


class TestSkillClassQuickReference(unittest.TestCase):
    """SKILL.md 의 Class Quick Reference 표가 template.html 의 CSS 계약과
    맞는지 확인한다. 표는 에이전트가 template.html 을 열지 않고도 사용
    가능한 클래스를 알 수 있게 하는 권위이므로, 표가 template.html 과
    어긋나면 이 테스트가 잡아야 한다.
    """

    #: CSS 클래스가 아니라 엘리먼트 셀렉터로 정의된 항목. 표에는 등재되어
    #: 있으나 defined_classes() 에는 나오지 않는 게 정상이다.
    NOT_A_CLASS = frozenset({"code"})

    @classmethod
    def setUpClass(cls):
        skill_path = (
            REPO_ROOT / "skills" / "mobile-web-planner" / "SKILL.md"
        )
        cls.skill_text = skill_path.read_text(encoding="utf-8")
        template = gd.TEMPLATE_PATH.read_text(encoding="utf-8")
        cls.css = gd.extract_style(template)
        cls.defined = gd.defined_classes(cls.css)

    def _table_class_names(self) -> set[str]:
        """SKILL.md 의 '# Class Quick Reference' 섹션(다음 '#' 헤딩
        전까지)에서 표 행의 첫 번째 셀에 있는 backtick 식별자를 모두
        추출한다. 한 셀에 여러 클래스가 나열된 행(예: ppt-top-bar)도
        지원한다."""
        match = re.search(
            r"# Class Quick Reference\n(.*?)(?=\n# )",
            self.skill_text,
            re.DOTALL,
        )
        self.assertIsNotNone(
            match, "SKILL.md 에 '# Class Quick Reference' 섹션이 없다"
        )
        section = match.group(1)

        names: set[str] = set()
        for line in section.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not cells:
                continue
            first_cell = cells[0]
            # 헤더/구분선 행 스킵 ("클래스" 헤더, "---" 구분선)
            if first_cell in ("클래스", "") or set(first_cell) <= {"-", ":"}:
                continue
            names.update(re.findall(r"`([^`]+)`", first_cell))
        return names

    def test_every_table_class_is_defined_or_allowed(self):
        table_names = self._table_class_names()
        self.assertTrue(table_names, "표에서 클래스명을 하나도 못 찾았다")

        for name in sorted(table_names):
            # code 는 '<code>' 처럼 태그 형태로 적혀 있어 이름 자체가
            # 클래스명이 아니다 — <> 를 벗겨 NOT_A_CLASS 와 비교한다.
            bare_name = name.strip("<>")
            if bare_name in self.NOT_A_CLASS:
                continue
            with self.subTest(name=name):
                self.assertTrue(
                    name in self.defined or name in gd.WHITELIST,
                    f"SKILL.md 표의 '{name}' 이 template.html 의 CSS 에도, "
                    f"gd.WHITELIST 에도 없다. template.html 에 정의를 "
                    "추가하거나, SKILL.md 표에서 항목을 빼거나, "
                    "gd.WHITELIST/NOT_A_CLASS 에 명시적으로 등록할 것.",
                )


if __name__ == "__main__":
    unittest.main()
