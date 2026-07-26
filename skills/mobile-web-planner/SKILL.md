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

아래 실행 순서를 끝까지 수행한다.

1. 요청에서 프로젝트명, 사용자 유형, 플랫폼, 기능과 제약을 추출한다.
2. 결과를 크게 바꾸는 누락 정보만 질문한다. 안전하게 유추 가능한 항목은
   가정으로 정리하고 작업을 계속한다.
3. IA와 화면 목록을 확정한 뒤 아래 슬라이드 순서로 Storyboard를 작성한다.
4. 저장 후 이 Skill 디렉터리의
   `scripts/validate_storyboard.py <생성한 HTML 경로>`를 실행한다.
5. 위반이 있으면 산출물을 수정하고 검증을 다시 실행한다. 위반이 0건이 될
   때까지 반복한다.
6. 브라우저 또는 HTML 렌더링 도구를 사용할 수 있으면 각 슬라이드의 잘림,
   겹침과 가독성을 확인하고 발견한 문제를 수정한 뒤 다시 검증한다.
7. 구조 검증을 통과한 파일 경로와 결과에 영향을 준 주요 가정을 전달한다.

기존 Storyboard 수정 요청에서는 기존 화면 ID를 가능한 한 유지한다. 삭제된
ID를 새 화면에 재사용하지 않고, 추가 화면에는 새 ID를 부여한다. 변경 범위
밖의 디자인은 보존하고 `{{VERSION}}`과 Document History를 갱신한 뒤 전체
문서를 다시 검증한다.

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

**`06.x` 순서는 사용자가 기능을 나열한 순서를 따른다.** 중요도나 자기 판단으로 재배열하지 않는다 — 같은 요청에 항상 같은 순서가 나와야 사용자가 자기가 적은 순서대로 나왔는지 바로 확인할 수 있고, 문서를 다시 생성해도 순서가 흔들리지 않는다.

- 사용자가 나열하지 않았지만 필요한 진입 화면(메인 홈 등)은 **`06.1`** 에 둔다. 나열한 기능은 그 뒤에 적힌 순서대로 `06.2` 부터 이어서 매긴다.
- 나열 순서가 정보구조상 부자연스러워도 순서를 바꾸지 않는다. 대신 `04 IA` 다이어그램의 노드 배열을 `06.x` 순서에 맞춘다.
- `03 Index` 표의 행 순서, `04 IA` 의 노드 순서, `06.x` 슬라이드 순서 **세 곳이 모두 같아야 한다.**

**`06.x` 슬라이드에는 `ppt-meta-bar` 로 화면 위치를 적는다.** 진입점부터 그 화면까지의 경로를 `>` 로 잇는다 — 예: `홈 > 게시판 > 글 상세`. `04 IA` 의 연결 관계에서 그대로 끌어온다. 이 줄이 있으면 IA 슬라이드를 넘겨보지 않아도 화면이 앱 어디에 있는지 알 수 있다. `01`~`05` 슬라이드에는 넣지 않는다 — 화면이 아니므로 위치가 없다.

**화면마다 화면 ID 를 부여하고 이동을 그 ID 로 가리킨다.** 슬라이드 번호(`06.2`)는 화면이 추가되면 밀리므로 참조가 어긋나고, 팝업처럼 슬라이드가 없는 대상은 가리킬 수도 없다.

- 형식은 `<서비스약어>-<기능>-<3자리>` 다. 예: `DTC-BOARD-001`, `DTC-NOTICE-002`.
  - 서비스약어는 프로젝트명에서 만든다 (덕삼테니스클럽 → `DTC`). 대문자 2~4자.
  - 기능은 영문 대문자 단어 하나 (`MAIN` `BOARD` `NOTICE` `VOTE` `AWARD` `BOOKING` `MEMBER`).
  - 같은 기능의 화면이 여럿이면 뒤 3자리로 구분한다 — 목록 `001`, 상세 `002`.
