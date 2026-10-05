# doksam-skills - AI Agent Guidelines

> **기계 판독용 정보는 [`AGENTS.yaml`](AGENTS.yaml)** — 구성요소 그래프(`nodes`/`edges`), `commands`, `secret_files`(경로·키 이름만), `policies`, `known_issues` 등. 작업 전 이 파일을 먼저 읽고, 구성요소·경로·명령·환경변수가 바뀌면 이 문서와 **함께** 갱신한다. 두 파일이 어긋나면 실제 코드·파일시스템을 확인해 둘 다 고친다. 고친 뒤엔 `scripts/check-agents-yaml.sh` 로 검증한다. 날짜·버전 값은 항상 따옴표로 감싼다.

이 문서는 AI 에이전트(Gemini, Claude 등)가 이 저장소(Repository)에서 작업할 때 지켜야 할 규칙과 프로젝트 컨텍스트를 정의합니다. `GEMINI.md`, `CLAUDE.md` 등에서 이 파일을 참조합니다.

1장~3장은 스킬 개수와 무관한 **저장소 공통 규약**이고, 4장부터는 **스킬별 작업 지침**입니다.

## 1. 프로젝트 개요 (Project Context)

- **성격**: 이 저장소는 Agent Skill 모음(doksam-skills)입니다. `skills/` 아래 스킬 하나가 배포 단위이며, `install.sh` 가 전부를 Claude Code / Codex / Antigravity 경로에 심링크로 노출합니다.
- **소유 원칙**: **스킬 하나가 자기 자산을 전부 소유합니다.** 행동 계약(`SKILL.md`), 리소스, 스크립트, 테스트, 세 런타임 Agent Adapter 가 모두 `skills/<skill>/` 안에 있습니다. 저장소 루트에는 설치기와 공통 규약 검증만 둡니다. 특정 스킬에만 쓰이는 파일을 루트 `scripts/` 나 `tests/` 에 두지 않습니다.
- **기술 스택**: 스킬 정의는 Markdown, 템플릿은 HTML5 + Vanilla CSS, 검증/테스트 스크립트는 Python 3 stdlib 와 bash 입니다.
- **언어 정책 (한국어 우선)**: 이 저장소는 한국인 사용자를 위한 스킬 모음입니다. `SKILL.md` 본문·frontmatter `description`·Agent Adapter·문서·커밋/이슈/PR 본문은 **한국어**로 작성합니다. 단, 영어가 더 정확하거나 필수인 것은 영어를 유지합니다 — 코드 식별자·클래스명·명령어·파일/키 이름(`name`, `description` 키 등), 고유 기술용어(IA, Storyboard, SSOT, frontmatter 등), 외부 도구가 요구하는 형식. 트리거 매칭에 쓰이는 description 은 한국어 문장으로 쓰되 핵심 키워드는 한/영을 병기할 수 있습니다.

## 2. 스킬 레이아웃 규약

```text
skills/<skill>/
  SKILL.md            필수. frontmatter 는 name·description 두 개뿐이고 name 은 디렉터리명과 같다
  agents/             선택. 아래 파일명만 허용한다
    claude.md         Claude Code Agent Adapter
    codex.toml        Codex custom agent (name 은 스킬명의 - 를 _ 로 바꾼 것)
    antigravity.md    Gemini API Managed Agent 등록용 역할 정의 원본
    openai.yaml       Codex UI 용 스킬 메타데이터
  resources/          템플릿 등
  scripts/            이 스킬 전용 스크립트
  tests/              이 스킬 전용 테스트
```

루트 `.claude/agents/<skill>.md` 와 `.codex/agents/<skill_>.toml` 은 위 원본을 가리키는 **심링크**입니다. 원본을 그 자리에 직접 두지 않습니다.

Agent Adapter 에 스킬의 행동 규칙을 복제하지 않습니다. 공통 행동 계약은 `SKILL.md` 한 곳에서 관리하고 Adapter 는 역할·호출·완료 조건만 정의합니다.

