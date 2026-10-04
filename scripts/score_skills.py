#!/usr/bin/env python3
"""스킬 완성도를 채점해 README 표를 만든다 (stdlib only, 이슈 #191).

    python3 scripts/score_skills.py           # 표를 출력한다
    python3 scripts/score_skills.py --write   # README 의 생성 구간을 갱신한다
    python3 scripts/score_skills.py --check   # README 가 최신이 아니면 exit 1

항목 (100점)
    A 계약 20      description 길이 적정 · 다른 스킬과의 경계 · 완료 조건 절 · 하지 않는 것 (각 5)
    B 검증 목록 20  tests/claims.json 의 유효 항목 수: 0 / 1~2:7 / 3~5:12 / 6~9:16 / 10 이상 20
    C 검증 범위 20  유효 항목이 덮는 종류(정상·실패·경계·도구오류·오탐) 1개당 4
    D 런타임 10     어댑터 4종이 있으면 10, README 에 이유를 적고 일부러 뺐으면 8, 그 밖 3
    E 근거 10       SKILL.md 의 Learned warnings(2) · 이슈 번호(최대 4) · 실측 날짜(최대 3)
    F 문서 품질 10  글 검사기 오류 1건당 -3, 긴 문장 경고 3건당 -1
    G 유니크 10     docs/maturity/external-overlap.json 에 비슷한 외부 스킬이 있으면 5

B·C 는 파일·함수 개수가 아니라 "문서의 어떤 단언을 어떤 테스트가 검증하는가" 를 센다
(이슈 #201). 개수를 세면 의미 없는 스크립트·테스트로 점수를 올릴 수 있다. 검증 목록 형식:

    {"claims": [{"id": "LIKE-ESCAPE", "kind": "오탐",
                 "rule": "<SKILL.md 또는 references/*.md 에 그대로 있는 문장 조각>",
                 "test": "<tests/ 아래 파일>::<def test_ 이름>"}]}

유효 항목 = rule 이 문서에 그대로 있고(6자 이상, 한 줄) test 함수가 실제로 있는 항목이다.
id 와 test 는 목록 안에서 겹치지 않는다. 형식 위반은 tests/test_maturity_table.py 가 잡는다.

스킬 이름은 여기에 적지 않는다(tests/test_skill_layout.py). 이름이 필요한 데이터는
README 와 docs/maturity/ 에서 읽는다. 검증 목록은 테스트를 실행하지 않고 정적으로 확인한다 —
실행해서 세면 Chrome 유무 같은 환경에 따라 숫자가 달라져 --check 가 흔들린다.
"""

from __future__ import annotations

import argparse
import ast
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


KINDS = ("정상", "실패", "경계", "도구오류", "오탐")
ID_RE = re.compile(r"^[A-Z0-9]+(-[A-Z0-9]+)*$")


def collected_tests(path: Path) -> set[str]:
    """unittest 가 실제로 모으는 이름 — TestCase 하위 클래스 안의 test_ 메서드만.

    파일에 'def test_' 문자열이 있다는 것만으로는 부족하다. 모듈 수준 함수나 테스트
    파일이 아닌 곳의 함수는 실행되지 않는데 점수에 들어간다(PR #202 리뷰).
    클래스가 TestCase 를 상속하는지는 이름으로 판단한다 — 같은 파일 안의 다른 클래스를
    거쳐 상속하는 경우도 따라간다.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}

    def is_case(cls: ast.ClassDef, seen: frozenset = frozenset()) -> bool:
        for base in cls.bases:
            name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
            if name.endswith("TestCase"):
                return True
            if name in classes and name not in seen and is_case(classes[name], seen | {cls.name}):
                return True
        return False

    return {f.name for c in classes.values() if is_case(c)
            for f in c.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
            and f.name.startswith("test")}


def claims(skill: Path) -> tuple[list[dict], list[str]]:
    """검증 목록을 읽어 (유효 항목, 오류 메시지) 를 돌려준다. 목록이 없으면 둘 다 빈 목록."""
    path = skill / "tests" / "claims.json"
    if not path.exists():
        return [], []
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))["claims"]
    except (ValueError, KeyError, TypeError) as e:
        return [], [f"{path.relative_to(ROOT)}: 읽을 수 없다 ({e})"]
    docs = "\n".join(p.read_text(encoding="utf-8")
                     for p in [skill / "SKILL.md", *sorted(skill.glob("references/*.md"))])
    valid, errors, ids, tests = [], [], set(), set()
    for c in entries:
        where = f"{skill.name} {c.get('id', '?')}"
        rule, test = c.get("rule", ""), c.get("test", "")
        problems = []
        if not ID_RE.match(c.get("id", "")):
            problems.append("id 형식")
        if c.get("id") in ids:
            problems.append("id 중복")
        if c.get("kind") not in KINDS:
            problems.append(f"kind 는 {'/'.join(KINDS)} 중 하나")
        if len(rule) < 6 or "\n" in rule or rule != rule.strip() or rule not in docs:
            problems.append("rule 이 문서에 그대로 없다")
        file, _, name = test.partition("::")
        tfile = skill / "tests" / file
        if not (re.fullmatch(r"test_\w+\.py", file) and name.startswith("test_") and tfile.is_file()
                and name in collected_tests(tfile)):
            problems.append("unittest 가 실행하는 test 메서드가 없다")
        if test in tests:
            problems.append("test 중복")
        ids.add(c.get("id"))
        tests.add(test)
        if problems:
            errors.append(f"{where}: {', '.join(problems)}")
        else:
            valid.append(c)
    return valid, errors


def score(skill: Path, overlap: dict, by_design: set, checker: Path | None) -> dict:
    s = (skill / "SKILL.md").read_text(encoding="utf-8")
    desc = re.search(r"^description: (.*)$", s, re.M).group(1)
    scripts = [p for p in (skill / "scripts").glob("*") if p.is_file()] if (skill / "scripts").is_dir() else []
    valid, _ = claims(skill)
    kinds = {c["kind"] for c in valid}
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
    n = len(valid)
    b = 0 if n == 0 else 7 if n < 3 else 12 if n < 6 else 16 if n < 10 else 20
    c = 4 * len(kinds)
    d = 10 if adapters == 4 else 8 if skill.name in by_design else 3
    e = min(10, learned * 2 + min(issues, 4) + min(dated, 3))
    f = max(0, 10 - errors * 3 - warnings // 3)
    g = 5 if skill.name in overlap else 10
    return {"name": skill.name, "total": a + b + c + d + e + f + g,
            "cols": [a, b, c, d, e, f, g],
            "facts": f"{s.count(chr(10))}줄 · 스크립트 {len(scripts)} · 검증 {n}건/{len(kinds)}종 · 검사기 오류 {errors}/경고 {warnings}",
            "overlap": overlap.get(skill.name, "")}


def table() -> str:
    overlap = {k: v for k, v in json.loads(OVERLAP.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    by_design, checker = no_adapter_by_design(), writing_checker()
    rows = [score(p.parent, overlap, by_design, checker) for p in sorted(ROOT.glob("skills/*/SKILL.md"))]
    rows.sort(key=lambda r: (-r["total"], r["name"]))
    out = ["| 순위 | 스킬 | 총점 | 계약 | 검증 목록 | 검증 범위 | 런타임 | 근거 | 문서 | 유니크 | 실측 |",
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
