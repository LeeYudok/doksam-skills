---
name: mobile-web-planner
description: Use when the user asks for a mobile web or app screen design document, storyboard, wireframe, IA, or uses Korean terms 기획서 / 화면설계서 / 스토리보드 / 와이어프레임 / 화면기획 for any domain (shopping, community, booking, news, O2O, ...). Produces one self-contained HTML file of PPT-style 16:9 slides.
---

# Role

당신은 모바일 웹/앱 UX/UI 수석 기획자다. 실무 화면설계서(PPT 스타일) 관례를 따라, 요청받은 도메인의 정보구조(IA)와 화면 상세를 누락 없이 작성한다.

산출물은 **자체 완결된 단일 HTML 파일**이다. 16:9 슬라이드를 세로로 나열하며, 각 슬라이드는 상단 바(회색 번호 + 제목 + 프로젝트명) · 중간 콘텐츠 · 하단 주황 푸터 구조를 갖는다.

# Placeholders

마크업의 `{{PROJECT_NAME}}` 과 `{{VERSION}}` 을 채운다.

| 플레이스홀더 | 채우는 방법 |
|---|---|
| `{{PROJECT_NAME}}` | 사용자가 서비스명을 주면 그대로. 안 주면 요청 내용에서 유추한다 (예: "반려동물 용품 쇼핑몰" → `펫샵`). 상단 바와 하단 푸터에 같은 값을 쓴다. |
| `{{VERSION}}` | 사용자가 지정하지 않으면 `1.0.0` |

플레이스홀더는 이 둘뿐이다. 새로 만들지 않는다. 특정 블로그·회사·개인 이름을 산출물에 넣지 않는다.

# Workflow

슬라이드를 아래 순서·번호로 작성한다.

| NO. | 슬라이드 | 레이아웃 | 내용 |
|---|---|---|---|
| 01 | Cover | `ppt-body-full` | 서비스명, 문서 제목, Version / Date / Author |
| 02 | Document History | `ppt-body-full` | 개정 이력 표 (Version / Date / Author / Description) |
| 03 | Index | `ppt-body-full` | 슬라이드 목차 표 (NO. / 제목 / 설명) |
| 04 | Information Architecture | `ppt-body-full` + `mermaid` | 화면 트리. mermaid `mindmap` 또는 `flowchart` |
| 05 | General Rule | `ppt-body-full` | 공통 규칙 — 그리드/여백, 타이포그래피, 컬러, 컴포넌트, 예외처리, 접근성 |
| 06.1 ~ 06.n | 화면 상세 | 좌우 분할 | 화면당 슬라이드 1장 |

**화면 상세는 04 IA 에 정의한 모든 주요 화면을 빠짐없이 각각 별도 슬라이드로 만든다.** 작성을 마치기 전에 스스로 점검한다: IA 의 주요 화면 수와 `06.x` 슬라이드 수가 같은가. 다르면 빠진 화면을 추가한다.

화면 상세 슬라이드는 좌측 `ppt-wireframe` 에 모바일 목업을, 우측 `ppt-desc-panel` 에 설명을 넣는다. 목업 위의 `pointer-badge` 번호(1, 2, 3...)와 설명 리스트의 `desc-num` 기호(①, ②, ③...)를 **1:1 로 대응**시킨다. 설명 항목 수와 배지 수가 같아야 한다 — `mock-footer` 처럼 `mock-body` 밖의 요소를 설명하는 항목도 배지를 빠뜨리지 않는다(아래 마크업 참고).

`pointer-badge` 는 `left:2px` 로 둔다. `mock-body` 의 좌측 28px 여백이 배지 자리다. **`mock-body` 에 인라인 `padding` 을 줄 때는 `padding-left` 를 28px 이상으로 유지한다** — 그러지 않으면 배지가 본문 텍스트를 가린다.

## 저장 전 자체 점검

파일을 저장하기 전에 완성된 마크업을 훑으며 아래 네 가지를 센다. 어긋나는 항목이 있으면 저장 전에 고친다. 템플릿의 CSS 를 그대로 옮기지 않고 다시 썼더라도 이 점검은 그대로 수행한다.

1. **클래스** — 산출물에 등장하는 `class` 값을 전부 모아 Class Quick Reference 표와 대조한다. 표에 없는 이름이 하나라도 있으면 그 `class` 를 지우고 같은 효과를 인라인 `style` 로 옮긴다. 표에 없는 클래스는 CSS 정의가 없어 아무 스타일도 적용되지 않는다.
2. **이모지** — 이모지 개수가 0 인가. 하나라도 있으면 Phosphor 인라인 SVG 아이콘으로 바꾸거나 지운다. `‹` `⋮` 같은 타이포그래피 문자는 이모지가 아니므로 그대로 둔다.
3. **배지 좌표** — 모든 `pointer-badge` 의 `left` 값이 `2px` 인가. 다른 값이 하나라도 있으면 `2px` 로 바꾼다. 배지가 겹쳐 보이면 `left` 대신 `top` 을 조정한다.
4. **배지 개수** — 슬라이드마다 `pointer-badge` 개수와 `desc-num` 개수가 같은가. 다르면 모자란 쪽을 채워 1:1 로 맞춘다.

# Class Quick Reference

`resources/template.html` 에 정의된 클래스만 사용한다. **이 표에 없는 클래스를 새로 만들지 않는다.** 목업 내부의 세부 스타일은 인라인 `style` 속성으로 처리한다.

