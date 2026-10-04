"""check_handoff.py 가 SKILL.md 의 핸드오프 형식 단언을 판정하는지 본다 (stdlib only, 이슈 #201)."""

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_handoff", SKILL / "scripts" / "check_handoff.py")
m = importlib.util.module_from_spec(spec)
sys.modules["check_handoff"] = m
spec.loader.exec_module(m)

FAKE_PAT = "glpat-" + "ZZZZ1111aaaa2222bbbb"


def body(**over):
    f = {"이슈": "https://gitlab.example.com/a/b/-/issues/7", "작성": "2026-10-04 15:30:12.345",
         "작업 이슈/PR": "#7 (열림)", "브랜치": "`batch/claude-20261004`  ·  워크트리: 없음 — 새로 만들 것",
         "HEAD": "`abc1234` (push 됨)"}
    f.update(over)
    head = "\n".join(f"- {k}: {v}" for k, v in f.items())
    return f"""# HANDOFF — 테스트 요약

{head}

## 지금 어디까지

로그인 화면까지 끝냈다.

## 검증 결과 (원문)

```
Ran 3 tests ... OK
```

## 실행 중인 것

| 대상 | 주소 | 어떻게 띄웠나 |
| --- | --- | --- |
| dev 서버 | http://127.0.0.1:5173 | pnpm dev |

## 미결 판단

없음

## 다음에 칠 명령

```bash
cd /Users/me/repo
pnpm test
```

## 함정

포트가 점유돼 있으면 옮겨 간다.
"""


POINTER = """# HANDOFF (포인터)

세션 인계 본문은 GitLab 이슈에 있다. 이 파일은 그 위치만 가리킨다.

- 현재 핸드오프: https://gitlab.example.com/a/b/-/issues/9
- 작성: 2026-10-04 15:30:12.345
- 요약: 리뷰 답글 대기
- 전체 목록: https://gitlab.example.com/a/b/-/issues?label_name=handoff
"""


def run(argv, stdin=None):
    out, err = io.StringIO(), io.StringIO()
    old = sys.stdin
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = m.main(argv)
    finally:
        sys.stdin = old
    return code, out.getvalue(), err.getvalue()


class CheckHandoff(unittest.TestCase):
    def test_filled_body_passes(self):
        code, out, _ = run(["-"], stdin=body())
        self.assertEqual((code, out.strip()), (0, "위반 0건, 경고 0건"))

    def test_iso_timestamp_rejected(self):
        for ts in ("2026-10-04T15:30:12+09:00", "2026-10-04 15:30:12"):
            code, out, _ = run(["-"], stdin=body(작성=ts))
            self.assertEqual(code, 1, ts)
            self.assertIn("작성 시각", out)

    def test_iso_in_prose_rejected_but_plain_date_ok(self):
        text = body().replace("로그인 화면까지", "2026-10-04T15:30:12.000+09:00 에 로그인 화면까지")
        self.assertIn("ISO 8601", run(["-"], stdin=text)[1])
        ok = body().replace("로그인 화면까지", "2026-10-04 에 로그인 화면까지")
        self.assertEqual(run(["-"], stdin=ok)[0], 0)

    def test_missing_section_and_field(self):
        text = body().replace("## 함정", "## 기타")
        text = text.replace("- HEAD: `abc1234` (push 됨)\n", "")
        code, out, _ = run(["-"], stdin=text)
        self.assertEqual(code, 1)
        self.assertIn("섹션 `## 함정` 이 없다", out)
        self.assertIn("필드 `HEAD`", out)

    def test_unfilled_template_placeholders(self):
        code, out, _ = run(["-"], stdin=body(브랜치="`<branch>`").replace("pnpm test", "<command>"))
        self.assertEqual(code, 1)
        self.assertIn("자리표시자", out)

    def test_relative_command_dir_rejected(self):
        text = body().replace("cd /Users/me/repo", "cd repo")
        self.assertIn("절대경로 `cd`", run(["-"], stdin=text)[1])

    def test_empty_verification_block_rejected(self):
        text = body().replace("Ran 3 tests ... OK", "")
        self.assertIn("검증 결과", run(["-"], stdin=text)[1])
        # 안 돌렸다는 사실은 원문 자리에 적으면 통과한다.
        self.assertEqual(run(["-"], stdin=body().replace("Ran 3 tests ... OK", "안 돌림"))[0], 0)

    def test_secret_reported_by_position_never_value(self):
        text = body().replace("포트가 점유돼", f"토큰은 {FAKE_PAT} 이고 포트가 점유돼")
        code, out, err = run(["-"], stdin=text)
        self.assertEqual(code, 1)
        self.assertIn("[glpat]", out)
        self.assertRegex(out, r"줄 \d+: 시크릿")
        self.assertNotIn(FAKE_PAT, out + err)
        self.assertNotIn("ZZZZ", out + err)

    def test_env_var_references_are_not_secrets(self):
        text = body().replace("pnpm test", 'export GITLAB_TOKEN=$(cat t)\ncurl -H "Authorization: token $FORGEJO_TOKEN" x')
        self.assertEqual(run(["-"], stdin=text)[0], 0)

    def test_pointer_form_passes(self):
        self.assertEqual(run(["-"], stdin=POINTER)[0], 0)

    def test_body_in_repo_handoff_md_rejected_when_tracker_exists(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t, "HANDOFF.md")
            p.write_text(body(), encoding="utf-8")
            code, out, _ = run([str(p), "--as-file"])
            self.assertEqual(code, 1)
            self.assertIn("포인터만", out)
            # 파일 모드(트래커 없음)는 본문이 원본이므로 통과한다.
            p.write_text(body(이슈="없음 — 이 파일이 원본"), encoding="utf-8")
            self.assertEqual(run([str(p), "--as-file"])[0], 0)

    def test_pointer_must_not_carry_body(self):
        text = POINTER + "\n## 다음에 칠 명령\n\n```bash\ncd /x\n```\n"
        code, out, _ = run(["-"], stdin=text)
        self.assertEqual(code, 1)
        self.assertIn("포인터에 본문 섹션", out)

    def test_pointer_without_url_rejected(self):
        code, out, _ = run(["-"], stdin=POINTER.replace("https://gitlab.example.com/a/b/-/issues/9", "곧 만듦"))
        self.assertEqual(code, 1)
        self.assertIn("URL", out)

    def test_file_mode_requires_explicit_marker(self):
        code, out, _ = run(["-"], stdin=body(이슈="없음"))
        self.assertEqual(code, 1)
        self.assertIn("이 파일이 원본", out)

    def test_unreadable_input_is_tool_error(self):
        code, _, err = run(["/no/such/file.md"])
        self.assertEqual(code, 2)
        self.assertIn("읽지 못했다", err)


