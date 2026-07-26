# Mobile Web Planner 크로스런타임 Agent Adapter 구현 계획

**Goal:** 공통 Skill을 자체 검증 가능한 실행 코어로 만들고 Claude Code,
Codex, Google Antigravity용 Agent Adapter를 제공한다.

**설계 문서:** `docs/superpowers/specs/2026-07-26-cross-runtime-agent-adapters-design.md`

## 작업

- [x] Skill 내부에 구조 검증기를 번들링하고 기존 CLI 호환 래퍼를 둔다.
- [x] `SKILL.md`에 생성·수정·검증·시각 QA Workflow와 완료 조건을 추가한다.
- [x] `agents/openai.yaml` UI 메타데이터를 추가한다.
- [x] Claude Code Agent Adapter를 추가한다.
- [x] Codex Agent Adapter를 추가한다.
- [x] Antigravity Managed Agent용 역할 정의 원본을 추가한다.
- [x] `install.sh`에 `--skill-only`와 `--with-agent`를 추가한다.
- [x] Agent와 설치 동작 테스트를 추가한다.
- [x] 전체 테스트와 예시 불변식을 검증한다.