**`claude.md` 와 `antigravity.md` 는 YAML frontmatter(`name`·`description`)가 필수입니다.** 특히 agy 는 frontmatter 가 없는 agent md 를 **오류도 경고도 없이 무시합니다** — 플러그인에는 파일이 복사돼 있는데 `agy agents` 에는 안 나오는 상태가 됩니다 (2026-08-11 agy 1.1.11 실측, 이슈 #110). 등록 여부는 파일 존재가 아니라 `agy agents` 출력으로 확인하세요.

**어댑터는 넷을 한 세트로 둡니다.** `agents/` 를 만든다는 것은 그 스킬을 위임형 에이전트로 노출하겠다는 결정이고, 그 결정이 런타임마다 다를 이유는 없습니다. 하나만 빠지면 그 런타임에서만 조용히 안 보이는 상태가 됩니다 — 실제로 `openai.yaml` 이 10개 중 1개에만 있었습니다 (이슈 #131). 어댑터를 **아예 두지 않는 것**은 별개의 선택이며, `yd-session-recording` 이 그 경우입니다 (5장 참조).

이 규약 위반은 `tests/test_skill_layout.py` 가 스킬을 순회하며 잡습니다.

### 런타임별 발견 경로 (2026-08-11 실측, Antigravity 는 2026-10-05 재실측)

| 런타임 | 스킬 | Agent Adapter | 확인 방법 |
|---|---|---|---|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/<skill>.md` | 세션 로드 |
| Codex | `~/.agents/skills/` · 프로젝트 `.agents/skills/` | `~/.codex/agents/<skill_>.toml` | `codex debug prompt-input` |
| Antigravity | `~/.gemini/config/skills/` · 프로젝트 `.agents/skills/` | 플러그인 `agents/*.md` (`agy plugin install`) | `agy agents` |

**Antigravity 는 문서의 CLI 경로를 읽지 않습니다 (agy 1.2.16, 2026-10-05 실측, 이슈 #209).** 공식 문서(https://antigravity.google/docs/skills/)는 제품별로 경로를 달리 적습니다.

| 문서의 경로 | 문서가 말하는 제품 | agy 1.2.16 이 로드하는가 |
|---|---|---|
| `<저장소 루트>/.agents/skills/` | 2.0 · CLI · IDE 프로젝트 | 로드한다 |
| `~/.gemini/config/skills/` | 2.0 · IDE 전역 | 로드한다 |
| `~/.gemini/antigravity-cli/skills/` | CLI 전역 | **로드하지 않는다** |
| `~/.gemini/antigravity-cli/plugins/<이름>/skills/` 직접 배치 | CLI 플러그인 | **로드하지 않는다** — `agy plugin validate` 는 통과하는데 `agy plugin list` 에 없다 |

플러그인은 `agy plugin install <경로>` 로 설치해야 하고, 그러면 `~/.gemini/config/plugins/<이름>/` 에 복사돼 그 안의 `skills/` 도 로드됩니다. 그래서 `install.sh` 는 전역 스킬을 `~/.gemini/config/skills/` 에 걸고, 플러그인은 에이전트 어댑터에만 씁니다. 문서의 CLI 경로로 옮기면 스킬이 전부 안 보입니다. 이 표는 문서가 아니라 실측이 근거이므로, agy 가 올라가면 같은 방법으로 다시 확인해 고칩니다.

재확인 방법: 후보 경로마다 `description` 에만 고유 마커(`MARK-…`)를 적은 프로브 스킬을 하나씩 두고, 저장소 루트인 임시 폴더에서 `~/.local/bin/agy --mode plan -p '도구는 쓰지 말고, 로드된 스킬 중 zz-probe- 로 시작하는 것의 마커와 파일 경로를 답해'` 로 묻습니다. 마커가 description 에만 있어 로드되지 않았다면 답할 수 없습니다. 끝나면 프로브와 `agy plugin uninstall` 로 설치한 플러그인을 지웁니다.

Codex 는 `~/.codex/skills/` 도 읽지만 그쪽은 시스템 스킬 자리이므로 쓰지 않습니다. Antigravity 는 `~/.gemini/config/agents/` 를 탐색하지 않으므로 에이전트는 반드시 플러그인으로 등록합니다.

스킬마다 에이전트가 있는지와 경로 기준 설치 상태만 빠르게 보려면 `./install.sh --list` 를 씁니다. 스킬 이름에는 에이전트 유무를 담지 않습니다 — 어댑터를 넣거나 뺄 때마다 이름이 바뀌면 설치 경로와 호출 이름이 깨지기 때문입니다. README 스킬 표의 `에이전트` 열이 같은 정보를 보여주고, `tests/test_readme_skills.py` 가 그 열과 실제 `agents/` 를 대조합니다.

세 런타임을 한 번에 대조하려면 `./install.sh --verify`(에이전트까지 보려면 `--with-agent` 를 함께) 를 씁니다. 위 "확인 방법" 열의 명령을 실행해 그 출력과 저장소의 스킬 목록을 맞춰 보고, 하나라도 없으면 exit 1 합니다. **파일 존재를 등록의 증거로 삼지 마세요** — 이슈 #110 이 정확히 파일은 제자리에 있는데 런타임이 조용히 무시한 경우였습니다. 질의할 CLI 가 없는 자리(Claude Code 의 스킬, Codex 의 커스텀 에이전트)는 경로 존재로 판정하며, 출력에 근거가 함께 찍힙니다. 대상이 사라진 심링크는 `broken` 으로 따로 보고합니다 — 레포를 옮기거나 스킬 이름을 바꾸면 링크가 조용히 끊기는데, 예전 판정은 링크 존재만 보고 ok 로 쳐서 62개가 끊긴 채 지나갔습니다 (이슈 #170). 지금 스킬 목록에 없는 이름이라도 이 레포의 `skills/` 를 가리키던 끊긴 링크면 `stale <이름>` 으로 잡습니다.

## 3. 저장소 공통 작업

### 새 스킬 추가

```bash
./scripts/new_skill.sh my-skill "한 줄 설명"
```

뼈대와 세 런타임 Adapter, 루트 심링크까지 만들어집니다. `install.sh` 와 루트 `tests/` 는 스킬을 순회하므로 스킬을 추가할 때 손댈 필요가 없습니다. 반대로 **거기에 스킬명을 하드코딩하면 테스트가 실패합니다.**

### 테스트

Python 은 **stdlib 만** 씁니다. 이 환경의 Homebrew Python 3.14 는 외부 라이브러리 import 가 깨져 있습니다.

예외는 `scripts/check-agents-yaml.sh` 하나입니다. 이 검증기는 PyYAML 이 필요해 stdlib 전용 `test.yml` 대신 `.github/workflows/agents-yaml.yml` job 에서 돕니다. 그 job 은 PyYAML 을 설치하고, 회귀 테스트(`skills/yd-agents-yaml/tests/`)에 skip 이 하나라도 섞이면 실패합니다. 로컬에 PyYAML 이 없으면 `run_tests.sh` 에서는 skip 사유가 찍히고 넘어갑니다.

```bash
# 루트 규약 + 모든 스킬 테스트 + 설치기 테스트를 한 번에
./scripts/run_tests.sh

# 개별 실행
python3 -m unittest discover -s tests -t tests -v
python3 -m unittest discover -s skills/<skill>/tests -t skills/<skill>/tests -v
./tests/test_install.sh
```

README 의 완성도 표는 `scripts/score_skills.py` 가 만듭니다. 스킬을 고친 MR 은 `python3 scripts/score_skills.py --write` 로 표를 다시 만들어 함께 커밋합니다. 빠뜨리면 `tests/test_maturity_table.py` 가 실패합니다. 채점 기준은 스크립트 docstring 이 원본입니다.

이 저장소는 생성 산출물(HTML)을 커밋하지 않습니다. 산출물 검증은 사용자가 생성한 파일을 인자로 넘겨 수행합니다.

## 4. 스킬별 작업 지침: yd-mobile-web-planner

사용자의 요청(예: "쇼핑몰 기획해줘")에 따라 IA 와 화면 설계서(HTML 기반 스토리보드)를 생성하는 스킬입니다.

- `skills/yd-mobile-web-planner/SKILL.md`: 기획자 페르소나, 워크플로우, 클래스 Quick Reference, 마크업 예시가 정의된 핵심 파일.
- `skills/yd-mobile-web-planner/resources/template.html`: 기획서 결과물의 HTML/CSS 스켈레톤. **CSS 클래스의 유일한 정의처**.
- `skills/yd-mobile-web-planner/scripts/scaffold.py`: 템플릿 head 를 복사한 빈 산출물 뼈대 생성기. 에이전트가 430줄 CSS 를 손으로 옮겨 적지 않게 한다.
- `skills/yd-mobile-web-planner/scripts/validate_storyboard.py`: 산출물 구조 검증기.
- `skills/yd-mobile-web-planner/scripts/check_badge_overflow.py`: 배지 좌표가 목업 밖으로 나가는지 점검하는 보조 스크립트.
- `skills/yd-mobile-web-planner/scripts/check_badge_alignment.py`: 배지 겹침과 라벨-좌표 순서 역전을 점검하는 보조 스크립트.
- `skills/yd-mobile-web-planner/scripts/apply_badge_audit.py`: badge-audit 실측 JSON 을 받아 인라인 `top` 을 일괄 반영하고 정적 검증기를 재실행하는 스크립트.
- `skills/yd-mobile-web-planner/resources/badge-audit.js`: 브라우저에서 실행해 배지가 실제로 무엇을 가리키는지 실측하는 스니펫. 목업이 0.9배로 축소되어 인라인 `top` 만으로는 정렬을 알 수 없다.
- `skills/yd-mobile-web-planner/scripts/export_deck.py`: 산출물 HTML 에서 PDF 와 PPTX 를 함께 만드는 내보내기 스크립트.
- `skills/yd-mobile-web-planner/scripts/check_layout_runtime.py`: Chrome headless 로 렌더해 레이아웃 회귀(슬라이드 overflow · 배지 이탈/겹침 · 설명 패널 잘림)를 잡는 검사기.
- `skills/yd-mobile-web-planner/resources/layout-probe.js`: 위 검사기가 주입하는 좌표 수집 스니펫. **판정은 하지 않는다** — 임계값은 파이썬 한 곳에만 둔다.

### 클래스 계약 (가장 중요)

`resources/template.html` 에 CSS 로 정의된 클래스만 사용한다. 유일한 예외는 `mermaid` (mermaid.js 가 렌더하므로 CSS 불필요).

- 새 클래스가 필요하면 **먼저 `template.html` 에 정의를 추가**하고, `SKILL.md` 의 Class Quick Reference 표에도 등재한다.
- 목업 내부의 세부 스타일은 인라인 `style` 속성으로 처리한다. 일회성 클래스를 만들지 않는다.
- 이 계약이 깨지면 검증기가 exit 1 로 막는다.

### 산출물 검증

```bash
python3 skills/yd-mobile-web-planner/scripts/validate_storyboard.py   <생성된파일.html>
python3 skills/yd-mobile-web-planner/scripts/check_badge_overflow.py  <생성된파일.html>
python3 skills/yd-mobile-web-planner/scripts/check_badge_alignment.py <생성된파일.html>
```

셋 다 exit 0 이어야 완료다. 미정의 클래스가 보고되면 `template.html` 에 정의를 추가하거나 사용을 제거한다.

### 레이아웃 회귀 검사 (브라우저)

```bash
python3 skills/yd-mobile-web-planner/scripts/check_layout_runtime.py <생성된파일.html>
```

정적 검사기는 마크업의 인라인 좌표만 본다. 템플릿 CSS 가 바뀌어 목업 높이·gutter·설명
패널 밀도가 달라지면 마크업은 그대로인데 결과만 깨진다 — 그건 렌더해야 보인다. 실제로
이 검사기가 `.mock-footer` 에 `position: relative` 가 없어 푸터 배지가 `.mock` 기준으로
떠 있던 것을 잡았다(이슈 #71 은 헤더만 고쳤다).

- 판정은 **구조·좌표**다. 전체 픽셀 비교는 브라우저·폰트 버전이 바뀔 때마다 false
  positive 를 내므로 도입하지 않는다. 필요해지면 허용 오차가 있는 부분 비교를 나중에 얹는다.
- 렌더는 기본이 **오프라인**이다(외부 폰트 `@import` 와 mermaid CDN 제거). 러너의 네트워크
  상태가 판정을 흔들면 회귀 검사가 아니다. mermaid 슬라이드는 overflow 판정에서 빠지며 그
  사실이 출력에 찍힌다.
- 렌더 폭은 설계 기준 `DESIGN_W`(1400px)로 고정한다 — 목업 높이와 배지 top 이 전부 그
  폭에서 나온 절대값이라, 좁은 창의 잘림을 회귀로 보고하면 안 된다.
- fixture 의 `<head>` 는 커밋하지 않는다. `scaffold.py` 로 `template.html` 에서 매번
  가져오고 슬라이드 조각(`tests/fixtures/layout/baseline-slides.html`)만 커밋한다 —
  그래야 템플릿이 바뀔 때 fixture 가 따라온다.
- CI 는 `.github/workflows/layout.yml` 의 **별도 job** 이다. stdlib 전용인 `test.yml` 에
  브라우저를 끌어들이지 않는다. 그 job 은 Chrome 이 없으면 `google-chrome --version`
  단계에서 실패한다 — 테스트가 조용히 skip 되어 초록으로 통과하는 것을 막는다.

### 내보내기 (PDF · PPTX)

`export_deck.py` 는 두 형식을 **다른 경로로** 만든다 — PDF 는 인쇄 CSS + `--print-to-pdf`(텍스트 벡터), PPTX 는 슬라이드별 PNG + OOXML 조립(텍스트 이미지). 같은 HTML 을 같은 엔진으로 그리므로 내용은 같다. **PDF 를 이미지로 바꾸지 마세요** — 텍스트 선택·검색과 인쇄 선명도를 잃습니다.

pptx 는 `zipfile` 로 직접 조립합니다(이 환경은 stdlib 만 씁니다). 골격은 이미 열리는 것이 확인된 파일과 같아야 하며, `skills/yd-mobile-web-planner/tests/test_export_deck.py` 가 이를 강제합니다.

**관계 타입 URL 을 패키지 네임스페이스에서 파생시키지 마세요.** 둘은 다른 네임스페이스이고, 문자열 조작으로 합치면 `package/2006/officeDocument/2006/...` 같은 무효 URL 이 나옵니다. XML 은 여전히 well-formed 라 파싱 검사로는 안 잡히고 **열 때야 실패합니다** — 실제로 그 버그가 있었습니다.

정적 검사로는 배지가 **의도한 요소를 가리키는지** 알 수 없다 — 목업이 0.9배로 축소되고 콘텐츠 높이가 런타임에 정해지기 때문이다. 브라우저를 쓸 수 있으면 `resources/badge-audit.js` 를 실행해 `misaligned` 가 비어 있는지 확인한다.

### 새 검증 규칙 추가 체크리스트 (이슈 #77)

`validate_storyboard.py` 에 규칙을 추가·강화하는 PR 은 아래 세 가지에 답해야 합니다.

1. **규칙 세트 분류** — 이 규칙이 최신 규칙 세트에서 도입됐음을 표시합니다:
   위반 메시지의 식별 부분 문자열을 `V2_RULE_MARKERS`(세트가 갈리면 다음 버전 상수)에
   등록하고, 규칙 세트 경계가 바뀌면 `RULESET_VERSION` 을 올립니다. 등록하지 않으면
   옛 문서(사후 도입 규칙 면제 대상)가 일괄 위반으로 뒤집힙니다.
2. **기존 산출물 마이그레이션 판단** — (a) 기존 문서를 고친다 / (b) 그대로 둔다
   (기본 모드에서 참고로만 보고됨) / (c) 기계 변환 스크립트를 제공한다 중 하나를
   PR 본문에 명시합니다. 원문자→2단 번호처럼 기계 변환이 가능한 규칙은 (c) 가 맞습니다.
3. **픽스처 재판정** — `tests/fixtures/runtime-parity/` 세 파일의 판정
   (claude 0건 / codex·agy 위반)이 유지되는지 확인하고, 판정이 바뀌면 README 와
   `test_mock_content.py` 기준선을 함께 갱신합니다.

### 스킬 및 프롬프트 수정

- 기획자의 말투, 프로세스, 결과물 형식을 변경할 경우 `SKILL.md` 를 수정한다.
- 슬라이드 번호 체계는 `01 Cover / 02 Document History / 03 Index / 04 Information Architecture / 05 Screen List / 06 Service Flow / 07.x Sequence Diagram / 08 General Rule / 09.x 화면 상세` 다. 바꾸려면 `SKILL.md` 와 `skills/yd-mobile-web-planner/scripts/validate_storyboard.py` 를 함께 수정한다.
- 산출물에 특정 블로그·회사·개인 이름을 넣지 않는다. 플레이스홀더는 `{{PROJECT_NAME}}` 과 `{{VERSION}}` 두 개뿐이다.

### 템플릿(HTML/CSS) 수정

- 디자인이나 레이아웃 변경은 `resources/template.html` 을 수정한다.
- **Vanilla CSS** 만 쓴다. TailwindCSS 등 프레임워크를 도입하지 않는다.
- `@import` 는 `@font-face` 를 포함한 모든 규칙보다 앞에 있어야 유효하다 (CSS 스펙).
- 클래스 네이밍은 직관적으로, 스타일은 `<style>` 태그 안에 정리한다.

## 5. 스킬별 작업 지침: yd-memory-factcheck

에이전트 영속 메모리를 코드·DB·이슈 등 실제 근거와 대조해 낡은 기억을 교정하는 감사 스킬입니다. 명세는 `skills/yd-memory-factcheck/SKILL.md` 한 곳입니다.

### Agent Adapter 가 없는 스킬 — `yd-session-recording`

`yd-session-recording` 에는 `agents/` 가 없습니다. **빠진 것이 아니라 뺀 것입니다.** (`yd-handoff`·`yd-agents-yaml`·`yd-agents-mem`·`yd-git-ship` 도 어댑터가 없습니다 — 대화 중에 바로 쓰는 절차형 스킬이라 위임할 작업 단위가 없습니다.)

이 스킬은 한 번의 작업이 아니라 세션을 소유합니다 — `whisper-stream` 과 `ffmpeg` 를 백그라운드로 몇 시간 살려 두고, 10분 간격 요약 루프를 돌리며, 진행 중에 "중간 요약"·"녹음종료" 같은 대화형 트리거를 받습니다. 한 턴에 끝나고 사라지는 위임형 에이전트는 이 중 어느 것도 유지할 수 없어, 어댑터를 만들면 **호출은 되는데 동작하지 않는 입구**가 생깁니다. 없는 것보다 나쁩니다 (이슈 #122).

커버리지를 맞추려고 채워 넣지 마세요. 스킬 자체는 세 런타임에서 그대로 동작합니다.

## 6. 스킬별 작업 지침: yd-doksam-ui

doksam 프로젝트 UI 를 ui.doksam.com 표준에 맞추는 스킬입니다. **한 스킬이 두 모드를 겸합니다.**

- 모드 A(소비자) — 다른 프로젝트에서 표준을 적용한다. 원천은 사이트의 `/llms.txt`·`/rules.md` 이고, 스킬은 그것을 live fetch 하라고 지시할 뿐 목록을 문서에 박지 않습니다. 브랜드 프로필이 늘어도 문서가 낡지 않아야 합니다.
- 모드 B(생산자) — 카탈로그 레포(doksam-ui) 자체를 확장한다. 계층별 체크리스트는 `skills/yd-doksam-ui/references/catalog-workflow.md` 에 있습니다.

규칙 조항의 진짜 원본은 카탈로그 레포의 `lib/rules-markdown.ts` 입니다. `SKILL.md` 는 위반 빈발 항목만 다이제스트로 요약하고, **규칙 문장을 복제하지 않습니다** — 어긋나면 원본이 옳고 스킬이 틀린 것입니다.

자가 검증은 `skills/yd-doksam-ui/scripts/check_standards.py` 가 맡습니다(하드코딩 색·이모지·외부 URL·TypeScript `any`). 맨손 `grep` 으로 되돌리지 마세요 — `grep -r ' any'` 는 `company` 를, `grep -r '[^\x00-\x7F]'` 는 한글 텍스트를 전부 잡아 통과 판정이 무의미해집니다. 이 계약은 `skills/yd-doksam-ui/tests/` 가 강제합니다.

### yd-nextjs-implementer의 호환 이름과 구현 모드

`yd-nextjs-implementer`는 기존 설치 경로와 호출의 호환성을 위해 이름을 유지하지만,
화면설계서 구현 프론트는 Next.js App Router와 Vite + React SPA 중 선택합니다.
모드별 상세는 `skills/yd-nextjs-implementer/references/implementation-modes.md`가
소유합니다. Vite·pnpm·번들 설정은 `yd-frontend-build`, 컴포넌트 판단은
`yd-react-expert`, UI 표준은 `yd-doksam-ui`를 참조하며 규칙을 복제하지 않습니다.

데이터 모델·API 계약으로 넘어가는 경계는
`skills/yd-nextjs-implementer/references/data-contract-handoff.md` 가 소유합니다.
**별도 `schema-architect` 스킬을 만들지 않기로 한 결정**(이슈 #144)의 결과이며,
이유는 트리거 경계가 `yd-db-expert`·`yd-nextjs-implementer` 와 성립하지 않고, 기획
산출물에 엔티티·관계·보존 정책을 결정할 정보가 애초에 없기 때문입니다. 그 문서는
스키마 설계법을 적지 않습니다 — 무엇이 답해져야 넘어갈 수 있는지의 입력표와,
답이 없을 때 가정으로 표시하는 규약만 둡니다. 설계 판단은 `yd-db-expert` 가
소유합니다.

## 6.1 스킬별 작업 지침: yd-finguard

`yd-finguard`는 외부 FinGuard 원본 도구의 `scan --format rdjsonl`을 로컬 보안
게이트로 연결합니다. 원본 룰·매핑·금보원 근거 문구는 복사하지 않습니다.

- 로컬 `scan`은 finding이 있어도 exit 0일 수 있으므로 자동 게이트는
  `skills/yd-finguard/scripts/run_gate.py`를 사용합니다.
- 스킬은 SCA·동적 분석·모의해킹을 대체한다고 약속하지 않습니다.
- AI-SDLC 단계 계약과 pre-commit 예시는 스킬 소유 reference에 둡니다.

## 6.2 스킬별 작업 지침: yd-sdlc-orchestrator

`yd-sdlc-orchestrator` 는 기획 → 구현 → 보안 → 로컬 기동을 순서대로 위임하는 메타 스킬입니다. **각 단계의 규칙을 복제하지 않고 게이트만 확인합니다** — 단계별 입출력과 중단 조건의 원본은 `skills/yd-finguard/references/ai-sdlc.md` 입니다.

문서가 가리키는 게이트가 실제로 존재해야 합니다. 경로가 틀리거나 단계를 "추가 예정" 으로 적어 두면 에이전트는 오류 없이 그 단계를 **조용히 건너뛰고 검증했다고 보고합니다** — 게이트가 있다고 믿는 상태가 없는 상태보다 나쁩니다. 실제로 이 스킬이 `yd-finguard` 를 "추가 예정" 으로 적은 채 머지된 적이 있습니다. `tests/test_referenced_paths.py` 가 저장소의 모든 스킬 문서에 대해 두 가지를 강제합니다 — 문서가 가리키는 스크립트·reference 가 존재하는지, 이미 있는 스킬을 미구현으로 적지 않았는지.

## 6.3 스킬별 작업 지침: yd-git-ship

- `scripts/glab-as.sh` 는 `~/workspace/.env.toml` 의 `[gitlab_<agent>_ai].token` 을 `scripts/read_token.py` 로 읽어 `GITLAB_TOKEN` 으로만 넘긴다. 토큰을 출력하는 코드를 넣지 않는다.
- 환경변수: `GITLAB_HOST`(기본 `gitlab.doksam.com`), `YD_ENV_TOML`(토큰 파일 경로 덮어쓰기, 테스트용), `YD_TOML_FALLBACK=1`(tomllib 대신 대체 읽기 경로 강제, 테스트용).
- 맥 `/bin/sh` 는 bash 3.2 라 `$(...)` 안 heredoc 의 따옴표를 잘못 파싱한다. 셸 스크립트 안에 파이썬 코드를 heredoc 으로 넣지 말고 별도 파일로 둔다(#203).
- 호출한 셸에 따라 `python3` 가 3.9(맥 `bash -l`)일 수 있다. `read_token.py` 는 tomllib 없이도 동작해야 한다.

## 7. 스킬별 작업 지침: 기술 스택 스킬 7종

`yd-frontend-build` · `yd-react-expert` · `yd-go-expert` · `yd-sqlite-expert` · `yd-db-expert` · `yd-pg-expert` · `yd-oracle-expert` 는 하나의 묶음으로 관리합니다.

### 트리거 경계 (겹치면 안 됩니다)

스킬은 description 으로 선택되므로 경계가 흐리면 여러 개가 동시에 뜨고 서로를 밀어냅니다. 기술이 아니라 **작업 단위**로 나눕니다.

| 스킬 | 맡는 것 | 맡지 않는 것 |
|---|---|---|
| `yd-frontend-build` | pnpm·Vite·의존성·번들·폐쇄망 self-host·산출물 내장 | 컴포넌트 코드 |
| `yd-react-expert` | 컴포넌트·상태·effect·접근성·렌더 성능 | 빌드 설정, 디자인 토큰 |
| `yd-go-expert` | Go 관용구·에러·동시성·`net/http`·`go:embed`·테스트 | SQL·스키마 |
| `yd-sqlite-expert` | SQLite 엔진 고유 문제 (읽기전용·WAL·잠금·동적 테이블명) | 설계 이론, PostgreSQL |
| `yd-db-expert` | 엔진 공통 관계형 설계 (정규화·키·제약·인덱스 선택·트랜잭션 경계·마이그레이션 단계) | PostgreSQL·Oracle·SQLite 고유 주제 |
| `yd-pg-expert` | PostgreSQL 고유 동작 + pig 공유 클러스터 운영 | 엔진 공통 설계 |
| `yd-oracle-expert` | Oracle 엔진 고유 문제 (빈 문자열 NULL·DATE·VARCHAR2 바이트·ROWNUM·암묵 커밋·SQL*Plus) | 엔진 공통 설계, PostgreSQL |

UI 표준(토큰·컴포넌트 선택)은 `yd-doksam-ui` 가 단일 진실원천입니다. 위 스킬들은 그것을 **참조만 하고 규정하지 않습니다.**

이 경계는 `tests/test_trigger_boundaries.py` 가 **모든 스킬**에 대해 강제합니다(이 7종만이 아닙니다). description 에서 조사를 뗀 판별 키워드를 뽑아 스킬 쌍의 겹침을 재고, 임계값을 넘으면 실패합니다. 면제는 허용 목록이 아니라 조건입니다 — **한쪽 description 이 상대 스킬 이름을 불러 무엇을 맡지 않는지 명시한 쌍**만 통과합니다(`yd-db-expert` 가 "SQLite 고유 주제는 yd-sqlite-expert 를 쓴다" 라고 적은 것이 그 예). 새 스킬이 기존 스킬과 겹치면 경계를 다시 긋거나 이 문장을 넣으세요.

### 유지 원칙

- **모델이 이미 아는 일반론을 적지 않습니다.** "함수는 작게 유지한다" 류를 늘리면 토큰만 쓰고 판단은 바뀌지 않습니다. 담는 것은 네 가지뿐입니다 — 버전별 함정, 실측으로 확인한 사실, doksam 고유 규약, 판단이 갈리는 지점의 기준.
- 항목을 추가할 때 **"이게 없으면 에이전트가 실제로 틀리는가"** 에 답할 수 있어야 합니다. 답이 "아니오"면 넣지 않습니다.
- **단언은 재현으로 고정합니다.** 각 스킬의 `scripts/verify_*_claims.py` 가 문서 단언을 실제 엔진·도구로 재현하고, `tests/claims.json` 이 단언과 테스트를 잇습니다. PostgreSQL 은 `YD_PG_PSQL`, Oracle 은 `YD_ORACLE_SQLPLUS`(SQL 을 stdin 으로 받는 명령), React 는 `YD_REACT_VERIFY=1` 이 있어야 돌고, 없으면 사유를 찍고 건너뜁니다. 대상은 버리는 로컬 컨테이너뿐이며 pig 운영 DB 에 돌리지 않습니다. CI 는 전용 job(`pg.yml`·`oracle.yml`·`go-claims.yml`·`react-claims.yml`)이 돌리고 skip 이 섞이면 실패합니다. 재현이 문서와 다르면 문서를 고치거나 단언에 버전을 적습니다.
- 버전에 묶인 사실(pnpm 10 의 lifecycle 차단, TS6 의 `baseUrl` 제거, Go 1.22 ServeMux 패턴 등)은 **어느 버전부터인지 함께** 적습니다. 버전을 안 적으면 낡았는지 판단할 수 없습니다.

### 검사기

`skills/yd-frontend-build/scripts/check_bundle.py` 가 빌드 산출물의 외부 출처·소스맵·번들 예산을 검사합니다(`skills/yd-frontend-build/tests/` 가 강제).

**URL 이 있다고 요청이 나가는 것은 아닙니다.** React·react-router·Tailwind 는 에러 메시지에 문서 링크를 심어 두므로 단순 `grep https://` 는 정상 빌드에서도 여러 건을 뱉습니다. 그래서 `src=`/`href=`/`url()`/`@import`/`fetch()` 같은 **요청 유발 문맥**만 판정하고, 전수 감사는 `--strict` 로 분리했습니다. 이 구분을 없애면 노이즈에 묻혀 통과 판정이 무의미해집니다.

## 8. 아이콘 — 이모지 금지

`skills/**` 와 생성 산출물 HTML 에 이모지를 아이콘 대용으로 쓰지 않는다. Phosphor Icons(MIT) 의 `path` 를 인라인 `<svg class="icon">` 으로 넣는다.

원본: `https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/<name>.svg`

뒤로가기 `&lsaquo;`, 케밥 메뉴 `&#8942;` 같은 타이포그래피 문자는 이모지가 아니므로 그대로 써도 된다.

## 9. 제3자 저작물 표기

외부 자산을 들여오면 `THIRD-PARTY-NOTICES.md` 에 출처·라이선스·저작권 줄을 추가합니다. 라이선스는 **원문을 확인해서** 적습니다 — "아마 MIT" 로 적지 않습니다.

판단 기준은 **저장소에 들어오는가** 입니다.

- **들어온다** (아이콘 `path` 를 복사하는 등) → MIT·Apache 등 대부분이 고지를 요구하므로 **의무**입니다. 라이선스 전문까지 넣습니다.
- **산출물이 실행 시 내려받는다** (CDN 스크립트·웹폰트) → 우리가 재배포하는 것이 아니라 의무는 없지만, 산출물이 의존하므로 적습니다.

**`LICENSE` 파일에 덧붙이지 마세요.** MIT 전문에 내용을 붙이면 GitHub 의 라이선스 자동 인식이 깨질 수 있습니다. 표기는 `THIRD-PARTY-NOTICES.md` 에만 둡니다.

`tests/test_third_party_notices.py` 가 산출물 템플릿의 외부 호스트와 커밋된 Phosphor `path` 를 훑어 누락을 잡습니다.

## 10. 커뮤니케이션 가이드

- 변경 사항을 제안할 때는 "어떤 의도로 프롬프트/템플릿을 수정했는지" 명확히 설명하세요.
- 한국어로 소통하며, 기획/디자인 전문 용어(IA, Wireframe, Storyboard, User Flow 등)를 적절히 활용하세요.

## 메모리 경로 오버라이드

이 프로젝트의 auto-memory SSOT는 `.claude/memory/` 이다.

- 시스템 기본 경로(`~/.claude/projects/.../memory/`)는 사용하지 않는다.
- 모든 메모리 읽기/쓰기는 `.claude/memory/` 하위에서 수행한다.
- `MEMORY.md` 가 인덱스(단일). `user_*.md` 만 개인, 그 외는 팀 공유.