def git(d, *a):
    return subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@e.com", *a],
                          check=True, capture_output=True, text=True).stdout.strip()


class VerifyGit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = self.tmp.name
        git(self.d, "init", "-q", "-b", "main")
        git(self.d, "commit", "-q", "--allow-empty", "-m", "one")
        git(self.d, "checkout", "-q", "-b", "work")
        git(self.d, "commit", "-q", "--allow-empty", "-m", "two")
        self.head = git(self.d, "rev-parse", "HEAD")

    def verify(self, **over):
        over.setdefault("브랜치", "`work`")
        over.setdefault("HEAD", f"`{self.head[:10]}`")
        return run(["-", "--verify-git", self.d], stdin=body(**over))

    def test_matching_branch_and_head_pass(self):
        code, out, _ = self.verify()
        self.assertEqual((code, out.strip()), (0, "위반 0건, 경고 0건"))

    def test_branch_ahead_is_warning_only(self):
        git(self.d, "commit", "-q", "--allow-empty", "-m", "three")
        code, out, _ = self.verify()
        self.assertEqual(code, 0)
        self.assertIn("1커밋 앞서", out)

    def test_diverged_head_is_violation(self):
        git(self.d, "checkout", "-q", "main")
        git(self.d, "checkout", "-q", "-b", "other")
        git(self.d, "commit", "-q", "--allow-empty", "-m", "side")
        side = git(self.d, "rev-parse", "HEAD")
        code, out, _ = self.verify(HEAD=f"`{side[:10]}`")  # work 의 조상이 아니다
        self.assertEqual(code, 1)
        self.assertIn("조상이 아니다", out)

    def test_missing_branch_and_unknown_commit(self):
        code, out, _ = self.verify(브랜치="`gone`")
        self.assertEqual(code, 1)
        self.assertIn("어디에도 없다", out)
        code, out, _ = self.verify(HEAD="`deadbeef`")
        self.assertEqual(code, 1)
        self.assertIn("커밋이 이 레포에 없다", out)

    def test_verify_does_not_change_repo(self):
        before = git(self.d, "status", "--porcelain=v1", "-b") + git(self.d, "rev-parse", "HEAD")
        self.verify()
        after = git(self.d, "status", "--porcelain=v1", "-b") + git(self.d, "rev-parse", "HEAD")
        self.assertEqual(before, after)

    def test_not_a_git_repo_is_tool_error(self):
        with tempfile.TemporaryDirectory() as t:
            code, _, err = run(["-", "--verify-git", t], stdin=body())
        self.assertEqual(code, 2)
        self.assertIn("git 대조를 하지 못했다", err)


if __name__ == "__main__":
    unittest.main()
