"""README 의 스킬 표가 실제 skills/ 와 맞는지 확인한다 (이슈 #177).

스킬 이름에는 에이전트 유무를 담지 않는다. 대신 README 표의 `에이전트` 열이
그 정보를 보여준다. 표는 손으로 고치므로, 어댑터를 넣거나 빼고 README 를
잊으면 여기서 잡는다.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
ROW = re.compile(r"^\| \[([a-z0-9-]+)\]\(skills/\1/SKILL\.md\) \| ([^|]+) \|", re.M)


def skill_section():
    start = README.index("## 스킬")
    return README[start:README.index("\n## ", start + 1)]


class ReadmeSkillTable(unittest.TestCase):
    def setUp(self):
        self.rows = ROW.findall(skill_section())

    def test_every_skill_listed_once(self):
        names = [n for n, _ in self.rows]
        self.assertEqual(sorted(names), SKILLS, "README 스킬 표와 skills/ 가 다르다")

    def test_count_sentence(self):
        m = re.search(r"스킬은 (\d+)개입니다", skill_section())
        self.assertIsNotNone(m, "README 에 '스킬은 N개입니다' 문장이 없다")
        self.assertEqual(int(m.group(1)), len(SKILLS))

    def test_agent_column_matches_adapters(self):
        for name, cell in self.rows:
            has = (ROOT / "skills" / name / "agents" / "claude.md").is_file()
            expected = f"`{name}` / `{name.replace('-', '_')}`" if has else "없음"
            with self.subTest(skill=name):
                self.assertEqual(cell.strip(), expected)


if __name__ == "__main__":
    unittest.main()
