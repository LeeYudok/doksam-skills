"""nextjs-implementer 가 참조하는 외부 계약의 드리프트 검출 (stdlib only).

이 스킬의 SKILL.md 는 mobile-web-planner 산출물의 구조(Business Rules 4개 절)
를 구현 체크리스트로 쓴다고 약속한다. 기획 스킬이 절 이름을 바꾸면 이 약속이
조용히 낡으므로, 두 스킬 문서를 대조해 어긋남을 테스트로 잡는다.
"""
import re
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = SKILL_ROOT.parent


def flat(text):
    """줄바꿈으로 갈라진 구문도 잡히게 공백을 한 칸으로 정규화한다."""
    return re.sub(r"\s+", " ", text)


SKILL_MD = flat((SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"))

# SKILL.md 가 "4개 절"로 약속하는 Business Rules 섹션 명칭.
BR_SECTIONS = ("입력 검증", "출력 규칙", "인터랙션", "엣지케이스")


class TestPlannerContract(unittest.TestCase):
    """mobile-web-planner 산출물 구조에 대한 참조가 실제와 일치해야 한다."""

    @classmethod
    def setUpClass(cls):
        cls.planner = flat((
            SKILLS_DIR / "mobile-web-planner" / "SKILL.md"
        ).read_text(encoding="utf-8"))

    def test_br_sections_exist_in_planner(self):
        """참조하는 4개 절 명칭이 기획 스킬 문서에도 그대로 있어야 한다."""
        for section in BR_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, self.planner)
                self.assertIn(section, SKILL_MD)

    def test_storyboard_slide_refs_exist_in_planner(self):
        """참조하는 슬라이드 번호(05/06/07.x/08/09.x)가 기획 스킬의 번호
        체계에 존재해야 한다 — 체계가 바뀌면 여기서 드리프트가 잡힌다."""
        for ref in ("05 Screen List", "06 Service Flow", "08 General Rule"):
            with self.subTest(ref=ref):
                self.assertIn(ref, SKILL_MD)
                self.assertIn(ref.split(" ", 1)[1], self.planner)
        self.assertIn("07.x", SKILL_MD)
        self.assertIn("09.x", SKILL_MD)

    def test_deliverable_filename_patterns_match_planner(self):
        """입력 파일명 패턴이 기획 스킬의 산출물 명명과 일치해야 한다."""
        for pattern in ("_storyboard.html", "_business-rules.md"):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, SKILL_MD)
                self.assertIn(pattern, self.planner)


class TestBackendModeConsistency(unittest.TestCase):
    """백엔드 모드 표기가 SKILL.md 와 Adapter 3종에서 일관돼야 한다."""

    ADAPTERS = ("claude.md", "codex.toml", "antigravity.md")

    def test_java_version_is_consistent(self):
        self.assertIn("Java 1.8", SKILL_MD)
        for name in self.ADAPTERS:
            with self.subTest(adapter=name):
                text = (SKILL_ROOT / "agents" / name).read_text(
                    encoding="utf-8")
                self.assertIn("Java 1.8", text)

    def test_spring_boot_line_is_java8_compatible(self):
        """Spring Boot 는 2.7 (Java 8 을 지원하는 마지막 라인)로 고정한다."""
        self.assertIn("Spring Boot 2.7", SKILL_MD)
        self.assertNotRegex(
            SKILL_MD, r"Spring Boot 3",
            "Spring Boot 3 은 Java 17 필수 — Java 1.8 계약과 모순된다")

    def test_doksam_ui_link_targets_existing_skill(self):
        """doksam-ui 연계 문구가 있다면 그 스킬이 실제로 존재해야 한다."""
        if "doksam-ui" not in SKILL_MD:
            self.skipTest("doksam-ui 연계 문구 없음")
        self.assertTrue(
            (SKILLS_DIR / "doksam-ui" / "SKILL.md").is_file(),
            "SKILL.md 가 doksam-ui Skill 을 참조하지만 스킬이 없다")


if __name__ == "__main__":
    unittest.main()
