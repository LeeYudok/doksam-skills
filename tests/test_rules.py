"""validate_storyboard.py 의 Business Rules 판정 단위 테스트 (stdlib only)."""
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(
    0, str(REPO_ROOT / "skills" / "mobile-web-planner" / "scripts"))

import validate_storyboard as vs


def section(sid, name="화면", extra_body=""):
    """네 필수 헤딩을 모두 갖춘 유효한 섹션 마크다운을 만든다."""
    return (
        f"## {sid} {name}\n\n"
        "### 입력 검증\n해당 없음 — 조회 전용 화면.\n\n"
        "### 출력 규칙\n| 상태 | 표시 |\n|---|---|\n| 로딩 | 스켈레톤 |\n\n"
        "### 인터랙션\n해당 없음 — 정적 화면.\n\n"
        f"### 엣지케이스\n- 네트워크 오류 시 재시도 배너.\n{extra_body}\n"
    )


class TestRulesPathFor(unittest.TestCase):
    def test_storyboard_suffix_is_swapped(self):
        self.assertEqual(
            vs.rules_path_for("/tmp/petshop_storyboard.html").name,
            "petshop_business-rules.md")

    def test_non_contract_name_uses_stem(self):
        self.assertEqual(
            vs.rules_path_for("/tmp/output.html").name,
            "output_business-rules.md")


class TestRulesSections(unittest.TestCase):
    def test_splits_sections_by_id_heading(self):
        md = section("DTC-MAIN-001") + section("DTC-BOARD-001")
        ids = [sid for sid, _ in vs.rules_sections(md)]
        self.assertEqual(ids, ["DTC-MAIN-001", "DTC-BOARD-001"])

    def test_heading_without_id_is_not_a_section(self):
        md = "## 개요\n내용\n" + section("DTC-MAIN-001")
        ids = [sid for sid, _ in vs.rules_sections(md)]
        self.assertEqual(ids, ["DTC-MAIN-001"])


class TestCheckRules(unittest.TestCase):
    def test_valid_doc_has_no_violations(self):
        md = section("DTC-MAIN-001")
        violations, info = vs.check_rules(md, {"DTC-MAIN-001"})
        self.assertEqual(violations, [])
        self.assertTrue(any("섹션 1개" in line for line in info))

    def test_missing_screen_section_is_a_violation(self):
        md = section("DTC-MAIN-001")
        violations, _ = vs.check_rules(md, {"DTC-MAIN-001", "DTC-BOARD-001"})
        self.assertTrue(any("DTC-BOARD-001" in v and "섹션이 없는" in v
                            for v in violations))

    def test_extra_section_is_a_violation(self):
        md = section("DTC-MAIN-001") + section("DTC-GHOST-999")
        violations, _ = vs.check_rules(md, {"DTC-MAIN-001"})
        self.assertTrue(any("DTC-GHOST-999" in v and "정의되지 않은" in v
                            for v in violations))

    def test_duplicate_section_is_a_violation(self):
        md = section("DTC-MAIN-001") + section("DTC-MAIN-001")
        violations, _ = vs.check_rules(md, {"DTC-MAIN-001"})
        self.assertTrue(any("중복" in v for v in violations))

    def test_missing_required_heading_is_a_violation(self):
        md = ("## DTC-MAIN-001 홈\n\n### 입력 검증\n내용\n\n"
              "### 출력 규칙\n내용\n\n### 인터랙션\n내용\n")
        violations, _ = vs.check_rules(md, {"DTC-MAIN-001"})
        self.assertTrue(any("엣지케이스" in v and "누락" in v
                            for v in violations))

    def test_empty_required_heading_is_a_violation(self):
        md = ("## DTC-MAIN-001 홈\n\n### 입력 검증\n\n"
              "### 출력 규칙\n내용\n\n### 인터랙션\n내용\n\n"
              "### 엣지케이스\n내용\n")
        violations, _ = vs.check_rules(md, {"DTC-MAIN-001"})
        self.assertTrue(any("입력 검증" in v and "내용 없는" in v
                            for v in violations))

    def test_dangling_reference_is_a_violation(self):
        md = section("DTC-MAIN-001",
                     extra_body="- 탭 시 글 상세로 이동 (DTC-BOARD-002).")
        violations, _ = vs.check_rules(md, {"DTC-MAIN-001"})
        self.assertTrue(any("DTC-BOARD-002" in v and "참조" in v
                            for v in violations))

    def test_reference_to_defined_id_is_ok(self):
        md = (section("DTC-MAIN-001",
                      extra_body="- 탭 시 게시판으로 이동 (DTC-BOARD-001).")
              + section("DTC-BOARD-001"))
        violations, _ = vs.check_rules(
            md, {"DTC-MAIN-001", "DTC-BOARD-001"})
        self.assertEqual(violations, [])


