---
name: skill-evolve
description: 피드백 기반으로 SKILL.md를 자동 개선하는 메타 스킬
---

# 스킬 자기개선

실행 중 발견한 문제, 사용자 피드백을 해당 스킬의 SKILL.md에 반영.

## 트리거

`/skill-evolve <스킬명> <피드백>`

## 프로세스

1. **대상 읽기**: `skills/<스킬명>/SKILL.md` 전체를 읽어 현재 내용 파악.
2. **분석**: 피드백 + 최근 실행 로그를 분석해 변경 부분 결정.
   - 새로운 gotcha → `## Learned warnings` 섹션에 추가
   - 단계 수정 → 프로세스 섹션 업데이트
   - 잘못된 명령 → 수정
3. **제안**: 기존 내용 인용 + 변경 diff(추가/삭제 라인별)를 명확히 제시.
4. **적용**: 확인 후 SKILL.md 직접 수정.
5. **커밋**: 브랜치 재확인 후 `git add . && git commit -m "Evolve skill/<스킬명>: <요약>"`.
6. **검증**: 수정된 스킬을 간단한 입력으로 한 번 실행해 동작 확인.

## 규칙

- 기존 경고는 삭제하지 않고 누적
- 날짜 태그 포함: `(YYYY-MM-DD)`
- 중복 경고는 병합
- 커밋 직전 브랜치 재확인 (자동 main 체크아웃으로 main 위 커밋 방지)

## 출력 형식

```text
개선 제안
기존: [인용]
제안: [수정안]

diff:
+ 추가 라인
- 삭제 라인

적용하시겠습니까? (Y/n)
```

## Learned warnings

- (2026-06-20) dok3node `srope-sk-skill-evolve` 흡수: frontmatter(`argument-hint`/`allowed-tools`), 기존내용 인용, 수정 후 검증 단계, diff 출력 형식 추가.
- (2026-08-01) doksam-skills 구조에 맞게 대상 파일 경로(`skills/<스킬명>/SKILL.md`) 및 frontmatter 형식(오직 `name`, `description`만 허용) 수정.
