# mobile-web-planner 스킬 정합성 복구 및 크로스런타임 배포 — 설계

- 이슈: [#3](https://github.com/leeyudok/mobile-web-planner-agent/issues/3)
- 브랜치: `fix/issue-3-skill-consistency`
- 작성일: 2026-07-26

## 1. 목표

`mobile-web-planner` 스킬을 Claude Code · Codex · Gemini(Antigravity) 세 런타임에서 동일하게 사용해, 도메인 무관하게 모바일 화면설계서(PPT 스타일 단일 HTML 스토리보드)를 생성할 수 있게 한다.

현재는 스킬 정의 · 템플릿 · 생성 스크립트 · 산출물 예시가 서로 다른 규격을 참조해 동작이 깨져 있고, 배포 수단이 없다. 이 작업은 **기존 설계를 유지한 채 정합성만 복구**한다. 새 기능이나 레이아웃 재설계는 하지 않는다.

## 2. 현재 구조와 결함 요약

```
skills/mobile_web_planner/
  SKILL.md                  페르소나 + 워크플로 + 슬라이드 마크업 예시 (85행)
  resources/template.html   PPT 16:9 슬라이드 프레임 CSS (252행)
generate_doksam.py          예시 생성 스크립트 (258행)
examples/
  doksam_news_storyboard.html  산출물 예시 · 슬라이드 5장 (501행)
  mobile_news_plan.md
```

핵심 결함은 커밋 `b507cae` 에서 템플릿·예시만 새 PPT 레이아웃으로 전환하고 `generate_doksam.py` 가 따라가지 않은 데서 비롯한다. 전체 목록은 이슈 #3 참조.

실측 근거:

| 측정 | 결과 |
|---|---|
| `generate_doksam.py` 실행 후 예시 diff | 469줄 |
| 커밋된 예시 슬라이드 수 | 5장 (`NO.01` `NO.02` `NO.03` `NO.3.1` `NO.3.2`) |
| 스크립트 산출물 슬라이드 수 | 1장, PPT 프레임 미사용 |
| 스크립트 산출물의 CSS 미정의 클래스 | 44개 + `var(--navy-deep)` |
| 커밋된 예시의 CSS 미정의 클래스 | `mermaid` 1개 (JS 전용, 정상) |

## 3. 아키텍처

세 개의 독립 단위로 분리한다. 각 단위는 명확한 하나의 책임을 갖고, 나머지 단위의 내부를 몰라도 이해·검증할 수 있다.

```
┌─────────────────────────────────────────────┐
│ 1. 스킬 패키지 (단일 원본)                   │
│    skills/mobile-web-planner/               │
│      SKILL.md              생성 규약         │
│      resources/template.html  렌더 계약      │
└─────────────────────────────────────────────┘
        │ 참조                    ▲ 심링크/복사
        ▼                         │
┌──────────────────────┐  ┌──────────────────────┐
│ 2. 검증 도구          │  │ 3. 배포 도구          │
│    generate_doksam.py│  │    install.sh        │
│    예시 재생성 +      │  │    3개 런타임 경로에   │
│    클래스 계약 검증   │  │    스킬 노출          │
└──────────────────────┘  └──────────────────────┘
```

### 계약 (contract)

- **`template.html` 이 CSS 클래스의 유일한 정의처다.** `SKILL.md` 와 산출물은 여기 정의된 클래스만 사용한다. 이 계약을 기계적으로 강제하는 것이 검증기의 역할이다.
- **`SKILL.md` 는 클래스 목록을 자체적으로 제시한다.** 에이전트가 `template.html` 을 읽지 않아도 올바른 클래스를 쓸 수 있어야 한다. (읽는 편이 낫지만, 안 읽었을 때 창작하는 것이 현재의 실패 모드다.)
- **`install.sh` 는 스킬 내용을 알지 못한다.** 디렉터리를 경로에 노출하는 일만 한다.

## 4. 단위별 설계

### 4.1 스킬 패키지 — `skills/mobile-web-planner/`

디렉터리를 `mobile_web_planner` → `mobile-web-planner` 로 rename 한다 (frontmatter `name` 과 일치, 스킬 네이밍 규약).

#### `SKILL.md` 변경

**frontmatter**

```yaml
---
name: mobile-web-planner
description: Use when the user asks for a mobile web/app screen design document, storyboard, wireframe, IA, or 화면설계서/기획서 for any domain (shopping, community, booking, news, ...) — produces a single self-contained HTML file of PPT-style 16:9 slides.
---
```

`Use when...` 트리거형으로 전환한다. 존재하지 않는 "캡쳐 이미지 모방" 서술을 제거한다. 한국어 트리거어(`기획서`, `화면설계서`, `스토리보드`, `와이어프레임`)를 포함해 한국어 요청에도 매칭되게 한다.

**슬라이드 번호 체계** — `SKILL.md` 와 예시를 하나로 통일한다.

| NO. | 슬라이드 | 좌우 분할 |
|---|---|---|
| 01 | Cover | 없음 (`ppt-body-full`) |
| 02 | Document History | 없음 |
| 03 | Index | 없음 |
| 04 | Information Architecture | 없음 (mermaid) |
| 05 | General Rule | 없음 |
| 06.1 ~ 06.n | 화면 상세 (IA의 모든 주요 화면) | 있음 (`ppt-wireframe` + `ppt-desc-panel`) |

기존 `NO.05` 다음 `NO.3.x` 모순을 해소한다.

**플레이스홀더** — 마크업 예시의 하드코딩 브랜딩을 치환한다.

| 위치 | 기존 | 변경 |
|---|---|---|
| `SKILL.md` `ppt-top-proj` | `덕삼뉴스 기획이야기 \|` | `{{PROJECT_NAME}}` |
| `SKILL.md` `ppt-footer` | `<외부 블로그명>'s blog 기획이야기 \| Ver.1.0.0` | `{{PROJECT_NAME}} \| Ver.{{VERSION}}` |
| `SKILL.md` 페르소나 | `'덕삼이'` | 중립 서술 (고유명 제거) |
| 예시 `ppt-footer` ×5 | `덕삼뉴스 기획이야기 \| Ver.1.0.0` | `덕삼뉴스 \| Ver.1.0.0` |

`<외부 블로그명>'s blog 기획이야기` 는 이 레포와 무관한 외부 블로그 브랜딩이므로 **완전히 제거**한다. 플레이스홀더는 `{{PROJECT_NAME}}` · `{{VERSION}}` 두 개로 충분하며, 별도의 푸터 문구 슬롯을 두지 않는다 (푸터 = 프로젝트명 + 버전).

`SKILL.md` 에 플레이스홀더 채우는 규칙을 명시한다: 사용자가 프로젝트명을 주면 그것을, 안 주면 요청 내용에서 유추하고 `VERSION` 은 `1.0.0` 을 기본값으로 한다. 상단·하단 모두 같은 `{{PROJECT_NAME}}` 을 쓴다.

**Quick Reference** — 사용 가능한 클래스 전체 표를 추가한다.

| 클래스 | 용도 |
|---|---|
| `docwrap` | 전체 슬라이드 컨테이너 (`body` 직하위 1개) |
| `ppt-slide` | 슬라이드 1장 (16:9) |
| `ppt-top-bar` / `ppt-top-no` / `ppt-top-title` / `ppt-top-proj` | 상단 바 / 회색 번호 / 제목 / 우측 프로젝트명 |
| `ppt-content` | 중간 영역 (좌우 분할 컨테이너) |
| `ppt-body-full` | 분할하지 않는 통짜 콘텐츠 (표지·이력·목차·IA·공통규칙) |
| `ppt-wireframe` | 좌측 와이어프레임 패널 |
| `ppt-desc-panel` / `ppt-desc-header` / `ppt-desc-body` | 우측 설명 패널 / 헤더 / 본문 |
| `desc-list` / `desc-num` | 설명 리스트 / ①②③ 번호 |
| `pointer-badge` | 와이어프레임 위 주황 번호 배지 (`desc-num` 과 1:1 대응) |
| `mock` / `mock-screen` / `mock-status` / `mock-header` / `mock-body` / `mock-footer` | 모바일 목업 프레임 / 화면 / 상태바 / 헤더 / 본문 / 하단 |
| `mock-tab` (`.active`) | 하단 탭 항목 |
| `ppt-footer` | 하단 주황 푸터 바 |
| `code` | 디자인 시스템 컴포넌트명 표기용 인라인 태그 |
| `mermaid` | IA 다이어그램 (CSS 없음 · mermaid.js 가 렌더) |

**금지 규칙** — 표 아래에 명시한다: 위 목록에 없는 클래스를 새로 만들지 않는다. 목업 내부의 세부 스타일은 인라인 `style` 로 처리한다. (실제 실패가 "없는 클래스 창작" 이므로 규칙 형태로 명시하고, 검증기로 기계 강제한다.)

**출력 방식** — 채팅 코드 블록 출력 → 파일 저장으로 변경한다. 런타임 중립적으로 기술한다: "사용 중인 런타임의 파일 쓰기 수단으로 `<프로젝트명>_storyboard.html` 로 저장하고 경로를 사용자에게 알린다."

**이모지** — 헤딩의 `👑` `📋` `📝` 를 제거한다.

#### `resources/template.html` 변경

1. `@import` (29행) 를 `@font-face` (24~28행) 앞으로 이동한다. 현재는 CSS 스펙상 무시되어 Regular 400 만 로드되고 `font-weight: 800` 이 전부 합성 볼드로 렌더된다.
2. 미사용 `<link rel="preconnect" href="https://cdnjs.cloudflare.com">` 을 제거한다. 실제 CDN 호스트는 `cdn.jsdelivr.net` 이므로 그쪽으로 `preconnect` 를 건다.
3. 아이콘용 이모지를 Phosphor 인라인 SVG 로 교체한다 (`github.com/phosphor-icons/core`, MIT). 빌드 파이프라인이 없는 단일 HTML 이므로 `path` 만 추출해 인라인 `<svg>` 로 embed 한다.

**이모지 제거 범위** — 시각 산출물과 스킬 정의에 한정한다.

| 파일 | 현재 이모지 | 처리 |
|---|---|---|
| `skills/**/SKILL.md` | `👑` `📋` `📝` (헤딩 장식) | 제거 |
| `examples/doksam_news_storyboard.html` | `🔍` `🔔` `🔗` `⭐` (목업 액션 아이콘) | Phosphor SVG 로 교체 |
| `README.md` | `📱🚀📁📦📂📜🛠` (문서 장식·구조 트리) | 범위 외 — 마크다운 문서이며 시각 산출물이 아니다 |
| `examples/mobile_news_plan.md` | `📱` `➡` (문서 장식·플로우 화살표) | 범위 외 — 동일 |

`ppt-*` / `mock-*` 클래스 정의와 레이아웃 수치는 변경하지 않는다.

### 4.2 검증 도구 — `generate_doksam.py`

현재는 템플릿의 `<style>` 만 추출해 하드코딩된 구 레이아웃 본문을 출력한다. 다음 두 책임으로 재작성한다.

**책임 1 — 예시 재생성.** 현행 PPT 레이아웃(4.1의 번호 체계, 슬라이드 7장: Cover / History / Index / IA / General Rule / 06.1 Main Home / 06.2 Article Detail) 을 `template.html` 의 `<style>` 을 주입해 생성한다. 슬라이드 본문은 스크립트 안에 데이터로 유지한다 — 예시는 고정 산출물이므로 템플릿 엔진을 도입하지 않는다.

**불변식**: 스크립트를 실행한 뒤 `git diff --exit-code examples/` 가 clean 해야 한다. 즉 커밋된 예시는 항상 스크립트 출력과 동일하다. 이것이 stale 재발을 막는 장치다.

**책임 2 — 클래스 계약 검증.** 생성된 HTML 의 모든 `class="..."` 토큰을 수집해 `template.html` 의 CSS 셀렉터에 정의되지 않은 것을 검출한다.

- 미정의 클래스가 있으면 stderr 에 전부 나열하고 `exit 1`
- 화이트리스트: `mermaid` (JS 가 렌더, CSS 불필요)
- 통과 시 생성 경로와 슬라이드 수를 stdout 에 출력하고 `exit 0`

구현 제약: 이 맥북의 Homebrew Python 3.14 는 pyexpat dlopen 이 깨져 있어 외부 라이브러리를 쓸 수 없다. **stdlib(`re`, `pathlib`, `sys`) 만으로 구현한다.** 클래스 추출은 정규식으로 충분하다 (입력이 우리가 생성한 HTML 이므로 임의 HTML 파싱 견고성이 필요 없다).

레포 루트 기준 상대경로 동작(`Path(__file__).resolve().parent`) 은 커밋 `94b6397` 에서 이미 확보되었으므로 유지한다.

### 4.3 배포 도구 — `install.sh`

bash, 외부 의존성 없음. 스킬 디렉터리를 각 런타임이 인식하는 경로에 노출한다.

```
./install.sh                        전역 3경로에 심링크
./install.sh --copy                 심링크 대신 복사
./install.sh --project <dir>        해당 레포의 프로젝트 스킬 경로에
./install.sh --dry-run              수행할 작업만 출력
./install.sh --uninstall            설치 제거
./install.sh --force                충돌하는 기존 항목을 교체
```

**타깃 경로**

| 모드 | 경로 | 대상 런타임 |
|---|---|---|
| 전역 | `~/.agents/skills/mobile-web-planner` | Codex, Gemini CLI (공용 alias) |
| 전역 | `~/.claude/skills/mobile-web-planner` | Claude Code |
| 전역 | `~/.gemini/antigravity/skills/mobile-web-planner` | Antigravity |
| `--project <dir>` | `<dir>/.claude/skills/mobile-web-planner` | Claude Code |
| `--project <dir>` | `<dir>/.antigravity/skills/mobile-web-planner` | Antigravity |

**동작 규칙**

- 부모 디렉터리가 없으면 `mkdir -p` 로 생성한다 (이 맥북에 `~/.gemini/antigravity/skills` 는 아직 없다).
- 심링크는 **절대경로**로 건다. 레포를 어디에 두어도 동작해야 한다.
- **멱등**: 타깃이 이미 우리 원본을 가리키는 심링크면 `skip` 을 출력하고 넘어간다.
- **충돌 시 파괴하지 않는다**: 타깃이 존재하되 (a) 다른 곳을 가리키는 심링크이거나 (b) 실제 디렉터리/파일이면, 경고를 출력하고 `exit 1` 한다. `--force` 를 준 경우에만 교체한다. 사용자가 손으로 만든 스킬을 조용히 덮어쓰는 사고를 막는다.
- `--uninstall` 은 **우리 원본을 가리키는 심링크만** 제거한다. 실제 디렉터리(= `--copy` 설치분 또는 남의 것)는 경로를 안내하고 손대지 않는다. 파괴적 삭제를 스크립트가 임의로 수행하지 않는다.
- 각 작업을 `symlink` / `copy` / `skip` / `conflict` / `remove` 로 한 줄씩 출력하고, 마지막에 성공·skip·실패 건수를 요약한다.

### 4.4 런타임 진입 문서

`AGENTS.md`(원본) ← `CLAUDE.md` · `GEMINI.md` 가 `@AGENTS.md` 를 참조하는 구조가 이미 워킹트리에 있으나 커밋되지 않았다. 이번 작업에 포함해 커밋한다. `.gitignore` 의 미커밋 변경(`lastworks.resume`, `.DS_Store` 추가) 도 함께 커밋한다.

`AGENTS.md` 갱신 사항:

- 디렉터리 구조를 `skills/mobile-web-planner/` 로 반영
- 검증 절차를 새 스크립트 기준으로 교체 — "`python generate_doksam.py` 실행 후 `git diff --exit-code examples/` 가 clean 한지 확인. 미정의 클래스가 있으면 스크립트가 exit 1 로 알린다."
- 클래스 계약(`template.html` 이 유일한 정의처, 없는 클래스 창작 금지) 을 에이전트 지침에 명시
- 이모지 아이콘 금지 및 Phosphor 사용 방침 명시

`README.md` 갱신 사항: 3개 런타임 설치 안내를 `install.sh` 기준으로 재작성, 구조 트리 갱신.

## 5. 데이터 흐름 (스킬 실행 시)

```
사용자: "반려동물 용품 쇼핑몰 모바일웹 기획해줘"
  │
  ├─ 런타임이 description 트리거로 SKILL.md 로드
  │
  ├─ 워크플로 수행
  │    01 Cover → 02 History → 03 Index
  │    → 04 IA (mermaid 로 화면 트리 작성)
  │    → 05 General Rule
  │    → 06.1..06.n 화면 상세 (04의 모든 주요 화면, 누락 없이)
  │
  ├─ 각 화면 상세: 좌측 mock 목업 + pointer-badge ①②③
  │                우측 desc-list 의 desc-num ①②③ 과 1:1 대응
  │
  ├─ template.html 의 <style> 을 인라인한 단일 HTML 조립
  │    (Quick Reference 표의 클래스만 사용)
  │
  └─ <프로젝트명>_storyboard.html 로 저장 + 경로 안내
```

## 6. 오류 처리

| 상황 | 처리 |
|---|---|
| 검증기가 미정의 클래스 발견 | 클래스명 전부 stderr 출력, `exit 1`. 부분 산출물을 남기지 않는다 (검증 통과 후 파일 쓰기) |
| `install.sh` 타깃 충돌 | 경고 + `exit 1`. `--force` 없이는 덮어쓰지 않는다 |
| `install.sh --uninstall` 대상이 실제 디렉터리 | 경로 안내만 하고 삭제하지 않는다 |
| `--project` 대상이 디렉터리가 아님 | 즉시 `exit 1` |
| 스킬 실행 시 IA 화면 수와 상세 슬라이드 수 불일치 | `SKILL.md` 에 자체 점검 항목으로 명시 (기계 강제는 범위 외) |

## 7. 검증

| # | 검증 | 통과 기준 |
|---|---|---|
| 1 | `python generate_doksam.py` | `exit 0`, 슬라이드 7장 보고 |
| 2 | `git diff --exit-code examples/` (1 직후) | clean |
| 3 | 검증기 역방향 — 없는 클래스를 일시 주입해 실행 | `exit 1` + 해당 클래스명 출력 |
| 4a | `grep -rn "기획이야기" .` (docs 제외) | 0건 — 외부 블로그 브랜딩(`기획이야기`)이 남아있는지 확인하는 durable marker. 완전 제거 |
| 4b | `grep -rn "덕삼\|기획이야기" skills/` | 0건 — 스킬 정의에 도메인 고유명 없음 (`examples/` 의 `덕삼뉴스` 는 예시 프로젝트명이므로 유지) |
| 5 | 이모지 grep — `skills/**`, `examples/doksam_news_storyboard.html` | 0건 |
| 6 | `./install.sh --dry-run` | 3경로 계획 출력, 파일시스템 변경 없음 |
| 7 | `./install.sh` → `readlink` ×3 | 전부 레포 원본 절대경로 |
| 8 | `./install.sh` 재실행 | 3건 `skip`, `exit 0` |
| 9 | `./install.sh --uninstall` | 심링크 3개 제거, `exit 0` |
| 10 | 렌더 확인 | `mongoose` 로 예시 서빙 → 크롬으로 전체 슬라이드 스크린샷. 목업 잘림 없음, 볼드가 합성체가 아님 |

## 8. 범위 외 (후속 이슈 후보)

- 외부 CDN 의존 제거 — Pretendard woff2 · mermaid.min.js 로컬 벤더링. 오프라인·사내망 환경 대응
- 슬라이드 반응형 — `.ppt-slide` 의 `aspect-ratio: 16/9` + `overflow: hidden` 과 `.mock` 의 `height: 600px` (scale 0.9 → 540px) 고정이 충돌한다. 1400px 폭에서는 가용 675px 로 들어가지만 창을 좁히면 목업 하단이 잘린다
- 스킬 pressure 테스트 — baseline 실패 관측 후 rationalization 대응 문구 작성 (`superpowers:writing-skills` 절차)
- IA 화면 수 ↔ 상세 슬라이드 수 자동 검증
