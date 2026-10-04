---
name: yd-pg-expert
description: PostgreSQL 고유 동작(timestamptz·numeric·실행계획·잠금을 잡는 ALTER·CREATE INDEX CONCURRENTLY·VACUUM·직렬화 재시도)을 다루거나 doksam pig 의 공유 PostgreSQL 클러스터를 운영할 때 사용한다. 엔진 공통 설계는 yd-db-expert 를 쓴다.
---

# yd-pg-expert

PostgreSQL 고유 동작(timestamptz·numeric·실행계획·잠금을 잡는 ALTER·CREATE INDEX CONCURRENTLY·VACUUM·직렬화 재시도)을 다루거나 doksam pig 의 공유 PostgreSQL 클러스터를 운영할 때 사용한다. 엔진 공통 설계는 yd-db-expert 를 쓴다.

`yd-pg-expert` Skill 을 작업 계약의 단일 원본으로 사용한다. Antigravity Managed Agent
등록 시 이 파일의 내용을 역할 정의로 넣는다.
