# mobile-web-planner 스킬 정합성 복구 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `mobile-web-planner` 스킬의 정의·템플릿·생성 스크립트·산출물 예시를 하나의 규격으로 정합화하고, Claude Code / Codex / Antigravity 세 런타임에 배포하는 `install.sh` 를 추가한다.

**Architecture:** 세 단위로 분리한다. (1) 스킬 패키지 `skills/mobile-web-planner/` — `template.html` 이 CSS 클래스의 유일한 정의처이고 `SKILL.md` 이 생성 규약이다. (2) 검증 도구 `generate_doksam.py` — 예시를 재생성하면서 "정의되지 않은 클래스 사용" 을 기계적으로 차단한다. (3) 배포 도구 `install.sh` — 스킬 내용을 모른 채 디렉터리를 각 런타임 경로에 노출한다.

**Tech Stack:** Markdown (`SKILL.md`), HTML5 + Vanilla CSS (`template.html`), Python 3 stdlib only (`generate_doksam.py`, `unittest`), Bash (`install.sh`)

**설계 문서:** `docs/superpowers/specs/2026-07-26-skill-consistency-design.md`
**이슈:** [#3](https://github.com/leeyudok/mobile-web-planner-agent/issues/3)

## Global Constraints

- **브랜치:** `fix/issue-3-skill-consistency` (이미 생성·푸시됨). 커밋 메시지 끝에 `(#3)` 과 `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>` 를 붙인다.
- **Python:** **stdlib 만 사용한다.** 이 머신의 Homebrew Python 3.14 는 pyexpat dlopen 이 깨져 외부 라이브러리 import 가 실패한다. 실행은 `python3` 로 한다.
- **CSS:** Vanilla CSS 만. TailwindCSS 등 프레임워크 도입 금지.
- **클래스 계약:** `skills/mobile-web-planner/resources/template.html` 에 CSS 로 정의된 클래스만 사용한다. 유일한 예외는 `mermaid` (mermaid.js 가 렌더, CSS 불필요).
- **이모지 금지 범위:** `skills/**` 와 `examples/doksam_news_storyboard.html` 에는 이모지를 쓰지 않는다. 아이콘은 Phosphor Icons(MIT) 인라인 SVG. `README.md` 와 `examples/mobile_news_plan.md` 의 장식 이모지는 이번 범위 밖이므로 건드리지 않는다.
- **플레이스홀더:** `{{PROJECT_NAME}}` 과 `{{VERSION}}` 두 개만. 그 외 플레이스홀더를 새로 만들지 않는다.
- **제거 대상 문자열:** `쀼어` 는 레포 전역에서 0건이어야 한다(`docs/` 의 설계·계획 문서에 기록된 인용은 예외). `기획이야기` 는 `skills/` 와 `examples/*.html` 에서 0건.
- **슬라이드 번호 체계:** `01 Cover` / `02 Document History` / `03 Index` / `04 Information Architecture` / `05 General Rule` / `06.1`~`06.n 화면 상세`.
- **타임스탬프 표기:** 문서 내 날짜는 `YYYY-MM-DD` (또는 기존 예시 관례인 `YYYY.MM.DD`) 로 통일. ISO8601 `T` 표기 금지.
- **범위 외:** CDN 로컬 벤더링, 슬라이드 반응형 재설계, 스킬 pressure 테스트. 손대지 않는다.

---

## File Structure

| 파일 | 상태 | 책임 |
|---|---|---|
| `skills/mobile-web-planner/SKILL.md` | rename + 재작성 | 생성 규약 — 페르소나, 워크플로, 클래스 Quick Reference, 마크업 예시, 출력 방식 |
| `skills/mobile-web-planner/resources/template.html` | rename + 수정 | 렌더 계약 — CSS 클래스 정의처. `@import` 순서 수정, `preconnect` 정정, `.icon` 클래스 추가 |
| `generate_doksam.py` | 재작성 | 예시 재생성 + 클래스 계약 검증기 |
| `tests/test_generate.py` | 신규 | 검증기 단위 테스트 (stdlib `unittest`) |
| `tests/test_install.sh` | 신규 | `install.sh` 동작 테스트 (임시 HOME 격리) |
| `examples/doksam_news_storyboard.html` | 재생성 산출물 | 사람이 직접 편집하지 않는다. `generate_doksam.py` 의 출력 |
| `install.sh` | 신규 | 3개 런타임 경로에 스킬 노출 |
| `AGENTS.md` | 수정 | 에이전트 지침 — 새 구조, 검증 절차, 클래스 계약, 이모지 방침 |
| `README.md` | 수정 | 3개 런타임 설치 안내, 구조 트리 |

**Task 순서 근거:** 템플릿(계약) → 스킬 정의(계약 소비자) → 검증기(계약 강제) → 예시(검증기 산출물) → 배포 → 문서. 검증기가 예시보다 앞에 오는 이유는 예시가 검증기의 출력이기 때문이다.

---

### Task 1: 디렉터리 rename 및 template.html 계약 수정

**Files:**
- Rename: `skills/mobile_web_planner/` → `skills/mobile-web-planner/`
- Modify: `skills/mobile-web-planner/resources/template.html:1-31` (head/CSS 선두), `:236-244` (`code` 규칙 뒤에 `.icon` 추가)

**Interfaces:**
- Consumes: 없음 (첫 태스크)
- Produces: `skills/mobile-web-planner/resources/template.html` 경로. CSS 클래스 정의 집합에 `.icon` 추가. 이후 모든 태스크가 이 경로를 참조한다.

- [ ] **Step 1: 디렉터리 rename**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git mv skills/mobile_web_planner skills/mobile-web-planner
ls skills/mobile-web-planner/
```

기대 출력: `SKILL.md  resources`

- [ ] **Step 2: `@import` 를 `@font-face` 앞으로 이동하고 `preconnect` 를 정정한다**

`skills/mobile-web-planner/resources/template.html` 의 7행과 23~30행이 현재 이렇다.

```html
<link rel="preconnect" href="https://cdnjs.cloudflare.com">
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
```

```css
<style>
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Regular.woff2') format('woff2');
  font-weight: 400;
}
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
```

7행의 `<link rel="preconnect" href="https://cdnjs.cloudflare.com">` 을 아래로 교체한다. `cdnjs.cloudflare.com` 은 이 문서에서 한 번도 요청하지 않는 호스트이고, 실제 호스트는 `cdn.jsdelivr.net` 이다.

```html
<link rel="preconnect" href="https://cdn.jsdelivr.net">
```

그리고 `<style>` 선두를 아래로 교체한다. `@import` 가 `@font-face` **앞**에 와야 한다 — CSS 스펙상 `@import` 는 `@charset`/`@layer` 를 제외한 모든 규칙보다 앞에 있어야 하며, 지금은 뒤에 있어서 무시되고 있다. 그 결과 Regular 400 만 로드되어 `font-weight: 800` 지정이 전부 합성 볼드로 렌더된다.

```css
<style>
/* @import 는 @font-face 를 포함한 모든 규칙보다 앞에 있어야 유효하다 (CSS 스펙) */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@font-face {
  font-family: 'Pretendard';
  src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/woff2/Pretendard-Regular.woff2') format('woff2');
  font-weight: 400;
}
```

- [ ] **Step 3: `.icon` 클래스를 추가한다**

`template.html` 의 `code { ... }` 규칙(현재 237~244행) **뒤**, `</style>` 앞에 아래를 추가한다. 목업 안의 액션 아이콘을 이모지 대신 Phosphor 인라인 SVG 로 넣기 위한 유일한 신규 클래스다.

```css
/* Phosphor Icons (MIT) 인라인 SVG 용 — 이모지 아이콘 대체 */
.icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
  vertical-align: -2px;
  flex: none;
}
```

- [ ] **Step 4: 수정 결과를 검증한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
grep -n "@import\|@font-face\|^\* {" skills/mobile-web-planner/resources/template.html | head -4
grep -c "cdnjs.cloudflare.com" skills/mobile-web-planner/resources/template.html
grep -n "^\.icon {" skills/mobile-web-planner/resources/template.html
```

기대: `@import` 행번호 < `@font-face` 행번호 < `* {` 행번호. `cdnjs.cloudflare.com` 카운트는 `0`. `.icon {` 는 1건.