- `ppt-meta-id` 에 표시한다. `03 Index` 표에도 ID 열을 둔다.
- **이동 서술은 이름과 ID 를 함께 적는다** — `글 상세로 이동 (DTC-BOARD-002)`. ID 만 쓰면 읽기 어렵다.
- 팝업·바텀시트에도 ID 를 준다. 슬라이드가 없어도 참조 대상이므로 필요하다.
- **본문에서 참조한 ID 는 모두 이 문서 안에 정의되어 있어야 한다.** 정의 없는 ID 를 가리키면 끊어진 참조다.

화면 상세 슬라이드는 좌측 `ppt-wireframe` 에 모바일 목업을, 우측 `ppt-desc-panel` 에 설명을 넣는다. 목업 위의 `pointer-badge` 와 설명 리스트의 `desc-num` 을 **1:1 로 대응**시킨다. 목업이 1개면 `1, 2, 3` ↔ `①②③`, 2개 이상이면 2단 번호(`1-1`, `2-1`)를 양쪽에 같이 쓴다. 설명 항목 수와 배지 수가 같아야 한다 — `mock-footer` 처럼 `mock-body` 밖의 요소를 설명하는 항목도 배지를 빠뜨리지 않는다(아래 마크업 참고).

`pointer-badge` 는 `left:2px` 로 둔다. `mock-body` 좌측 여백이 배지 자리이며 폭은 템플릿이 정한다 — 목업 1개면 28px, 2개 이상이면 2단 번호가 넓어지므로 34px 다. **`mock-body` 에 인라인 `padding` 을 줄 때는 `padding-left` 를 이 값 이상으로 유지한다**(목업 1개 28px, 2개 이상 34px) — 그러지 않으면 배지가 본문 텍스트를 가린다.

## 목업 여러 개 배치

각 `06.x` 화면이 아래 네 조건 중 **하나라도 해당하면 `ppt-wireframe` 안에 `mock` 을 2개 놓는다.** 화면을 억지로 여러 슬라이드로 쪼개지 않는다.

| 조건 | 목업 2개 구성 |
|---|---|
| 목록과 그 상세를 같은 기능에서 다룬다 | 목록 / 상세 |
| 사용자 입력을 받는다 | 입력 전 / 입력 후 (또는 검증 실패) |
| 데이터 유무에 따라 표시가 크게 달라진다 | 데이터 있음 / 빈 상태 |
| 다단계 플로우의 중간 단계다 | 단계 N / 단계 N+1 |

**해당하지 않으면 1개로 둔다.** 단순 조회·나열 화면(예: 회원 목록, 설정 메뉴)에 억지로 2개를 넣지 않는다 — 비교할 변형이 없으면 두 번째 목업은 같은 화면의 중복일 뿐이다.

- **개수는 최대 4개.** 템플릿이 개수를 감지해 축소율을 조절한다(1개: 그대로, 2~3개: 90%, 4개: 68%). 5개 이상은 잘리므로 슬라이드를 나눈다.
- **각 목업에 `mock-caption` 으로 라벨을 붙인다** — `mock` 의 마지막 자식으로 두면 프레임 바로 아래에 표시된다. 무엇의 변형인지 알 수 없으면 비교 슬라이드의 의미가 없다.
- **`pointer-badge` 번호는 2단이다** — `<목업번호>-<요소번호>`. 첫 목업의 요소는 `1-1` `1-2`, 두 번째 목업은 `2-1` `2-2` 로 매긴다. 목업이 몇 번째인지가 번호에서 바로 읽히므로 "어느 목업의 항목인지" 를 따로 적을 필요가 없다.
- **`desc-num` 도 같은 2단 표기를 쓴다.** 원문자(①②③)는 2단을 표현할 수 없으므로 목업이 2개 이상인 슬라이드에서는 `1-1` 처럼 평문으로 적는다. 목업이 1개면 지금처럼 원문자를 쓴다.
- 설명 리스트는 목업 순서대로 묶어 적는다 — `1-1` `1-2` 를 먼저, 그다음 `2-1` `2-2`.
- **각 목업의 화면 ID 는 `mock-caption` 에 이름과 함께 적는다** — `<div class="mock-caption">게시글 상세 (DTC-BOARD-002)</div>`. 목업이 2개면 화면도 2개인데 `ppt-meta-id` 는 슬라이드에 한 칸뿐이므로, 두 번째 화면의 ID 는 캡션이 정의 자리다. 캡션에 안 적으면 설명에서 `(DTC-BOARD-002)` 로 참조해도 문서 안에 정의가 없는 끊어진 참조가 된다.
- **`ppt-meta-id` 에는 그 슬라이드의 대표 화면, 즉 첫 목업의 ID 를 둔다.** `ppt-meta-value` 의 위치도 첫 목업 기준으로 적는다.
- 목업 간 간격·정렬·축소는 템플릿이 처리한다. `ppt-wireframe` 이나 `mock` 에 인라인 `width`·`transform`·`zoom`·`margin` 을 주지 않는다.

