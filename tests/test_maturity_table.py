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

    def test_by_design_list_found_in_readme(self):
        found = score_skills.no_adapter_by_design()
        self.assertTrue(found, "README '에이전트를 두지 않는 이유' 표를 못 읽었다")
        for name in found:
            with self.subTest(skill=name):
                self.assertIn(name, SKILLS)
                self.assertFalse((ROOT / "skills" / name / "agents").is_dir())


if __name__ == "__main__":
    unittest.main()