- [ ] **Step 5: 커밋**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git add skills/
git commit -m "$(cat <<'EOF'
fix: 스킬 디렉터리 하이픈 rename 및 template.html CSS 계약 수정 (#3)

- skills/mobile_web_planner -> skills/mobile-web-planner (frontmatter name 과 일치)
- @import 를 @font-face 앞으로 이동. CSS 스펙상 @import 는 다른 규칙보다
  앞에 있어야 유효하며, 기존 순서에서는 무시되어 Regular 400 만 로드되고
  font-weight 800 지정이 전부 합성 볼드로 렌더되고 있었다.
- 요청하지 않는 cdnjs.cloudflare.com preconnect 를 실제 호스트인
  cdn.jsdelivr.net 으로 정정
- 이모지 아이콘을 Phosphor 인라인 SVG 로 대체하기 위한 .icon 클래스 추가

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: SKILL.md 재작성

**Files:**
- Modify: `skills/mobile-web-planner/SKILL.md` (전체 재작성, 85행 → 약 130행)

**Interfaces:**
- Consumes: Task 1 의 `resources/template.html` 클래스 집합(`.icon` 포함)
- Produces: 슬라이드 번호 체계(`01`~`05`, `06.1`~`06.n`), 플레이스홀더 이름 `{{PROJECT_NAME}}` · `{{VERSION}}`. Task 4 의 예시가 이 체계를 따라야 한다.

- [ ] **Step 1: `SKILL.md` 를 아래 내용으로 전체 교체한다**

기존 파일의 문제를 한 번에 해소한다 — `description` 이 트리거가 아니라 기능 설명이던 점, 존재하지 않는 "캡쳐 이미지 모방" 서술, `NO.05` 다음 `NO.3.x` 번호 모순, 하드코딩 브랜딩(`덕삼이` / `덕삼뉴스 기획이야기` / `쀼어's blog 기획이야기`), 클래스 목록 부재, 채팅 코드블록 출력, 헤딩 이모지.

````markdown
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

화면 상세 슬라이드는 좌측 `ppt-wireframe` 에 모바일 목업을, 우측 `ppt-desc-panel` 에 설명을 넣는다. 목업 위의 `pointer-badge` 번호(1, 2, 3...)와 설명 리스트의 `desc-num` 기호(①, ②, ③...)를 **1:1 로 대응**시킨다.

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
| `pointer-badge` | 목업 위 주황 번호 배지. `desc-num` 과 1:1 대응 |
| `mock` | 모바일 목업 외곽 프레임 |
| `mock-screen` | 목업 화면 |
| `mock-status` | 목업 상태바 |
| `mock-header` | 목업 헤더 |
| `mock-body` | 목업 본문 |
| `mock-footer` | 목업 하단 탭 바 |
| `mock-tab` | 하단 탭 항목. 활성 탭에 `active` 추가 |
| `ppt-footer` | 하단 주황 푸터 바 |
| `code` | 디자인 시스템 컴포넌트명 인라인 표기 |
| `icon` | Phosphor 인라인 SVG 아이콘 |
| `mermaid` | IA 다이어그램. CSS 정의 없음 — mermaid.js 가 렌더 |

# Icons

**이모지를 아이콘으로 쓰지 않는다.** 아이콘이 필요하면 Phosphor Icons(MIT) 의 `path` 만 인라인 SVG 로 넣는다.

```html
<svg class="icon" viewBox="0 0 256 256"><path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"/></svg>
```

`path` 는 `https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/<name>.svg` 에서 가져온다. 뒤로가기 `‹` 나 케밥 메뉴 `⋮` 같은 타이포그래피 문자는 그대로 써도 된다.

# Output

`resources/template.html` 의 `<style>` 블록을 그대로 인라인한 단일 HTML 파일을 만든다. 채팅에 코드 블록으로 출력하지 않는다 — 사용 중인 런타임의 파일 쓰기 수단으로 `<프로젝트명>_storyboard.html` 로 저장하고, 저장 경로를 사용자에게 알린다.

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
            <span class="pointer-badge" style="position:absolute; top:20px; left:-12px; z-index:10;">1</span>
            <!-- 목업 내용. 세부 스타일은 인라인 style 로 -->
          </div>
          <div class="mock-footer">
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
````

- [ ] **Step 2: 제약 위반이 없는지 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
echo "--- 하드코딩 브랜딩 (0건 기대) ---"
grep -c "덕삼\|쀼어\|기획이야기" skills/mobile-web-planner/SKILL.md
echo "--- 이모지 (0건 기대) ---"
grep -oP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}]' skills/mobile-web-planner/SKILL.md | wc -l
echo "--- description 이 Use when 으로 시작 (1건 기대) ---"
grep -c "^description: Use when" skills/mobile-web-planner/SKILL.md
echo "--- 구 번호 체계 NO. 3.x (0건 기대) ---"
grep -c "NO\. 3\." skills/mobile-web-planner/SKILL.md
```

기대: 순서대로 `0`, `0`, `1`, `0`.

- [ ] **Step 3: 커밋**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git add skills/mobile-web-planner/SKILL.md
git commit -m "$(cat <<'EOF'
fix: SKILL.md 정합화 - 번호 체계, 플레이스홀더, 클래스 계약 (#3)

- description 을 트리거형(Use when...)으로 전환하고, 실제로 입력받지 않는
  '캡쳐 이미지 모방' 서술을 제거. 한국어 트리거어를 포함해 매칭 범위 확보
- 번호 체계 통일: 01 Cover / 02 History / 03 Index / 04 IA /
  05 General Rule / 06.x 화면 상세. 기존에는 NO.05 다음 NO.3.1 이 오는
  모순이 있었다
- 하드코딩 브랜딩 제거 및 {{PROJECT_NAME}} / {{VERSION}} 플레이스홀더화
- Class Quick Reference 표 추가. 에이전트가 template.html 을 읽지 않아도
  올바른 클래스를 쓸 수 있게 하고, 목록에 없는 클래스 창작을 금지한다
- 이모지 아이콘 금지 및 Phosphor 인라인 SVG 사용법 명시
- 출력 방식을 채팅 코드 블록에서 파일 저장으로 변경 (런타임 중립 서술)

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: 클래스 계약 검증기 (TDD)

**Files:**
- Create: `tests/test_generate.py`
- Modify: `generate_doksam.py` (전체 재작성 — 이 태스크에서는 검증 함수와 CLI 골격만. 슬라이드 데이터는 Task 4)

**Interfaces:**
- Consumes: Task 1 의 `skills/mobile-web-planner/resources/template.html`
- Produces: `generate_doksam.py` 의 아래 공개 함수. Task 4 가 `build_html()` 과 `main()` 을 채운다.
  - `extract_style(template_html: str) -> str` — `<style>...</style>` 내부 CSS 반환
  - `defined_classes(css: str) -> set[str]` — CSS 셀렉터에서 클래스명 집합 추출
  - `used_classes(html: str) -> set[str]` — `class="..."` 속성에서 클래스명 집합 추출
  - `undefined_classes(html: str, css: str) -> list[str]` — 정렬된 미정의 클래스 목록. `WHITELIST` 를 제외
  - `WHITELIST: frozenset[str]` — `frozenset({"mermaid"})`

- [ ] **Step 1: 실패하는 테스트를 작성한다**

`tests/test_generate.py` 를 만든다. stdlib `unittest` 만 쓴다 (외부 라이브러리 import 는 이 머신에서 실패한다).

```python
"""generate_doksam.py 의 클래스 계약 검증기 단위 테스트 (stdlib only)."""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import generate_doksam as gd


class TestExtractStyle(unittest.TestCase):
    def test_returns_css_between_style_tags(self):
        html = "<head><style>\n.a { color: red; }\n</style></head>"
        self.assertIn(".a { color: red; }", gd.extract_style(html))

    def test_raises_when_no_style_block(self):
        with self.assertRaises(ValueError):
            gd.extract_style("<head></head>")


class TestDefinedClasses(unittest.TestCase):
    def test_extracts_simple_class_selectors(self):
        css = ".ppt-slide { color: red; }\n.mock-tab { color: blue; }"
        self.assertEqual(gd.defined_classes(css), {"ppt-slide", "mock-tab"})

    def test_extracts_compound_and_descendant_selectors(self):
        css = ".mock-tab.active { color: red; }\n.desc-list li { margin: 0; }"
        self.assertEqual(gd.defined_classes(css), {"mock-tab", "active", "desc-list"})

    def test_ignores_element_and_pseudo_selectors(self):
        css = "body { margin: 0; }\n* { box-sizing: border-box; }\ncode { color: red; }"
        self.assertEqual(gd.defined_classes(css), set())

    def test_ignores_decimal_values_in_declarations(self):
        css = ".a { transform: scale(0.9); box-shadow: 0 2px 4px rgba(0,0,0,0.3); }"
        self.assertEqual(gd.defined_classes(css), {"a"})

    def test_ignores_at_import_url_extension(self):
        css = "@import url('https://cdn.example.com/pretendard.css');\n.a { color: red; }"
        self.assertEqual(gd.defined_classes(css), {"a"})