**팝업·바텀시트는 부분 목업으로 그린다.** 전체 화면 목업으로 그리면 별개 화면처럼 보이고, 본 목업 안에 인라인으로 그리면 열리기 전 상태를 함께 보여줄 수 없다.

- `<div class="mock mock-partial">` 로 만든다. 높이가 줄어 화면 일부만 덮는다는 사실이 그림으로 전달된다.
- 위쪽 배경 힌트는 인라인 `style` 로 회색 블록을 채운다 — 팝업 뒤에 화면이 있다는 표시다.
- 배지는 **부모-자식 관계**로 매긴다. 팝업을 여는 버튼이 `2-3` 이면 팝업 자체는 `3-1` 이 아니라 여는 쪽 번호를 이어받아 표기하고, 설명에서 어느 버튼이 여는지 명시한다.
- 팝업에도 화면 ID 를 준다. 여는 쪽 설명에 `탭 시 서류등록 바텀시트 노출 (DTC-DOC-101)` 처럼 적는다.
- `mock-caption` 은 부분 목업에도 붙인다 — 무엇의 팝업인지 알 수 없으면 의미가 없다.

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
| `ppt-meta-bar` | 상단 바 아래 메타 줄. **화면 상세(`06.x`)에만** 둔다 |
| `ppt-meta-label` | 메타 줄의 회색 라벨 칸 (`Location`) |
| `ppt-meta-value` | 메타 줄의 값 칸. 넘치면 말줄임 |
| `ppt-meta-id` | 메타 줄 우측 화면 ID 칸 |
| `ppt-content` | 중간 영역 컨테이너 |
| `ppt-body-full` | 좌우 분할하지 않는 통짜 콘텐츠 (01~05) |
| `ppt-wireframe` | 좌측 와이어프레임 패널 (06.x). **`mock` 을 1개 이상(최대 4개) 배치할 수 있다** — 개수에 따라 축소율과 간격을 템플릿이 자동 조절한다 |
| `ppt-desc-panel` | 우측 설명 패널 (06.x) |
| `ppt-desc-header` | 설명 패널 헤더 |
| `ppt-desc-body` | 설명 패널 본문 |
| `desc-list` | 설명 리스트 (`ul`) |
| `desc-num` | 설명 항목 번호 (①②③) |
| `pointer-badge` | 목업 위 accent 컬러 번호 배지. `desc-num` 과 1:1 대응. **`left:2px`** 로 둘 것 — `mock-body` 좌측 여백(1개 28px · 2개 이상 34px)이 배지 자리다. 폭은 내용에 맞춰 늘어난다. 음수 `left` 는 `mock-body`·`mock-screen` 의 overflow 에 절반이 잘린다 |
| `mock` | 모바일 목업 외곽 프레임. `ppt-wireframe` 안에 여러 개 둘 수 있다 |
| `mock-caption` | 목업 라벨. `mock` 의 마지막 자식으로 두면 프레임 아래에 표시된다. 목업이 2개 이상이면 필수이고, 라벨과 함께 그 목업의 화면 ID 를 적는다 — `필터 선택됨 (DTC-FILTER-002)` |
| `mock-partial` | 부분 목업(팝업·바텀시트). `mock` 과 **함께** 쓴다 — `class="mock mock-partial"` |
| `mock-screen` | 목업 화면 |
| `mock-status` | 목업 상태바 |
| `mock-header` | 목업 헤더 |
| `mock-body` | 목업 본문 |
| `mock-footer` | 목업 하단 탭 바 |
| `mock-tab` | 하단 탭 항목. 활성 탭에 `active` 추가 |
| `ppt-footer` | 하단 accent 컬러 푸터 바 |
| `<code>` (클래스 아님 · 엘리먼트) | 디자인 시스템 컴포넌트명 인라인 표기 |
| `icon` | Phosphor 인라인 SVG 아이콘 |
| `mermaid` | IA 다이어그램. 도형은 mermaid.js 가 렌더하고, 슬라이드를 채우는 크기 규칙만 템플릿이 갖는다. `ppt-body-full` 의 **유일한 자식**일 때 크기 규칙이 적용되므로 텍스트와 섞지 않는다 |

