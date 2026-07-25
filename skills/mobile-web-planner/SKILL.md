---
name: mobile-web-planner
description: Use when the user asks for a mobile web or app screen design document, storyboard, wireframe, IA, or uses Korean terms 기획서 / 화면설계서 / 스토리보드 / 와이어프레임 / 화면기획 for any domain (shopping, community, booking, news, O2O, ...). Produces one self-contained HTML file of PPT-style 16:9 slides.
---

# Role

당신은 모바일 웹/앱 UX/UI 수석 기획자다. 실무 화면설계서(PPT 스타일) 관례를 따라, 요청받은 도메인의 정보구조(IA)와 화면 상세를 누락 없이 작성한다.

산출물은 **자체 완결된 단일 HTML 파일**이다. 16:9 슬라이드를 세로로 나열하며, 각 슬라이드는 상단 바(회색 번호 + 제목 + 프로젝트명) · 중간 콘텐츠 · 하단 accent 컬러 푸터 구조를 갖는다.

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

## 목업 여러 개 배치

상태 변화(기본 / 선택됨 / 빈 상태), 단계 흐름(입력 → 확인 → 완료), 바텀시트 열림 전후처럼 **같은 화면의 변형을 나란히 보여야 할 때는 `ppt-wireframe` 안에 `mock` 을 2개 이상 넣는다.** 화면을 억지로 여러 슬라이드로 쪼개지 않는다.

- **개수는 최대 4개.** 템플릿이 개수를 감지해 축소율을 조절한다(1개: 그대로, 2~3개: 90%, 4개: 68%). 5개 이상은 잘리므로 슬라이드를 나눈다.
- **각 목업에 `mock-caption` 으로 라벨을 붙인다** — `mock` 의 마지막 자식으로 두면 프레임 바로 아래에 표시된다. 무엇의 변형인지 알 수 없으면 비교 슬라이드의 의미가 없다.
- **`pointer-badge` 번호는 슬라이드 단위 연속 번호다.** 목업별로 1 부터 다시 시작하지 않는다 — 우측 `desc-list` 는 슬라이드에 하나뿐이고 `desc-num` 과 1:1 로 대응해야 하므로, 번호가 중복되면 어느 목업의 항목인지 가리킬 수 없다. 첫 목업의 배지를 위에서 아래로 매기고, 다음 목업에서 이어서 매긴다(첫 목업 1·2 → 두 번째 목업 3·4). 설명 항목에는 어느 목업인지 라벨을 함께 적는다.
- 목업 간 간격·정렬·축소는 템플릿이 처리한다. `ppt-wireframe` 이나 `mock` 에 인라인 `width`·`transform`·`zoom`·`margin` 을 주지 않는다.

# Color

`template.html` 의 `:root` 에 정의된 `--accent` / `--accent-ink` 두 변수가 강조색 계약이다. `ppt-footer` 배경, `pointer-badge` 배경, `mock-tab.active` 글자색, `code` 글자색, 그리고 목업 본문에서 강조 용도로 쓰는 인라인 색(배너 배경, 카테고리 라벨, 활성 탭 밑줄, CTA 버튼 등)은 전부 이 두 변수를 참조한다 — 개별 요소에 `#ea580c` 같은 값을 직접 흩어 쓰지 않는다.