class TestUsedClasses(unittest.TestCase):
    def test_extracts_single_and_multiple_classes(self):
        html = '<div class="ppt-slide"><span class="mock-tab active"></span></div>'
        self.assertEqual(gd.used_classes(html), {"ppt-slide", "mock-tab", "active"})

    def test_collapses_extra_whitespace(self):
        html = '<div class="  a   b  "></div>'
        self.assertEqual(gd.used_classes(html), {"a", "b"})

    def test_returns_empty_when_no_class_attribute(self):
        self.assertEqual(gd.used_classes("<div></div>"), set())


class TestUndefinedClasses(unittest.TestCase):
    CSS = ".ppt-slide { color: red; }\n.mock-tab { color: blue; }"

    def test_returns_empty_when_all_defined(self):
        html = '<div class="ppt-slide"><span class="mock-tab"></span></div>'
        self.assertEqual(gd.undefined_classes(html, self.CSS), [])

    def test_reports_undefined_sorted(self):
        html = '<div class="storyboard"><span class="dochead"></span></div>'
        self.assertEqual(gd.undefined_classes(html, self.CSS), ["dochead", "storyboard"])

    def test_mermaid_is_whitelisted(self):
        html = '<div class="mermaid">mindmap</div>'
        self.assertEqual(gd.undefined_classes(html, self.CSS), [])

    def test_whitelist_contains_mermaid(self):
        self.assertIn("mermaid", gd.WHITELIST)


class TestAgainstRealTemplate(unittest.TestCase):
    """실제 template.html 로 계약이 성립하는지 확인한다."""

    def setUp(self):
        path = REPO_ROOT / "skills" / "mobile-web-planner" / "resources" / "template.html"
        self.css = gd.extract_style(path.read_text(encoding="utf-8"))

    def test_core_classes_are_defined(self):
        for name in ("docwrap", "ppt-slide", "ppt-top-no", "ppt-body-full",
                     "ppt-wireframe", "ppt-desc-panel", "desc-num",
                     "pointer-badge", "mock", "mock-tab", "ppt-footer", "icon"):
            with self.subTest(name=name):
                self.assertIn(name, gd.defined_classes(self.css))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 테스트를 실행해 실패를 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
python3 -m unittest discover -s tests -v
```

기대: `AttributeError: module 'generate_doksam' has no attribute 'extract_style'` 계열로 대량 실패. (현재 `generate_doksam.py` 는 import 하는 순간 파일을 쓰는 스크립트이므로, import 자체가 부작용을 낸다는 점도 이 단계에서 드러난다.)

- [ ] **Step 3: `generate_doksam.py` 를 함수 구조로 재작성한다**

기존 파일 전체를 아래로 교체한다. 이 태스크에서는 검증기와 CLI 골격만 완성한다 — `SLIDES` 는 Task 4 에서 채운다.

```python
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


def build_html(styles: str) -> str:
    """예시 스토리보드 HTML 전체를 조립한다. (Task 4 에서 구현)"""
    raise NotImplementedError


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
```

- [ ] **Step 4: 테스트가 통과하는지 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
python3 -m unittest discover -s tests -v
```

기대: 전부 PASS (`OK`). `build_html` 은 아직 `NotImplementedError` 지만 테스트가 호출하지 않으므로 무관하다.

