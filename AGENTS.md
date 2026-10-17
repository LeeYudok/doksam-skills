# doksam-skills — 에이전트 지침

AI 에이전트(Claude Code·Codex·Antigravity)가 이 저장소에서 작업할 때 지킬 규칙이다. 기계 판독용 정보(구성요소 그래프·명령·환경변수 키·정책·알려진 문제)는 [`AGENTS.yaml`](AGENTS.yaml) 에 있다.

## 한눈에

| 먼저 지킬 것 | 근거 |
|---|---|
| 스킬 하나가 자기 자산을 전부 소유한다. 스킬 전용 파일을 루트 `scripts/`·`tests/` 에 두지 않는다 | [2장](#2-스킬-레이아웃-규약) |
| 사용자에게는 한국어로 답한다. 문서·커밋·이슈·PR 본문도 한국어이고 문장은 `yd-writer-kr` 규칙을 따른다 | [1장](#1-개요와-언어) |
| Python 은 stdlib 만 쓴다. 예외는 `scripts/check-agents-yaml.sh` 하나다 | [4장](#4-공통-작업) |
| `install.sh` 와 루트 테스트에 스킬 이름을 적지 않는다. 스킬을 순회한다 | [4장](#4-공통-작업) |
| 등록 여부는 파일이 아니라 런타임 출력으로 판정한다 | [3장](#3-런타임별-발견-경로) |
| 이모지 아이콘, 한쪽 색 띠 같은 AI 냄새 나는 UI 장식을 쓰지 않는다 | [5장](#5-공통-금지와-표기) |
| 구성요소·경로·명령·환경변수가 바뀌면 이 문서와 `AGENTS.yaml` 을 함께 고친다 | 아래 |

```bash
./scripts/run_tests.sh                    # 루트 규약 + 모든 스킬 + 설치기 테스트
python3 scripts/score_skills.py --write   # 스킬을 고쳤으면 README 완성도 표를 다시 만든다
scripts/check-agents-yaml.sh              # AGENTS.yaml 검증 (PyYAML 필요)
./install.sh --verify --with-agent        # 세 런타임에 실제로 등록됐는지 확인
```

두 파일이 어긋나면 실제 코드·파일시스템을 확인해 둘 다 고친다. 날짜·버전 값은 항상 따옴표로 감싼다. 코드·구성이 바뀐 뒤 남은 낡은 참조는 `yd-doc-sync` 로 찾는다(범위는 `AGENTS.yaml` 의 `x-doc-sync`).

## 1. 개요와 언어

- **성격**: Agent Skill 모음이다. `skills/` 아래 스킬 하나가 배포 단위이고, `install.sh` 가 전부를 세 런타임 경로에 심링크로 노출한다.
- **기술 스택**: 스킬 정의는 Markdown, 템플릿은 HTML5 + Vanilla CSS 다. 검증·테스트는 Python 3 stdlib 와 bash 다. 앱을 품은 스킬은 TypeScript + Vite 다(`yd-blueprint` 템플릿은 React, `yd-script-editor` 앱).
- **응답 언어**: 사용자에게 **항상 한국어로 답한다.** 영어로 묻거나 영어 자료를 다룰 때도 같다. 사용자가 다른 언어를 명시한 경우만 예외다.
- **작성 언어**: `SKILL.md` 본문·frontmatter `description`·어댑터·문서·커밋/이슈/PR 본문은 한국어로 쓴다. 영어를 유지하는 것은 셋이다. 코드 식별자·명령어·파일/키 이름, 고유 기술용어(IA, Storyboard, SSOT, frontmatter 등), 외부 도구가 요구하는 형식. description 은 한국어 문장으로 쓰되 핵심 키워드는 한/영을 병기할 수 있다.
- **문장**: 사람이 읽을 문서는 `yd-writer-kr` 규칙으로 쓴다(번역투·군더더기 없이, 문장 60자 안팎). 자가 점검은 `python3 skills/yd-writer-kr/scripts/check_writing.py <파일>` 이다.

## 2. 스킬 레이아웃 규약

```text
skills/<skill>/
  SKILL.md            필수. frontmatter 는 name·description 두 개뿐이고 name 은 디렉터리명과 같다
  agents/             선택. 아래 넷을 한 세트로 둔다
    claude.md         Claude Code 어댑터
    codex.toml        Codex custom agent (name 은 스킬명의 - 를 _ 로 바꾼 것)
    antigravity.md    Antigravity 플러그인 에이전트 / Gemini API Managed Agent 등록 원본
    openai.yaml       Codex UI 용 스킬 메타데이터
  references/         SKILL.md 가 가리키는 상세 문서
  resources/·assets/  템플릿
  scripts/            이 스킬 전용 스크립트
  tests/              이 스킬 전용 테스트와 claims.json
```

- 루트 `.claude/agents/<skill>.md` 와 `.codex/agents/<skill_>.toml` 은 위 원본을 가리키는 **심링크**다. 원본을 그 자리에 두지 않는다.
- 어댑터에 행동 규칙을 복제하지 않는다. 행동 계약은 `SKILL.md` 한 곳에 두고, 어댑터는 역할·호출·완료 조건만 적는다.
- **`claude.md` 와 `antigravity.md` 는 frontmatter(`name`·`description`)가 필수다.** agy 는 frontmatter 가 없는 에이전트 md 를 오류 없이 무시한다. agy 1.1.11 에서 2026-08-11 에 실측했다(이슈 #110).
- **어댑터는 넷을 한 세트로 두거나 아예 두지 않는다.** 하나만 빠지면 그 런타임에서만 조용히 안 보인다. 실제로 `openai.yaml` 이 10개 중 1개에만 있었다(이슈 #131).
- **어댑터를 두지 않는 스킬은 8개다.** 위임할 작업 단위가 없어서다. `yd-session-recording` 은 세션을 소유하고, `yd-handoff`·`yd-agents-mem`·`yd-git-ship`·`yd-git-sync`·`yd-claude-auth-sync`·`yd-agents-yaml` 은 지금 세션의 상태·계정이 필요하다. `yd-typescript` 는 구현 에이전트가 바로 적용하는 기준이다. 목록과 이유의 원본은 README 「에이전트를 두지 않는 이유」 표이고, `scripts/score_skills.py` 가 그 표를 읽는다. 커버리지를 맞추려고 채워 넣지 않는다 — 호출은 되는데 동작하지 않는 입구가 생긴다(이슈 #122).
- 스킬 이름에는 에이전트 유무를 담지 않는다. 어댑터를 넣거나 뺄 때마다 이름이 바뀌면 설치 경로와 호출 이름이 깨진다. README 스킬 표의 `에이전트` 열이 그 정보를 보이고, `tests/test_readme_skills.py` 가 실제 `agents/` 와 대조한다.
- 이 규약 위반은 `tests/test_skill_layout.py` 가 잡는다.

## 3. 런타임별 발견 경로

2026-08-11 실측, Antigravity 는 2026-10-05 재실측이다.

| 런타임 | 스킬 | 에이전트 어댑터 | 등록 확인 |
|---|---|---|---|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/<skill>.md` | 세션 로드 |
| Codex | `~/.agents/skills/` · 프로젝트 `.agents/skills/` | `~/.codex/agents/<skill_>.toml` | `codex debug prompt-input` |
| Antigravity | `~/.gemini/config/skills/` · 프로젝트 `.agents/skills/` | 플러그인 `agents/*.md` (`agy plugin install`) | `agy agents` |

- Codex 는 `~/.codex/skills/` 도 읽지만 시스템 스킬 자리라 쓰지 않는다.
- Antigravity 는 `~/.gemini/config/agents/` 를 탐색하지 않는다. 에이전트는 반드시 플러그인으로 등록한다.

**Antigravity 는 공식 문서의 CLI 경로를 읽지 않는다(agy 1.2.16, 2026-10-05 실측, 이슈 #209).** 문서(https://antigravity.google/docs/skills/)는 제품마다 경로를 달리 적는다.

| 문서의 경로 | 문서가 말하는 제품 | agy 1.2.16 이 로드하는가 |
|---|---|---|
| `<저장소 루트>/.agents/skills/` | 2.0 · CLI · IDE 프로젝트 | 로드한다 |
| `~/.gemini/config/skills/` | 2.0 · IDE 전역 | 로드한다 |
| `~/.gemini/antigravity-cli/skills/` | CLI 전역 | **로드하지 않는다** |
| `~/.gemini/antigravity-cli/plugins/<이름>/skills/` 직접 배치 | CLI 플러그인 | **로드하지 않는다** — `agy plugin validate` 는 통과하는데 `agy plugin list` 에 없다 |

플러그인은 `agy plugin install <경로>` 로 설치해야 `~/.gemini/config/plugins/<이름>/` 에 복사되고 그 안의 `skills/` 도 로드된다. 그래서 `install.sh` 는 전역 스킬을 `~/.gemini/config/skills/` 에 걸고, 플러그인은 에이전트 어댑터에만 쓴다. 이 표는 문서가 아니라 실측이 근거다. agy 가 올라가면 같은 방법으로 다시 확인해 고친다.

재확인 방법: 후보 경로마다 `description` 에만 고유 마커(`MARK-…`)를 적은 프로브 스킬을 둔다. 저장소 루트인 임시 폴더에서 `~/.local/bin/agy --mode plan -p '도구는 쓰지 말고, 로드된 스킬 중 zz-probe- 로 시작하는 것의 마커와 파일 경로를 답해'` 로 묻는다. 마커가 description 에만 있으므로 로드되지 않았다면 답할 수 없다. 끝나면 프로브와 `agy plugin uninstall` 로 설치한 플러그인을 지운다.

**등록 확인은 `./install.sh --verify`(에이전트까지는 `--with-agent`)로 한다.** 위 "등록 확인" 열의 명령 출력과 저장소 스킬 목록을 맞춰 보고, 하나라도 없으면 exit 1 이다. 질의할 CLI 가 없는 자리(Claude Code 스킬, Codex 커스텀 에이전트)는 경로 존재로 판정하고 근거를 함께 찍는다. 끊긴 심링크는 `broken`, 목록에 없는 스킬을 가리키던 링크는 `stale <이름>` 으로 보고한다. 예전 판정은 링크 존재만 보고 ok 로 쳐서, 62개가 끊긴 채 지나갔다(이슈 #170). 경로 기준 설치 상태만 빨리 볼 때는 `./install.sh --list` 를 쓴다.

## 4. 공통 작업

**새 스킬**은 `./scripts/new_skill.sh <이름> "한 줄 설명"` 으로 만든다. 뼈대·어댑터 넷·루트 심링크가 함께 생긴다. `install.sh` 와 루트 `tests/` 는 스킬을 순회하므로 손대지 않는다. **거기에 스킬 이름을 적으면 테스트가 실패한다.**

**테스트**는 Python stdlib 만 쓴다. 이 환경의 Homebrew Python 3.14 는 외부 라이브러리 import 가 깨져 있다.

```bash
./scripts/run_tests.sh                                                     # 전부
python3 -m unittest discover -s tests -t tests -v                          # 루트 규약
python3 -m unittest discover -s skills/<skill>/tests -t skills/<skill>/tests -v  # 스킬 하나
./tests/test_install.sh                                                    # 설치기
```

- 예외는 `scripts/check-agents-yaml.sh` 하나다. PyYAML 이 필요해서 stdlib 전용 `test.yml` 이 아니라 `.github/workflows/agents-yaml.yml` 에서 돈다. 그 job 은 회귀 테스트(`skills/yd-agents-yaml/tests/`)에 skip 이 섞이면 실패한다. 로컬에 PyYAML 이 없으면 `run_tests.sh` 는 skip 사유를 찍고 넘어간다.
- 엔진·도구가 필요한 단언 재현은 전용 job 에서 돈다: `pg.yml`·`oracle.yml`·`go-claims.yml`·`react-claims.yml`·`ts-claims.yml`(skip 이 섞이면 실패), 브라우저 렌더는 `layout.yml`.

**완성도 표**: README 의 표는 `scripts/score_skills.py` 가 만든다. 스킬을 고친 PR 은 `python3 scripts/score_skills.py --write` 로 표를 다시 만들어 함께 커밋한다. 빠뜨리면 `tests/test_maturity_table.py` 가 실패한다. 채점 기준의 원본은 스크립트 docstring 이다.

**올리기**: 이슈를 먼저 열고, `batch/claude-<YYYYMMDD>-<8자리 hex>` 브랜치에서 PR 을 연다. PR 본문에는 `Closes #N` 을 쓰고, 머지는 merge commit 으로 한다(squash 금지). `main` 은 `test` workflow 통과가 필수다.

## 5. 공통 금지와 표기

- **생성 산출물을 커밋하지 않는다.** 화면설계서 HTML 같은 산출물 검증은 사용자가 만든 파일을 인자로 넘겨 한다.
- **이모지를 아이콘 대용으로 쓰지 않는다**(`skills/**`·생성 산출물). Phosphor Icons(MIT)의 `path` 를 인라인 `<svg class="icon">` 으로 넣는다. 원본은 `https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/<name>.svg` 다. `&lsaquo;`·`&#8942;` 같은 타이포그래피 문자는 이모지가 아니다.
- **AI 냄새 나는 UI 장식을 쓰지 않는다.** 카드 한쪽 가장자리 색 띠, 색 줄 달린 숫자 카드, 테두리 배지 나열, 그라디언트·글로우·큰 그림자가 그 예다. 상태는 테두리 색과 글자로 보인다(`.claude/memory/feedback_ui-no-accent-stripe.md`).
- **제3자 저작물**은 `THIRD-PARTY-NOTICES.md` 에 출처·라이선스·저작권 줄을 적는다. 라이선스는 원문을 확인해 적는다.
  - 저장소에 들어오는 자산(아이콘 `path` 복사 등)은 고지가 **의무**이고 라이선스 전문까지 넣는다.
  - 산출물이 실행 시 내려받는 자산(CDN 스크립트·웹폰트)은 의무는 아니지만 산출물이 의존하므로 적는다.
  - `LICENSE` 에 덧붙이지 않는다. MIT 전문에 내용을 붙이면 GitHub 라이선스 자동 인식이 깨질 수 있다.
  - `tests/test_third_party_notices.py` 가 템플릿의 외부 호스트와 커밋된 Phosphor `path` 를 훑어 누락을 잡는다.

## 6. 스킬별 지침

스킬의 행동 규칙은 각 `SKILL.md` 가 원본이다. 여기에는 저장소를 고칠 때 알아야 할 것만 둔다.

### 6.1 yd-mobile-web-planner

IA 와 화면설계서(HTML 스토리보드)를 만드는 스킬이다. 파일은 `skills/yd-mobile-web-planner/` 아래에 있다.

| 파일 | 하는 일 |
|---|---|
| `SKILL.md` | 기획자 페르소나, 워크플로, 클래스 Quick Reference, 마크업 예시 |
| `resources/template.html` | 산출물 HTML/CSS 스켈레톤. **CSS 클래스의 유일한 정의처** |
| `scripts/scaffold.py` | 템플릿 head 를 복사한 빈 뼈대 생성기. 630줄 CSS 를 손으로 옮겨 적지 않게 한다 |
| `scripts/validate_storyboard.py` | 산출물 구조 검증기 |
| `scripts/check_badge_overflow.py` · `check_badge_alignment.py` | 배지가 목업 밖으로 나가는지, 겹치거나 라벨-좌표 순서가 뒤집혔는지 본다 |
| `resources/badge-audit.js` · `scripts/apply_badge_audit.py` | 브라우저에서 배지가 실제로 가리키는 곳을 실측하고, 그 JSON 으로 인라인 `top` 을 일괄 반영한다 |
| `scripts/check_layout_runtime.py` · `resources/layout-probe.js` | Chrome headless 로 렌더해 슬라이드 overflow·배지 이탈/겹침·설명 패널 잘림을 잡는다. 스니펫은 좌표만 모으고 판정은 파이썬 한 곳에서 한다 |
| `scripts/export_deck.py` · `resources/desc-measure.js` | 산출물에서 PDF 와 PPTX 를 만든다. 설명 패널을 PPT 텍스트 상자로 얹을 때(`--editable-desc`) 스니펫으로 위치를 잰다 |

**클래스 계약(가장 중요)**: `template.html` 에 CSS 로 정의된 클래스만 쓴다. 예외는 `mermaid` 하나다. 새 클래스가 필요하면 먼저 `template.html` 에 정의하고 `SKILL.md` Quick Reference 표에도 올린다. 목업 세부 스타일은 인라인 `style` 로 처리하고 일회성 클래스를 만들지 않는다. 계약이 깨지면 검증기가 exit 1 로 막는다.

**산출물 검증**: 아래 셋이 exit 0 이어야 완료다. 정적 검사는 배지가 **의도한 요소를** 가리키는지 모른다 — 목업이 0.9배로 축소되고 높이가 런타임에 정해진다. 브라우저를 쓸 수 있으면 `badge-audit.js` 의 `misaligned` 가 비었는지도 본다.

```bash
python3 skills/yd-mobile-web-planner/scripts/validate_storyboard.py   <파일.html>
python3 skills/yd-mobile-web-planner/scripts/check_badge_overflow.py  <파일.html>
python3 skills/yd-mobile-web-planner/scripts/check_badge_alignment.py <파일.html>
```

**레이아웃 회귀 검사**: `check_layout_runtime.py <파일.html>`. 템플릿 CSS 가 바뀌면 마크업은 그대로인데 결과만 깨지고, 그건 렌더해야 보인다. 실제로 `.mock-footer` 에 `position: relative` 가 없어 푸터 배지가 `.mock` 기준으로 떠 있던 것을 이 검사기가 잡았다(이슈 #71 은 헤더만 고쳤다).

- 판정은 **구조·좌표**다. 전체 픽셀 비교는 브라우저·폰트 버전마다 false positive 를 내므로 쓰지 않는다.
- 렌더는 기본이 **오프라인**이다(외부 폰트와 mermaid CDN 제거). 실제 서체로 보려면 `--online` 을 준다. mermaid 슬라이드는 overflow 판정에서 빠지고 그 사실이 출력에 찍힌다.
- 렌더 폭은 설계 기준 `DESIGN_W`(1400px)로 고정한다. 목업 높이와 배지 top 이 그 폭에서 나온 절대값이다.
- fixture 의 `<head>` 는 커밋하지 않는다. `scaffold.py` 로 매번 가져오고 슬라이드 조각(`tests/fixtures/layout/baseline-slides.html`)만 커밋한다.
- CI 는 `layout.yml` 의 별도 job 이다. Chrome 이 없으면 `google-chrome --version` 단계에서 실패해, 테스트가 조용히 skip 되어 초록으로 통과하는 것을 막는다.

**내보내기**: PDF 는 인쇄 CSS + `--print-to-pdf`(텍스트 벡터), PPTX 는 슬라이드별 PNG + OOXML 조립으로 만든다. **PDF 를 이미지로 바꾸지 않는다** — 텍스트 선택·검색과 인쇄 선명도를 잃는다. pptx 는 stdlib `zipfile` 로 조립하고, 골격은 열리는 것이 확인된 파일과 같아야 한다(`tests/test_export_deck.py`). **관계 타입 URL 을 패키지 네임스페이스에서 파생시키지 않는다.** 문자열로 합치면 `package/2006/officeDocument/2006/...` 같은 무효 URL 이 나오는데, XML 은 well-formed 라 파싱 검사로는 안 잡히고 열 때야 실패한다.

**새 검증 규칙을 넣는 PR**(이슈 #77)은 셋에 답한다.

1. **규칙 세트 분류** — 위반 메시지의 식별 부분 문자열을 `V2_RULE_MARKERS`(세트가 갈리면 다음 버전 상수)에 등록한다. 경계가 바뀌면 `RULESET_VERSION` 을 올린다. 등록하지 않으면 옛 문서가 일괄 위반으로 뒤집힌다.
2. **기존 산출물 마이그레이션** — PR 본문에 셋 중 하나를 적는다. 고친다 / 그대로 둔다(기본 모드에서 참고로만 보고) / 기계 변환 스크립트를 준다.
3. **픽스처 재판정** — `tests/fixtures/runtime-parity/` 세 파일의 판정(claude 0건 / codex·agy 위반)이 유지되는지 본다. 바뀌면 README 와 `test_mock_content.py` 기준선을 함께 고친다. 이 픽스처는 과거 산출물이라 템플릿을 바꿔도 고치지 않는다.

**고칠 때**

- 말투·프로세스·결과물 형식은 `SKILL.md` 를 고친다. 기획 용어(IA, Wireframe, Storyboard, User Flow)는 그대로 쓴다.
- 슬라이드 번호 체계는 `01 Cover / 02 Document History / 03 Index / 04 Information Architecture / 05 Screen List / 06 Service Flow / 07.x Sequence Diagram / 08 General Rule / 09.x 화면 상세` 다. 바꾸려면 `SKILL.md` 와 `validate_storyboard.py` 를 함께 고친다.
- 산출물에 특정 블로그·회사·개인 이름을 넣지 않는다. 플레이스홀더는 `{{PROJECT_NAME}}` 과 `{{VERSION}}` 둘뿐이다.
- 템플릿은 Vanilla CSS 만 쓴다. `@import` 는 `@font-face` 를 포함한 모든 규칙보다 앞에 있어야 유효하다(CSS 스펙). 본문 서체는 D2Coding 1.4.0 이다(태그 고정, `THIRD-PARTY-NOTICES.md`).

### 6.2 yd-doksam-ui · yd-nextjs-implementer

**yd-doksam-ui** 는 doksam 프로젝트 UI 를 ui.doksam.com 표준에 맞춘다. 한 스킬이 두 모드를 겸한다.

- 모드 A(소비자) — 다른 프로젝트에 표준을 적용한다. 원천은 사이트의 `/llms.txt`·`/rules.md` 이고, 스킬은 live fetch 하라고만 지시한다. 목록을 문서에 박지 않아야 브랜드 프로필이 늘어도 낡지 않는다.
- 모드 B(생산자) — 카탈로그 레포(doksam-ui)를 넓힌다. 체크리스트는 `skills/yd-doksam-ui/references/catalog-workflow.md` 다.
- 규칙 조항의 원본은 카탈로그 레포의 `lib/rules-markdown.ts` 다. `SKILL.md` 는 위반 빈발 항목만 요약하고 규칙 문장을 복제하지 않는다. 어긋나면 원본이 옳다.
- 자가 검증은 `skills/yd-doksam-ui/scripts/check_standards.py` 가 맡는다(하드코딩 색·이모지·외부 URL·TypeScript `any`). 맨손 `grep` 으로 되돌리지 않는다 — `grep -r ' any'` 는 `company` 를, `grep -r '[^\x00-\x7F]'` 는 한글을 전부 잡는다.

**yd-nextjs-implementer** 는 호환을 위해 이름을 유지한다. 화면설계서 구현 프론트는 Next.js App Router 와 Vite + React SPA 중에서 고른다. 모드 상세는 `references/implementation-modes.md` 가 소유한다. Vite·pnpm·번들은 `yd-frontend-build`, 컴포넌트는 `yd-react-expert`, UI 표준은 `yd-doksam-ui` 를 참조하고 규칙을 복제하지 않는다.

데이터 모델·API 계약으로 넘어가는 경계는 `references/data-contract-handoff.md` 가 소유한다. **별도 `schema-architect` 스킬을 만들지 않기로 했다**(이슈 #144). 트리거 경계가 `yd-db-expert`·`yd-nextjs-implementer` 와 성립하지 않고, 기획 산출물에는 엔티티·관계·보존 정책을 정할 정보가 없다. 그 문서는 무엇이 답해져야 넘어가는지와, 답이 없을 때 가정으로 표시하는 규약만 둔다. 설계 판단은 `yd-db-expert` 가 소유한다.

### 6.3 yd-finguard · yd-sdlc-orchestrator

**yd-finguard** 는 외부 FinGuard 도구의 `scan --format rdjsonl` 을 로컬 보안 게이트로 잇는다. 원본 룰·매핑·금보원 근거 문구는 복사하지 않는다. 로컬 `scan` 은 finding 이 있어도 exit 0 일 수 있으므로 자동 게이트는 `skills/yd-finguard/scripts/run_gate.py` 를 쓴다. SCA·동적 분석·모의해킹을 대체한다고 약속하지 않는다. AI-SDLC 단계 계약과 pre-commit 예시는 스킬의 reference 에 둔다.

**yd-sdlc-orchestrator** 는 기획 → 구현 → 보안 → 로컬 기동을 차례로 위임한다. 단계 규칙을 복제하지 않고 게이트만 확인한다. 단계별 입출력과 중단 조건의 원본은 `skills/yd-finguard/references/ai-sdlc.md` 다.

**문서가 가리키는 게이트는 실제로 있어야 한다.** 경로가 틀리거나 "추가 예정" 으로 적으면 에이전트는 그 단계를 조용히 건너뛰고 검증했다고 보고한다. 실제로 이 스킬이 `yd-finguard` 를 "추가 예정" 으로 적은 채 머지된 적이 있다. `tests/test_referenced_paths.py` 가 모든 스킬 문서에서 두 가지를 강제한다. 가리키는 스크립트·reference 가 있어야 하고, 이미 있는 스킬을 미구현으로 적으면 안 된다.

### 6.4 yd-git-ship

- `scripts/glab-as.sh` 는 `~/workspace/.env.toml` 의 `[gitlab_<agent>_ai].token` 을 `scripts/read_token.py` 로 읽어 `GITLAB_TOKEN` 으로만 넘긴다. 토큰을 출력하는 코드를 넣지 않는다.
- 환경변수는 셋이다.
  - `GITLAB_HOST`: 없으면 glab 이 git remote·기본 호스트로 정한다.
  - `YD_ENV_TOML`: 토큰 파일 경로를 바꾼다(테스트용).
  - `YD_TOML_FALLBACK=1`: tomllib 대신 대체 경로를 강제한다(테스트용).
- 맥 `/bin/sh` 는 bash 3.2 라 `$(...)` 안 heredoc 의 따옴표를 잘못 파싱한다. 셸 스크립트에 파이썬을 heredoc 으로 넣지 말고 별도 파일로 둔다(#203).
- 호출한 셸에 따라 `python3` 가 3.9(맥 `bash -l`)일 수 있다. `read_token.py` 는 tomllib 없이도 동작해야 한다.

### 6.5 기술 스택 스킬 8종

`yd-frontend-build`·`yd-typescript`·`yd-react-expert`·`yd-go-expert`·`yd-sqlite-expert`·`yd-db-expert`·`yd-pg-expert`·`yd-oracle-expert` 는 한 묶음으로 관리한다.

스킬은 description 으로 선택되므로 경계가 흐리면 여러 개가 동시에 뜬다. 기술이 아니라 **작업 단위**로 나눈다.

| 스킬 | 맡는 것 | 맡지 않는 것 |
|---|---|---|
| `yd-frontend-build` | pnpm·Vite·의존성·번들·폐쇄망 self-host·산출물 내장 | 컴포넌트 코드 |
| `yd-typescript` | 정적 타입과 실행 데이터의 경계·strict·비동기 UI·DOM 접근 | 빌드·의존성, React 컴포넌트 설계 |
| `yd-react-expert` | 컴포넌트·상태·effect·접근성·렌더 성능 | 빌드 설정, 디자인 토큰 |
| `yd-go-expert` | Go 관용구·에러·동시성·`net/http`·`go:embed`·테스트 | SQL·스키마 |
| `yd-sqlite-expert` | SQLite 엔진 고유 문제(읽기전용·WAL·잠금·동적 테이블명) | 설계 이론, PostgreSQL |
| `yd-db-expert` | 엔진 공통 관계형 설계(정규화·키·제약·인덱스 선택·트랜잭션 경계·마이그레이션 단계) | PostgreSQL·Oracle·SQLite 고유 주제 |
| `yd-pg-expert` | PostgreSQL 고유 동작 + 공유 클러스터 운영 | 엔진 공통 설계 |
| `yd-oracle-expert` | Oracle 고유 문제(빈 문자열 NULL·DATE·VARCHAR2 바이트·ROWNUM·암묵 커밋·SQL*Plus) | 엔진 공통 설계, PostgreSQL |

UI 표준(토큰·컴포넌트 선택)은 `yd-doksam-ui` 가 단일 진실원천이다. 위 스킬들은 참조만 하고 규정하지 않는다.

경계는 `tests/test_trigger_boundaries.py` 가 **모든 스킬**에서 강제한다(이 8종만이 아니다). description 에서 판별 키워드를 뽑아 스킬 쌍의 겹침을 재고, 임계값을 넘으면 실패한다. 면제는 조건이다 — **한쪽 description 이 상대 스킬 이름을 불러 맡지 않는 것을 적은 쌍**만 통과한다. 새 스킬이 겹치면 경계를 다시 긋거나 그 문장을 넣는다.

**유지 원칙**

- 모델이 이미 아는 일반론을 적지 않는다. 담는 것은 넷뿐이다 — 버전별 함정, 실측으로 확인한 사실, doksam 고유 규약, 판단이 갈리는 지점의 기준.
- 항목을 더할 때 "이게 없으면 에이전트가 실제로 틀리는가" 에 답할 수 있어야 한다.
- **단언은 재현으로 고정한다.** 각 스킬의 `scripts/verify_*_claims.py` 가 문서 단언을 실제 엔진·도구로 재현하고, `tests/claims.json` 이 단언과 테스트를 잇는다. 재현은 환경변수가 있어야 돈다. PostgreSQL 은 `YD_PG_PSQL`, Oracle 은 `YD_ORACLE_SQLPLUS`(SQL 을 stdin 으로 받는 명령)다. React 는 `YD_REACT_VERIFY=1`, TypeScript·Bun 은 `YD_TS_VERIFY=1` 이다. 없으면 사유를 찍고 건너뛴다. 대상은 버리는 로컬 컨테이너뿐이고 운영 DB 에 돌리지 않는다. 재현이 문서와 다르면 문서를 고치거나 단언에 버전을 적는다.
- 버전에 묶인 사실은 어느 버전부터인지 함께 적는다. pnpm 10 의 lifecycle 차단, TS6 의 `baseUrl` 제거, Go 1.22 ServeMux 패턴이 그 예다.

**검사기**: `skills/yd-frontend-build/scripts/check_bundle.py` 가 빌드 산출물의 외부 출처·소스맵·번들 예산을 본다. **URL 이 있다고 요청이 나가는 것은 아니다.** React·react-router·Tailwind 는 에러 메시지에 문서 링크를 심어 둔다. 그래서 `src=`·`href=`·`url()`·`@import`·`fetch()` 같은 요청 유발 문맥만 판정한다. 전수 감사는 `--strict` 로 분리했다.

## 7. 메모리 경로

이 프로젝트의 auto-memory 원본은 `.claude/memory/` 다. 시스템 기본 경로(`~/.claude/projects/.../memory/`)는 쓰지 않는다. `MEMORY.md` 가 인덱스이고, `user_*.md` 만 개인(커밋 제외), 나머지는 팀 공유다.
