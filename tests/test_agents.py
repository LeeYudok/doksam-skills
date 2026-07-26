"""크로스런타임 Agent Adapter와 번들 검증기 계약 테스트."""
import importlib.util
import re
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "skills" / "mobile-web-planner"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"모듈을 불러올 수 없다: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestClaudeAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (
            REPO_ROOT / ".claude" / "agents" / "mobile-web-planner.md"
        ).read_text(encoding="utf-8")

    def test_has_required_identity(self):
        self.assertIn("name: mobile-web-planner", self.text)
        self.assertIn("description:", self.text)

    def test_preloads_common_skill(self):
        self.assertRegex(
            self.text,
            r"skills:\s*\n\s*-\s+mobile-web-planner",
        )


class TestCodexAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = REPO_ROOT / ".codex" / "agents" / "mobile_web_planner.toml"
        with path.open("rb") as file:
            cls.config = tomllib.load(file)

    def test_has_required_fields(self):
        for field in ("name", "description", "developer_instructions"):
            with self.subTest(field=field):
                self.assertTrue(self.config.get(field))

    def test_references_common_skill(self):
        self.assertIn(
            "mobile-web-planner skill",
            self.config["developer_instructions"],
        )


class TestAntigravityAdapter(unittest.TestCase):
    def test_references_common_skill_and_validation(self):
        text = (
            REPO_ROOT / "adapters" / "antigravity" / "AGENTS.md"
        ).read_text(encoding="utf-8")
        self.assertIn("`mobile-web-planner` Skill", text)
        self.assertIn("검증기", text)


class TestOpenAiSkillMetadata(unittest.TestCase):
    def test_has_minimum_interface_fields(self):
        text = (
            SKILL_ROOT / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            with self.subTest(field=field):
                self.assertIn(field, text)
        self.assertIn("$mobile-web-planner", text)


class TestSkillFrontmatter(unittest.TestCase):
    def test_has_only_portable_required_fields(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        fields = {
            line.split(":", 1)[0].strip()
            for line in match.group(1).splitlines()
            if ":" in line
        }
        self.assertEqual(fields, {"name", "description"})
        self.assertIn("name: mobile-web-planner", match.group(1))


class TestBundledValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module(
            "validate_storyboard",
            SKILL_ROOT / "scripts" / "validate_storyboard.py",
        )

    def test_uses_only_skill_local_template(self):
        self.assertEqual(
            self.validator.TEMPLATE,
            SKILL_ROOT / "resources" / "template.html",
        )

    def test_accepts_committed_example(self):
        template = self.validator.TEMPLATE.read_text(encoding="utf-8")
        css = self.validator.extract_style(template)
        violations, _ = self.validator.check(
            REPO_ROOT / "examples" / "doksam_news_storyboard.html",
            css,
        )
        self.assertEqual(violations, [])

    def test_legacy_wrapper_runs_same_validator(self):
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "check_output.py"),
                str(REPO_ROOT / "examples" / "doksam_news_storyboard.html"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("계약 위반 없음", result.stdout)


if __name__ == "__main__":
    unittest.main()
