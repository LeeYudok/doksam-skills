#!/usr/bin/env python3
"""스킬 완성도를 채점해 README 표를 만든다 (stdlib only, 이슈 #191).

    python3 scripts/score_skills.py           # 표를 출력한다
    python3 scripts/score_skills.py --write   # README 의 생성 구간을 갱신한다
    python3 scripts/score_skills.py --check   # README 가 최신이 아니면 exit 1

항목 (100점)
    A 계약 20      description 길이 적정 · 다른 스킬과의 경계 · 완료 조건 절 · 하지 않는 것 (각 5)
    B 자동 검증 20  scripts/ 의 검사 스크립트 1개당 7 (최대 20)
    C 테스트 20     tests/ 의 def test_ 개수: 0 / <10:8 / <30:14 / <100:18 / 그 이상 20
    D 런타임 10     어댑터 4종이 있으면 10, README 에 이유를 적고 일부러 뺐으면 8, 그 밖 3
    E 근거 10       SKILL.md 의 Learned warnings(2) · 이슈 번호(최대 4) · 실측 날짜(최대 3)
    F 문서 품질 10  글 검사기 오류 1건당 -3, 긴 문장 경고 3건당 -1
    G 유니크 10     docs/maturity/external-overlap.json 에 비슷한 외부 스킬이 있으면 5

스킬 이름은 여기에 적지 않는다(tests/test_skill_layout.py). 이름이 필요한 데이터는
README 와 docs/maturity/ 에서 읽는다. 테스트 수는 실행하지 않고 정적으로 센다 —
실행해서 세면 Chrome 유무 같은 환경에 따라 숫자가 달라져 --check 가 흔들린다.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
OVERLAP = ROOT / "docs" / "maturity" / "external-overlap.json"
BEGIN, END = "<!-- BEGIN GENERATED: maturity -->", "<!-- END GENERATED: maturity -->"


def no_adapter_by_design() -> set[str]:
    """README '에이전트를 두지 않는 이유' 표의 스킬 이름."""
    text = README.read_text(encoding="utf-8")
    m = re.search(r"\| 스킬 \| 에이전트를 두지 않는 이유 \|\n\|[-| ]+\|\n((?:\|.*\n)+)", text)
    return {row.split("|")[1].strip() for row in m.group(1).splitlines()} if m else set()


def writing_checker() -> Path | None:
    found = sorted(ROOT.glob("skills/*/scripts/check_writing.py"))
    return found[0] if found else None


def score(skill: Path, overlap: dict, by_design: set, checker: Path | None) -> dict:
    s = (skill / "SKILL.md").read_text(encoding="utf-8")
    desc = re.search(r"^description: (.*)$", s, re.M).group(1)
    scripts = [p for p in (skill / "scripts").glob("*") if p.is_file()] if (skill / "scripts").is_dir() else []
    tests = sum(len(re.findall(r"^\s*def test_", p.read_text(encoding="utf-8"), re.M))
                for p in skill.glob("tests/test_*.py"))
    adapters = len(list((skill / "agents").glob("*"))) if (skill / "agents").is_dir() else 0
    learned = len(re.findall(r"^- \(\d{4}-\d{2}-\d{2}\)", s, re.M))
    issues = len(set(re.findall(r"#\d{2,3}\b", s)))
    dated = len(re.findall(r"20\d\d-\d\d-\d\d", s))
    errors = warnings = 0
    if checker:
        out = subprocess.run([sys.executable, str(checker), str(skill / "SKILL.md")],
                             capture_output=True, text=True).stdout.strip().splitlines()[-1]
        errors, warnings = map(int, re.findall(r"(\d+)건", out))

    a = ((5 if 60 <= len(desc) <= 600 else 2)
         + (5 if re.search(r"yd-[a-z-]+ ?(를|을|는|가|에|로)|쓴다", desc) else 0)
         + (5 if re.search(r"^#+ .*(완료 조건|Definition of Done|판정|검증)", s, re.M) else 0)
         + (5 if re.search(r"하지 않는|맡지 않|범위 밖|경계", s) else 0))
    b = min(20, len(scripts) * 7)
    c = 0 if tests == 0 else 8 if tests < 10 else 14 if tests < 30 else 18 if tests < 100 else 20
    d = 10 if adapters == 4 else 8 if skill.name in by_design else 3
    e = min(10, learned * 2 + min(issues, 4) + min(dated, 3))
    f = max(0, 10 - errors * 3 - warnings // 3)
    g = 5 if skill.name in overlap else 10
    return {"name": skill.name, "total": a + b + c + d + e + f + g,
            "cols": [a, b, c, d, e, f, g],
            "facts": f"{s.count(chr(10))}줄 · 스크립트 {len(scripts)} · 테스트 {tests} · 검사기 오류 {errors}/경고 {warnings}",
            "overlap": overlap.get(skill.name, "")}


def table() -> str:
    overlap = {k: v for k, v in json.loads(OVERLAP.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    by_design, checker = no_adapter_by_design(), writing_checker()
    rows = [score(p.parent, overlap, by_design, checker) for p in sorted(ROOT.glob("skills/*/SKILL.md"))]
    rows.sort(key=lambda r: (-r["total"], r["name"]))
    out = ["| 순위 | 스킬 | 총점 | 계약 | 검증 | 테스트 | 런타임 | 근거 | 문서 | 유니크 | 실측 |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        cols = " | ".join(str(c) for c in r["cols"])
        out.append(f"| {i} | {r['name']} | **{r['total']}** | {cols} | {r['facts']} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="스킬 완성도 채점")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="README 생성 구간을 갱신한다")
    mode.add_argument("--check", action="store_true", help="README 가 최신인지 검사한다")
    args = ap.parse_args(argv)

    block = f"{BEGIN}\n{table()}\n{END}"
    if not (args.write or args.check):
        print(block)
        return 0
    text = README.read_text(encoding="utf-8")
    m = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), text, re.S)
    if not m:
        print(f"README 에 {BEGIN} 구간이 없다", file=sys.stderr)
        return 1
    if args.check:
        if m.group(0) != block:
            print("README 완성도 표가 최신이 아니다 — python3 scripts/score_skills.py --write", file=sys.stderr)
            return 1
        print("README 완성도 표 최신")
        return 0
    README.write_text(text[:m.start()] + block + text[m.end():], encoding="utf-8")
    print("README 완성도 표를 갱신했다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
