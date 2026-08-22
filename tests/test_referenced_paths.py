"""스킬 문서가 가리키는 경로가 실제로 존재하는지 검사한다 (stdlib only).

문서는 "이 스크립트를 돌려라" 라고 지시하지만, 경로가 틀리거나 파일이 옮겨
가면 **에이전트는 오류를 보고하지 않고 그 단계를 조용히 건너뛴다.** 게이트가
있다고 믿는 상태가 게이트가 없는 상태보다 나쁘다 — sdlc-orchestrator 가
finguard 를 "추가 예정" 으로 적어 둔 채 머지된 것이 그 예다.

세 가지 표기를 모두 본다.

    skills/<skill>/scripts/x.py     저장소 루트 기준
    <스킬경로>/scripts/x.py          그 문서를 소유한 스킬 기준
    <other-스킬경로>/scripts/x.py    이름이 박힌 다른 스킬 기준
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

REPO_ROOTED = re.compile(r"\bskills/([a-z0-9-]+)/([A-Za-z0-9_/.-]+\.(?:py|js|md|html))")
OWN_SKILL = re.compile(r"<스킬경로>/([A-Za-z0-9_/.-]+\.(?:py|js))")
NAMED_SKILL = re.compile(r"<(?:설치된-)?([a-z0-9-]+?)-스킬(?:경로)?>/([A-Za-z0-9_/.-]+\.(?:py|js))")
MD_LINK = re.compile(r"\]\((references/[A-Za-z0-9_.-]+\.md)\)")


def docs():
    for path in sorted(SKILLS.rglob("*.md")):
        # 픽스처는 산출물 예시라 문서가 아니다.
        if "tests/fixtures" in path.as_posix():
            continue
        yield path


def owning_skill(path):
    return SKILLS / path.relative_to(SKILLS).parts[0]


class TestReferencedPaths(unittest.TestCase):
    def test_all_referenced_paths_exist(self):
        missing = []
        for doc in docs():
            text = doc.read_text(encoding="utf-8")
            skill_dir = owning_skill(doc)
            targets = []
            targets += [SKILLS / skill / rest for skill, rest in REPO_ROOTED.findall(text)]
            targets += [skill_dir / rest for rest in OWN_SKILL.findall(text)]
            targets += [SKILLS / skill / rest for skill, rest in NAMED_SKILL.findall(text)]
            targets += [doc.parent / rest for rest in MD_LINK.findall(text)]
            for target in targets:
                if not target.exists():
                    missing.append(f"{doc.relative_to(REPO)} → {target.relative_to(REPO)}")
        self.assertEqual(missing, [], "문서가 없는 경로를 가리킨다:\n" + "\n".join(missing))

    def test_pipeline_gates_are_not_left_as_todo(self):
        """이미 존재하는 스킬을 '추가 예정' 으로 적어 두지 않는다.

        오케스트레이터가 게이트를 미구현으로 적어 두면 그 단계가 통째로
        비활성 상태로 머지되고, 파이프라인은 검증했다고 보고한다.
        """
        existing = {path.name for path in SKILLS.iterdir() if path.is_dir()}
        for doc in docs():
            text = doc.read_text(encoding="utf-8")
            for name in existing:
                pattern = re.compile(
                    rf"`{re.escape(name)}`[^\n]*\((?:추가 예정|미구현|TODO)\)")
                with self.subTest(doc=str(doc.relative_to(REPO)), skill=name):
                    self.assertIsNone(
                        pattern.search(text),
                        f"{doc.relative_to(REPO)} 가 이미 있는 스킬 {name} 를 미구현으로 적었다")


if __name__ == "__main__":
    unittest.main()
