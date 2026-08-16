"""제3자 저작물 표기가 실제 사용과 어긋나지 않는지 검증한다 (stdlib only).

새 외부 자산을 들여올 때 표기를 빠뜨리기 쉽다. 산출물 템플릿이 참조하는 외부
호스트와 저장소에 커밋된 아이콘 데이터를 훑어, THIRD-PARTY-NOTICES.md 가 전부
다루는지 본다.
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTICES = REPO_ROOT / "THIRD-PARTY-NOTICES.md"
SKILLS_DIR = REPO_ROOT / "skills"

# 산출물에 그대로 실려 나가는 파일. 여기서 참조하는 외부 호스트는 사용자가
# 받아보는 문서가 실행 시 의존하는 것이므로 표기 대상이다.
SHIPPED = ("resources/template.html",)

# 표기 대상이 아닌 호스트 — 문서의 예시나 표준 식별자다.
IGNORED_HOSTS = {
    "www.w3.org",              # SVG 네임스페이스
    "schemas.openxmlformats.org",  # ECMA-376 네임스페이스
    "example.com", "cdn.example.com", "fonts.example.com",
    "ui.doksam.com", "www.doksam.com",  # 자체 자산
}


def external_hosts(text):
    hosts = set()
    for url in re.findall(r"https?://([A-Za-z0-9.\-]+)", text):
        host = url.rstrip(".")
        if host not in IGNORED_HOSTS:
            hosts.add(host)
    return hosts


class TestNoticesExist(unittest.TestCase):
    def test_notices_file_exists(self):
        self.assertTrue(NOTICES.is_file(), "THIRD-PARTY-NOTICES.md 가 없다")

    def test_license_file_is_unmodified_mit(self):
        """LICENSE 에 표기를 덧붙이지 않는다.

        MIT 전문에 내용을 붙이면 GitHub 의 라이선스 자동 인식이 깨질 수 있다.
        표기는 별도 파일에 둔다.
        """
        text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertNotIn("Third-Party", text)
        self.assertNotIn("Phosphor", text)


class TestCoverage(unittest.TestCase):
    def setUp(self):
        self.notices = NOTICES.read_text(encoding="utf-8")

    def test_every_external_host_in_shipped_files_is_documented(self):
        """산출물이 실행 시 부르는 외부 호스트는 전부 표기돼 있어야 한다."""
        for skill in sorted(SKILLS_DIR.iterdir()):
            for rel in SHIPPED:
                path = skill / rel
                if not path.is_file():
                    continue
                for host in external_hosts(path.read_text(encoding="utf-8")):
                    with self.subTest(file=f"{skill.name}/{rel}", host=host):
                        self.assertIn(host, self.notices,
                                      f"{host} 가 표기되지 않았다")

    def test_committed_phosphor_paths_are_attributed(self):
        """Phosphor path 가 저장소에 있으면 MIT 고지가 필요하다."""
        committed = [p for p in SKILLS_DIR.rglob("*")
                     if p.is_file() and p.suffix in {".md", ".html"}
                     and 'viewBox="0 0 256 256"' in p.read_text(encoding="utf-8", errors="ignore")]
        if not committed:
            self.skipTest("커밋된 Phosphor path 가 없다")
        self.assertIn("Phosphor Icons", self.notices)
        self.assertIn("Copyright (c) 2023 Phosphor Icons", self.notices)
        # MIT 는 고지문 전체를 포함하라고 요구한다
        self.assertIn("THE SOFTWARE IS PROVIDED \"AS IS\"", self.notices)

    def test_each_documented_entry_names_a_license(self):
        for name in ("Phosphor Icons", "mermaid", "Pretendard"):
            with self.subTest(entry=name):
                self.assertIn(name, self.notices)
        for license_name in ("MIT License", "SIL Open Font License"):
            with self.subTest(license=license_name):
                self.assertIn(license_name, self.notices)

    def test_readme_points_at_the_notices(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("THIRD-PARTY-NOTICES.md", readme)


if __name__ == "__main__":
    unittest.main()
