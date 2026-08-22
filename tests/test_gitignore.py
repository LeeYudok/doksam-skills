"""`.gitignore` 계약 테스트 (stdlib only).

두 방향을 모두 본다.

1. **추적 중인 파일이 무시되면 안 된다.** `*_business-rules.md` 처럼 산출물
   이름을 그대로 쓰는 픽스처가 있어서, 무심코 전역 패턴을 넣으면 픽스처가
   조용히 무시 대상이 된다. 이미 추적 중인 파일은 계속 추적되므로 그 순간에는
   아무 일도 안 일어나고, **다음에 추가되는 픽스처만 사라진다.**
2. **막기로 한 것은 실제로 막혀야 한다.** 규칙을 지우거나 파일을 통째로
   갈아엎으면 여기서 잡힌다.

판정은 문자열 매칭이 아니라 `git check-ignore` 다 — 패턴 문법(앵커 `/`,
디렉터리 `/`, 순서)을 우리가 다시 구현하지 않는다.
"""
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: 무시돼야 하는 경로. 왜 막는지는 .gitignore 의 주석에 있다.
MUST_IGNORE = (
    "demo/storyboard.html",
    "demo1/generate.py",
    "demos/out.html",
    "some_storyboard.html",
    "some_business-rules.md",
    "deck.pdf",
    "deck.pptx",
    ".codegraph/index.db",
    "node_modules/react/index.js",
    "dist/assets/app.js",
    ".next/trace",
    "run.log",
    "__pycache__/x.pyc",
    "output/x.html",
    "tmp/x.html",
    ".env",
)

#: 무시되면 안 되는 경로. 산출물과 이름이 겹치는 픽스처들이다.
MUST_TRACK = (
    "skills/mobile-web-planner/tests/fixtures/runtime-parity/agy_business-rules.md",
    "skills/mobile-web-planner/tests/fixtures/runtime-parity/agy.html",
    "skills/mobile-web-planner/tests/fixtures/layout/baseline-slides.html",
    "skills/mobile-web-planner/resources/template.html",
    ".claude/agents/mobile-web-planner.md",
)


def check_ignore(paths):
    """무시되는 경로만 돌려준다. git 이 판정 주체다."""
    result = subprocess.run(
        ["git", "check-ignore", "--stdin"], cwd=REPO,
        input="\n".join(paths), capture_output=True, text=True)
    if result.returncode not in (0, 1):  # 0=일부 매치, 1=매치 없음
        raise AssertionError(f"git check-ignore 실패: {result.stderr.strip()}")
    return set(result.stdout.split())


class TestGitignore(unittest.TestCase):
    def test_no_tracked_file_is_ignored(self):
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True
        ).stdout.split()
        self.assertTrue(tracked, "추적 파일 목록이 비었다 — git 저장소가 맞는지 확인")
        ignored = check_ignore(tracked)
        self.assertEqual(sorted(ignored), [],
                         "추적 중인 파일이 .gitignore 에 걸린다")

    def test_generated_artifacts_are_ignored(self):
        ignored = check_ignore(MUST_IGNORE)
        for path in MUST_IGNORE:
            with self.subTest(path=path):
                self.assertIn(path, ignored, f"{path} 가 무시되지 않는다")

    def test_fixtures_are_not_ignored(self):
        ignored = check_ignore(MUST_TRACK)
        for path in MUST_TRACK:
            with self.subTest(path=path):
                self.assertNotIn(path, ignored, f"{path} 가 무시된다")


if __name__ == "__main__":
    unittest.main()
