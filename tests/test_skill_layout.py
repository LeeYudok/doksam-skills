"""모든 스킬이 공통 레이아웃 규약을 지키는지 검증한다 (stdlib only).

스킬을 순회하므로 skills/ 아래에 새 스킬을 추가하면 이 테스트가 자동으로
그 스킬까지 검증한다. 스킬 고유의 계약은 각 스킬의 tests/ 가 맡는다.

규약:
  skills/<skill>/SKILL.md        필수. frontmatter 는 name·description 두 개뿐이고
                                 name 은 디렉터리명과 같다
  skills/<skill>/agents/         선택. 있으면 아래 파일명만 허용한다
      claude.md                  Claude Code Agent Adapter
      codex.toml                 Codex custom agent
      antigravity.md             Antigravity/Gemini managed agent 역할 정의
      openai.yaml                Codex UI 메타데이터
  .claude/agents/<skill>.md      claude.md 가 있으면 그것을 가리키는 심링크
  .codex/agents/<skill_us>.toml  codex.toml 이 있으면 그것을 가리키는 심링크
"""
import re
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
ALLOWED_ADAPTERS = {"claude.md", "codex.toml", "antigravity.md", "openai.yaml"}


def skill_dirs():
    return sorted(d for d in SKILLS_DIR.iterdir() if (d / "SKILL.md").is_file())


def frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if match is None:
        raise AssertionError("frontmatter 블록이 없다")
    return match.group(1)


def frontmatter_fields(block: str) -> set:
    return {
        line.split(":", 1)[0].strip()
        for line in block.splitlines()
        if ":" in line and not line.startswith((" ", "\t", "-"))
    }


class TestSkillsDiscovered(unittest.TestCase):
    def test_at_least_one_skill_exists(self):
        self.assertTrue(skill_dirs(), "skills/ 아래에 SKILL.md 를 가진 스킬이 없다")

    def test_skill_dir_has_no_unexpected_top_level_entries(self):
        allowed = {
            "SKILL.md", "agents", "resources", "scripts", "tests", "docs",
            "references", "assets", "__pycache__",
        }
        for skill in skill_dirs():
            for entry in skill.iterdir():
                with self.subTest(skill=skill.name, entry=entry.name):
                    self.assertIn(entry.name, allowed)


class TestSkillManifest(unittest.TestCase):
    def test_frontmatter_is_portable_and_matches_dir_name(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                block = frontmatter(
                    (skill / "SKILL.md").read_text(encoding="utf-8"))
                self.assertEqual(frontmatter_fields(block),
                                 {"name", "description"})
                self.assertIn(f"name: {skill.name}", block)


class TestAdapterLayout(unittest.TestCase):
    def test_only_known_adapter_filenames(self):
        for skill in skill_dirs():
            agents = skill / "agents"
            if not agents.is_dir():
                continue
            for entry in agents.iterdir():
                with self.subTest(skill=skill.name, entry=entry.name):
                    self.assertIn(entry.name, ALLOWED_ADAPTERS)

    def test_claude_adapter_identity_and_skill_preload(self):
        for skill in skill_dirs():
            adapter = skill / "agents" / "claude.md"
            if not adapter.is_file():
                continue
            with self.subTest(skill=skill.name):
                block = frontmatter(adapter.read_text(encoding="utf-8"))
                self.assertIn(f"name: {skill.name}", block)
                self.assertIn("description:", block)
                self.assertRegex(block, rf"skills:\s*\n\s*-\s+{skill.name}\b")

    def test_codex_adapter_has_required_fields(self):
        for skill in skill_dirs():
            adapter = skill / "agents" / "codex.toml"
            if not adapter.is_file():
                continue
            with self.subTest(skill=skill.name):
                with adapter.open("rb") as file:
                    config = tomllib.load(file)
                for field in ("name", "description", "developer_instructions"):
                    self.assertTrue(config.get(field), f"{field} 가 비어 있다")
                self.assertEqual(config["name"], skill.name.replace("-", "_"))
                self.assertIn(skill.name, config["developer_instructions"])

    def test_antigravity_adapter_has_frontmatter(self):
        """agy 는 frontmatter 없는 agent md 를 오류도 경고도 없이 무시한다.

        2026-08-11 agy 1.1.11 실측: 빈 플러그인에 frontmatter 가 있는 파일과
        없는 파일을 하나씩 넣으면 `agy agents` 에 앞의 것만 나타난다. 본문에
        스킬명이 있는지만 보던 이전 검사는 이 결함을 통과시켰다 (이슈 #110).
        """
        for skill in skill_dirs():
            adapter = skill / "agents" / "antigravity.md"
            if not adapter.is_file():
                continue
            with self.subTest(skill=skill.name):
                block = frontmatter(adapter.read_text(encoding="utf-8"))
                self.assertIn(f"name: {skill.name}", block)
                description = re.search(r"^description:\s*(\S.*)$",
                                        block, re.MULTILINE)
                self.assertIsNotNone(description, "description 이 비어 있다")

    def test_openai_metadata_has_minimum_interface_fields(self):
        for skill in skill_dirs():
            adapter = skill / "agents" / "openai.yaml"
            if not adapter.is_file():
                continue
            with self.subTest(skill=skill.name):
                text = adapter.read_text(encoding="utf-8")
                for field in ("display_name:", "short_description:",
                              "default_prompt:"):
                    self.assertIn(field, text)
                self.assertIn(f"${skill.name}", text)


class TestRepoAdapterSymlinks(unittest.TestCase):
    """루트의 런타임 탐색 경로는 스킬이 소유한 원본을 가리키는 심링크여야 한다."""

    def _assert_symlink(self, link: Path, target: Path):
        self.assertTrue(link.is_symlink(), f"{link} 가 심링크가 아니다")
        self.assertEqual(link.resolve(), target.resolve())

    def test_claude_agent_links_point_at_skill_sources(self):
        for skill in skill_dirs():
            adapter = skill / "agents" / "claude.md"
            if not adapter.is_file():
                continue
            with self.subTest(skill=skill.name):
                self._assert_symlink(
                    REPO_ROOT / ".claude" / "agents" / f"{skill.name}.md",
                    adapter,
                )

    def test_codex_agent_links_point_at_skill_sources(self):
        for skill in skill_dirs():
            adapter = skill / "agents" / "codex.toml"
            if not adapter.is_file():
                continue
            with self.subTest(skill=skill.name):
                name = skill.name.replace("-", "_")
                self._assert_symlink(
                    REPO_ROOT / ".codex" / "agents" / f"{name}.toml",
                    adapter,
                )


class TestRootIsSkillAgnostic(unittest.TestCase):
    """루트 설치기·스크립트는 특정 스킬 이름을 알아서는 안 된다."""

    def _root_texts(self):
        paths = [REPO_ROOT / "install.sh"]
        scripts = REPO_ROOT / "scripts"
        if scripts.is_dir():
            paths += sorted(p for p in scripts.iterdir() if p.is_file())
        return paths

    def test_no_skill_name_is_hardcoded(self):
        names = [skill.name for skill in skill_dirs()]
        for path in self._root_texts():
            text = path.read_text(encoding="utf-8")
            for name in names:
                with self.subTest(file=path.name, skill=name):
                    self.assertNotIn(name, text)
                    self.assertNotIn(name.replace("-", "_"), text)


if __name__ == "__main__":
    unittest.main()
