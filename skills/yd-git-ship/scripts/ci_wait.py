#!/usr/bin/env python3
"""Wait for the pipeline of a commit on doksam GitLab and report its result.

Usage: ci_wait.py [--agent claude|codex|agy] <ns/repo> <sha> [--timeout 3600] [--interval 30]
Run it in the background (run_in_background=true). Exit 0 = success or no
pipeline, 1 = failed/canceled, 2 = timed out.
With --agent, glab runs through glab-as.sh so the agent token from
~/workspace/.env.toml is used (needed where glab has no stored login);
without it, glab's own login is used. The token never leaves glab.
"""
import os
import argparse
import json
import subprocess
import sys
import time
import urllib.parse

DONE_OK = {"success", "skipped"}
DONE_BAD = {"failed", "canceled"}


GLAB_AS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glab-as.sh")


def api(path, agent=None):
    cmd = ["glab", "api", "--hostname", "gitlab.doksam.com", path]
    if agent:
        cmd = ["sh", GLAB_AS, agent] + cmd[1:]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("sha")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--agent", choices=["claude", "codex", "agy"])
    a = ap.parse_args()
    proj = urllib.parse.quote(a.repo, safe="")
    deadline = time.time() + a.timeout
    seen_none = 0
    while time.time() < deadline:
        pipes = api(f"projects/{proj}/pipelines?sha={a.sha}&per_page=1", a.agent)
        if not pipes:
            seen_none += 1
            if seen_none >= 4:
                print(f"no pipeline for {a.sha[:8]} (repo has no CI for this ref)")
                return 0
        else:
            p = pipes[0]
            if p["status"] in DONE_OK | DONE_BAD:
                print(f'pipeline {p["id"]} {p["status"]} {p["web_url"]}')
                return 0 if p["status"] in DONE_OK else 1
        time.sleep(a.interval)
    print(f"timeout waiting for {a.sha[:8]}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
