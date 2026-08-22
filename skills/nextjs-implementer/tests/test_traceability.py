import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "validate_traceability", ROOT / "scripts" / "validate_traceability.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


RULES = """# T Business Rules

## DTC-MAIN-001 홈

### 출력 규칙
| 상태 | 표시 |
|---|---|
| DTC-MAIN-001.OUT-01 · 로딩 | 스켈레톤 |
"""


class TestTraceability(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "home.tsx").write_text("export {}", encoding="utf-8")
        (self.root / "src" / "home.test.tsx").write_text("export {}", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self):
        return {"screens": [{
            "screenId": "DTC-MAIN-001",
            "route": "/",
            "implementation": ["src/home.tsx"],
            "rules": [{
                "ruleId": "DTC-MAIN-001.OUT-01",
                "tests": ["src/home.test.tsx"],
            }],
        }]}

    def test_valid_manifest_passes(self):
        self.assertEqual(validator.validate(self.manifest(), RULES, self.root), [])

    def test_missing_rule_and_file_are_reported(self):
        manifest = self.manifest()
        manifest["screens"][0]["implementation"] = ["src/missing.tsx"]
        manifest["screens"][0]["rules"] = []
        joined = "\n".join(validator.validate(manifest, RULES, self.root))
        self.assertIn("구현 파일 없음", joined)
        self.assertIn("규칙 ID 누락", joined)

    def test_wrong_screen_and_duplicate_rule_are_reported(self):
        manifest = self.manifest()
        rule = manifest["screens"][0]["rules"][0]
        rule["ruleId"] = "DTC-OTHER-001.OUT-01"
        manifest["screens"][0]["rules"].append(dict(rule))
        joined = "\n".join(validator.validate(manifest, RULES, self.root))
        self.assertIn("다른 화면", joined)
        self.assertIn("중복 규칙 ID", joined)


if __name__ == "__main__":
    unittest.main()
