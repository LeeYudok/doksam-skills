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
- `skills/mobile_web_planner/SKILL.md`: 기획자 페르소나, 워크플로우, 시스템 프롬프트가 정의된 핵심 파일.
- `skills/mobile_web_planner/resources/template.html`: 기획서 결과물로 출력될 HTML/CSS 스켈레톤.
- `generate_doksam.py`: `template.html`을 파싱하여 가상의 데이터(덕삼뉴스 예시)를 넣고 결과물을 생성해보는 테스트 스크립트.
- `examples/`: 생성된 결과물 예시가 저장되는 디렉토리.

## 4. 에이전트 작업 지침 (Agent Instructions)

### 스킬 및 프롬프트 수정
- 기획자의 말투, 프로세스, 결과물 형식을 변경해야 할 경우 `SKILL.md`를 수정하세요.
- 프롬프트는 명확하고 구체적으로 작성하며, 변수나 플레이스홀더를 적절히 활용하세요.

### 템플릿(HTML/CSS) 수정
- 화면 설계서의 디자인이나 레이아웃을 변경할 때는 `resources/template.html`을 수정하세요.
- 복잡함을 줄이기 위해 TailwindCSS 같은 프레임워크 대신 **Vanilla CSS**를 사용합니다.
- 클래스 네이밍은 직관적으로 작성하고, 인라인 스타일보다는 `<style>` 태그 내부에 정리하는 것을 권장합니다.
- AI가 쉽게 파싱하고 데이터를 채워 넣을 수 있도록 구조를 단순하게 유지하세요.

### 테스트 및 검증
- 템플릿(`template.html`)을 수정한 후에는 반드시 터미널에서 다음 명령어를 실행하여 렌더링에 문제가 없는지 확인하세요.
  ```bash
  python generate_doksam.py
  ```
- 실행 후 `examples/doksam_news_storyboard.html` 파일이 정상적으로 갱신되었는지 확인하고, 필요한 경우 변경 사항을 사용자에게 설명하세요.

## 5. 커뮤니케이션 가이드
- 변경 사항을 제안할 때는 "어떤 의도로 프롬프트/템플릿을 수정했는지" 명확히 설명하세요.
- 한국어로 소통하며, 기획/디자인 전문 용어(IA, Wireframe, Storyboard, User Flow 등)를 적절히 활용하세요.
