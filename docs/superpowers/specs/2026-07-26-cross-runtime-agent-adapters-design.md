# Mobile Web Planner 크로스런타임 Agent Adapter — 설계

- 작성일: 2026-07-26
- 대상: Claude Code, Codex, Google Antigravity

## 1. 목표

`mobile-web-planner`의 기획 규칙을 한 곳에서 관리하면서 세 런타임에서
전문 기획자 Agent로 호출할 수 있게 한다. 공통 Skill은 생성·검증 절차를
자체 포함하고, 플랫폼별 Agent 파일은 역할과 Skill 연결만 담당한다.

## 2. 원칙

1. `skills/mobile-web-planner/SKILL.md`를 행동 계약의 단일 원본으로 둔다.
2. 플랫폼별 Agent 파일에 화면설계 규칙이나 마크업 예시를 복제하지 않는다.
3. 구조 검증기는 설치되는 Skill 내부에 둔다.
4. 기존 `scripts/check_output.py` 명령은 호환 래퍼로 유지한다.
5. 기본 설치는 기존과 동일하게 Skill만 설치한다.
6. `--with-agent`를 지정한 경우에만 플랫폼별 Agent Adapter도 설치한다.
7. Google 로컬 Antigravity는 공통 Skill을 Agent에 장착한다. Gemini API
   Managed Agent용 `AGENTS.md`는 등록 소스로 제공하되 API 등록은 별도
   배포 단계로 남긴다.

## 3. 구조

```text
skills/mobile-web-planner/
  SKILL.md
  agents/openai.yaml
  resources/template.html
  scripts/validate_storyboard.py

.claude/agents/mobile-web-planner.md
.codex/agents/mobile_web_planner.toml
.agents/AGENTS.md

scripts/check_output.py
install.sh
```

## 4. 실행 계약

공통 Agent Workflow는 다음 순서를 따른다.

1. 요청에서 프로젝트명, 사용자, 기능, 플랫폼과 제약을 추출한다.
2. 결과를 크게 바꾸는 누락 정보만 질문하고, 안전하게 유추 가능한 내용은
   가정으로 처리한다.
3. IA와 화면 목록을 확정한다.
4. `resources/template.html`을 사용해 단일 HTML Storyboard를 생성한다.
5. `scripts/validate_storyboard.py`를 실행한다.
6. 위반이 있으면 수정하고 검증을 반복한다.
7. 브라우저 도구가 있으면 렌더링하여 잘림·겹침·가독성을 확인한다.
8. 검증을 통과한 파일 경로와 주요 가정을 전달한다.

기존 문서 수정 시 화면 ID를 가능한 한 유지하고, 버전과 Document History를
갱신한 뒤 전체 문서를 다시 검증한다.

## 5. 플랫폼별 책임

### Claude Code

`.claude/agents/mobile-web-planner.md`가 `mobile-web-planner` Skill을
preload한다. Agent 본문에는 완료 조건과 공통 Skill 준수만 둔다.

### Codex

`.codex/agents/mobile_web_planner.toml`이 `name`, `description`,
`developer_instructions`를 정의한다. 모델과 sandbox는 호출 세션에서
상속하여 배포 환경을 강제로 제한하지 않는다.

### Google Antigravity

로컬 Antigravity 제품군은 설치된 공통 Skill을 사용한다.
`.agents/AGENTS.md`는 Gemini API Managed Agent 등록 시 사용할
역할 정의 원본이다. 인증과 원격 Agent 생성은
외부 상태 변경이므로 이 저장소 설치 과정에서 자동 수행하지 않는다.

## 6. 설치 정책

- `./install.sh` 또는 `--skill-only`: 기존 Skill 설치만 수행한다.
- `./install.sh --with-agent`: Skill과 Claude/Codex Agent Adapter를 설치한다.
- `--project <dir> --with-agent`: 대상 프로젝트에 Skill과 프로젝트 범위
  Claude/Codex Agent Adapter를 설치한다.
- Antigravity Managed Agent 등록 원본은 설치 결과에 경로를 안내한다.
- 충돌, `--force`, `--copy`, `--uninstall` 정책은 기존 설치 계약을 그대로
  적용한다.

## 7. 검증

- Python 단위 테스트: Agent 필수 필드, 공통 Skill 연결, 번들 검증기
- Bash 설치 테스트: 기본 호환성, `--with-agent`, 프로젝트 설치, 제거
- 기존 예시 재생성 및 클래스 계약
- `git diff --exit-code examples/` 불변식
