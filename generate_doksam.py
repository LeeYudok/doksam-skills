#!/usr/bin/env python3
"""예시 스토리보드 생성 + 클래스 계약 검증.

skills/mobile-web-planner/resources/template.html 이 CSS 클래스의 유일한
정의처다. 이 스크립트는 예시 산출물을 재생성하면서, 생성된 HTML 이 정의되지
않은 클래스를 쓰고 있으면 exit 1 로 막는다.

stdlib 만 사용한다 (이 환경의 Homebrew Python 3.14 는 외부 라이브러리
import 가 깨져 있다).

사용법:
    python3 generate_doksam.py

불변식:
    실행 후 `git diff --exit-code examples/` 가 clean 해야 한다.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = REPO_ROOT / "skills" / "mobile-web-planner" / "resources" / "template.html"
OUTPUT_PATH = REPO_ROOT / "examples" / "doksam_news_storyboard.html"

#: CSS 정의가 없어도 되는 클래스. mermaid.js 가 런타임에 렌더한다.
WHITELIST = frozenset({"mermaid"})

PROJECT_NAME = "덕삼뉴스"
VERSION = "1.0.0"
DOC_DATE = "2026.07.25"
DOC_AUTHOR = "모바일웹 기획 에이전트"


def extract_style(template_html: str) -> str:
    """<style> 블록 내부 CSS 를 반환한다."""
    match = re.search(r"<style>(.*?)</style>", template_html, re.DOTALL)
    if match is None:
        raise ValueError("template 에 <style> 블록이 없다")
    return match.group(1)


def defined_classes(css: str) -> set[str]:
    """CSS 셀렉터에 등장하는 클래스명 집합을 반환한다.

    선언 블록({...})과 세미콜론으로 끝나는 at-rule(@import, @charset)을
    먼저 제거한 뒤 남은 셀렉터에서만 .name 을 찾는다. 선언 값의 소수점
    (0.5)이나 @import URL 의 확장자(.css)를 클래스로 오인하지 않는다.
    """
    selectors = re.sub(r"\{[^{}]*\}", " ", css)
    selectors = re.sub(r"@[\w-]+[^;{}]*;", " ", selectors)
    return set(re.findall(r"\.(-?[A-Za-z_][A-Za-z0-9_-]*)", selectors))


def used_classes(html: str) -> set[str]:
    """class 속성에 등장하는 클래스명 집합을 반환한다."""
    names: set[str] = set()
    for value in re.findall(r'class="([^"]*)"', html):
        names.update(value.split())
    return names


def undefined_classes(html: str, css: str) -> list[str]:
    """정의되지 않은 채 사용된 클래스명을 정렬해 반환한다."""
    return sorted(used_classes(html) - defined_classes(css) - WHITELIST)


ICON_MAGNIFYING_GLASS = (
    '<svg class="icon" viewBox="0 0 256 256"><path d="M229.66,218.34l-50.07-50.06a88.11,'
    '88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,'
    '72.08,0,0,1,40,112Z"/></svg>'
)
ICON_BELL = (
    '<svg class="icon" viewBox="0 0 256 256"><path d="M221.8,175.94C216.25,166.38,208,139.33,'
    '208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,'
    '0,0,78.38,0H208a16,16,0,0,0,13.8-24.06ZM128,216a24,24,0,0,1-22.62-16h45.24A24,24,0,0,1,128,'
    '216ZM48,184c7.7-13.24,16-43.92,16-80a64,64,0,1,1,128,0c0,36.05,8.28,66.73,16,80Z"/></svg>'
)
ICON_LINK = (
    '<svg class="icon" viewBox="0 0 256 256"><path d="M240,88.23a54.43,54.43,0,0,1-16,37L189.25,'
    '160a54.27,54.27,0,0,1-38.63,16h-.05A54.63,54.63,0,0,1,96,119.84a8,8,0,0,1,16,.45A38.62,'
    '38.62,0,0,0,150.58,160h0a38.39,38.39,0,0,0,27.31-11.31l34.75-34.75a38.63,38.63,0,0,0-54.63'
    '-54.63l-11,11A8,8,0,0,1,135.7,59l11-11A54.65,54.65,0,0,1,224,48,54.86,54.86,0,0,1,240,'
    '88.23ZM109,185.66l-11,11A38.41,38.41,0,0,1,70.6,208h0a38.63,38.63,0,0,1-27.29-65.94L78,'
    '107.31A38.63,38.63,0,0,1,144,135.71a8,8,0,0,0,16,.45A54.86,54.86,0,0,0,144,96a54.65,54.65,'
    '0,0,0-77.27,0L32,130.75A54.62,54.62,0,0,0,70.56,224h0a54.28,54.28,0,0,0,38.64-16l11-11A8,8,'
    '0,0,0,109,185.66Z"/></svg>'
)
ICON_STAR = (
    '<svg class="icon" viewBox="0 0 256 256"><path d="M239.18,97.26A16.38,16.38,0,0,0,224.92,'
    '86l-59-4.76L143.14,26.15a16.36,16.36,0,0,0-30.27,0L90.11,81.23,31.08,86a16.46,16.46,0,0,0'
    '-9.37,28.86l45,38.83L53,211.75a16.38,16.38,0,0,0,24.5,17.82L128,198.49l50.53,31.08A16.4,'
    '16.4,0,0,0,203,211.75l-13.76-58.07,45-38.83A16.43,16.43,0,0,0,239.18,97.26Zm-15.34,5.47-48.7,'
    '42a8,8,0,0,0-2.56,7.91l14.88,62.8a.37.37,0,0,1-.17.48c-.18.14-.23.11-.38,0l-54.72-33.65a8,8,'
    '0,0,0-8.38,0L69.09,215.94c-.15.09-.19.12-.38,0a.37.37,0,0,1-.17-.48l14.88-62.8a8,8,0,0,0'
    '-2.56-7.91l-48.7-42c-.12-.1-.23-.19-.13-.5s.18-.27.33-.29l63.92-5.16A8,8,0,0,0,103,91.86l24.62'
    '-59.61c.08-.17.11-.25.35-.25s.27.08.35.25L153,91.86a8,8,0,0,0,6.75,4.92l63.92,5.16c.15,0,.24,'
    '0,.33.29S224,102.63,223.84,102.73Z"/></svg>'
)

TH = 'style="padding:12px; border:1px solid #ddd;"'
TD = 'style="padding:12px; border:1px solid #ddd;"'


def _slide(no: str, title: str, body: str, location: str = "", screen_id: str = "") -> str:
    """슬라이드 1장을 조립한다.

    body 는 ppt-content 내부 마크업. location 을 주면 상단 바 아래에
    메타 줄(화면 위치)을 넣는다 — 화면 상세(06.x) 에만 해당한다.
    """
    meta = ""
    if location:
        sid = f'\n      <div class="ppt-meta-id">{screen_id}</div>' if screen_id else ""
        meta = (f'\n    <div class="ppt-meta-bar">'
                f'\n      <div class="ppt-meta-label">Location</div>'
                f'\n      <div class="ppt-meta-value">{location}</div>'
                f'{sid}'
                f'\n    </div>')
    return f"""
  <div class="ppt-slide">
    <div class="ppt-top-bar">
      <div class="ppt-top-no">NO. {no}</div>
      <div class="ppt-top-title">{title}</div>
      <div class="ppt-top-proj">{PROJECT_NAME}</div>
    </div>{meta}
    <div class="ppt-content">
{body}
    </div>
    <div class="ppt-footer">
      {PROJECT_NAME} | Ver.{VERSION}
    </div>
  </div>
