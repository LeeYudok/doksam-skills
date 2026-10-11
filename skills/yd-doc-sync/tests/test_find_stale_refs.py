"""find_stale_refs.py 회귀 테스트 (stdlib only). 임시 git 레포에서 돌린다."""
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "find_stale_refs.py"


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def write(root, rel, body):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body), encoding="utf-8")


def commit(root, msg):
    sh(root, "git", "add", "-A")
    sh(root, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          capture_output=True, text=True).stdout.strip()


def run(root, *args):
    out = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--json", *args],
                         capture_output=True, text=True)
    return out.returncode, (json.loads(out.stdout) if out.stdout.strip().startswith("{") else out.stderr)


class FindStaleRefsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sh(self.root, "git", "init", "-q")
        write(self.root, "backend/cmd/server/main.go", "package main\n")
        write(self.root, "backend/README.md", "# backend\n")
        write(self.root, "app/web/src/index.ts", "export {}\n")
        write(self.root, "pack/config/catalog.yaml", "a: 1\n")
        write(self.root, "docs/12_specs.md", "# specs\n")
        write(self.root, "old_name.md", "# old\n")
        self.base = commit(self.root, "base")

        sh(self.root, "git", "rm", "-q", "-r", "backend")
        sh(self.root, "git", "mv", "old_name.md", "new_name.md")
        write(self.root, "AGENTS.md", """\
            # 지침
            서버는 `backend/cmd/server` 로 띄운다.
            예전 샘플 `backend/` 는 #9 에서 제거했다.
            웹 소스는 `web/src` 아래에 있다.
            카탈로그는 `config/catalog.yaml` 이다(팩 기준).
            명세는 `docs/12` 를 본다.
            안내는 [old](old_name.md) 를 본다.
            형식은 `docs/pack-vX.Y.Z` 처럼 쓴다.
            URL `https://example.com/backend/x` 는 경로가 아니다.
            """)
        write(self.root, "CHANGELOG.md", "- `backend/cmd/server` 추가\n")
        commit(self.root, "remove backend")

    def tearDown(self):
        self.tmp.cleanup()

    def refs(self, data, kind):
        return {(f["file"], f["ref"]) for f in data[kind]}

    def test_removed_since_finds_current_and_history(self):
        code, data = run(self.root, "--removed-since", self.base)
        self.assertEqual(code, 1)
        current = self.refs(data, "current")
        history = self.refs(data, "history")
        self.assertIn(("AGENTS.md", "backend/cmd/server"), current)
        self.assertIn(("AGENTS.md", "backend"), history)  # 「제거했다」 표지
        self.assertIn(("CHANGELOG.md", "backend/cmd/server"), history)  # 이력 파일

    def test_rename_reports_new_path(self):
        code, data = run(self.root, "--removed-since", self.base)
        renamed = [f for f in data["current"] if f["ref"] == "old_name.md"]
        self.assertEqual(len(renamed), 1)
        self.assertEqual(renamed[0]["reason"], "renamed -> new_name.md")

    def test_paths_existing_elsewhere_are_not_reported(self):
        _, data = run(self.root, "--removed-since", self.base)
        refs = {f["ref"] for f in data["current"] + data["history"]}
        self.assertNotIn("web/src", refs)              # app/web/src 꼬리
        self.assertNotIn("config/catalog.yaml", refs)  # pack/config 꼬리
        self.assertNotIn("docs/12", refs)              # 번호 축약
        self.assertNotIn("docs/pack-vX.Y.Z", refs)     # 자리표시자

    def test_existence_mode_and_strict(self):
        write(self.root, "README.md", "자세한 건 `docs/13_missing.md` 를 본다.\n")
        commit(self.root, "add readme")
        code, data = run(self.root)
        self.assertEqual(code, 1)
        current = {f["ref"] for f in data["current"]}
        self.assertIn("docs/13_missing.md", current)  # 첫 조각 docs/ 는 있다
        self.assertNotIn("docs/12", current)
        # 통째로 지운 최상위 폴더는 존재 검사가 아니라 --removed-since 몫이다
        self.assertNotIn("backend/cmd/server", current)
        (self.root / "README.md").write_text("ok\n", encoding="utf-8")
        clean = self.root / "AGENTS.md"
        clean.write_text("이력: 예전 `backend/` 는 #9 에서 제거했다.\n", encoding="utf-8")
        commit(self.root, "fix docs")
        (self.root / "CHANGELOG.md").write_text("ok\n", encoding="utf-8")
        commit(self.root, "drop changelog line")
        code, _ = run(self.root, "--removed-since", self.base)
        self.assertEqual(code, 0, "history 만 남으면 기본은 통과")
        code, _ = run(self.root, "--removed-since", self.base, "--strict")
        self.assertEqual(code, 1, "--strict 는 history 도 실패")

    def test_ignore_regex_and_bad_rev(self):
        _, data = run(self.root, "--removed-since", self.base, "--ignore", "띄운다")
        self.assertNotIn(("AGENTS.md", "backend/cmd/server"), self.refs(data, "current"))
        code, _ = run(self.root, "--removed-since", "no-such-rev")
        self.assertEqual(code, 2)

    def test_repo_config_history_and_exclude(self):
        write(self.root, "AGENTS.yaml", """\
            x-doc-sync:
              history:
                - AGENTS.md   # 이 레포에선 지침도 이력 취급(테스트용)
              exclude: ['notes/{a,b}/**']
            """)
        write(self.root, "notes/a/x.md", "`backend/cmd/server`\n")
        commit(self.root, "config")
        _, data = run(self.root, "--removed-since", self.base)
        files = {f["file"] for f in data["current"]}
        self.assertNotIn("AGENTS.md", files)
        self.assertIn(("AGENTS.md", "backend/cmd/server"), self.refs(data, "history"))
        self.assertNotIn("notes/a/x.md", {f["file"] for f in data["current"] + data["history"]})

    def test_repo_config_without_pyyaml(self):
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            import find_stale_refs as mod
        finally:
            sys.path.pop(0)
        write(self.root, "AGENTS.yaml", "name: x\nx-doc-sync:\n  history:\n    - CHANGELOG.md\n    - 'plans/**'\n  exclude: [data/**, \"b/*\"]\nother: 1\n")
        saved = sys.modules.get("yaml")
        sys.modules["yaml"] = None  # import yaml -> ImportError
        try:
            cfg = mod.repo_config(self.root)
        finally:
            if saved is None:
                sys.modules.pop("yaml", None)
            else:
                sys.modules["yaml"] = saved
        self.assertEqual(cfg, {"history": ["CHANGELOG.md", "plans/**"], "exclude": ["data/**", "b/*"]})
        self.assertTrue(mod.glob_match("docs/x/plans/a.md", ["docs/x/{plans,specs}/**"]))
        self.assertFalse(mod.glob_match("docs/x/other.md", ["docs/x/{plans,specs}/**"]))


if __name__ == "__main__":
    unittest.main()
