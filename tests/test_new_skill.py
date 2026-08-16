"""new_skill.sh 가 만드는 뼈대가 곧바로 유효한지 검증한다 (stdlib only).

생성기는 저장소에 실제 파일과 심링크를 만들므로, 스크립트만 임시 디렉터리로
복사해 그곳을 REPO_ROOT 로 삼아 돌린다 — new_skill.sh 는 자기 위치에서
REPO_ROOT 를 유도한다.
"""
import re
import shutil
import subprocess
import tomllib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "scripts" / "new_skill.sh"

# 설명에 따옴표와 역슬래시를 넣는다. 트리거 발화를 인용하는 스킬이 실제로
# 있고(memory-factcheck), 이스케이프를 빠뜨리면 codex.toml 이 깨진다.
TRICKY_DESC = '사용자가 "정리해줘" / "감사해줘" 라고 할 때 쓴다. 역슬래시 \\ 포함.'


class TestGeneratedSkeleton(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "scripts").mkdir()
        shutil.copy2(GENERATOR, self.root / "scripts" / "new_skill.sh")
        (self.root / "skills").mkdir()
        (self.root / ".claude" / "agents").mkdir(parents=True)
        (self.root / ".codex" / "agents").mkdir(parents=True)

    def generate(self, name, desc):
        result = subprocess.run(
            [str(self.root / "scripts" / "new_skill.sh"), name, desc],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.root / "skills" / name

    def test_codex_toml_parses_when_description_has_quotes(self):
        """description 은 TOML basic string 이라 " 와 \\ 를 이스케이프해야 한다.

        빠뜨리면 tomllib 이 파싱에 실패해 어댑터가 통째로 죽는다 (이슈 #122).
        """
        skill = self.generate("quote-probe", TRICKY_DESC)
        with (skill / "agents" / "codex.toml").open("rb") as file:
            config = tomllib.load(file)
        self.assertEqual(config["name"], "quote_probe")
        self.assertEqual(config["description"], TRICKY_DESC)

    def test_frontmatter_survives_quotes_in_description(self):
        """agy 는 frontmatter 가 깨진 agent md 를 조용히 무시한다 (이슈 #110)."""
        skill = self.generate("quote-probe", TRICKY_DESC)
        for adapter in ("claude.md", "antigravity.md"):
            with self.subTest(adapter=adapter):
                text = (skill / "agents" / adapter).read_text(encoding="utf-8")
                block = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
                self.assertIsNotNone(block, f"{adapter} 에 frontmatter 가 없다")
                self.assertIn("name: quote-probe", block.group(1))
                self.assertIn(TRICKY_DESC, block.group(1))

    def test_openai_metadata_is_generated_and_quote_safe(self):
        """생성기가 openai.yaml 을 빠뜨리면 커버리지가 또 벌어진다 (이슈 #131).

        YAML 큰따옴표 스칼라 안의 " 는 값을 끊어 버리므로 설명에서 제거한다.
        """
        skill = self.generate("quote-probe", TRICKY_DESC)
        text = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            self.assertIn(field, text)
        self.assertIn("$quote-probe", text)
        for line in text.splitlines():
            if ": " not in line:
                continue
            value = line.split(": ", 1)[1]
            with self.subTest(line=line):
                self.assertEqual(value.count('"'), 2,
                                 "값 안의 따옴표가 스칼라를 끊는다")

    def test_skill_md_frontmatter_is_portable(self):
        skill = self.generate("plain-probe", "평범한 설명이다.")
        block = re.match(r"^---\n(.*?)\n---\n",
                         (skill / "SKILL.md").read_text(encoding="utf-8"), re.DOTALL)
        fields = {line.split(":", 1)[0].strip()
                  for line in block.group(1).splitlines() if ":" in line
                  and not line.startswith((" ", "\t", "-"))}
        self.assertEqual(fields, {"name", "description"})

    def test_root_symlinks_point_at_the_skill_sources(self):
        skill = self.generate("link-probe", "설명.")
        claude = self.root / ".claude" / "agents" / "link-probe.md"
        codex = self.root / ".codex" / "agents" / "link_probe.toml"
        self.assertTrue(claude.is_symlink())
        self.assertTrue(codex.is_symlink())
        self.assertEqual(claude.resolve(), (skill / "agents" / "claude.md").resolve())
        self.assertEqual(codex.resolve(), (skill / "agents" / "codex.toml").resolve())

    def test_rejects_non_kebab_case_names(self):
        result = subprocess.run(
            [str(self.root / "scripts" / "new_skill.sh"), "Bad_Name", "설명."],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