"""


def _cover() -> str:
    body = f"""      <div class="ppt-body-full" style="display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
        <h1 style="font-size:48px; margin-bottom:16px; color:#333;">{PROJECT_NAME} (Doksam News)</h1>
        <h2 style="font-size:24px; font-weight:400; color:#666; margin-bottom:40px;">모바일 앱 화면 기획서</h2>
        <div style="font-size:18px; color:#555; line-height:1.8;">
          <div><b>Version:</b> {VERSION}</div>
          <div><b>Date:</b> {DOC_DATE}</div>
          <div><b>Author:</b> {DOC_AUTHOR}</div>
        </div>
      </div>"""
    return _slide("01", "Cover", body)


def _history() -> str:
    body = f"""      <div class="ppt-body-full">
        <h2 style="border-bottom:2px solid var(--accent); padding-bottom:10px; margin-bottom:20px; color:#333;">개정 이력</h2>
        <table style="width:100%; border-collapse:collapse; text-align:left;">
          <tr style="background:#f4f4f4; border-bottom:2px solid #ccc;">
            <th {TH}>Version</th>
            <th {TH}>Date</th>
            <th {TH}>Author</th>
            <th {TH}>Description</th>
          </tr>
          <tr>
            <td {TD}>{VERSION}</td>
            <td {TD}>{DOC_DATE}</td>
            <td {TD}>{DOC_AUTHOR}</td>
            <td {TD}>초안 작성. PPT 스타일 16:9 슬라이드 레이아웃 적용</td>
          </tr>
        </table>
      </div>"""
    return _slide("02", "Document History", body)


def _index() -> str:
    rows = [
        ("01", "Cover", "", "문서 표지 — 서비스명, 버전, 작성일"),
        ("02", "Document History", "", "개정 이력"),
        ("03", "Index", "", "본 목차"),
        ("04", "Information Architecture", "", "화면 트리 및 정보구조"),
        ("05", "General Rule", "", "공통 규칙 — 레이아웃, 타이포, 컬러, 예외처리"),
        ("06.1", "Main Home", "DSN-MAIN-001", "메인 홈 화면 상세"),
        ("06.2", "Article Detail", "DSN-ARTICLE-001", "기사 상세 화면 상세"),
    ]
    tr = "\n".join(
        f"          <tr><td {TD}>{no}</td><td {TD}>{title}</td>"
        f"<td {TD}>{sid}</td><td {TD}>{desc}</td></tr>"
        for no, title, sid, desc in rows
    )
    body = f"""      <div class="ppt-body-full">
        <h2 style="border-bottom:2px solid var(--accent); padding-bottom:10px; margin-bottom:20px; color:#333;">목차</h2>
        <table style="width:100%; border-collapse:collapse; text-align:left;">
          <tr style="background:#f4f4f4; border-bottom:2px solid #ccc;">
            <th {TH} width="90">NO.</th>
            <th {TH} width="220">제목</th>
            <th {TH} width="180">화면 ID</th>
            <th {TH}>설명</th>
          </tr>
{tr}
        </table>
      </div>"""
    return _slide("03", "Index", body)


def _ia() -> str:
    body = """      <div class="ppt-body-full" style="display:flex; justify-content:center; align-items:center;">
        <div class="mermaid" style="font-size:18px;">
