"""크로스런타임 Agent Adapter와 번들 검증기 계약 테스트."""
import contextlib
import importlib.util
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "skills" / "mobile-web-planner"
TEMPLATE = SKILL_ROOT / "resources" / "template.html"


@contextlib.contextmanager
def minimal_storyboard():
    """검증기가 위반 0건으로 통과해야 하는 최소 산출물을 임시 파일로 만든다.

    저장소는 생성 산출물(HTML)을 커밋하지 않으므로, 검증기 계약은 커밋된
    예시 대신 이 픽스처로 확인한다. 화면 ID 를 정의하지 않으므로 짝을
    이루는 Business Rules 문서도 요구되지 않는다.
    """
    template = TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"<style>(.*?)</style>", template, re.DOTALL)
    if match is None:
        raise RuntimeError("template.html 에 <style> 블록이 없다")
    html = (
        "<!DOCTYPE html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
        f"<style>{match.group(1)}</style></head><body>"
        "<div class=\"docwrap\">"
        "<div class=\"ppt-slide\"><div class=\"ppt-top-no\">NO. 01</div></div>"
        "</div>"
        "<script src=\"https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js\">"
        "</script></body></html>"
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture_storyboard.html"
        path.write_text(html, encoding="utf-8")
        yield path


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
            REPO_ROOT / ".agents" / "AGENTS.md"
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

    def test_accepts_minimal_conforming_storyboard(self):
        css = self.validator.extract_style(
            self.validator.TEMPLATE.read_text(encoding="utf-8"))
        with minimal_storyboard() as path:
            violations, _ = self.validator.check(path, css)
        self.assertEqual(violations, [])

    def test_legacy_wrapper_runs_same_validator(self):
        with minimal_storyboard() as path:
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "check_output.py"),
                    str(path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("계약 위반 없음", result.stdout)


if __name__ == "__main__":
    unittest.main()
