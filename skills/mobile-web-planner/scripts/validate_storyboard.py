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
    python3 scripts/validate_storyboard.py <산출물.html> [<산출물2.html> ...]

종료 코드: 위반이 하나도 없으면 0, 있으면 1.
"""
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "resources" / "template.html"
WHITELIST = frozenset({"mermaid"})


def extract_style(html):
    """첫 번째 style 블록의 CSS를 반환한다."""
    match = re.search(r"<style[^>]*>(.*?)</style>", html, re.S | re.I)
    if not match:
        raise ValueError("template.html 에 <style> 블록이 없다")
    return match.group(1)


def defined_classes(css):
    """CSS selector에 정의된 클래스 이름을 반환한다."""
    selectors = re.sub(r"\{[^{}]*\}", " ", css)
    selectors = re.sub(r"@[\w-]+[^;{}]*;", " ", selectors)
    return set(re.findall(r"\.(-?[A-Za-z_][A-Za-z0-9_-]*)", selectors))


def used_classes(html):
    """HTML class 속성에서 사용한 클래스 이름을 반환한다."""
    names = set()
    for raw in re.findall(r'class\s*=\s*"([^"]*)"', html, re.I):
        names.update(raw.split())
    return names


def undefined_classes(html, css):
    """CSS에 정의되지 않은 HTML 클래스 이름을 정렬해 반환한다."""
    return sorted(used_classes(html) - defined_classes(css) - WHITELIST)

#: 이모지 코드포인트 구간. 타이포그래피 문자(‹ ⋮ 등)는 포함하지 않는다.
EMOJI_RANGES = ((0x1F000, 0x1F2FF), (0x1F300, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF))


def markup_only(html):
    """<style> 블록을 걷어낸 마크업만 반환한다.

    템플릿 CSS 주석에는 `<div class="mock mock-partial">` 같은 사용 예시가
    들어 있다. 마크업 판정을 원문 전체에 대고 돌리면 그 예시를 실제 목업으로
    세어 오탐이 난다.
    """
    return re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.S | re.I)


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



ID_RE = r"\b[A-Z]{2,6}-[A-Z]{2,12}-\d{3}\b"


def screen_ids(html):
    """정의된 화면 ID 집합을 반환한다.

    정의 자리는 두 곳이다 — 슬라이드 대표 화면의 `ppt-meta-id`, 그리고 목업이
    2개 이상인 슬라이드에서 각 목업의 `mock-caption`. 캡션까지 정의로 세는
    이유는 `ppt-meta-id` 가 슬라이드당 한 칸뿐이어서 두 번째 목업의 화면 ID 를
    담을 자리가 없기 때문이다.
    """
    ids = set()
    for raw in re.findall(r'class="ppt-meta-id">([^<]+)<', html):
        ids.update(re.findall(ID_RE, raw))
    for raw in re.findall(r'class="mock-caption">([^<]*)<', html):
        ids.update(re.findall(ID_RE, raw))
    return ids


def referenced_ids(html):
    """본문에서 언급된 화면 ID 후보를 반환한다.

    형식은 <서비스약어>-<기능>-<3자리> 다. 정의 자리(ppt-meta-id 와
    mock-caption)는 제외하고, 설명 문장에서 참조된 것만 센다.
    """
    stripped = re.sub(r'class="ppt-meta-id">[^<]+<', 'class="ppt-meta-id"><', html)
    stripped = re.sub(r'class="mock-caption">[^<]*<', 'class="mock-caption"><', stripped)
    return set(re.findall(ID_RE, stripped))



def meta_locations(html):
    """06.x 슬라이드의 (번호, Location) 을 반환한다."""
    out = []
    for m in re.finditer(r"NO\.\s*(06\.\d+)(.*?)(?=NO\.\s*06\.|\Z)", html, re.S):
        loc = re.search(r'class="ppt-meta-value">([^<]*)<', m.group(2))
        out.append((m.group(1), loc.group(1).strip() if loc else ""))
    return out


def badge_labels(html):
    """pointer-badge 라벨을 반환한다."""
    return re.findall(r'class="pointer-badge"[^>]*>([^<]+)<', html)


def check(path, css):
    """한 산출물을 판정해 (위반 목록, 정보 목록) 을 반환한다."""
    html = Path(path).read_text(encoding="utf-8")
    markup = markup_only(html)
    violations, info = [], []

    undefined = undefined_classes(html, css)
    if undefined:
        violations.append(f"미정의 클래스 {len(undefined)}종: {', '.join(undefined)}")

    emoji = emoji_in(markup)
    if emoji:
        kinds = sorted(set(emoji))
        violations.append(f"이모지 {len(emoji)}개 / {len(kinds)}종: {''.join(kinds)}")

    lefts = badge_lefts(markup)
    off = sorted({v for v in lefts if v != 2})
    if off:
        violations.append(f"배지 left 가 2px 아닌 값 {off} (전체 {len(lefts)}개 중)")

    mism = badge_desc_mismatch(markup)
    if mism:
        detail = ", ".join(f"{no}({b}/{d})" for no, b, d in mism)
        violations.append(f"배지-desc_num 불일치: {detail}")

    if "mermaid.min.js" not in html:
        violations.append("mermaid 런타임 누락 — IA 다이어그램이 원문 텍스트로 남는다")

    if "{{" in html:
        violations.append(f"치환 안 된 플레이스홀더 {html.count('{{')}건")

    defined = screen_ids(markup)
    dangling = sorted(referenced_ids(markup) - defined)
    if defined and dangling:
        violations.append(
            f"정의되지 않은 화면 ID 를 참조한다: {', '.join(dangling)}"
        )

    nums = slide_numbers(markup)
    info.append(f"슬라이드 {len(nums)}장: {' '.join(nums)}")
    info.append(f"크기 {len(html):,} bytes / 배지 {len(lefts)}개")
    accent = re.search(r"--accent:\s*([^;]+);", html)
    info.append(f"accent {accent.group(1).strip() if accent else '변수 없음'}")

    order = screen_order(markup)
    info.append("화면 순서: " + " / ".join(f"{n} {t.strip()}" for n, t in order))
    if defined:
        info.append(f"화면 ID {len(defined)}개: {' '.join(sorted(defined))}")
    mocks = mock_counts(markup)
    multi = [f"{n}({c})" for n, c in mocks if c >= 2]
    info.append(f"목업 2개 이상 슬라이드 {len(multi)}개" + (f": {' '.join(multi)}" if multi else ""))

    locs = meta_locations(markup)
    filled = [n for n, v in locs if v]
    info.append(f"Location {len(filled)}/{len(locs)} 슬라이드"
                + (f" (미기입 {', '.join(n for n, v in locs if not v)})" if len(filled) != len(locs) else ""))

    # class 속성만 센다 — 본문 텍스트나 CSS 주석에 등장하는 같은 문자열은 목업이 아니다.
    partial = len(re.findall(r'class="[^"]*\bmock-partial\b[^"]*"', markup))
    info.append(f"부분 목업(팝업) {partial}개")

    labels = badge_labels(markup)
    two = [x for x in labels if "-" in x]
    info.append(f"2단 배지 {len(two)}/{len(labels)}개")
    return violations, info


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    css = extract_style(TEMPLATE.read_text(encoding="utf-8"))
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
