"""yd-blueprint 뼈대 생성기와 검사기(check.ts)의 동작을 고정한다.

생성기 테스트는 bash 와 git 만 있으면 돌고, 검사기 테스트는 bun 이 있어야 돈다
(없으면 skip). 검사기는 node_modules 없이 돌도록 만들어져 있어 bun install 은 하지 않는다.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
NEW = SKILL / "scripts" / "new-blueprint.sh"
HAS_RUNTIME = shutil.which("bun") is not None or shutil.which("node") is not None


def sh(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)


def line(**kw):
    return json.dumps(kw, ensure_ascii=False)


META = line(kind="meta", title="t", asOf="2026-10-05")
LANE = line(kind="lane", id="front", title="프론트")
LANE2 = line(kind="lane", id="back", title="백엔드")


def node(id="a", lane="front", row=0, **extra):
    base = dict(kind="node", id=id, lane=lane, row=row, title="상자", state="done", summary="요약")
    base.update(extra)
    return line(**base)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="yd-blueprint-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        sh(["git", "init", "-q"], self.tmp)
        (self.tmp / "README.md").write_text("x\n", encoding="utf-8")

    def scaffold(self, *extra, cwd=None, env=None):
        return sh([str(NEW), "--no-install", *extra], cwd or self.tmp, env)

    @property
    def app(self):
        return self.tmp / "frontend"

    def write_data(self, *lines):
        (self.app / "data" / "blueprint.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def check(self, *args):
        return sh(["sh", "scripts/check.sh", *args], self.app)


class ScaffoldTests(Base):
    def test_scaffold_vite_base_blueprint(self):
        r = self.scaffold()
        self.assertEqual(r.returncode, 0, r.stderr)
        cfg = (self.app / "vite.config.ts").read_text(encoding="utf-8")
        self.assertIn('base: "/blueprint/"', cfg)
        self.assertNotIn("port:", cfg)  # 기본 포트를 그대로 쓴다
        pkg = json.loads((self.app / "package.json").read_text(encoding="utf-8"))
        self.assertTrue(pkg["name"].endswith("-blueprint"))
        self.assertNotIn("__NAME__", json.dumps(pkg))
        self.assertTrue((self.app / "data" / "blueprint.jsonl").is_file())

    def test_package_scripts_are_manager_neutral(self):
        self.assertEqual(self.scaffold().returncode, 0)
        pkg = json.loads((self.app / "package.json").read_text(encoding="utf-8"))
        for name, command in pkg["scripts"].items():
            for word in ("bun", "bunx", "pnpm", "npm ", "node "):
                self.assertNotIn(word, command, f"scripts.{name} 가 {word!r} 를 직접 부른다")
        self.assertEqual(pkg["scripts"]["check"], "sh scripts/check.sh")

    def test_pm_option_is_validated_and_printed(self):
        r = self.scaffold("--pm", "yarn")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("bun·pnpm·npm", r.stderr)
        r = self.scaffold("--pm", "pnpm")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pnpm run dev", r.stdout)

    def test_scaffold_pins_loopback_host(self):
        self.assertEqual(self.scaffold().returncode, 0)
        cfg = (self.app / "vite.config.ts").read_text(encoding="utf-8")
        self.assertIn('host: "127.0.0.1"', cfg)

    def test_scaffold_refuses_existing(self):
        self.assertEqual(self.scaffold().returncode, 0)
        before = (self.app / "data" / "blueprint.jsonl").read_text(encoding="utf-8")
        r = self.scaffold()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("덮어쓰지 않는다", r.stderr)
        self.assertEqual(before, (self.app / "data" / "blueprint.jsonl").read_text(encoding="utf-8"))

    def test_scaffold_dir_cannot_escape_root(self):
        r = self.scaffold("--dir", "../outside")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.tmp.parent / "outside").exists())

    def test_not_git_repo_needs_root(self):
        plain = Path(tempfile.mkdtemp(prefix="yd-blueprint-plain-"))
        self.addCleanup(shutil.rmtree, plain, ignore_errors=True)
        r = self.scaffold(cwd=plain)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--root", r.stderr)
        r = self.scaffold("--root", str(plain), cwd=plain)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_missing_bun_message(self):
        bare = {"PATH": "/usr/bin:/bin"}
        if shutil.which("bun", path=bare["PATH"]):
            self.skipTest("/usr/bin 에 bun 이 있다")
        r = sh([str(NEW)], self.tmp, env={**os.environ, **bare})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("패키지 매니저가 없다", r.stderr)
        self.assertIn("oven-sh/bun", r.stderr)
        self.assertFalse(self.app.exists())


@unittest.skipUnless(HAS_RUNTIME, "bun 또는 node 가 필요하다")
class CheckTests(Base):
    def setUp(self):
        super().setUp()
        self.assertEqual(self.scaffold().returncode, 0)

    @unittest.skipUnless(shutil.which("node"), "node 가 필요하다")
    def test_check_runs_on_node_without_bun(self):
        only_node = self.tmp / "only-node"
        only_node.mkdir()
        os.symlink(shutil.which("node"), only_node / "node")
        env = {**os.environ, "PATH": f"{only_node}:/usr/bin:/bin"}
        if shutil.which("bun", path=env["PATH"]):
            self.skipTest("/usr/bin 에 bun 이 있다")
        r = sh(["sh", "scripts/check.sh", "--stale-days", "100000"], self.app, env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[OK]", r.stdout)

    def test_check_passes_sample(self):
        r = self.check("--stale-days", "100000")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[OK]", r.stdout)

    def test_check_catches_missing_path(self):
        self.write_data(META, LANE, node(paths=["README.md", "src/nope.py"]))
        r = self.check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("없는 경로 'src/nope.py'", r.stderr)
        self.assertNotIn("README.md'", r.stderr)

    def test_no_paths_flag_skips_existence(self):
        self.write_data(META, LANE, node(paths=["src/nope.py"]))
        self.assertEqual(self.check("--no-paths").returncode, 0)

    def test_check_rejects_unknown_field(self):
        self.write_data(META, LANE, node(colour="red"))
        r = self.check("--no-paths")
        self.assertEqual(r.returncode, 1)
        self.assertIn("알 수 없는 필드 'colour'", r.stderr)

    def test_check_rejects_cell_collision(self):
        self.write_data(META, LANE, node("a"), node("b"))
        r = self.check("--no-paths")
        self.assertEqual(r.returncode, 1)
        self.assertIn("이미 노드가 있습니다", r.stderr)

    def test_check_rejects_edge_to_unknown_node(self):
        self.write_data(META, LANE, node("a"), line(kind="edge", **{"from": "a", "to": "ghost"}))
        r = self.check("--no-paths")
        self.assertEqual(r.returncode, 1)
        self.assertIn("없는 to 'ghost'", r.stderr)

    def test_check_rejects_bad_json_and_names_the_line(self):
        self.write_data(META, "{not json}", LANE)
        r = self.check("--no-paths")
        self.assertEqual(r.returncode, 1)
        self.assertIn("blueprint.jsonl:2", r.stderr)

    def test_check_rejects_impossible_date(self):
        self.write_data(line(kind="meta", title="t", asOf="2026-13-45"), LANE, node())
        r = self.check("--no-paths")
        self.assertEqual(r.returncode, 1)
        self.assertIn("asOf", r.stderr)

    def test_stale_warns_but_passes(self):
        self.write_data(line(kind="meta", title="t", asOf="2020-01-01"), LANE, node())
        r = self.check("--no-paths")
        self.assertEqual(r.returncode, 0)
        self.assertIn("[WARN] 기준일", r.stderr)

    def test_wide_title_warns_but_passes(self):
        self.write_data(META, LANE, node(title="아주아주아주 긴 상자 제목이 폭을 넘는다 정말로"))
        r = self.check("--no-paths", "--stale-days", "100000")
        self.assertEqual(r.returncode, 0)
        self.assertIn("상자 폭을 넘을 수 있습니다", r.stderr)

    def test_short_latin_title_does_not_warn(self):
        self.write_data(META, LANE, node(title="nginx 게이트 · LAN", lines=["127.0.0.1:18555 · POST 두 개"]))
        r = self.check("--no-paths", "--stale-days", "100000")
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("[WARN]", r.stderr)

    def test_links_accept_paths_and_reject_script_urls(self):
        ok = line(kind="meta", title="t", asOf="2026-10-05", links=[{"label": "감지 화면", "href": "/detect/201/"}])
        self.write_data(ok, LANE, node())
        self.assertEqual(self.check("--no-paths", "--stale-days", "100000").returncode, 0)
        bad = line(kind="meta", title="t", asOf="2026-10-05", links=[{"label": "x", "href": "javascript:alert(1)"}])
        self.write_data(bad, LANE, node())
        r = self.check("--no-paths")
        self.assertEqual(r.returncode, 1)
        self.assertIn("links", r.stderr)

    def test_blank_lines_are_ignored(self):
        self.write_data(META, "", LANE, "   ", node(), "")
        r = self.check("--no-paths", "--stale-days", "100000")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_check_without_repo_needs_flag(self):
        plain = Path(tempfile.mkdtemp(prefix="yd-blueprint-plain-"))
        self.addCleanup(shutil.rmtree, plain, ignore_errors=True)
        self.assertEqual(self.scaffold("--root", str(plain), cwd=plain).returncode, 0)
        r = sh(["sh", "scripts/check.sh"], plain / "frontend")
        self.assertEqual(r.returncode, 1)
        self.assertIn("--repo-root", r.stderr)


if __name__ == "__main__":
    unittest.main()
