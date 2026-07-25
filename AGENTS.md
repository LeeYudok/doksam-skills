# Mobile Web Planner Agent - AI Agent Guidelines

이 문서는 AI 에이전트(Gemini, Claude 등)가 이 저장소(Repository)에서 작업할 때 지켜야 할 규칙과 프로젝트 컨텍스트를 정의합니다. `GEMINI.md`, `CLAUDE.md` 등에서 이 파일을 참조합니다.

## 1. 프로젝트 개요 (Project Context)
- **목적**: Google Antigravity 등 범용 AI 에이전트를 '모바일 웹/앱 UX/UI 수석 기획자'로 동작하게 만드는 커스텀 스킬 패키지입니다.
- **핵심 역할**: 사용자의 요청(예: "쇼핑몰 기획해줘")에 따라 IA 및 화면 설계서(HTML 기반 스토리보드)를 자동 생성합니다.

## 2. 기술 스택 (Tech Stack)
- **프롬프트/스킬 정의**: Markdown (`SKILL.md`)
- **템플릿 디자인**: HTML5, Vanilla CSS (외부 프레임워크 지양)
- **테스트 스크립트**: Python 3 (`generate_doksam.py`)

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

## 5. 커뮤니케이션 가이드
- 변경 사항을 제안할 때는 "어떤 의도로 프롬프트/템플릿을 수정했는지" 명확히 설명하세요.
- 한국어로 소통하며, 기획/디자인 전문 용어(IA, Wireframe, Storyboard, User Flow 등)를 적절히 활용하세요.
