# Memory Index

이 프로젝트 auto-memory SSOT는 `.claude/memory/` (시스템 기본 경로 미사용).
타입접두: `project_`/`feedback_`/`reference_`/`user_`. `user_*`만 개인, 그 외는 팀 공유.

> 2026-08-04 auto-memory 감사 — 고아 경로 2곳(`...-doksam-skills/`, `...-mobile-web-planner-agent/`)에서 이관.
> mobile-web-planner 스킬은 이 레포 `skills/mobile-web-planner/` 로 흡수됐으므로 그 경로의 메모리도 여기가 주인이다.

> 2026-08-17 사실 확인 — `project_polish-backlog.md`(다듬기 후보 2건) 해소·삭제. 헤더 배지 gutter 는
> `template.html` `.mock-header:has(.pointer-badge)` 로, BR 배지 인용 검증은 `validate_storyboard.py` 의
> `BADGE_CITE_RE` 로 이미 들어가 있었다 (이슈 #132).

## 피드백
- [스킬 품질 픽스는 계약 3층위로](feedback_quality-fix-at-contract-level.md) — 템플릿 CSS > 검증기 > SKILL.md 순으로 보장하고, 콜드 재생성 실증까지 한 세트

## 참고
- [로컬 HTML 렌더 QA 파이프라인](reference_local-html-render-qa.md) — mongoose 서빙 + headless Chrome 스크린샷. 검증기 통과 ≠ 렌더 정상
- [JB금융 AX 전사 용어집](reference_transcription-glossary-si-project.md) — 정본은 `~/.config/session-recording/glossary.d/`, 스킬이 `--prompt` 로 자동 주입
