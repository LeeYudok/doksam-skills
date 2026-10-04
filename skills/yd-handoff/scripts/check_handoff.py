#!/usr/bin/env python3
"""핸드오프 본문·포인터가 SKILL.md 의 형식을 지키는지 검사한다 (stdlib only).

핸드오프는 "재개 가능한 상태" 여야 하는데, 템플릿을 덜 채우거나 시각을 ISO 8601 로 쓰거나
토큰을 본문에 남겨도 겉보기엔 멀쩡하다. 게시 전에 이 검사기를 돌린다. 형식의 원본은
SKILL.md 의 "본문"·"포인터" 템플릿이며 여기서는 그 항목이 채워졌는지만 본다.

    python3 check_handoff.py <파일 | ->                  본문(이슈·코멘트·파일 모드)
    python3 check_handoff.py HANDOFF.md --as-file         레포의 HANDOFF.md: 트래커가 있으면 포인터여야 한다
    python3 check_handoff.py <본문> --verify-git <레포>   기록한 브랜치·HEAD 를 git 과 대조한다(읽기 전용)

형식은 첫 제목으로 고른다: `# HANDOFF (포인터)` 면 포인터, 그 밖엔 본문.
시크릿은 줄 번호와 패턴 이름만 출력하고 값은 출력하지 않는다.

종료 코드: 위반이 없으면 0, 있으면 1, 입력·git 을 쓸 수 없으면 2.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TS = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$")
ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}|\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})\b")
SECTIONS = ["지금 어디까지", "검증 결과 (원문)", "실행 중인 것", "미결 판단", "다음에 칠 명령", "함정"]
FIELDS = ["이슈", "작성", "작업 이슈/PR", "브랜치", "HEAD"]
POINTER_FIELDS = ["현재 핸드오프", "작성", "요약", "전체 목록"]
PLACEHOLDER = re.compile(r"<[^<>\n]*[가-힣][^<>\n]*>|<(?:YYYY[^<>\n]*|sha|branch|path|command|URL|N|M)>")
SECRETS = [
    ("glpat", re.compile(r"glpat-[A-Za-z0-9_-]{8,}")),
    ("ghp", re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}")),
    ("github_pat", re.compile(r"github_pat_[A-Za-z0-9_]{16,}")),
    ("sk-key", re.compile(r"sk-[A-Za-z0-9]{20}")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{16,}")),
    ("url-credentials", re.compile(r"://[^/\s:@<$]+:[^/\s@<$]+@")),
    ("password/token/secret", re.compile(r"(?:password|secret|token)\s*[:=]\s*[^<$(\s`\"']", re.I)),
]


def fields(lines: list[str], names: list[str]) -> dict[str, tuple[int, str]]:
    out = {}
    for i, line in enumerate(lines, 1):
        m = re.match(r"^- (%s):\s*(.*)$" % "|".join(map(re.escape, names)), line)
        if m and m.group(1) not in out:
            out[m.group(1)] = (i, m.group(2).strip())
    return out


def sections(lines: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    cur, fence = None, False
    for line in lines:
        if line.startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def fenced(body: list[str]) -> list[list[str]]:
    blocks, cur = [], None
    for line in body:
        if line.startswith("```"):
            if cur is None:
                cur = []
            else:
                blocks.append(cur)
                cur = None
        elif cur is not None:
            cur.append(line)
    return blocks


def common(lines: list[str], errors: list[str]) -> None:
    for i, line in enumerate(lines, 1):
        for name, rx in SECRETS:
            if rx.search(line):
                errors.append(f"줄 {i}: 시크릿 모양 [{name}] — 값은 출력하지 않는다. 키 이름까지만 적는다")
        if ISO.search(line):
            errors.append(f"줄 {i}: ISO 8601 시각(T·Z·+09:00)은 쓰지 않는다 — YYYY-MM-DD HH:MM:SS.mmm")
        if PLACEHOLDER.search(line):
            errors.append(f"줄 {i}: 템플릿 자리표시자가 남아 있다")


def check_body(lines: list[str], errors: list[str]) -> dict[str, tuple[int, str]]:
    f = fields(lines, FIELDS)
    for name in FIELDS:
        if name not in f or not f[name][1]:
            errors.append(f"필드 `{name}` 이 없거나 비어 있다")
    if "작성" in f and f["작성"][1] and not TS.match(f["작성"][1]):
        errors.append(f"줄 {f['작성'][0]}: 작성 시각이 YYYY-MM-DD HH:MM:SS.mmm 형식이 아니다")
    if "이슈" in f and f["이슈"][1] and not re.match(r"https?://|없음", f["이슈"][1]):
        errors.append(f"줄 {f['이슈'][0]}: 이슈는 URL 이거나 \"없음 — 이 파일이 원본\" 이어야 한다")
    if "이슈" in f and f["이슈"][1].startswith("없음") and "이 파일이 원본" not in f["이슈"][1]:
        errors.append(f"줄 {f['이슈'][0]}: 파일 모드는 \"없음 — 이 파일이 원본\" 으로 적는다")
    if "작업 이슈/PR" in f and f["작업 이슈/PR"][1] and not re.search(r"#\d+|없음", f["작업 이슈/PR"][1]):
        errors.append(f"줄 {f['작업 이슈/PR'][0]}: 작업 이슈/PR 에 #번호 또는 없음이 필요하다")
    if "브랜치" in f and f["브랜치"][1] and not re.search(r"`[^`\s]+`|없음", f["브랜치"][1]):
        errors.append(f"줄 {f['브랜치'][0]}: 브랜치를 백틱으로 적는다")
    if "HEAD" in f and f["HEAD"][1] and not re.search(r"`[0-9a-f]{7,40}`", f["HEAD"][1]):
        errors.append(f"줄 {f['HEAD'][0]}: HEAD 는 백틱 안의 커밋 해시(7~40자리)여야 한다")
    secs = sections(lines)
    for name in SECTIONS:
        if name not in secs:
            errors.append(f"섹션 `## {name}` 이 없다")
        elif not any(l.strip() for l in secs[name]):
            errors.append(f"섹션 `## {name}` 이 비어 있다")
    if "검증 결과 (원문)" in secs:
        blocks = fenced(secs["검증 결과 (원문)"])
        if not blocks or not any(l.strip() for b in blocks for l in b):
            errors.append("`검증 결과 (원문)` 에 코드블록 원문이 없다 (안 돌렸으면 \"안 돌림\" 이라고 적는다)")
    if "다음에 칠 명령" in secs:
        cmds = [l for b in fenced(secs["다음에 칠 명령"]) for l in b]
        if not any(re.match(r"\s*cd\s+(/|~)", l) for l in cmds):
            errors.append("`다음에 칠 명령` 은 절대경로 `cd` 로 실행 디렉터리를 포함해야 한다")
    return f


def check_pointer(lines: list[str], errors: list[str]) -> None:
    f = fields(lines, POINTER_FIELDS)
    for name in POINTER_FIELDS:
        if name not in f or not f[name][1]:
            errors.append(f"포인터 필드 `{name}` 이 없거나 비어 있다")
    for name in ("현재 핸드오프", "전체 목록"):
        if name in f and f[name][1] and not re.search(r"https?://", f[name][1]):
            errors.append(f"줄 {f[name][0]}: `{name}` 는 URL 이어야 한다")
    if "작성" in f and f["작성"][1] and not TS.match(f["작성"][1]):
        errors.append(f"줄 {f['작성'][0]}: 작성 시각이 YYYY-MM-DD HH:MM:SS.mmm 형식이 아니다")
    in_fence = False
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            in_fence = not in_fence
            errors.append(f"줄 {i}: 포인터에 코드블록을 두지 않는다 — 본문은 이슈에 있다")
        elif line.startswith("## "):
            errors.append(f"줄 {i}: 포인터에 본문 섹션(`{line.strip()}`)을 두지 않는다 — 본문은 이슈에 있다")
    if sum(1 for l in lines if l.strip()) > 15:
        errors.append("포인터가 15줄을 넘는다 — URL·시각·요약·목록 링크만 남긴다")


def git(repo: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr.strip().splitlines() or ["git 실패"])[-1])
    return r.stdout.strip()


def git_ok(repo: str, *args: str) -> bool:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True).returncode == 0


def verify_git(f: dict, repo: str, errors: list[str], warnings: list[str]) -> None:
    git(repo, "rev-parse", "--git-dir")  # 레포가 아니면 RuntimeError → 도구 오류
    bm = re.search(r"`([^`\s]+)`", f.get("브랜치", (0, ""))[1])
    hm = re.search(r"`([0-9a-f]{7,40})`", f.get("HEAD", (0, ""))[1])
    if not bm or not hm:
        errors.append("--verify-git: 브랜치·HEAD 를 본문에서 읽지 못했다")
        return
    branch, sha = bm.group(1), hm.group(1)
    if not git_ok(repo, "cat-file", "-e", f"{sha}^{{commit}}"):
        errors.append(f"기록한 HEAD {sha} 커밋이 이 레포에 없다")
        return
    tip = next((git(repo, "rev-parse", ref) for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}")
                if git_ok(repo, "rev-parse", "--verify", "-q", ref)), None)
    if tip is None:
        errors.append(f"기록한 브랜치 {branch} 가 로컬·origin 어디에도 없다")
        return
    if tip.startswith(sha):
        return
    if git_ok(repo, "merge-base", "--is-ancestor", sha, tip):
        n = git(repo, "rev-list", "--count", f"{sha}..{tip}")
        warnings.append(f"브랜치 {branch} 가 기록한 HEAD 보다 {n}커밋 앞서 있다 — 기록이 낡았다")
    else:
        errors.append(f"기록한 HEAD {sha} 가 브랜치 {branch} 의 조상이 아니다 (되감겼거나 갈라졌다)")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", help="검사할 파일, - 는 stdin")
    ap.add_argument("--as-file", action="store_true", help="레포의 HANDOFF.md 로 본다")
    ap.add_argument("--verify-git", metavar="REPO")
    args = ap.parse_args(argv)
    try:
        text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"오류: 입력을 읽지 못했다 ({e})", file=sys.stderr)
        return 2
    lines = text.splitlines()
    errors: list[str] = []
    warnings: list[str] = []
    first = next((l for l in lines if l.strip()), "")
    if not text.strip():
        errors.append("내용이 비어 있다")
    elif first.startswith("# HANDOFF (포인터)"):
        check_pointer(lines, errors)
        common(lines, errors)
        f = {}
    else:
        if not re.match(r"#{1,2} (HANDOFF — |착수 메모 — )", first):
            errors.append("첫 제목이 `# HANDOFF — <요약>` 또는 `## 착수 메모 — <날짜>` 가 아니다")
        f = check_body(lines, errors)
        common(lines, errors)
        if args.as_file and f.get("이슈", (0, ""))[1].startswith("http"):
            errors.append("트래커 이슈가 있는데 HANDOFF.md 에 본문이 있다 — 인프라가 있으면 포인터만 둔다")
    if args.verify_git:
        try:
            verify_git(f, args.verify_git, errors, warnings)
        except (RuntimeError, OSError) as e:
            print(f"오류: git 대조를 하지 못했다 ({e})", file=sys.stderr)
            return 2
    for e in errors:
        print(f"위반: {e}")
    for w in warnings:
        print(f"경고: {w}")
    print(f"위반 {len(errors)}건, 경고 {len(warnings)}건")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