- [ ] **Step 5: 커밋**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git add generate_doksam.py tests/test_generate.py
git commit -m "$(cat <<'EOF'
feat: 클래스 계약 검증기 추가 및 generate_doksam.py 함수 구조화 (#3)

template.html 이 CSS 클래스의 유일한 정의처라는 계약을 기계적으로 강제한다.
생성 HTML 이 정의되지 않은 클래스를 쓰면 stderr 에 전부 나열하고 exit 1 한다
(mermaid 는 mermaid.js 가 렌더하므로 화이트리스트).

기존 스크립트는 import 만으로 파일을 쓰는 구조여서 테스트가 불가능했다.
extract_style / defined_classes / used_classes / undefined_classes 로 분리하고
파일 쓰기는 main() 으로 옮긴다. 파일 쓰기는 검증 통과 후에만 수행하므로
부분 산출물이 남지 않는다.

테스트는 stdlib unittest 만 사용한다 (이 환경의 Homebrew Python 3.14 는
외부 라이브러리 import 가 깨져 있다).

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: 예시 스토리보드 7장 재생성

**Files:**
- Modify: `generate_doksam.py` (`build_html()` 구현 + `SLIDES` 데이터)
- Regenerate: `examples/doksam_news_storyboard.html` (5장 → 7장)

**Interfaces:**
- Consumes: Task 3 의 `extract_style()`, `undefined_classes()`, `main()`, 상수 `PROJECT_NAME` / `VERSION` / `DOC_DATE` / `DOC_AUTHOR`. Task 2 의 번호 체계.
- Produces: `examples/doksam_news_storyboard.html`. 이후 `python3 generate_doksam.py` 를 실행하면 항상 동일한 내용이 나와야 한다 (불변식).

- [ ] **Step 1: 불변식 테스트를 추가한다**

`tests/test_generate.py` 의 `TestAgainstRealTemplate` 클래스 **뒤**, `if __name__ == "__main__":` **앞**에 아래를 추가한다.

```python
class TestBuiltExample(unittest.TestCase):
    """생성 결과가 계약과 번호 체계를 지키는지 확인한다."""

    def setUp(self):
        template = gd.TEMPLATE_PATH.read_text(encoding="utf-8")
        self.css = gd.extract_style(template)
        self.html = gd.build_html(self.css)

    def test_has_seven_slides(self):
        self.assertEqual(self.html.count('class="ppt-slide"'), 7)

    def test_slide_numbers_follow_scheme(self):
        numbers = re.findall(r'class="ppt-top-no">NO\. ([\d.]+)<', self.html)
        self.assertEqual(numbers, ["01", "02", "03", "04", "05", "06.1", "06.2"])

    def test_no_undefined_classes(self):
        self.assertEqual(gd.undefined_classes(self.html, self.css), [])

    def test_no_stale_branding(self):
        for banned in ("쀼어", "기획이야기", "덕삼이"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, self.html)

    def test_project_name_is_present(self):
        self.assertIn(gd.PROJECT_NAME, self.html)

    def test_no_emoji(self):
        found = re.findall(
            r"[\U0001F300-\U0001FAFF☀-➿⬀-⯿]", self.html
        )
        self.assertEqual(found, [])

    def test_styles_are_inlined(self):
        self.assertIn(".ppt-slide", self.html)
```

`re` 를 쓰므로 파일 상단 import 에 이미 있는지 확인한다. 없으면 `import re` 를 `import sys` 위에 추가한다.

- [ ] **Step 2: 테스트를 실행해 실패를 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
python3 -m unittest tests.test_generate.TestBuiltExample -v
```

기대: 7개 테스트 전부 `NotImplementedError` 로 ERROR.

- [ ] **Step 3: `build_html()` 을 구현한다**

`generate_doksam.py` 의 `build_html` 정의를 아래로 교체한다 (`raise NotImplementedError` 를 지우고 실제 구현을 넣는다). Phosphor `path` 는 `raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/` 에서 가져온 실제 값이다.

```python
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


def _slide(no: str, title: str, body: str) -> str:
    """슬라이드 1장을 조립한다. body 는 ppt-content 내부 마크업."""
    return f"""
  <div class="ppt-slide">
    <div class="ppt-top-bar">
      <div class="ppt-top-no">NO. {no}</div>
      <div class="ppt-top-title">{title}</div>
      <div class="ppt-top-proj">{PROJECT_NAME}</div>
    </div>
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
        <h2 style="border-bottom:2px solid #ea580c; padding-bottom:10px; margin-bottom:20px; color:#333;">개정 이력</h2>
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
        ("01", "Cover", "문서 표지 — 서비스명, 버전, 작성일"),
        ("02", "Document History", "개정 이력"),
        ("03", "Index", "본 목차"),
        ("04", "Information Architecture", "화면 트리 및 정보구조"),
        ("05", "General Rule", "공통 규칙 — 레이아웃, 타이포, 컬러, 예외처리"),
        ("06.1", "Main Home", "메인 홈 화면 상세"),
        ("06.2", "Article Detail", "기사 상세 화면 상세"),
    ]
    tr = "\n".join(
        f"          <tr><td {TD}>{no}</td><td {TD}>{title}</td><td {TD}>{desc}</td></tr>"
        for no, title, desc in rows
    )
    body = f"""      <div class="ppt-body-full">
        <h2 style="border-bottom:2px solid #ea580c; padding-bottom:10px; margin-bottom:20px; color:#333;">목차</h2>
        <table style="width:100%; border-collapse:collapse; text-align:left;">
          <tr style="background:#f4f4f4; border-bottom:2px solid #ccc;">
            <th {TH} width="90">NO.</th>
            <th {TH} width="240">제목</th>
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
        <h2 style="border-bottom:2px solid #ea580c; padding-bottom:10px; margin-bottom:20px; color:#333;">공통 규칙</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px 40px; font-size:15px; color:#333; line-height:1.7;">
          <div>
            <h3 style="font-size:16px; color:#ea580c; margin:0 0 8px;">레이아웃 · 그리드</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>기준 해상도 360 x 640 (mdpi)</li>
              <li>좌우 안전 여백 16px 고정</li>
              <li>블록 간 수직 간격 16px</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:#ea580c; margin:0 0 8px;">타이포그래피</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>본문 14px / 행간 1.6</li>
              <li>제목 20px / 굵기 800</li>
              <li>메타 정보 11px / 색상 #888</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:#ea580c; margin:0 0 8px;">컬러</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>Primary <code>#ea580c</code></li>
              <li>Text <code>#111</code> / Sub <code>#888</code></li>
              <li>Divider <code>#eee</code></li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:#ea580c; margin:0 0 8px;">예외 처리</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>로딩: 카드 스켈레톤 노출</li>
              <li>네트워크 오류: 상단 배너 "오프라인 상태입니다"</li>
              <li>빈 목록: 안내 문구 + 재시도 버튼</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:#ea580c; margin:0 0 8px;">인터랙션</h3>
            <ul style="margin:0; padding-left:20px;">
              <li>목록 최상단에서 Pull-to-refresh 지원</li>
              <li>탭 전환은 좌우 스와이프 병행</li>
              <li>터치 영역 최소 44 x 44px</li>
            </ul>
          </div>
          <div>
            <h3 style="font-size:16px; color:#ea580c; margin:0 0 8px;">접근성</h3>
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

              <span class="pointer-badge" style="position:absolute; top:20px; left:-12px; z-index:10;">1</span>
              <div style="background:#ea580c; border-radius:4px; padding:16px; margin-bottom:16px; color:#fff;">
                <div style="font-size:10px; font-weight:800; margin-bottom:6px;">BREAKING NEWS</div>
                <div style="font-size:15px; font-weight:700;">글로벌 혁신 AI, 세상을 바꾸다</div>
              </div>

              <span class="pointer-badge" style="position:absolute; top:130px; left:-12px; z-index:10;">2</span>
              <div style="display:flex; gap:16px; border-bottom:1px solid #ccc; padding-bottom:8px; margin-bottom:16px;">
                <div style="font-size:13px; font-weight:800; color:#ea580c; border-bottom:2px solid #ea580c; padding-bottom:6px;">Top Stories</div>
                <div style="font-size:13px; font-weight:500; color:#555;">World</div>
                <div style="font-size:13px; font-weight:500; color:#555;">Business</div>
              </div>

              <span class="pointer-badge" style="position:absolute; top:190px; left:-12px; z-index:10;">3</span>
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
                가장 중요한 속보 기사를 상단에 강조 표시. 클릭 시 06.2 기사 상세로 이동.<br>
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
    return _slide("06.1", "Main Home", body)


def _article_detail() -> str:
    body = f"""      <div class="ppt-wireframe">
        <div class="mock">
          <div class="mock-screen" style="position:relative;">
            <div class="mock-status"></div>

            <span class="pointer-badge" style="position:absolute; top:20px; left:-12px; z-index:10;">1</span>
            <div style="height:160px; background:#ddd; position:relative;">
              <div class="mock-header" style="background:transparent; border:none; position:absolute; top:0; width:100%;">
                <span style="color:#111; font-weight:800; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:4px;">&lsaquo;</span>
                <span style="color:#111; font-weight:800; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:4px;">&#8942;</span>
              </div>
            </div>

            <div class="mock-body" style="background:#fff; border-radius:16px 16px 0 0; margin-top:-16px; position:relative; z-index:2; padding:24px 16px;">
              <div style="font-size:12px; color:#ea580c; font-weight:800; margin-bottom:8px;">TECH</div>
              <div style="font-size:20px; font-weight:800; color:#111; line-height:1.4; margin-bottom:16px;">새로운 모바일 기획 에이전트 출시, UX/UI 패러다임 전환</div>

              <span class="pointer-badge" style="position:absolute; top:120px; left:-12px; z-index:10;">2</span>
              <div style="font-size:14px; color:#333; line-height:1.6; margin-bottom:30px;">
                새롭게 출시된 모바일웹 플래너 에이전트는 기획자의 의도를 파악해 완결된 스토리보드를 구축합니다.
              </div>

              <span class="pointer-badge" style="position:absolute; bottom:20px; left:-12px; z-index:10;">3</span>
              <div style="display:flex; justify-content:center; gap:16px;">
                <div style="flex:1; padding:12px 0; border:1px solid #ccc; border-radius:8px; display:flex; justify-content:center; align-items:center; gap:8px; font-size:13px; font-weight:700;">
                  {ICON_LINK} Copy Link
                </div>
                <div style="flex:1; padding:12px 0; border:1px solid #ea580c; color:#ea580c; border-radius:8px; display:flex; justify-content:center; align-items:center; gap:8px; font-size:13px; font-weight:700;">
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
    return _slide("06.2", "Article Detail", body)


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
```

주의: f-string 안의 mermaid 설정 중괄호는 `{{` `}}` 로 이스케이프해야 한다. 위 코드에 이미 반영되어 있다.

- [ ] **Step 4: 테스트가 통과하는지 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
python3 -m unittest discover -s tests -v
```

기대: 전부 PASS (`OK`).

- [ ] **Step 5: 예시를 재생성하고 불변식을 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
python3 generate_doksam.py
echo "exit=$?"
```

기대: `생성 완료: examples/doksam_news_storyboard.html (슬라이드 7장)`, `exit=0`

이어서 **두 번 연속 실행해도 결과가 같은지**(멱등) 확인한다.

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git add examples/doksam_news_storyboard.html
python3 generate_doksam.py
git diff --exit-code examples/ && echo "불변식 OK: 재생성 결과가 스테이징 내용과 동일"
```

기대: `불변식 OK: ...` 출력.

- [ ] **Step 6: 검증기 역방향 테스트 — 없는 클래스를 주입하면 exit 1 인지 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
cp generate_doksam.py /tmp/generate_doksam.py.bak
python3 - <<'PY'
from pathlib import Path
p = Path("generate_doksam.py")
s = p.read_text(encoding="utf-8")
s = s.replace('<div class="docwrap">', '<div class="docwrap totally-undefined-class">', 1)
p.write_text(s, encoding="utf-8")
PY
python3 generate_doksam.py; echo "exit=$?"
cp /tmp/generate_doksam.py.bak generate_doksam.py
rm /tmp/generate_doksam.py.bak
git diff --exit-code generate_doksam.py examples/ && echo "원복 OK"
```

기대: stderr 에 `- totally-undefined-class` 가 나열되고 `exit=1`. 그 뒤 `원복 OK`.

- [ ] **Step 7: 제약 위반이 없는지 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
echo "--- 쀼어 (0 기대) ---"
grep -rc "쀼어" examples/doksam_news_storyboard.html generate_doksam.py
echo "--- 기획이야기 (0 기대) ---"
grep -rc "기획이야기" examples/doksam_news_storyboard.html generate_doksam.py
echo "--- 이모지 (0 기대) ---"
grep -oP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}]' examples/doksam_news_storyboard.html | wc -l
echo "--- 슬라이드 번호 ---"
grep -oP 'ppt-top-no">NO\. [\d.]+' examples/doksam_news_storyboard.html
```

기대: `쀼어`·`기획이야기` 모두 `0`, 이모지 `0`, 번호가 `01 02 03 04 05 06.1 06.2` 순.

- [ ] **Step 8: 커밋**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git add generate_doksam.py tests/test_generate.py examples/doksam_news_storyboard.html
git commit -m "$(cat <<'EOF'
fix: 예시 스토리보드를 현행 규격 7장으로 재생성 (#3)

커밋 b507cae 에서 템플릿과 예시만 새 PPT 레이아웃으로 전환하고 생성
스크립트가 따라가지 않아, AGENTS.md 가 지시하는 검증 명령을 실행하면
예시가 469줄 diff 로 파괴되고 CSS 미정의 클래스 44개를 쓰는 문서가
만들어지던 상태를 해소한다.

- build_html() 을 슬라이드 단위 함수로 구현. 누락되어 있던
  03 Index / 05 General Rule 을 추가해 5장 -> 7장
- 번호 체계를 01/02/03/04/05/06.1/06.2 로 정렬 (기존 NO.3.x 제거)
- 하드코딩된 외부 블로그 브랜딩 및 '기획이야기' 문구 제거
- 목업 액션 아이콘의 이모지를 Phosphor 인라인 SVG 로 교체
- 불변식 확보: 재생성 결과가 커밋 내용과 항상 동일하다

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: install.sh — 3개 런타임 배포

**Files:**
- Create: `install.sh` (실행 권한 부여)
- Create: `tests/test_install.sh` (실행 권한 부여)

**Interfaces:**
- Consumes: Task 1 의 `skills/mobile-web-planner/` 디렉터리
- Produces: `install.sh` CLI. 옵션 `--copy` `--project <dir>` `--dry-run` `--uninstall` `--force` `--help`. 종료 코드 0(성공/멱등 skip) / 1(충돌·오류).

- [ ] **Step 1: 실패하는 테스트를 작성한다**

`tests/test_install.sh` 를 만든다. 실제 `$HOME` 을 건드리지 않도록 임시 디렉터리를 `HOME` 으로 덮어써서 격리한다.

```bash
#!/usr/bin/env bash
# install.sh 동작 테스트. 임시 HOME 으로 격리하므로 실제 홈 디렉터리를 건드리지 않는다.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="$REPO_ROOT/install.sh"
SRC="$REPO_ROOT/skills/mobile-web-planner"

pass=0
fail=0

check() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  ok   $label"
    pass=$((pass + 1))
  else
    echo "  FAIL $label — expected '$expected', got '$actual'"
    fail=$((fail + 1))
  fi
}

new_sandbox() {
  SANDBOX="$(mktemp -d)"
  export HOME="$SANDBOX"
}

drop_sandbox() {
  rm -rf "$SANDBOX"
}

echo "test: --dry-run 은 파일시스템을 바꾸지 않는다"
new_sandbox
"$INSTALL" --dry-run >/dev/null 2>&1
check "exit code" "0" "$?"
check "심링크 미생성" "absent" "$([[ -e "$HOME/.claude/skills/mobile-web-planner" ]] && echo present || echo absent)"
drop_sandbox

echo "test: 기본 설치는 전역 3경로에 심링크를 만든다"
new_sandbox
"$INSTALL" >/dev/null 2>&1
check "exit code" "0" "$?"
for t in ".agents/skills" ".claude/skills" ".gemini/antigravity/skills"; do
  link="$HOME/$t/mobile-web-planner"
  check "$t 심링크" "$SRC" "$(readlink "$link" 2>/dev/null)"
done
drop_sandbox

echo "test: 재실행은 멱등하다 (skip)"
new_sandbox
"$INSTALL" >/dev/null 2>&1
out="$("$INSTALL" 2>&1)"
check "exit code" "0" "$?"
check "skip 3건" "3" "$(grep -c '^skip' <<<"$out")"
drop_sandbox

echo "test: 남의 디렉터리가 있으면 덮어쓰지 않고 실패한다"
new_sandbox
mkdir -p "$HOME/.claude/skills/mobile-web-planner"
touch "$HOME/.claude/skills/mobile-web-planner/SKILL.md"
"$INSTALL" >/dev/null 2>&1
check "exit code" "1" "$?"
check "기존 파일 보존" "present" "$([[ -f "$HOME/.claude/skills/mobile-web-planner/SKILL.md" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --force 는 충돌 항목을 교체한다"
new_sandbox
mkdir -p "$HOME/.claude/skills/mobile-web-planner"
"$INSTALL" --force >/dev/null 2>&1
check "exit code" "0" "$?"
check "심링크로 교체" "$SRC" "$(readlink "$HOME/.claude/skills/mobile-web-planner" 2>/dev/null)"
drop_sandbox

echo "test: --copy 는 심링크 대신 복사한다"
new_sandbox
"$INSTALL" --copy >/dev/null 2>&1
check "exit code" "0" "$?"
target="$HOME/.claude/skills/mobile-web-planner"
check "심링크 아님" "notlink" "$([[ -L "$target" ]] && echo link || echo notlink)"
check "SKILL.md 복사됨" "present" "$([[ -f "$target/SKILL.md" ]] && echo present || echo absent)"
check "template.html 복사됨" "present" "$([[ -f "$target/resources/template.html" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --project 는 프로젝트 스킬 경로에 설치한다"
new_sandbox
proj="$SANDBOX/myrepo"
mkdir -p "$proj"
"$INSTALL" --project "$proj" >/dev/null 2>&1
check "exit code" "0" "$?"
check ".claude/skills" "$SRC" "$(readlink "$proj/.claude/skills/mobile-web-planner" 2>/dev/null)"
check ".antigravity/skills" "$SRC" "$(readlink "$proj/.antigravity/skills/mobile-web-planner" 2>/dev/null)"
check "전역 미설치" "absent" "$([[ -e "$HOME/.claude/skills/mobile-web-planner" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --project 대상이 디렉터리가 아니면 실패한다"
new_sandbox
"$INSTALL" --project "$SANDBOX/nope" >/dev/null 2>&1
check "exit code" "1" "$?"
drop_sandbox

echo "test: --uninstall 은 우리 심링크만 제거한다"
new_sandbox
"$INSTALL" >/dev/null 2>&1
"$INSTALL" --uninstall >/dev/null 2>&1
check "exit code" "0" "$?"
for t in ".agents/skills" ".claude/skills" ".gemini/antigravity/skills"; do
  check "$t 제거" "absent" "$([[ -e "$HOME/$t/mobile-web-planner" ]] && echo present || echo absent)"
done
drop_sandbox

echo "test: --uninstall 은 실제 디렉터리를 삭제하지 않는다"
new_sandbox
"$INSTALL" --copy >/dev/null 2>&1
"$INSTALL" --uninstall >/dev/null 2>&1
check "복사본 보존" "present" "$([[ -f "$HOME/.claude/skills/mobile-web-planner/SKILL.md" ]] && echo present || echo absent)"
drop_sandbox

echo
echo "pass=$pass fail=$fail"
[[ $fail -eq 0 ]]
```

실행 권한을 준다.

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
chmod +x tests/test_install.sh
```

- [ ] **Step 2: 테스트를 실행해 실패를 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
./tests/test_install.sh
```

기대: `install.sh` 가 없으므로 대량 FAIL, 마지막 줄 `pass=0 fail=...`, 종료 코드 1.

- [ ] **Step 3: `install.sh` 를 작성한다**

```bash
#!/usr/bin/env bash
# mobile-web-planner 스킬을 Claude Code / Codex / Gemini(Antigravity) 가
# 인식하는 경로에 노출한다. 기본은 심링크이므로 이 레포에서 SKILL.md 를
# 수정하면 세 런타임에 즉시 반영된다.
set -uo pipefail

SKILL_NAME="mobile-web-planner"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_ROOT/skills/$SKILL_NAME"

MODE="symlink"     # symlink | copy
ACTION="install"   # install | uninstall
DRY_RUN=0
FORCE=0
PROJECT=""

ok=0
skipped=0
failed=0

usage() {
  cat <<'USAGE'
사용법: ./install.sh [옵션]

옵션:
  (없음)              전역 3경로에 심링크를 만든다
                        ~/.agents/skills/                (Codex, Gemini CLI)
                        ~/.claude/skills/                (Claude Code)
                        ~/.gemini/antigravity/skills/    (Antigravity)
  --copy              심링크 대신 복사한다
  --project <dir>     전역 대신 해당 레포의 프로젝트 스킬 경로에 설치한다
                        <dir>/.claude/skills/
                        <dir>/.antigravity/skills/
  --dry-run           수행할 작업만 출력하고 파일시스템은 바꾸지 않는다
  --uninstall         이 레포를 가리키는 심링크를 제거한다
  --force             충돌하는 기존 항목을 교체한다
  -h, --help          이 도움말

동작 규칙:
  - 이미 이 레포를 가리키는 심링크면 skip 한다 (멱등)
  - 다른 것을 가리키는 심링크나 실제 디렉터리가 있으면 덮어쓰지 않고
    exit 1 한다. --force 를 준 경우에만 교체한다
  - --uninstall 은 이 레포를 가리키는 심링크만 제거한다. 실제 디렉터리
    (--copy 설치분 등)는 경로를 안내하고 손대지 않는다
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy)      MODE="copy"; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    --uninstall) ACTION="uninstall"; shift ;;
    --force)     FORCE=1; shift ;;
    --project)
      if [[ $# -lt 2 ]]; then
        echo "오류: --project 에 디렉터리 인자가 필요하다" >&2
        exit 1
      fi
      PROJECT="$2"; shift 2 ;;
    -h|--help)   usage; exit 0 ;;
    *)
      echo "오류: 알 수 없는 옵션 '$1'" >&2
      usage >&2
      exit 1 ;;
  esac
done

if [[ ! -d "$SRC" ]]; then
  echo "오류: 스킬 원본이 없다 — $SRC" >&2
  exit 1
fi

# 타깃 목록 구성
targets=()
if [[ -n "$PROJECT" ]]; then
  if [[ ! -d "$PROJECT" ]]; then
    echo "오류: --project 대상이 디렉터리가 아니다 — $PROJECT" >&2
    exit 1
  fi
  project_abs="$(cd "$PROJECT" && pwd)"
  targets+=("$project_abs/.claude/skills/$SKILL_NAME")
  targets+=("$project_abs/.antigravity/skills/$SKILL_NAME")
else
  targets+=("$HOME/.agents/skills/$SKILL_NAME")
  targets+=("$HOME/.claude/skills/$SKILL_NAME")
  targets+=("$HOME/.gemini/antigravity/skills/$SKILL_NAME")
fi

points_at_src() {
  [[ -L "$1" ]] && [[ "$(readlink "$1")" == "$SRC" ]]
}

do_uninstall() {
  local target="$1"
  if points_at_src "$target"; then
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "remove    $target"
    else
      rm "$target"
      echo "remove    $target"
    fi
    ok=$((ok + 1))
  elif [[ -L "$target" ]]; then
    echo "skip      $target (다른 곳을 가리키는 심링크: $(readlink "$target"))"
    skipped=$((skipped + 1))
  elif [[ -e "$target" ]]; then
    echo "skip      $target (실제 디렉터리 — 직접 확인 후 제거할 것)"
    skipped=$((skipped + 1))
  else
    echo "skip      $target (없음)"
    skipped=$((skipped + 1))
  fi
}

do_install() {
  local target="$1"

  if points_at_src "$target"; then
    echo "skip      $target (이미 설치됨)"
    skipped=$((skipped + 1))
    return 0
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    if [[ $FORCE -eq 0 ]]; then
      local what="실제 디렉터리"
      [[ -L "$target" ]] && what="다른 곳을 가리키는 심링크: $(readlink "$target")"
      echo "conflict  $target ($what) — 덮어쓰지 않는다. 교체하려면 --force" >&2
      failed=$((failed + 1))
      return 0
    fi
    if [[ $DRY_RUN -eq 0 ]]; then
      rm -rf "$target"
    fi
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "$MODE   $target -> $SRC"
    ok=$((ok + 1))
    return 0
  fi

  mkdir -p "$(dirname "$target")"
  if [[ "$MODE" == "copy" ]]; then
    cp -R "$SRC" "$target"
    echo "copy      $target"
  else
    ln -s "$SRC" "$target"
    echo "symlink   $target -> $SRC"
  fi
  ok=$((ok + 1))
}

if [[ $DRY_RUN -eq 1 ]]; then
  echo "(dry-run — 파일시스템을 바꾸지 않는다)"
fi

for target in "${targets[@]}"; do
  if [[ "$ACTION" == "uninstall" ]]; then
    do_uninstall "$target"
  else
    do_install "$target"
  fi
done

echo
echo "완료: ok=$ok skip=$skipped conflict=$failed"
[[ $failed -eq 0 ]]
```

실행 권한을 준다.

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
chmod +x install.sh
```

- [ ] **Step 4: 테스트가 통과하는지 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
./tests/test_install.sh
```

기대: 마지막 줄 `fail=0`, 종료 코드 0.

- [ ] **Step 5: 실제 홈에 설치해 확인한 뒤 되돌린다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
./install.sh --dry-run
./install.sh
for t in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.gemini/antigravity/skills"; do
  printf '%s -> %s\n' "$t/mobile-web-planner" "$(readlink "$t/mobile-web-planner")"
done
./install.sh   # 멱등 확인 — skip 3건
```

기대: 3경로 모두 `.../skills/mobile-web-planner` 절대경로를 가리키고, 재실행 시 `skip` 3건.

이 상태는 그대로 둔다 — 실제로 세 런타임에서 스킬을 쓰려는 것이 목적이다. (되돌리려면 `./install.sh --uninstall`)

- [ ] **Step 6: 커밋**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git add install.sh tests/test_install.sh
git commit -m "$(cat <<'EOF'
feat: install.sh 추가 - Claude Code / Codex / Antigravity 배포 (#3)

런타임별 스킬 경로가 달라 수동 복사를 요구하던 것을 스크립트화한다.
기본은 심링크이므로 레포에서 SKILL.md 를 수정하면 세 런타임에 즉시
반영된다.

  ~/.agents/skills/               Codex, Gemini CLI (공용 alias)
  ~/.claude/skills/               Claude Code
  ~/.gemini/antigravity/skills/   Antigravity

파괴 방지 규칙을 둔다. 이미 이 레포를 가리키는 심링크면 skip 하고,
다른 것을 가리키는 심링크나 실제 디렉터리가 있으면 덮어쓰지 않고 exit 1
한다(--force 로만 교체). --uninstall 은 이 레포를 가리키는 심링크만
제거하며 실제 디렉터리는 경로만 안내한다.

테스트는 임시 디렉터리를 HOME 으로 덮어써 격리하므로 실제 홈을 건드리지
않는다.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: AGENTS.md · README.md 갱신

**Files:**
- Modify: `AGENTS.md` (섹션 3, 4 전면 갱신)
- Modify: `README.md` (사용 방법, 구조 트리)

**Interfaces:**
- Consumes: Task 1~5 의 결과 — 새 디렉터리 경로, 검증 명령, `install.sh` 옵션
- Produces: 없음 (문서 태스크)

- [ ] **Step 1: `AGENTS.md` 의 3~4절을 교체한다**

기존 3절("디렉토리 및 파일 역할")과 4절("에이전트 작업 지침") 전체를 아래로 교체한다. 기존 내용은 구 디렉터리명을 쓰고, 검증 절차가 실제로는 예시를 파괴하는 명령이며, 클래스 계약과 이모지 방침이 없다.

```markdown
## 3. 디렉토리 및 파일 역할

- `skills/mobile-web-planner/SKILL.md`: 기획자 페르소나, 워크플로우, 클래스 Quick Reference, 마크업 예시가 정의된 핵심 파일.
- `skills/mobile-web-planner/resources/template.html`: 기획서 결과물의 HTML/CSS 스켈레톤. **CSS 클래스의 유일한 정의처**.
- `generate_doksam.py`: 예시 스토리보드를 재생성하면서 클래스 계약을 검증하는 스크립트.
- `install.sh`: 스킬을 Claude Code / Codex / Antigravity 경로에 설치.
- `tests/test_generate.py`: 검증기 단위 테스트 (stdlib `unittest`).
- `tests/test_install.sh`: `install.sh` 동작 테스트 (임시 HOME 격리).
- `examples/doksam_news_storyboard.html`: **생성 산출물이므로 직접 편집하지 않는다.** 내용을 바꾸려면 `generate_doksam.py` 를 수정하고 재생성한다.
- `docs/superpowers/specs/`, `docs/superpowers/plans/`: 설계 및 구현 계획 문서.

## 4. 에이전트 작업 지침 (Agent Instructions)

### 클래스 계약 (가장 중요)

`resources/template.html` 에 CSS 로 정의된 클래스만 사용한다. 유일한 예외는 `mermaid` (mermaid.js 가 렌더하므로 CSS 불필요).

- 새 클래스가 필요하면 **먼저 `template.html` 에 정의를 추가**하고, `SKILL.md` 의 Class Quick Reference 표에도 등재한다.
- 목업 내부의 세부 스타일은 인라인 `style` 속성으로 처리한다. 일회성 클래스를 만들지 않는다.
- 이 계약이 깨지면 `generate_doksam.py` 가 exit 1 로 막는다.

### 스킬 및 프롬프트 수정

- 기획자의 말투, 프로세스, 결과물 형식을 변경할 경우 `SKILL.md` 를 수정한다.
- 슬라이드 번호 체계는 `01 Cover / 02 Document History / 03 Index / 04 Information Architecture / 05 General Rule / 06.x 화면 상세` 다. 바꾸려면 `SKILL.md` 와 `generate_doksam.py` 를 함께 수정한다.
- 산출물에 특정 블로그·회사·개인 이름을 넣지 않는다. 플레이스홀더는 `{{PROJECT_NAME}}` 과 `{{VERSION}}` 두 개뿐이다.

### 아이콘 — 이모지 금지

`skills/**` 와 `examples/*.html` 에 이모지를 아이콘 대용으로 쓰지 않는다. Phosphor Icons(MIT) 의 `path` 를 인라인 `<svg class="icon">` 으로 넣는다.

원본: `https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/<name>.svg`

뒤로가기 `&lsaquo;`, 케밥 메뉴 `&#8942;` 같은 타이포그래피 문자는 이모지가 아니므로 그대로 써도 된다.

### 템플릿(HTML/CSS) 수정

- 디자인이나 레이아웃 변경은 `resources/template.html` 을 수정한다.
- **Vanilla CSS** 만 쓴다. TailwindCSS 등 프레임워크를 도입하지 않는다.
- `@import` 는 `@font-face` 를 포함한 모든 규칙보다 앞에 있어야 유효하다 (CSS 스펙).
- 클래스 네이밍은 직관적으로, 스타일은 `<style>` 태그 안에 정리한다.

### 테스트 및 검증

Python 은 **stdlib 만** 쓴다. 이 환경의 Homebrew Python 3.14 는 외부 라이브러리 import 가 깨져 있다.

```bash
# 단위 테스트
python3 -m unittest discover -s tests -v
./tests/test_install.sh

# 예시 재생성 + 클래스 계약 검증
python3 generate_doksam.py

# 불변식: 재생성 결과가 커밋 내용과 동일해야 한다
git diff --exit-code examples/
```

`generate_doksam.py` 가 exit 1 이면 정의되지 않은 클래스를 쓰고 있다는 뜻이다. stderr 에 나열된 클래스를 `template.html` 에 정의하거나 사용을 제거한다.

`git diff --exit-code examples/` 가 clean 하지 않으면 예시를 손으로 편집했거나 스크립트가 stale 하다는 뜻이다. 둘을 일치시킨다.
```

- [ ] **Step 2: `README.md` 의 사용 방법과 구조 트리를 교체한다**

`## 🚀 사용 방법 (How to Use)` 섹션 본문(1~4번 항목)과 `## 📁 구조 (Structure)` 섹션의 트리 및 그 아래 `generate_doksam.py` 설명 문단을 아래로 교체한다. README 의 헤딩 이모지는 이번 범위 밖이므로 그대로 둔다.

사용 방법 본문:

```markdown
1. 이 저장소를 클론합니다.
2. 설치 스크립트를 실행합니다. 기본은 심링크이므로, 이후 저장소에서 `SKILL.md` 를 수정하면 세 런타임에 즉시 반영됩니다.

   ```bash
   ./install.sh
   ```

   | 런타임 | 설치 경로 |
   |---|---|
   | Codex, Gemini CLI | `~/.agents/skills/mobile-web-planner` |
   | Claude Code | `~/.claude/skills/mobile-web-planner` |
   | Antigravity | `~/.gemini/antigravity/skills/mobile-web-planner` |

   특정 프로젝트에만 넣으려면 `--project` 를 씁니다.

   ```bash
   ./install.sh --project ~/work/my-service
   # -> ~/work/my-service/.claude/skills/mobile-web-planner
   # -> ~/work/my-service/.antigravity/skills/mobile-web-planner
   ```

   심링크 대신 복사하려면 `--copy`, 미리 확인만 하려면 `--dry-run`, 제거는 `--uninstall` 입니다. 전체 옵션은 `./install.sh --help` 를 참고하세요.

3. 에이전트에게 요청합니다.

   > *"새로운 반려동물 용품 쇼핑몰 모바일웹 기획해줘"*
   > *"동네 맛집 리뷰 커뮤니티 앱 화면 기획서 작성해볼래?"*

4. 에이전트가 스킬을 감지하고, 해당 도메인의 IA와 화면 설계서를 단일 HTML 파일로 저장해 줍니다.
```

구조 트리:

```text
📦 mobile-web-planner-agent
 ┣ 📂 skills
 ┃ ┗ 📂 mobile-web-planner
 ┃   ┣ 📜 SKILL.md (기획자 페르소나, 워크플로우, 클래스 Quick Reference)
 ┃   ┗ 📂 resources
 ┃     ┗ 📜 template.html (기획서 HTML/CSS 스켈레톤 · CSS 클래스 정의처)
 ┣ 📂 examples
 ┃ ┣ 📜 doksam_news_storyboard.html (생성 산출물 예시 · 슬라이드 7장)
 ┃ ┣ 📜 mobile_news_plan.md (뉴스 앱 기획 예시)
 ┃ ┗ 📂 images (목업 이미지)
 ┣ 📂 tests
 ┃ ┣ 📜 test_generate.py (검증기 단위 테스트)
 ┃ ┗ 📜 test_install.sh (install.sh 동작 테스트)
 ┣ 📂 docs
 ┃ ┗ 📂 superpowers (설계 · 구현 계획 문서)
 ┣ 📜 install.sh (3개 런타임 설치)
 ┣ 📜 generate_doksam.py (예시 재생성 + 클래스 계약 검증)
 ┗ 📜 README.md
```

트리 아래 설명 문단:

```markdown
`generate_doksam.py` 는 예시 스토리보드를 재생성하면서, 생성된 HTML 이 `template.html` 에 정의되지 않은 CSS 클래스를 쓰고 있으면 exit 1 로 막습니다. 저장소 루트 기준 상대경로로 동작하므로 클론 후 바로 실행할 수 있습니다.

```bash
python3 generate_doksam.py
```

`examples/doksam_news_storyboard.html` 은 이 스크립트의 산출물이므로 직접 편집하지 않습니다.
```

- [ ] **Step 3: 문서에 구 경로가 남아있지 않은지 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
echo "--- 구 디렉터리명 (0 기대) ---"
grep -rn "mobile_web_planner" README.md AGENTS.md CLAUDE.md GEMINI.md | grep -v "mobile-web-planner" | wc -l
echo "--- .antigravity/skills 수동 복사 안내 잔존 (0 기대) ---"
grep -c "다운로드한 \`skills\` 폴더" README.md
```

기대: 둘 다 `0`.

- [ ] **Step 4: 커밋**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git add README.md AGENTS.md
git commit -m "$(cat <<'EOF'
docs: AGENTS.md 검증 절차 및 README 설치 안내 갱신 (#3)

AGENTS.md 가 지시하던 검증 명령은 실행 시 예시를 파괴하는 상태였다.
클래스 계약을 최우선 지침으로 올리고, 검증 절차를 단위 테스트 +
재생성 + git diff 불변식 확인으로 교체한다. 이모지 금지 및 Phosphor
사용법, stdlib 제약도 명시한다.

README 는 Antigravity 경로 수동 복사 안내를 install.sh 기준으로
재작성하고 구조 트리를 갱신한다.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: 통합 검증 및 PR

**Files:**
- 변경 없음 (검증 및 PR 생성)

**Interfaces:**
- Consumes: Task 1~6 전체
- Produces: PR, 이슈 #3 클로즈

- [ ] **Step 1: 설계 문서의 검증 표 10항목을 전부 실행한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent

echo "===== 1. 예시 재생성 ====="
python3 generate_doksam.py; echo "exit=$?"

echo "===== 2. 불변식 ====="
git diff --exit-code examples/ && echo "PASS: clean"

echo "===== 3. 검증기 역방향 ====="
cp generate_doksam.py /tmp/gd.bak
python3 - <<'PY'
from pathlib import Path
p = Path("generate_doksam.py")
p.write_text(p.read_text(encoding="utf-8").replace(
    '<div class="docwrap">', '<div class="docwrap bogus-class">', 1), encoding="utf-8")
PY
python3 generate_doksam.py; echo "exit=$? (1 기대)"
cp /tmp/gd.bak generate_doksam.py && rm /tmp/gd.bak
python3 generate_doksam.py >/dev/null && git diff --exit-code examples/ && echo "PASS: 원복 확인"

echo "===== 4a. 쀼어 (docs 제외 0 기대) ====="
grep -rn "쀼어" --include="*.md" --include="*.html" --include="*.py" --include="*.sh" . | grep -v "^./docs/" | wc -l

echo "===== 4b. 스킬 내 도메인 고유명 (0 기대) ====="
grep -rn "덕삼\|기획이야기" skills/ | wc -l

echo "===== 5. 이모지 (0 기대) ====="
grep -roP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}]' skills/ examples/doksam_news_storyboard.html | wc -l

echo "===== 단위 테스트 ====="
python3 -m unittest discover -s tests -v 2>&1 | tail -3
./tests/test_install.sh | tail -2

echo "===== 6-9. install.sh ====="
./install.sh --dry-run | tail -2
./install.sh | tail -2
for t in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.gemini/antigravity/skills"; do
  printf '%s -> %s\n' "$t/mobile-web-planner" "$(readlink "$t/mobile-web-planner")"
done
./install.sh | tail -2   # 멱등: skip 3건
```

기대: 1 `exit=0`, 2 `PASS: clean`, 3 `exit=1` 후 `PASS: 원복 확인`, 4a/4b/5 모두 `0`, 단위 테스트 `OK` 및 `fail=0`, install 심링크 3개가 레포 절대경로.

- [ ] **Step 2: 렌더를 눈으로 확인한다**

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
mongoose -d examples -l http://127.0.0.1:8765 &
sleep 1
echo "http://127.0.0.1:8765/doksam_news_storyboard.html"
```

브라우저로 위 URL 을 열어 확인한다.

- 슬라이드 7장이 `01 → 02 → 03 → 04 → 05 → 06.1 → 06.2` 순으로 나오는가
- 04 IA 의 mermaid mindmap 이 렌더되는가
- 06.1 / 06.2 의 목업이 슬라이드 하단에 잘리지 않는가
- 목업 헤더·액션 버튼 아이콘이 이모지가 아니라 선형 SVG 인가
- 제목의 굵기가 합성 볼드처럼 뭉개지지 않는가 (`@import` 수정 효과)
- 푸터가 `덕삼뉴스 | Ver.1.0.0` 인가 (`기획이야기` 없음)

확인 후 서버를 정리한다.

```bash
pkill -f "mongoose -d examples" || true
```

- [ ] **Step 3: 푸시하고 PR 을 만든다**

PR 본문은 파일로 쓴다 — 표와 코드 블록이 들어가므로 인라인 `-b` 로 넘기면 이스케이프가 깨진다.

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
git push origin fix/issue-3-skill-consistency
```

PR 본문을 `/tmp/pr-body.md` 에 쓴다. 아래 골격에 Step 1~2 의 **실제 출력**을 채운다 (어림짐작 금지).

```markdown
## 요약

`mobile-web-planner` 스킬의 정의·템플릿·생성 스크립트·산출물 예시를 하나의 규격으로 정합화하고, Claude Code / Codex / Antigravity 세 런타임 배포 스크립트를 추가한다.

Closes #3

## 변경

| 영역 | 내용 |
|---|---|
| 스킬 패키지 | `skills/mobile_web_planner` → `skills/mobile-web-planner`. `SKILL.md` 재작성 — 트리거형 `description`, 번호 체계 통일, 플레이스홀더, 클래스 Quick Reference, 파일 저장 출력 |
| 템플릿 | `@import` 를 `@font-face` 앞으로 이동(합성 볼드 해소), `preconnect` 정정, `.icon` 클래스 추가 |
| 검증 | `generate_doksam.py` 재작성 — 예시 재생성 + 클래스 계약 검증기(미정의 클래스 시 exit 1) |
| 예시 | 5장 → 7장. 누락된 `03 Index` / `05 General Rule` 추가, 브랜딩 제거, 이모지 → Phosphor SVG |
| 배포 | `install.sh` 신규 — 전역 3경로 심링크, `--copy` / `--project` / `--dry-run` / `--uninstall` / `--force` |
| 테스트 | `tests/test_generate.py` (stdlib unittest), `tests/test_install.sh` (임시 HOME 격리) |
| 문서 | `AGENTS.md` 검증 절차·클래스 계약·이모지 방침, `README.md` 설치 안내. `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` 최초 커밋 |

## 검증 결과

(Step 1 의 실제 출력을 붙인다)

## 범위 외

- CDN 로컬 벤더링 (Pretendard, mermaid)
- 슬라이드 반응형 재설계 — `.ppt-slide` 16:9 + `overflow:hidden` 과 `.mock` 600px 고정 높이 충돌
- 스킬 pressure 테스트

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
gh pr create \
  --base main \
  --head fix/issue-3-skill-consistency \
  --title "fix: mobile-web-planner 스킬 정합성 복구 및 3개 런타임 배포 지원 (#3)" \
  --body-file /tmp/pr-body.md
```

- [ ] **Step 4: 머지하고 이슈를 클로즈한다**

사용자가 머지를 지시한 뒤에만 실행한다.

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
gh pr merge --squash --delete-branch
git checkout main && git pull
```

머지 후 `main` 에서 검증이 여전히 통과하는지 확인한다.

```bash
cd /Users/dok123/workspace/github.com/mobile-web-planner-agent
python3 -m unittest discover -s tests 2>&1 | tail -2
python3 generate_doksam.py && git diff --exit-code examples/ && echo "main 검증 PASS"
gh issue view 3 --json state --jq .state
```

`gh pr merge` 의 `Closes #3` 로 자동 클로즈되지 않았으면 수동으로 닫는다.

```bash
gh issue close 3 --comment "PR 머지 완료. main 에서 단위 테스트 및 재생성 불변식 통과 확인."
```

- [ ] **Step 5: 작업 완료 알림**

`yd_pg` MCP 쓰기 모드로 `notify_queue` 에 한 행 insert 한다. 메시지는 알림만 보고 이해되는 수준으로 쓴다.

```sql
INSERT INTO notify_queue (message, source, channel) VALUES (
'mobile-web-planner-agent · 기획서 생성 스킬 정합성 복구 완료

[이슈 #3 / PR 머지] github.com/leeyudok/mobile-web-planner-agent
- 문제: 템플릿·예시만 새 PPT 레이아웃으로 갱신되고 생성 스크립트가 stale 해서, AGENTS.md 가 지시하는 검증 명령을 실행하면 예시가 469줄 diff 로 파괴되고 CSS 미정의 클래스 44개를 쓰는 문서가 만들어지던 상태
- generate_doksam.py 재작성: 예시 재생성 + 클래스 계약 검증기 추가. 정의 안 된 CSS 클래스를 쓰면 exit 1 로 차단. 재생성 결과가 커밋 내용과 항상 같아야 한다는 불변식 확보
- SKILL.md 정합화: 슬라이드 번호 체계 통일(01 Cover ~ 05 General Rule, 06.x 화면상세), 외부 블로그 브랜딩 제거 후 플레이스홀더화, 클래스 Quick Reference 표 추가
- 예시 스토리보드 5장 -> 7장 (누락된 Index / General Rule 슬라이드 추가), 이모지 아이콘 -> Phosphor SVG 교체
- install.sh 신규: Claude Code / Codex / Gemini(Antigravity) 세 런타임 스킬 경로에 심링크 배포. 기존 항목 덮어쓰기 방지 및 멱등 동작

다음 액션 없음. CDN 로컬 벤더링과 슬라이드 반응형은 후속 이슈 후보로 남겨둠.',
'claude-code', 'telegram');
```

---

## Self-Review

**1. Spec coverage**

| 설계 문서 항목 | 담당 Task |
|---|---|
| §4.1 디렉터리 rename | Task 1 Step 1 |
| §4.1 frontmatter / description | Task 2 Step 1 |
| §4.1 번호 체계 | Task 2 Step 1, Task 4 Step 3 |
| §4.1 플레이스홀더 | Task 2 Step 1 |
| §4.1 Quick Reference | Task 2 Step 1 |
| §4.1 금지 규칙 | Task 2 Step 1 |
| §4.1 출력 방식 | Task 2 Step 1 |
| §4.1 이모지 제거 범위 표 | Task 2 (SKILL.md), Task 4 (예시 HTML), Task 1 (`.icon` 클래스) |
| §4.1 `@import` / `preconnect` | Task 1 Step 2 |
| §4.2 예시 재생성 + 불변식 | Task 4 Step 3, Step 5 |
| §4.2 클래스 검증기 + 화이트리스트 | Task 3 |
| §4.2 stdlib 제약 | Global Constraints, Task 3 Step 1 |
| §4.3 install.sh 전 옵션 | Task 5 Step 3 |
| §4.3 멱등 / 충돌 / uninstall 규칙 | Task 5 Step 1 테스트, Step 3 구현 |
| §4.4 AGENTS.md / README.md | Task 6 |
| §4.4 `AGENTS.md`·`CLAUDE.md`·`GEMINI.md`·`.gitignore` 커밋 | 이미 커밋 `bc52970` 에서 완료 |
| §6 오류 처리 전 항목 | Task 3 Step 3 (검증 후 쓰기), Task 5 Step 3 (충돌·uninstall·`--project`) |
| §7 검증 10항목 | Task 7 Step 1~2 |

누락 없음.

**2. Placeholder scan**

"TBD" / "TODO" / "적절히 처리" / "Task N 과 유사" 없음. 모든 코드 스텝에 실제 코드가 들어 있다. Task 4 의 Phosphor `path` 는 실제 조회한 값이다.

**3. Type consistency**

`extract_style` / `defined_classes` / `used_classes` / `undefined_classes` / `build_html` / `main` / `WHITELIST` / `TEMPLATE_PATH` / `OUTPUT_PATH` / `PROJECT_NAME` / `VERSION` / `DOC_DATE` / `DOC_AUTHOR` — Task 3 의 정의와 Task 4·7 의 사용, `tests/test_generate.py` 의 참조가 모두 일치한다. `install.sh` 의 옵션 이름이 Task 5 테스트·구현·Task 6 README 안내에서 일치한다.