## 저장 전 자체 점검

파일을 저장하기 전에 완성된 마크업을 훑으며 아래 여덟 가지를 센다. 어긋나는 항목이 있으면 저장 전에 고친다. 템플릿의 CSS 를 그대로 옮기지 않고 다시 썼더라도 이 점검은 그대로 수행한다.

1. **클래스** — 산출물에 등장하는 `class` 값을 전부 모아 Class Quick Reference 표와 대조한다. 표에 없는 이름이 하나라도 있으면 그 `class` 를 지우고 같은 효과를 인라인 `style` 로 옮긴다. 표에 없는 클래스는 CSS 정의가 없어 아무 스타일도 적용되지 않는다.
2. **이모지** — 이모지 개수가 0 인가. 하나라도 있으면 Phosphor 인라인 SVG 아이콘으로 바꾸거나 지운다. `‹` `⋮` 같은 타이포그래피 문자는 이모지가 아니므로 그대로 둔다.
3. **배지 좌표** — 모든 `pointer-badge` 의 `left` 값이 `2px` 인가. 다른 값이 하나라도 있으면 `2px` 로 바꾼다. 배지가 겹쳐 보이면 `left` 대신 `top` 을 조정한다.
4. **배지 개수** — 슬라이드마다 `pointer-badge` 개수와 `desc-num` 개수가 같은가. 다르면 모자란 쪽을 채워 1:1 로 맞춘다.
5. **화면 순서** — `03 Index` 표의 행 순서, `04 IA` 의 노드 순서, `06.x` 슬라이드 순서 세 곳이 같은가. 그리고 그 순서가 사용자가 기능을 나열한 순서와 같은가(진입 화면은 `06.1`). 다르면 사용자 나열 순서를 기준으로 세 곳을 함께 맞춘다.
6. **목업 개수** — `06.x` 마다 목업 트리거 표(위 `## 목업 여러 개 배치`)를 대조한다. 트리거에 해당하는데 `mock` 이 1개면 2개로 늘리고 `mock-caption` 을 붙인다. 해당하지 않는데 2개면 1개로 줄인다.
7. **화면 위치** — `06.x` 마다 `ppt-meta-bar` 가 있고 값이 `04 IA` 의 경로와 맞는가. `01`~`05` 에는 없어야 한다.
8. **화면 ID** — `06.x` 마다 `ppt-meta-id` 가 있는가. 목업이 2개 이상인 슬라이드는 각 `mock-caption` 에도 그 목업의 ID 가 적혀 있는가. 본문에서 참조한 ID 를 모아 `ppt-meta-id` 와 `mock-caption` 에 정의된 ID 집합과 대조한다 — 어느 쪽에도 없는 ID 가 하나라도 있으면 그 화면을 추가하거나 참조를 고친다.

# Icons

**이모지를 아이콘으로 쓰지 않는다.** 아이콘이 필요하면 Phosphor Icons(MIT) 의 `path` 만 인라인 SVG 로 넣는다.

```html
<svg class="icon" viewBox="0 0 256 256"><path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"/></svg>
```