mindmap
  root((Doksam News))
    ("메인 홈 (Home)")
      ("속보 배너")
      ("카테고리 필터")
      ("뉴스 피드")
    ("기사 상세 (Detail)")
      ("본문 영역")
      ("유틸리티 액션")
        </div>
      </div>"""
    return _slide("04", "Information Architecture", body)


def _general_rule() -> str:
    body = """      <div class="ppt-body-full">
        <h2 style="border-bottom:2px solid var(--accent); padding-bottom:10px; margin-bottom:20px; color:#333;">공통 규칙</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px 40px; font-size:15px; color:#333; line-height:1.7;">
          <div>
            <h3 style="font-size:16px; color:var(--accent); margin:0 0 8px;">레이아웃 · 그리드</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>기준 해상도 360 x 640 (mdpi)</li>
              <li>좌우 안전 여백 16px 고정</li>
              <li>블록 간 수직 간격 16px</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:var(--accent); margin:0 0 8px;">타이포그래피</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>본문 14px / 행간 1.6</li>
              <li>제목 20px / 굵기 800</li>
              <li>메타 정보 11px / 색상 #888</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:var(--accent); margin:0 0 8px;">컬러</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>Primary <code>var(--accent)</code> (이 예시는 기본값 #ea580c 사용)</li>
              <li>Text <code>#111</code> / Sub <code>#888</code></li>
              <li>Divider <code>#eee</code></li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:var(--accent); margin:0 0 8px;">예외 처리</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>로딩: 카드 스켈레톤 노출</li>
              <li>네트워크 오류: 상단 배너 "오프라인 상태입니다"</li>
              <li>빈 목록: 안내 문구 + 재시도 버튼</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:var(--accent); margin:0 0 8px;">인터랙션</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>목록 최상단에서 Pull-to-refresh 지원</li>
              <li>탭 전환은 좌우 스와이프 병행</li>
              <li>터치 영역 최소 44 x 44px</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:var(--accent); margin:0 0 8px;">접근성</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>본문 폰트 크기 OS 설정 연동</li>
              <li>다크 테마 지원</li>
              <li>모든 이미지에 대체 텍스트 제공</li>
            </ul>
          </div>
        </div>
      </div>"""
    return _slide("05", "General Rule", body)


def _main_home() -> str:
    body = f"""      <div class="ppt-wireframe">
        <div class="mock">
          <div class="mock-screen">
            <div class="mock-status"></div>
            <div class="mock-header">
              <span>DOKSAM NEWS</span>
              <span style="display:flex; gap:10px; color:#555;">{ICON_MAGNIFYING_GLASS}{ICON_BELL}</span>
            </div>
            <div class="mock-body" style="position:relative;">

              <span class="pointer-badge" style="position:absolute; top:20px; left:2px; z-index:10;">1</span>
              <div style="background:var(--accent); border-radius:4px; padding:16px; margin-bottom:16px; color:var(--accent-ink);">
                <div style="font-size:10px; font-weight:800; margin-bottom:6px;">BREAKING NEWS</div>
                <div style="font-size:15px; font-weight:700;">글로벌 혁신 AI, 세상을 바꾸다</div>
              </div>

              <span class="pointer-badge" style="position:absolute; top:130px; left:2px; z-index:10;">2</span>
              <div style="display:flex; gap:16px; border-bottom:1px solid #ccc; padding-bottom:8px; margin-bottom:16px;">
                <div style="font-size:13px; font-weight:800; color:var(--accent); border-bottom:2px solid var(--accent); padding-bottom:6px;">Top Stories</div>
                <div style="font-size:13px; font-weight:500; color:#555;">World</div>
                <div style="font-size:13px; font-weight:500; color:#555;">Business</div>
              </div>

              <span class="pointer-badge" style="position:absolute; top:190px; left:2px; z-index:10;">3</span>
              <div style="display:flex; gap:12px; align-items:flex-start; padding-bottom:16px; border-bottom:1px solid #eee;">
                <div style="width:72px; height:72px; background:#ddd; border-radius:8px;"></div>
                <div style="flex:1;">
                  <div style="font-size:14px; font-weight:700; color:#333; margin-bottom:4px; line-height:1.4;">경제 지표 회복세 뚜렷...</div>
                  <div style="font-size:11px; font-weight:500; color:#888;">Business · 2h ago</div>
                </div>
              </div>
            </div>

            <div class="mock-footer">
              <div class="mock-tab active">Home</div>
              <div class="mock-tab">Discover</div>
              <div class="mock-tab">Saved</div>
              <div class="mock-tab">Profile</div>
            </div>
          </div>
        </div>
      </div>

      <div class="ppt-desc-panel">
        <div class="ppt-desc-header">Description (화면설명)</div>
        <div class="ppt-desc-body">
          <ul class="desc-list">
            <li>
              <span class="desc-num">①</span>
              <div>
                <b>긴급 속보 배너</b><br>
                가장 중요한 속보 기사를 상단에 강조 표시. 클릭 시 기사 상세로 이동 (DSN-ARTICLE-001).<br>
                <code>Banner (danger)</code>
              </div>
            </li>
            <li>
              <span class="desc-num">②</span>
              <div>
                <b>카테고리 필터</b><br>
                좌우 스와이프를 지원하는 네비게이션 탭. 탭 변경 시 피드 갱신.<br>
                <code>Tabs</code>
              </div>
            </li>
            <li>
              <span class="desc-num">③</span>
              <div>
                <b>뉴스 피드 리스트</b><br>
                좌측 썸네일 72px, 우측 타이틀 및 메타 정보(분야 · 경과 시간).<br>
                <code>List</code>
              </div>
            </li>
          </ul>
        </div>
      </div>"""
    return _slide("06.1", "Main Home", body, "홈", "DSN-MAIN-001")


def _article_detail() -> str:
    body = f"""      <div class="ppt-wireframe">
        <div class="mock">
          <div class="mock-screen" style="position:relative;">
            <div class="mock-status"></div>

            <span class="pointer-badge" style="position:absolute; top:20px; left:2px; z-index:10;">1</span>
            <div style="height:160px; background:#ddd; position:relative;">
              <div class="mock-header" style="background:transparent; border:none; position:absolute; top:0; width:100%;">
                <span style="color:#111; font-weight:800; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:4px;">&lsaquo;</span>
                <span style="color:#111; font-weight:800; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:4px;">&#8942;</span>
              </div>
            </div>

            <div class="mock-body" style="background:#fff; border-radius:16px 16px 0 0; margin-top:-16px; position:relative; z-index:2; padding:24px 16px 24px 28px;">
              <div style="font-size:12px; color:var(--accent); font-weight:800; margin-bottom:8px;">TECH</div>
              <div style="font-size:20px; font-weight:800; color:#111; line-height:1.4; margin-bottom:16px;">새로운 모바일 기획 에이전트 출시, UX/UI 패러다임 전환</div>

              <span class="pointer-badge" style="position:absolute; top:120px; left:2px; z-index:10;">2</span>
              <div style="font-size:14px; color:#333; line-height:1.6; margin-bottom:30px;">
                새롭게 출시된 모바일웹 플래너 에이전트는 기획자의 의도를 파악해 완결된 스토리보드를 구축합니다.
              </div>

              <span class="pointer-badge" style="position:absolute; bottom:20px; left:2px; z-index:10;">3</span>
              <div style="display:flex; justify-content:center; gap:16px;">
                <div style="flex:1; padding:12px 0; border:1px solid #ccc; border-radius:8px; display:flex; justify-content:center; align-items:center; gap:8px; font-size:13px; font-weight:700;">
                  {ICON_LINK} Copy Link
                </div>
                <div style="flex:1; padding:12px 0; border:1px solid var(--accent); color:var(--accent); border-radius:8px; display:flex; justify-content:center; align-items:center; gap:8px; font-size:13px; font-weight:700;">
                  {ICON_STAR} Bookmark
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="ppt-desc-panel">
        <div class="ppt-desc-header">Description (화면설명)</div>
        <div class="ppt-desc-body">
          <ul class="desc-list">
            <li>
              <span class="desc-num">①</span>
              <div>
                <b>투명 헤더 · 더보기</b><br>
                헤더 이미지 위로 오버레이되는 투명 뒤로가기 및 케밥 메뉴. 스크롤 시 배경 불투명 전환.<br>
                <code>AppBar (transparent)</code>
              </div>
            </li>
            <li>
              <span class="desc-num">②</span>
              <div>
                <b>기사 본문</b><br>
                API 로 전달받은 마크다운 또는 HTML 을 행간 1.6 으로 렌더링. 폰트 크기는 OS 설정을 따른다.
              </div>
            </li>
            <li>
              <span class="desc-num">③</span>
              <div>
                <b>유틸리티 액션</b><br>
                링크 복사 및 저장(북마크). 저장 시 하단 탭의 Saved 와 동기화된다.<br>
                <code>Button (outlined)</code>
              </div>
            </li>
          </ul>
        </div>
      </div>"""
    return _slide("06.2", "Article Detail", body, "홈 > 기사 상세", "DSN-ARTICLE-001")


def build_html(styles: str) -> str:
    """예시 스토리보드 HTML 전체를 조립한다."""
    slides = "".join(
        [
            _cover(),
            _history(),
            _index(),
            _ia(),
            _general_rule(),
            _main_home(),
            _article_detail(),
        ]
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>화면설계서 · {PROJECT_NAME} | Ver.{VERSION}</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'base',
    themeVariables: {{
      primaryColor: '#ffffff',
      primaryTextColor: '#333333',
      primaryBorderColor: '#888888',
      lineColor: '#555555',
      secondaryColor: '#f4f4f4',
      tertiaryColor: '#eeeeee'
    }}
  }});
</script>
<style>
{styles}
</style>
</head>
<body>
<div class="docwrap">
{slides}</div>
</body>
</html>
"""


def main() -> int:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    styles = extract_style(template)
    html = build_html(styles)

    missing = undefined_classes(html, styles)
    if missing:
        print(
            "정의되지 않은 CSS 클래스를 사용하고 있다 "
            f"({TEMPLATE_PATH.relative_to(REPO_ROOT)} 에 정의를 추가하거나 "
            "사용을 제거할 것):",
            file=sys.stderr,
        )
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    slide_count = html.count('class="ppt-slide"')
    print(f"생성 완료: {OUTPUT_PATH.relative_to(REPO_ROOT)} (슬라이드 {slide_count}장)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
