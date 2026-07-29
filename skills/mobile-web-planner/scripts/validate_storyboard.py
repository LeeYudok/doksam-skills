#!/usr/bin/env python3
"""생성된 화면설계서 HTML 이 SKILL.md 의 계약을 지켰는지 판정한다.

`SKILL.md` 의 "저장 전 자체 점검" 항목과 그 외 기계적으로 판정 가능한
계약을 그대로 잰다. 위반으로 판정하는 것과, 참고로 보고만 하는 것을 구분한다
— 화면 순서와 목업 개수는 요청 맥락을 알아야 옳고 그름이 정해지므로
수치만 보고하고 판정은 사람이 한다. 런타임(Claude Code / Codex / Antigravity)이 만든
산출물을 같은 잣대로 비교하기 위한 도구다.

화면 ID 가 정의된 산출물은 짝을 이루는 Business Rules 문서
(`<이름>_business-rules.md`)도 함께 판정한다 — 화면 ID 커버리지, 필수
헤딩(입력 검증 / 출력 규칙 / 인터랙션 / 엣지케이스), 끊어진 ID 참조.

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
    """<style> 블록과 HTML 주석을 걷어낸 마크업만 반환한다.

    템플릿 CSS 주석에는 `<div class="mock mock-partial">` 같은 사용 예시가
    들어 있다. 마크업 판정을 원문 전체에 대고 돌리면 그 예시를 실제 목업으로
    세어 오탐이 난다.

    HTML 주석도 같은 이유로 걷어낸다. 슬라이드를 `<!-- ==== NO. 09.1 홈 ==== -->`
    처럼 구분하는 것은 흔한 관례인데, 그 문자열이 슬라이드 구간 경계로 잡히면
    한 슬라이드가 둘로 쪼개진다. 쪼개진 자리에서 배지와 desc-num 이 서로 다른
    구간으로 갈리면 불일치를 놓친다(미탐).
    """
    stripped = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    return re.sub(r"<style\b[^>]*>.*?</style>", "", stripped, flags=re.S | re.I)


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


def slide_sections(html, pattern=r"[\d.]+"):
    """상단 바 앵커로 자른 (번호, 본문) 목록. 번호가 pattern 에 완전일치하는 것만.

    구간은 `ppt-top-no` 앵커로만 잡고 **바로 다음 슬라이드**에서 끊는다. 두 가지를
    동시에 막는다.

    1. 본문 텍스트나 목차 표에 등장하는 "NO. 09.1" 같은 문자열은 슬라이드가 아니다.
    2. 09.x 뒤에 다른 번호의 슬라이드가 오더라도 그 내용이 마지막 화면 상세에
       합산되지 않는다 — 09.x 가 문서 마지막이어야 한다는 암묵 전제를 없앤다.
    """
    heads = list(re.finditer(r'class="ppt-top-no">NO\.\s*([\d.]+)<', html))
    out = []
    for i, m in enumerate(heads):
        if not re.fullmatch(pattern, m.group(1)):
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(html)
        out.append((m.group(1), html[m.end():end]))
    return out


def detail_slides(html):
    """09.x 화면 상세 슬라이드의 (번호, 본문) 목록."""
    return slide_sections(html, r"09\.\d+")


def badge_desc_mismatch(html):
    """슬라이드별 pointer-badge 수와 desc-num 수가 다른 슬라이드를 반환한다."""
    bad = []
    for no, body in detail_slides(html):
        b = body.count('class="pointer-badge"')
        d = body.count('class="desc-num"')
        if b != d:
            bad.append((no, b, d))
    return bad


def screen_order(html):
    """09.x 슬라이드의 (번호, 제목) 을 등장 순서대로 반환한다."""
    return re.findall(
        r'ppt-top-no">NO\.\s*(09\.\d+)</div>\s*<div class="ppt-top-title">([^<]+)', html)


def mock_counts(html):
    """09.x 슬라이드별 mock 개수를 반환한다."""
    return [(no, body.count('class="mock"')) for no, body in detail_slides(html)]



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



def caption_mismatch(html):
    """09.x 슬라이드별 목업 수와 mock-caption 수가 다른 슬라이드를 반환한다.

    캡션은 모든 목업에 필수다 — 단일 목업 슬라이드만 캡션이 없으면 문서
    전체에서 표현이 어긋난다. 목업 프레임은 `class="mock"` 과
    `class="mock mock-partial"` 두 형태라 접두 매칭으로 센다
    (`mock-caption` 등 하이픈 파생 클래스는 매칭되지 않는다).
    """
    bad = []
    for no, body in detail_slides(html):
        mocks = len(re.findall(r'class="mock[\s"]', body))
        caps = body.count('class="mock-caption"')
        if mocks != caps:
            bad.append((no, mocks, caps))
    return bad


def sequence_slides(html):
    """07.x 시퀀스 슬라이드의 (번호, 본문) 목록을 반환한다."""
    return slide_sections(html, r"07\.\d+")


def check_sequence_slides(markup):
    """07.x Sequence Diagram 계약을 판정한다.

    필요한 트랜잭션이 전부 그려졌는지는 기계로 잴 수 없다(자체 점검 소관).
    기계 판정은 하한선과 형식이다 — 최소 1장 존재, 각 장에 mermaid
    `sequenceDiagram` 과 관련 화면 ID. ID 정합은 기존 끊어진 참조 판정이
    함께 잡는다.
    """
    violations = []
    seqs = sequence_slides(markup)
    if not seqs:
        violations.append(
            "07.x Sequence Diagram 슬라이드 없음 — 상태 변경 트랜잭션당 1장을 그릴 것")
    for no, body in seqs:
        if 'class="mermaid"' not in body or "sequenceDiagram" not in body:
            violations.append(f"{no} 에 mermaid sequenceDiagram 이 없다")
        elif not re.findall(ID_RE, body):
            violations.append(
                f"{no} 시퀀스에 화면 ID 가 없다 — participant 라벨이나 note 에 적을 것")
    return violations


SCREEN_TYPES = ("바텀시트", "팝업", "화면")


def detail_defined_ids(html):
    """09.x 슬라이드 안에서 정의된 화면 ID 집합 (ppt-meta-id · mock-caption)."""
    ids = set()
    for _no, body in detail_slides(html):
        for raw in re.findall(r'class="ppt-meta-id">([^<]+)<', body):
            ids.update(re.findall(ID_RE, raw))
        for raw in re.findall(r'class="mock-caption">([^<]*)<', body):
            ids.update(re.findall(ID_RE, raw))
    return ids


def row_cells(row):
    """표 행의 셀 텍스트 목록. 태그를 걷어내고 공백을 정리한다."""
    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip() for c in cells]


def row_screen_type(row):
    """행의 유형(화면/팝업/바텀시트)을 반환한다. 판정 불가면 None.

    우선 **유형만 담은 셀**을 찾는다 — 셀 값이 유형 단어와 정확히 같아야 한다.
    그런 셀이 없으면 행 텍스트 매칭으로 되돌아가되, `화면` 은 다른 두 유형의
    설명 문구에도 흔히 섞이므로 마지막에 본다.
    """
    for cell in row_cells(row):
        if cell in SCREEN_TYPES:
            return cell
    return next((k for k in SCREEN_TYPES if k in row), None)


def check_screen_list_types(markup):
    """05 Screen List 의 유형 표기·정합을 판정한다.

    모든 행에 유형(화면/팝업/바텀시트)이 있어야 하고, 유형이 `화면` 인 ID 는
    09.x 슬라이드에 정의돼 있어야 한다 — 목록에만 있고 그려지지 않은 화면은
    구현 단계에서 범위를 즉석 결정하게 만든다(실구현 회고, 이슈 #41).
    유형은 **유형 열의 셀 값**으로 판정한다. 행 전체를 키워드 매칭하면
    "주요 내용" 칸의 설명 문구("화면 일부를 덮는 팝업" 등)에 걸려 오판한다.
    열 순서를 SKILL.md 와 다르게 쓴 문서를 위해, 유형만 담은 셀을 못 찾으면
    행 텍스트 매칭으로 되돌아간다 — 그때는 `바텀시트`·`팝업` 을 먼저 본다.
    """
    body = slide_body(markup, "05")
    if body is None:
        return []  # 슬라이드 존재 위반은 check_overview_slides 가 잰다
    violations = []
    detail_ids = detail_defined_ids(markup)
    untyped, undrawn = [], []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        ids = re.findall(ID_RE, row)
        if not ids:
            continue  # 헤더 행
        kind = row_screen_type(row)
        if kind is None:
            untyped += ids
        elif kind == "화면":
            undrawn += [i for i in ids if i not in detail_ids]
    if untyped:
        violations.append(
            f"05 Screen List 에 유형(화면/팝업/바텀시트) 표기 없는 행: {', '.join(untyped)}")
    if undrawn:
        violations.append(
            f"05 Screen List 유형이 '화면' 인데 09.x 에 정의되지 않은 ID: {', '.join(sorted(set(undrawn)))}")
    return violations


EVENT_LABELS = ("탭:", "스와이프:", "롱프레스:", "입력:")


def event_coverage(html):
    """09.x 슬라이드별 (번호, 이벤트 표기 항목 수, 전체 설명 항목 수).

    설명 항목(<li>)에 고정 이벤트 라벨(탭:/스와이프:/롱프레스:/입력:)이
    있는지 센다. 터치 요소가 있는 화면 상세에 이벤트 표기가 하나도 없으면
    동작 정의가 통째로 빠진 것이다 (이슈 #43).
    """
    out = []
    for no, body in detail_slides(html):
        items = re.findall(r"<li\b.*?</li>", body, re.S)
        ev = sum(1 for it in items if any(lb in it for lb in EVENT_LABELS))
        out.append((no, ev, len(items)))
    return out


def slide_body(html, number):
    """지정한 NO. 슬라이드의 본문을 반환한다. 없으면 None.

    `05` 처럼 점 없는 번호를 찾을 때 `05.1` 같은 하위 번호와 헷갈리지
    않도록 번호 전체를 정확히 비교한다.
    """
    heads = list(re.finditer(r'class="ppt-top-no">NO\.\s*([\d.]+)<', html))
    for i, m in enumerate(heads):
        if m.group(1) == number:
            end = heads[i + 1].start() if i + 1 < len(heads) else len(html)
            return html[m.end():end]
    return None


def check_overview_slides(markup, defined):
    """05 Screen List · 06 Service Flow 슬라이드 계약을 판정한다.

    Screen List 는 정의된 모든 화면 ID(팝업·바텀시트 포함)를 한 행씩 담는
    ID↔화면 매핑 기준표이고, Service Flow 는 정상 케이스 전체 흐름을 담는
    mermaid flowchart 다. 표·흐름도가 참조하는 ID 가 정의 집합 밖이면
    기존의 끊어진 참조 판정이 함께 잡는다.
    """
    violations = []
    screen_list = slide_body(markup, "05")
    if screen_list is None:
        violations.append(
            "05 Screen List 슬라이드 없음 — 화면 ID↔화면 매핑표를 추가할 것")
    else:
        missing = sorted(defined - set(re.findall(ID_RE, screen_list)))
        if missing:
            violations.append(
                f"05 Screen List 에 없는 화면 ID: {', '.join(missing)}")

    flow = slide_body(markup, "06")
    if flow is None:
        violations.append(
            "06 Service Flow 슬라이드 없음 — 정상 케이스 전체 흐름도를 추가할 것")
    elif 'class="mermaid"' not in flow:
        violations.append("06 Service Flow 에 mermaid 흐름도가 없다")
    elif not re.findall(ID_RE, flow):
        violations.append(
            "06 Service Flow 흐름도에 화면 ID 가 없다 — 노드 라벨에 화면명과 ID 를 함께 적을 것")
    return violations


def meta_locations(html):
    """09.x 슬라이드의 (번호, Location) 을 반환한다."""
    out = []
    for no, body in detail_slides(html):
        loc = re.search(r'class="ppt-meta-value">([^<]*)<', body)
        out.append((no, loc.group(1).strip() if loc else ""))
    return out


def badge_labels(html):
    """pointer-badge 라벨을 반환한다."""
    return re.findall(r'class="pointer-badge"[^>]*>([^<]+)<', html)


STORYBOARD_SUFFIX = "_storyboard.html"
RULES_SUFFIX = "_business-rules.md"
RULES_REQUIRED_HEADINGS = ("입력 검증", "출력 규칙", "인터랙션", "엣지케이스")


def rules_path_for(html_path):
    """산출물 HTML 과 짝을 이루는 Business Rules 문서 경로를 만든다.

    `<이름>_storyboard.html` → `<이름>_business-rules.md`. 접미사가 계약과
    다른 파일은 `<이름>.html` → `<이름>_business-rules.md` 로 유도한다.
    """
    p = Path(html_path)
    name = p.name
    if name.endswith(STORYBOARD_SUFFIX):
        stem = name[: -len(STORYBOARD_SUFFIX)]
    else:
        stem = p.stem
    return p.with_name(stem + RULES_SUFFIX)


def rules_sections(md):
    """`## <화면 ID> <이름>` 섹션을 (ID, 본문) 목록으로 반환한다.

    같은 ID 의 섹션이 여러 번 나오면 나온 만큼 목록에 들어간다 — 중복
    판정은 호출부가 한다.
    """
    heads = list(re.finditer(r"(?m)^##\s+(%s)[^\n]*$" % ID_RE, md))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(md)
        out.append((m.group(1), md[m.end():end]))
    return out


def rules_subsection_bodies(body):
    """섹션 본문을 `### 헤딩` 별로 나눠 {헤딩: 내용} 으로 반환한다."""
    heads = list(re.finditer(r"(?m)^###\s+([^\n]+)$", body))
    out = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        out[m.group(1).strip()] = body[m.end():end].strip()
    return out


#: 인터랙션 표 트리거 칸의 배지 인용. 목업 1개면 (1), 2개 이상이면 (1-2).
BADGE_CITE_RE = re.compile(r"\(\s*\d+(?:-\d+)?\s*\)")


def interaction_rows_without_badge(section_body):
    """`### 인터랙션` 표에서 트리거 칸에 배지 번호 인용이 없는 행의 트리거 텍스트.

    인용이 없으면 그 규칙이 화면의 어느 요소를 말하는지 추적할 수 없다 —
    storyboard 의 배지와 Business Rules 를 잇는 유일한 끈이다.
    표가 없거나 "해당 없음" 으로 적힌 섹션은 검사 대상이 아니다.
    """
    subs = rules_subsection_bodies(section_body)
    body = subs.get("인터랙션", "")
    if not body or body.lstrip().startswith("해당 없음"):
        return []

    bad = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        trigger = cells[0]
        # 헤더 행과 구분선 행은 건너뛴다.
        if trigger in ("트리거", "") or set(trigger) <= {"-", ":"}:
            continue
        if not BADGE_CITE_RE.search(trigger):
            bad.append(trigger)
    return bad


def check_rules(md, storyboard_ids):
    """Business Rules 문서를 판정해 (위반 목록, 정보 목록) 을 반환한다.

    storyboard_ids 는 storyboard 에 정의된 화면 ID 집합이다. SKILL.md 의
    계약 — 모든 화면 ID 가 정확히 하나의 `##` 섹션을 갖고, 각 섹션에 네
    필수 헤딩이 내용과 함께 있으며, 본문 참조 ID 가 전부 storyboard 에
    정의돼 있다 — 를 그대로 잰다.
    """
    violations, info = [], []
    sections = rules_sections(md)
    section_ids = [sid for sid, _ in sections]
    id_set = set(section_ids)

    dup = sorted({sid for sid in id_set if section_ids.count(sid) > 1})
    if dup:
        violations.append(f"Business Rules 에 중복 섹션: {', '.join(dup)}")

    missing = sorted(storyboard_ids - id_set)
    if missing:
        violations.append(
            f"Business Rules 에 섹션이 없는 화면 ID: {', '.join(missing)}")

    extra = sorted(id_set - storyboard_ids)
    if extra:
        violations.append(
            f"storyboard 에 정의되지 않은 화면 ID 섹션: {', '.join(extra)}")

    for sid, body in sections:
        subs = rules_subsection_bodies(body)
        absent = [h for h in RULES_REQUIRED_HEADINGS if h not in subs]
        if absent:
            violations.append(f"{sid} 섹션에 필수 헤딩 누락: {', '.join(absent)}")
        empty = [h for h in RULES_REQUIRED_HEADINGS
                 if h in subs and not subs[h]]
        if empty:
            violations.append(
                f"{sid} 섹션의 내용 없는 헤딩: {', '.join(empty)}"
                " — 해당 없으면 '해당 없음 — <이유>' 를 적을 것")

    for sid, body in sections:
        missing_cite = interaction_rows_without_badge(body)
        if missing_cite:
            shown = ", ".join(f'"{t}"' for t in missing_cite[:3])
            more = f" 외 {len(missing_cite) - 3}건" if len(missing_cite) > 3 else ""
            violations.append(
                f"{sid} 인터랙션 표에 배지 번호 인용이 없는 행: {shown}{more}"
                " — 트리거 칸에 (1) 또는 (1-2) 처럼 적을 것")

    body_only = re.sub(r"(?m)^##\s+[^\n]*$", "", md)
    dangling = sorted(set(re.findall(ID_RE, body_only)) - storyboard_ids)
    if dangling:
        violations.append(
            f"Business Rules 가 정의되지 않은 화면 ID 를 참조한다: "
            f"{', '.join(dangling)}")

    matrix = "있음" if re.search(r"(?m)^##\s+권한 매트릭스", md) else "없음"
    info.append(f"권한 매트릭스: {matrix} (역할 2개 이상이면 필수 — 판정은 자체 점검 소관)")
    info.append(f"Business Rules 섹션 {len(sections)}개 / {len(md):,} bytes")
    return violations, info


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

    cap = caption_mismatch(markup)
    if cap:
        detail = ", ".join(f"{no}(목업{m}/캡션{c})" for no, m, c in cap)
        violations.append(
            f"목업-캡션 불일치 — 모든 목업에 mock-caption 필수: {detail}")

    circled = re.findall(
        r'class="desc-num"[^>]*>([^<]*[\u2460-\u2473][^<]*)<', markup)
    if circled:
        violations.append(
            f"desc-num 원문자 사용 {len(circled)}건 — 배지와 같은 평문 표기(1, 1-1)로 바꿀 것")

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
    if defined:
        violations += check_overview_slides(markup, defined)
        violations += check_sequence_slides(markup)
        violations += check_screen_list_types(markup)
        cov = event_coverage(markup)
        no_event = [no for no, ev, total in cov if total and not ev]
        if no_event:
            violations.append(
                "이벤트 표기(탭:/스와이프:/롱프레스:/입력:) 없는 화면 상세: "
                + ", ".join(no_event))
        if cov:
            info.append(
                f"이벤트 표기 항목 {sum(e for _, e, _ in cov)}"
                f"/{sum(t for _, _, t in cov)}개")

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

    if defined:
        rules_file = rules_path_for(path)
        if rules_file.exists():
            r_viol, r_info = check_rules(
                rules_file.read_text(encoding="utf-8"), defined)
            violations += r_viol
            info += r_info
        else:
            violations.append(
                f"Business Rules 문서 없음: {rules_file.name}"
                " — storyboard 와 같은 디렉터리에 생성할 것")
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