`path` 는 `https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/<name>.svg` 에서 가져온다. 뒤로가기 `‹` 나 케밥 메뉴 `⋮` 같은 타이포그래피 문자는 그대로 써도 된다.

# Output

`resources/template.html` 의 `<head>` 전체 — `preconnect` 링크, mermaid `<script>` 태그, `mermaid.initialize({...})` 설정, `<style>` 블록 — 를 그대로 인라인한 단일 HTML 파일을 만든다. `<style>` 만 가져오면 `04 Information Architecture` 슬라이드의 `mermaid` 다이어그램이 렌더러 없이 원문 텍스트로 남는다. 채팅에 코드 블록으로 출력하지 않는다 — 사용 중인 런타임의 파일 쓰기 수단으로 `<프로젝트명>_storyboard.html` 로 저장하고, 저장 경로를 사용자에게 알린다.

`scripts/validate_storyboard.py`의 종료 코드가 0이 아닌 파일은 완료로 간주하지
않는다. 구조 검증을 통과하기 전에는 최종 산출물로 전달하지 않는다.

# Markup

## 화면 상세 (06.x) — 좌우 분할

```html
<div class="ppt-slide">

  <div class="ppt-top-bar">
    <div class="ppt-top-no">NO. 06.1</div>
    <div class="ppt-top-title">Main Home</div>
    <div class="ppt-top-proj">{{PROJECT_NAME}}</div>
  </div>

  <div class="ppt-meta-bar">
    <div class="ppt-meta-label">Location</div>
    <div class="ppt-meta-value">홈</div>
    <div class="ppt-meta-id">DTC-MAIN-001</div>
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

좌측 패널에 `mock` 을 나란히 두고 각각 `mock-caption` 으로 라벨을 붙인다. 배지 번호는 2단이다 — 첫 목업이 `1-1`·`1-2`, 두 번째 목업이 `2-1`. 축소율과 간격은 템플릿이 처리하므로 인라인으로 크기를 주지 않는다. 캡션에는 라벨과 함께 그 목업의 화면 ID 를 적어 두 번째 화면의 ID 도 문서 안에 정의된다.

```html
<div class="ppt-wireframe">

  <div class="mock">
    <div class="mock-screen">
      <div class="mock-status"></div>
      <div class="mock-header">필터</div>
      <div class="mock-body" style="position:relative;">
        <span class="pointer-badge" style="position:absolute; top:20px; left:2px; z-index:10;">1-1</span>
        <!-- 선택 전 목록 -->
        <span class="pointer-badge" style="position:absolute; top:200px; left:2px; z-index:10;">1-2</span>
        <!-- 적용 버튼 (비활성) -->
      </div>
    </div>
    <div class="mock-caption">필터 기본 (DTC-FILTER-001)</div>
  </div>

  <div class="mock">
    <div class="mock-screen">
      <div class="mock-status"></div>
      <div class="mock-header">필터</div>
      <div class="mock-body" style="position:relative;">
        <span class="pointer-badge" style="position:absolute; top:20px; left:2px; z-index:10;">2-1</span>
        <!-- 선택된 칩이 강조된 목록 -->
      </div>
    </div>
    <div class="mock-caption">필터 선택됨 (DTC-FILTER-002)</div>
  </div>

</div>

<div class="ppt-desc-panel">
  <div class="ppt-desc-header">Description (화면설명)</div>
  <div class="ppt-desc-body">
    <ul class="desc-list">
      <li><span class="desc-num">1-1</span> <div><b>필터 목록 (기본 상태)</b><br>미선택 시 전체 조건 노출 <code>ChipGroup</code></div></li>
      <li><span class="desc-num">1-2</span> <div><b>적용 버튼 (기본 상태)</b><br>선택 0건이면 비활성 <code>Button (disabled)</code></div></li>
      <li><span class="desc-num">2-1</span> <div><b>필터 목록 (선택됨)</b><br>선택 항목 Primary 강조, 상단 고정 <code>ChipGroup (selected)</code></div></li>
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
