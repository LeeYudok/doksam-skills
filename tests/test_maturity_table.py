"""README 완성도 표가 scripts/score_skills.py 결과와 같은지 확인한다 (이슈 #191)."""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("score_skills", ROOT / "scripts" / "score_skills.py")
score_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score_skills)

SKILLS = {p.parent.name for p in ROOT.glob("skills/*/SKILL.md")}


class MaturityTable(unittest.TestCase):
    def test_readme_is_current(self):
        self.assertEqual(score_skills.main(["--check"]), 0,
                         "python3 scripts/score_skills.py --write 로 README 표를 다시 만든다")

    def test_every_skill_scored(self):
        names = [line.split("|")[2].strip() for line in score_skills.table().splitlines()[2:]]
        self.assertEqual(sorted(names), sorted(SKILLS))

    def test_overlap_data_names_real_skills(self):
        data = json.loads(score_skills.OVERLAP.read_text(encoding="utf-8"))
        for name in (k for k in data if not k.startswith("_")):
            with self.subTest(skill=name):
                self.assertIn(name, SKILLS, "개명·삭제된 스킬이 외부 유사 목록에 남아 있다")

    def test_claims_lists_are_valid(self):
        for skill in sorted(ROOT.glob("skills/*/SKILL.md")):
            _, errors = score_skills.claims(skill.parent)
            with self.subTest(skill=skill.parent.name):
                self.assertEqual(errors, [], "tests/claims.json 형식은 scripts/score_skills.py docstring 참조")

    def test_invalid_claims_are_not_counted(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "x"
            (skill / "tests").mkdir(parents=True)
            (skill / "SKILL.md").write_text("읽기 전용으로 연다.\n", encoding="utf-8")
            (skill / "tests" / "test_x.py").write_text(
                "import unittest\n\n\ndef test_module_level():\n    pass\n\n\n"
                "class Base(unittest.TestCase):\n    pass\n\n\n"
                "class X(Base):\n    def test_ro(self):\n        pass\n\n\n"
                "class NotCase:\n    def test_plain(self):\n        pass\n", encoding="utf-8")
            (skill / "tests" / "notes.txt").write_text("def test_fake():\n", encoding="utf-8")
            (skill / "tests" / "claims.json").write_text(json.dumps({"claims": [
                {"id": "OK", "kind": "실패", "rule": "읽기 전용으로 연다", "test": "test_x.py::test_ro"},
                {"id": "DUP-TEST", "kind": "정상", "rule": "읽기 전용으로 연다", "test": "test_x.py::test_ro"},
                {"id": "NO-RULE", "kind": "정상", "rule": "문서에 없는 문장", "test": "test_x.py::test_ro"},
                {"id": "NO-TEST", "kind": "경계", "rule": "읽기 전용으로 연다", "test": "test_x.py::test_gone"},
                {"id": "BAD-KIND", "kind": "기타", "rule": "읽기 전용으로 연다", "test": "test_x.py::test_ro"},
                {"id": "MODULE-FN", "kind": "정상", "rule": "읽기 전용으로 연다", "test": "test_x.py::test_module_level"},
                {"id": "NOT-CASE", "kind": "정상", "rule": "읽기 전용으로 연다", "test": "test_x.py::test_plain"},
                {"id": "NOT-TEST-FILE", "kind": "정상", "rule": "읽기 전용으로 연다", "test": "notes.txt::test_fake"},
            ]}), encoding="utf-8")
            score_skills.ROOT = Path(tmp)
            try:
                valid, errors = score_skills.claims(skill)
            finally:
                score_skills.ROOT = ROOT
        self.assertEqual([c["id"] for c in valid], ["OK"])
        self.assertEqual(len(errors), 7)

    def test_by_design_list_found_in_readme(self):
        found = score_skills.no_adapter_by_design()
        self.assertTrue(found, "README '에이전트를 두지 않는 이유' 표를 못 읽었다")
        for name in found:
            with self.subTest(skill=name):
                self.assertIn(name, SKILLS)
                self.assertFalse((ROOT / "skills" / name / "agents").is_dir())


if __name__ == "__main__":
    unittest.main()
