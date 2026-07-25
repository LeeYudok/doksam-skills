#!/usr/bin/env python3
"""생성된 화면설계서 HTML 이 SKILL.md 의 계약을 지켰는지 판정한다.

`SKILL.md` 의 "저장 전 자체 점검" 항목과 그 외 기계적으로 판정 가능한
계약을 그대로 잰다. 위반으로 판정하는 것과, 참고로 보고만 하는 것을 구분한다
— 화면 순서와 목업 개수는 요청 맥락을 알아야 옳고 그름이 정해지므로
수치만 보고하고 판정은 사람이 한다. 런타임(Claude Code / Codex / Antigravity)이 만든
산출물을 같은 잣대로 비교하기 위한 도구다.

stdlib 만 사용한다 (이 환경의 Homebrew Python 3.14 는 외부 라이브러리
import 가 깨져 있다).

사용법:
    python3 scripts/check_output.py <산출물.html> [<산출물2.html> ...]

종료 코드: 위반이 하나도 없으면 0, 있으면 1.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import generate_doksam as gd  # noqa: E402  (경로 주입 후 import)

TEMPLATE = REPO_ROOT / "skills" / "mobile-web-planner" / "resources" / "template.html"

#: 이모지 코드포인트 구간. 타이포그래피 문자(‹ ⋮ 등)는 포함하지 않는다.
EMOJI_RANGES = ((0x1F000, 0x1F2FF), (0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF))


def emoji_in(text):
    """텍스트에 등장하는 이모지를 원문 순서대로 반환한다."""
    return [c for c in text if any(lo <= ord(c) <= hi for lo, hi in EMOJI_RANGES)]


def slide_numbers(html):
    """상단 바의 NO. 값을 등장 순서대로 반환한다."""
    return re.findall(r'class="ppt-top-no">NO\.\s*([\d.]+)<', html)


def badge_lefts(html):
    """pointer-badge 의 인라인 left 값(px)을 반환한다."""
    lefts = []
    for style in re.findall(r'class="pointer-badge"[^>]*style="([^"]*)"', html):
        m = re.search(r"left:\s*(-?\d+)px", style)
        if m:
            lefts.append(int(m.group(1)))
    return lefts


def badge_desc_mismatch(html):
    """슬라이드별 pointer-badge 수와 desc-num 수가 다른 슬라이드를 반환한다."""
    bad = []
    for m in re.finditer(r"NO\.\s*(06\.\d+)(.*?)(?=NO\.\s*06\.|\Z)", html, re.S):
        body = m.group(2)
        b = body.count('class="pointer-badge"')
        d = body.count('class="desc-num"')
        if b != d:
            bad.append((m.group(1), b, d))
    return bad


def screen_order(html):
    """06.x 슬라이드의 (번호, 제목) 을 등장 순서대로 반환한다."""
    return re.findall(
        r'ppt-top-no">NO\.\s*(06\.\d+)</div>\s*<div class="ppt-top-title">([^<]+)', html)


def mock_counts(html):
    """06.x 슬라이드별 mock 개수를 반환한다."""
    out = []
    for m in re.finditer(r"NO\.\s*(06\.\d+)(.*?)(?=NO\.\s*06\.|\Z)", html, re.S):
        out.append((m.group(1), m.group(2).count('class="mock"')))
    return out



def screen_ids(html):
    """ppt-meta-id 로 정의된 화면 ID 집합을 반환한다."""
    return set(re.findall(r'class="ppt-meta-id">([^<]+)<', html))


def referenced_ids(html):
    """본문에서 언급된 화면 ID 후보를 반환한다.

    형식은 <서비스약어>-<기능>-<3자리> 다. ppt-meta-id 안의 정의 자리는
    제외하고, 설명 문장에서 참조된 것만 센다.
    """
    stripped = re.sub(r'class="ppt-meta-id">[^<]+<', 'class="ppt-meta-id"><', html)
    return set(re.findall(r"\b([A-Z]{2,6}-[A-Z]{2,12}-\d{3})\b", stripped))


def check(path, css):
    """한 산출물을 판정해 (위반 목록, 정보 목록) 을 반환한다."""
    html = Path(path).read_text(encoding="utf-8")
    violations, info = [], []

    undefined = gd.undefined_classes(html, css)
    if undefined:
        violations.append(f"미정의 클래스 {len(undefined)}종: {', '.join(undefined)}")

    emoji = emoji_in(html)
    if emoji:
        kinds = sorted(set(emoji))
        violations.append(f"이모지 {len(emoji)}개 / {len(kinds)}종: {''.join(kinds)}")

    lefts = badge_lefts(html)
    off = sorted({v for v in lefts if v != 2})
    if off:
        violations.append(f"배지 left 가 2px 아닌 값 {off} (전체 {len(lefts)}개 중)")

    mism = badge_desc_mismatch(html)
    if mism:
        detail = ", ".join(f"{no}({b}/{d})" for no, b, d in mism)
        violations.append(f"배지-desc_num 불일치: {detail}")

    if "mermaid.min.js" not in html:
        violations.append("mermaid 런타임 누락 — IA 다이어그램이 원문 텍스트로 남는다")

    if "{{" in html:
        violations.append(f"치환 안 된 플레이스홀더 {html.count('{{')}건")

    defined = screen_ids(html)
    dangling = sorted(referenced_ids(html) - defined)
    if defined and dangling:
        violations.append(
            f"정의되지 않은 화면 ID 를 참조한다: {', '.join(dangling)}"
        )

    nums = slide_numbers(html)
    info.append(f"슬라이드 {len(nums)}장: {' '.join(nums)}")
    info.append(f"크기 {len(html):,} bytes / 배지 {len(lefts)}개")
    accent = re.search(r"--accent:\s*([^;]+);", html)
    info.append(f"accent {accent.group(1).strip() if accent else '변수 없음'}")

    order = screen_order(html)
    info.append("화면 순서: " + " / ".join(f"{n} {t.strip()}" for n, t in order))
    if defined:
        info.append(f"화면 ID {len(defined)}개: {' '.join(sorted(defined))}")
    mocks = mock_counts(html)
    multi = [f"{n}({c})" for n, c in mocks if c >= 2]
    info.append(f"목업 2개 이상 슬라이드 {len(multi)}개" + (f": {' '.join(multi)}" if multi else ""))
    return violations, info


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    css = gd.extract_style(TEMPLATE.read_text(encoding="utf-8"))
    total = 0
    for path in sys.argv[1:]:
        violations, info = check(path, css)
        total += len(violations)
        print(f"===== {path} =====")
        for line in info:
            print(f"  · {line}")
        if violations:
            for v in violations:
                print(f"  X {v}")
            print(f"  => 위반 {len(violations)}건")
        else:
            print("  => 계약 위반 없음")
        print()

    print(f"총 위반 {total}건")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