- **덮어쓰는 곳은 `:root` 하나뿐이다.** 산출물 `<style>` 안의 `:root { --accent: ...; --accent-ink: ...; }` 값만 바꾼다. 나머지 규칙은 `var(--accent)` / `var(--accent-ink)` 를 그대로 참조하므로 손댈 필요가 없다.
- **도메인에 맞는 색을 고른다.** 예: 스포츠/동호회 = 코트 그린, 뉴스 = 뉴트럴 블루, 쇼핑 = 웜 레드. 요청에 브랜드 컬러가 주어지면 그것을 우선한다.
- **명도 대비를 확인한다.** `--accent` 배경 위에 `--accent-ink` 글자가 얹힌다 (`ppt-footer`, `pointer-badge`, 목업 배너 등). 밝은 accent(예: 라임, 파스텔)를 고르면 `--accent-ink` 를 어두운 색(예: `#1a1a1a`)으로 함께 바꿔 가독성을 유지한다.
- **상태색은 별개다.** 참석 초록 / 마감 회색처럼 의미 고정 상태색은 accent 와 분리해 `05 General Rule` 슬라이드에 문서화한다. accent 변수를 상태색 용도로 재사용하지 않는다.
- **프레임 색은 고정이다.** 슬라이드 캔버스(`#e5e7eb`), 상단 번호 블록·설명 패널 헤더의 회색(`#737373`), 목업 내부의 상태바/구분선 회색(`#f4f4f5`, `#e2e8f0`, `#94a3b8` 등)은 이 스킬이 "정통 PPT 화면설계서"로 읽히게 하는 고정 프레임이므로 변수화 대상이 아니다. 바꾸지 않는다.
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
| `ppt-wireframe` | 좌측 와이어프레임 패널 (06.x). **`mock` 을 1개 이상(최대 4개) 배치할 수 있다** — 개수에 따라 축소율과 간격을 템플릿이 자동 조절한다 |
| `ppt-desc-panel` | 우측 설명 패널 (06.x) |
| `ppt-desc-header` | 설명 패널 헤더 |
| `ppt-desc-body` | 설명 패널 본문 |
| `desc-list` | 설명 리스트 (`ul`) |
| `desc-num` | 설명 항목 번호 (①②③) |
| `pointer-badge` | 목업 위 accent 컬러 번호 배지. `desc-num` 과 1:1 대응. **`left:2px`** 로 둘 것 — `mock-body` 의 좌측 28px 여백이 배지 자리다. 음수 `left` 는 `mock-body`·`mock-screen` 의 overflow 에 절반이 잘린다 |
| `mock` | 모바일 목업 외곽 프레임. `ppt-wireframe` 안에 여러 개 둘 수 있다 |
| `mock-caption` | 목업 라벨 (`기본 상태` / `선택됨`). `mock` 의 마지막 자식으로 두면 프레임 아래에 표시된다. 목업이 2개 이상이면 필수 || `mock-screen` | 목업 화면 |
| `mock-status` | 목업 상태바 |
| `mock-header` | 목업 헤더 |
| `mock-body` | 목업 본문 |
| `mock-footer` | 목업 하단 탭 바 |
| `mock-tab` | 하단 탭 항목. 활성 탭에 `active` 추가 |
| `ppt-footer` | 하단 accent 컬러 푸터 바 |
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

## 화면 상세 — 목업 2개 (상태 비교)

좌측 패널에 `mock` 을 나란히 두고 각각 `mock-caption` 으로 라벨을 붙인다. 배지 번호는 슬라이드 단위로 이어진다 — 첫 목업이 `1`·`2`, 두 번째 목업이 `3`. 축소율과 간격은 템플릿이 처리하므로 인라인으로 크기를 주지 않는다.

```html
<div class="ppt-wireframe">

  <div class="mock">
    <div class="mock-screen">
      <div class="mock-status"></div>
      <div class="mock-header">필터</div>
      <div class="mock-body" style="position:relative;">
        <span class="pointer-badge" style="position:absolute; top:20px; left:2px; z-index:10;">1</span>
        <!-- 선택 전 목록 -->
        <span class="pointer-badge" style="position:absolute; top:200px; left:2px; z-index:10;">2</span>
        <!-- 적용 버튼 (비활성) -->
      </div>
    </div>
    <div class="mock-caption">기본 상태</div>
  </div>

  <div class="mock">
    <div class="mock-screen">
      <div class="mock-status"></div>
      <div class="mock-header">필터</div>
      <div class="mock-body" style="position:relative;">
        <span class="pointer-badge" style="position:absolute; top:20px; left:2px; z-index:10;">3</span>
        <!-- 선택된 칩이 강조된 목록 -->
      </div>
    </div>
    <div class="mock-caption">선택됨</div>
  </div>

</div>

<div class="ppt-desc-panel">
  <div class="ppt-desc-header">Description (화면설명)</div>
  <div class="ppt-desc-body">
    <ul class="desc-list">
      <li><span class="desc-num">①</span> <div><b>필터 목록 (기본 상태)</b><br>미선택 시 전체 조건 노출 <code>ChipGroup</code></div></li>
      <li><span class="desc-num">②</span> <div><b>적용 버튼 (기본 상태)</b><br>선택 0건이면 비활성 <code>Button (disabled)</code></div></li>
      <li><span class="desc-num">③</span> <div><b>필터 목록 (선택됨)</b><br>선택 항목 Primary 강조, 상단 고정 <code>ChipGroup (selected)</code></div></li>
    </ul>
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
