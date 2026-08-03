# Memory Index

이 저장소 auto-memory SSOT는 `.claude/memory/` (시스템 기본 경로 미사용).
타입접두: `project_`/`feedback_`/`reference_`/`user_`. `user_*`만 개인, 그 외는 팀 공유.

> 2026-08-04 고아 auto-memory 경로 2곳(`...-doksam-skills/`, 흡수된 `...-mobile-web-planner-agent/`)에서 이관(#104).

## 프로젝트
- [다듬기 백로그](project_polish-backlog.md) — mobile-web-planner 미착수 다듬기 2건(헤더 배지 가림, BR 배지번호 인용 기계검증), 이슈 미등록 상태

## 피드백
- [스킬 품질 픽스는 계약 3층위로](feedback_quality-fix-at-contract-level.md) — 템플릿 CSS > 검증기 > SKILL.md 순 보장, 콜드 재생성으로 실증까지 한 세트

## 참고
- [로컬 HTML 렌더 QA 파이프라인](reference_local-html-render-qa.md) — mongoose 서빙 + headless Chrome 스크린샷, 검증기 통과 ≠ 렌더 정상
- [JB금융 AX 전사 용어집](reference_transcription-glossary-si-project.md) — 정본은 `~/.config/session-recording/glossary.d/si-project.txt`, 스킬이 `--prompt` 자동 주입