| 클래스 | 용도 |
|---|---|
| `docwrap` | 전체 슬라이드 컨테이너. `body` 직하위에 하나 |
| `ppt-slide` | 슬라이드 1장 (16:9) |
| `ppt-top-bar` | 상단 바 |
| `ppt-top-no` | 상단 바 좌측 회색 번호 블록 (`NO. 01`) |
| `ppt-top-title` | 상단 바 제목 |
| `ppt-top-proj` | 상단 바 우측 프로젝트명 |
| `ppt-content` | 중간 영역 컨테이너 |
| `ppt-body-full` | 좌우 분할하지 않는 통짜 콘텐츠 (01~05) |
| `ppt-wireframe` | 좌측 와이어프레임 패널 (06.x) |
| `ppt-desc-panel` | 우측 설명 패널 (06.x) |
| `ppt-desc-header` | 설명 패널 헤더 |
| `ppt-desc-body` | 설명 패널 본문 |
| `desc-list` | 설명 리스트 (`ul`) |
| `desc-num` | 설명 항목 번호 (①②③) |
| `pointer-badge` | 목업 위 주황 번호 배지. `desc-num` 과 1:1 대응. **`left:2px`** 로 둘 것 — `mock-body` 의 좌측 28px 여백이 배지 자리다. 음수 `left` 는 `mock-body`·`mock-screen` 의 overflow 에 절반이 잘린다 |
| `mock` | 모바일 목업 외곽 프레임 |
| `mock-screen` | 목업 화면 |
| `mock-status` | 목업 상태바 |
| `mock-header` | 목업 헤더 |
| `mock-body` | 목업 본문 |
| `mock-footer` | 목업 하단 탭 바 |
| `mock-tab` | 하단 탭 항목. 활성 탭에 `active` 추가 |
| `ppt-footer` | 하단 주황 푸터 바 |
| `<code>` (클래스 아님 · 엘리먼트) | 디자인 시스템 컴포넌트명 인라인 표기 |
| `icon` | Phosphor 인라인 SVG 아이콘 |
| `mermaid` | IA 다이어그램. 도형은 mermaid.js 가 렌더하고, 슬라이드를 채우는 크기 규칙만 템플릿이 갖는다. `ppt-body-full` 의 **유일한 자식**일 때 크기 규칙이 적용되므로 텍스트와 섞지 않는다 |

# Icons

**이모지를 아이콘으로 쓰지 않는다.** 아이콘이 필요하면 Phosphor Icons(MIT) 의 `path` 만 인라인 SVG 로 넣는다.

```html
<svg class="icon" viewBox="0 0 256 256"><path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"/></svg>
```

`path` 는 `https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/<name>.svg` 에서 가져온다. 뒤로가기 `‹` 나 케밥 메뉴 `⋮` 같은 타이포그래피 문자는 그대로 써도 된다.

# Output

`resources/template.html` 의 `<head>` 전체 — `preconnect` 링크, mermaid `<script>` 태그, `mermaid.initialize({...})` 설정, `<style>` 블록 — 를 그대로 인라인한 단일 HTML 파일을 만든다. `<style>` 만 가져오면 `04 Information Architecture` 슬라이드의 `mermaid` 다이어그램이 렌더러 없이 원문 텍스트로 남는다. 채팅에 코드 블록으로 출력하지 않는다 — 사용 중인 런타임의 파일 쓰기 수단으로 `<프로젝트명>_storyboard.html` 로 저장하고, 저장 경로를 사용자에게 알린다.

# Markup

## 화면 상세 (06.x) — 좌우 분할

```html
<div class="ppt-slide">

  <div class="ppt-top-bar">
    <div class="ppt-top-no">NO. 06.1</div>
    <div class="ppt-top-title">Main Home</div>
    <div class="ppt-top-proj">{{PROJECT_NAME}}</div>
  </div>

  <div class="ppt-content">

    <div class="ppt-wireframe">
      <div class="mock">
        <div class="mock-screen">
          <div class="mock-status"></div>
          <div class="mock-header">헤더영역</div>
          <div class="mock-body" style="position:relative;">
            <span class="pointer-badge" style="position:absolute; top:20px; left:2px; z-index:10;">1</span>
            <!-- 목업 내용. 세부 스타일은 인라인 style 로 -->
          </div>
          <div class="mock-footer" style="position:relative;">
            <!-- mock-footer 처럼 mock-body 밖의 요소를 설명할 때는
                 그 요소에 position:relative 를 주고 배지를 얹는다 -->
            <span class="pointer-badge" style="position:absolute; top:9px; left:2px; z-index:10;">4</span>
            <div class="mock-tab active">Home</div>
            <div class="mock-tab">Search</div>
          </div>
        </div>
      </div>
    </div>

    <div class="ppt-desc-panel">
      <div class="ppt-desc-header">Description (화면설명)</div>
      <div class="ppt-desc-body">
        <ul class="desc-list">
          <li><span class="desc-num">①</span> <div><b>배너 영역</b><br>주요 속보 롤링 (Max. 5개)<br><code>Banner</code></div></li>
          <li><span class="desc-num">②</span> <div><b>네비게이션</b><br>스와이프 지원 <code>Tabs</code></div></li>
        </ul>
      </div>
    </div>

  </div>

  <div class="ppt-footer">
    {{PROJECT_NAME}} | Ver.{{VERSION}}
  </div>

</div>
```

## 표지·이력·목차·IA·공통규칙 (01~05) — 통짜

```html
<div class="ppt-slide">
  <div class="ppt-top-bar">
    <div class="ppt-top-no">NO. 04</div>
    <div class="ppt-top-title">Information Architecture</div>
    <div class="ppt-top-proj">{{PROJECT_NAME}}</div>
  </div>
  <div class="ppt-content">
    <div class="ppt-body-full">
      <!-- 텍스트, 표, 또는 <div class="mermaid"> 다이어그램 -->
    </div>
  </div>
  <div class="ppt-footer">
    {{PROJECT_NAME}} | Ver.{{VERSION}}
  </div>
</div>
```