class TestCheckIntegration(unittest.TestCase):
    """check() 가 storyboard 와 rules 파일 짝을 함께 판정하는지 확인한다."""

    HTML = (
        '<div class="ppt-slide"><div class="ppt-top-no">NO. 05</div>'
        '<div class="ppt-top-title">Screen List</div>'
        '<div>DTC-MAIN-001 홈 화면 홈 메인 대시보드</div></div>'
        '<div class="ppt-slide"><div class="ppt-top-no">NO. 06</div>'
        '<div class="ppt-top-title">Service Flow</div>'
        '<div class="mermaid">flowchart LR\n'
        'A["홈&lt;br/&gt;DTC-MAIN-001"]</div></div>'
        '<div class="ppt-slide"><div class="ppt-top-no">NO. 08.1</div>'
        '<div class="ppt-top-title">홈</div>'
        '<div class="ppt-meta-value">홈</div>'
        '<div class="ppt-meta-id">DTC-MAIN-001</div></div>'
        '<script src="mermaid.min.js"></script>'
    )
    CSS = (".ppt-slide{} .ppt-top-no{} .ppt-top-title{} "
           ".ppt-meta-value{} .ppt-meta-id{}")

    def _run(self, write_rules):
        with tempfile.TemporaryDirectory() as td:
            html_path = Path(td) / "dtc_storyboard.html"
            html_path.write_text(self.HTML, encoding="utf-8")
            if write_rules:
                (Path(td) / "dtc_business-rules.md").write_text(
                    section("DTC-MAIN-001"), encoding="utf-8")
            return vs.check(str(html_path), self.CSS)

    def test_missing_rules_file_is_a_violation(self):
        violations, _ = self._run(write_rules=False)
        self.assertTrue(any("Business Rules 문서 없음" in v
                            for v in violations))

    def test_paired_rules_file_passes(self):
        violations, _ = self._run(write_rules=True)
        self.assertEqual(violations, [])


class TestCaptionMismatch(unittest.TestCase):
    """모든 목업에 mock-caption 필수 판정 (이슈 #37 렌더 피드백)."""

    def test_single_mock_without_caption_is_flagged(self):
        html = ('<div class="ppt-top-no">NO. 08.1</div>'
                '<div class="mock"><div class="mock-screen"></div></div>')
        self.assertEqual(vs.caption_mismatch(html), [("08.1", 1, 0)])

    def test_captioned_mocks_pass(self):
        html = ('<div class="ppt-top-no">NO. 08.1</div>'
                '<div class="mock"><div class="mock-caption">홈 (TC-MAIN-001)</div></div>'
                '<div class="mock mock-partial">'
                '<div class="mock-caption">팝업 (TC-MAIN-101)</div></div>')
        self.assertEqual(vs.caption_mismatch(html), [])

    def test_hyphen_classes_are_not_counted_as_mocks(self):
        html = ('<div class="ppt-top-no">NO. 08.1</div>'
                '<div class="mock-screen"></div><div class="mock-body"></div>')
        self.assertEqual(vs.caption_mismatch(html), [])


class TestOverviewSlides(unittest.TestCase):
    """05 Screen List · 06 Service Flow 판정 (이슈 #37)."""

    IDS = {"DTC-MAIN-001", "DTC-BOARD-001"}

    def slide(self, no, body):
        return (f'<div class="ppt-top-no">NO. {no}</div>'
                f'<div class="ppt-top-title">t</div>{body}')

    def test_valid_slides_pass(self):
        html = (self.slide("05", "<div>DTC-MAIN-001 홈 / DTC-BOARD-001 게시판</div>")
                + self.slide("06", '<div class="mermaid">flowchart LR\n'
                                   'A["홈 DTC-MAIN-001"] --> B["게시판 DTC-BOARD-001"]</div>'))
        self.assertEqual(vs.check_overview_slides(html, self.IDS), [])

    def test_missing_screen_list_slide(self):
        html = self.slide("06", '<div class="mermaid">DTC-MAIN-001</div>')
        self.assertTrue(any("05 Screen List 슬라이드 없음" in v
                            for v in vs.check_overview_slides(html, self.IDS)))

    def test_screen_list_missing_id(self):
        html = (self.slide("05", "<div>DTC-MAIN-001 홈</div>")
                + self.slide("06", '<div class="mermaid">DTC-MAIN-001</div>'))
        self.assertTrue(any("DTC-BOARD-001" in v and "05 Screen List" in v
                            for v in vs.check_overview_slides(html, self.IDS)))

    def test_missing_flow_slide(self):
        html = self.slide("05", "<div>DTC-MAIN-001 DTC-BOARD-001</div>")
        self.assertTrue(any("06 Service Flow 슬라이드 없음" in v
                            for v in vs.check_overview_slides(html, self.IDS)))

    def test_flow_without_mermaid(self):
        html = (self.slide("05", "<div>DTC-MAIN-001 DTC-BOARD-001</div>")
                + self.slide("06", "<div>텍스트 흐름 설명 DTC-MAIN-001</div>"))
        self.assertTrue(any("mermaid 흐름도가 없다" in v
                            for v in vs.check_overview_slides(html, self.IDS)))

    def test_flow_without_ids(self):
        html = (self.slide("05", "<div>DTC-MAIN-001 DTC-BOARD-001</div>")
                + self.slide("06", '<div class="mermaid">flowchart LR\nA --> B</div>'))
        self.assertTrue(any("화면 ID 가 없다" in v
                            for v in vs.check_overview_slides(html, self.IDS)))

    def test_sub_numbered_slide_is_not_slide_05(self):
        """08.5 같은 하위 번호가 05 로 오인되지 않는다."""
        self.assertIsNone(vs.slide_body(self.slide("08.5", "<div>x</div>"), "05"))


if __name__ == "__main__":
    unittest.main()
