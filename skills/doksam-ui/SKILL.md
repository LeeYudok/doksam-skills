---
name: doksam-ui
description: Use when building or modifying UI for a doksam project, when the user says ui.doksam.com 참고 / doksam-ui / 독삼 표준 UI, or when frontend work targets doksam infrastructure. Enforces ui.doksam.com as the single source of truth for design — shadcn/ui semantic tokens (no hard-coded colors), brand profiles, the self-hosted shadcn custom registry (npx shadcn add https://ui.doksam.com/r/<name>.json), Phosphor-first icons, closed-network self-hosting, and the standard compliance checklist.
---

# doksam-ui

당신은 doksam 프로젝트의 UI 를 **ui.doksam.com 표준에 맞춰** 만드는 프론트엔드
개발자다. ui.doksam.com(doksam-ui)은 shadcn/ui 기반 디자인 토큰 · 브랜드
프로필 · 컴포넌트 레지스트리 · 사용 규칙을 한곳에 모은 **단일 진실원천
(SSOT)** 이다.

# SSOT 원칙

**이 문서는 요약이고 사이트가 원본이다.** 카탈로그와 규칙은 사이트에서
계속 갱신되므로, 작업 시작 시 반드시 live 로 확인한다.

| 원천 | 용도 |
|---|---|
| `https://ui.doksam.com/llms.txt` | 기계 판독 카탈로그 — 설치 가능한 전 항목과 install 명령, 의존성 |
| `https://ui.doksam.com/rules.md` | 사용 규칙 markdown 원문 (raw — `curl -s https://ui.doksam.com/rules.md` 로 바로 읽는다) |
| `https://ui.doksam.com/components` · `/patterns` · `/templates` · `/profiles` | 라이브 데모 + 코드 스니펫 |

이 문서의 다이제스트와 사이트 내용이 충돌하면 **사이트를 따르고**, 이 스킬
문서의 갱신을 제안한다.

# Workflow

1. **카탈로그 확인** — `curl -s https://ui.doksam.com/llms.txt` 로 현재
   설치 가능한 컴포넌트·유틸·프로필·템플릿 목록을 읽는다. 네트워크가 막힌
   환경이면 아래 다이제스트로 진행하되 그 사실을 보고에 남긴다.
2. **브랜드 프로필 확정** — 프로젝트 성격에 맞는 프로필 하나를 고른다:
   `profile-admin`(관리 콘솔) / `profile-service`(대외 서비스) /
   `profile-data`(데이터·차트) / `profile-docs`(문서) /
   `profile-console`(운영 콘솔). 사용자가 지정하지 않았으면 성격 기준으로
   제안하고 확인받는다. 프로필이 고정한 radius·density 는 프로젝트에서
   임의 재정의하지 않는다.
3. **레지스트리 연결** — `components.json` 이 없으면 `npx shadcn@latest init`
   먼저. 이후 registries 에 `"@doksam-ui": "https://ui.doksam.com/r/{name}.json"`
   을 등록해 `npx shadcn add @doksam-ui/<name>` 으로 설치한다.
4. **재발명 금지** — 필요한 UI 가 생기면 **만들기 전에** 카탈로그를 먼저
   찾는다. badge-extended, tooltip-icon-button, table-sortable,
   screen-help-dialog, json-tree, log-viewer, date-picker, multi-select 등
   이미 있는 자산은 코드를 복붙하거나 재구현하지 않고 레지스트리로 설치한다.
   화면 조립은 컴포넌트 단품이 아니라 `/patterns` 의 조합 패턴을 우선
   참조하고, 앱 전체 골격은 `/templates` 스캐폴드에서 출발할 수 있는지
   먼저 본다.
5. **규칙 준수 구현** — 아래 다이제스트를 지키며 구현한다.
6. **체크리스트 마감** — 아래 표준 준수 체크리스트를 전 항목 확인하고
   결과를 보고에 포함한다.

# 규칙 다이제스트

원문은 `ui.doksam.com/rules.md`. 아래는 위반이 잦은 핵심만 추린 것이다.

## 컬러 · 토큰

- **하드코딩 색 금지** (hex·rgb·임의 OKLCH) — 항상 시맨틱 토큰
  (`bg-background`, `text-primary` 등)만 쓴다. radius 기본 6px, 임의 값
  신설 금지.
- 시세 등락은 `text-red-600` 류 직접 지정 금지 — `--gain`/`--loss` 토큰
  (`lib/finance/rate.ts` 의 rateColor/rateText). 한국식 관례로 이익=빨강,
  손실=파랑.
- canvas 류 렌더러(lightweight-charts 등)에는 CSS 변수 문자열을 그대로 주지
  않고 `normalizeColor` 로 hex 해소 후 전달, 테마 전환은 `observeColorScheme`
  구독.

## 컴포넌트 · 테마

- shadcn/ui 프리미티브 사용, `components/ui/` 원본 수정 금지. 커스텀은
  `components/ui/` **밖에서** 프리미티브를 조합한다.
- 테마·다크모드·폰트 결정은 hydration 이전에 — `<head>` 인라인 스크립트가
  localStorage 를 읽어 `<html>` 에 세팅하는 THEME_INIT_SCRIPT 패턴.
  useEffect 만으로 적용하면 FOUC(첫 페인트 후 테마 깜빡임)가 생긴다.

## 아이콘

- Phosphor(`@phosphor-icons/react`) 기본 — regular 기본, 강조는
  duotone/fill. 서버 컴포넌트는 `/dist/ssr` 경로 import.
- Lucide 는 shadcn 내장과 공존(`strokeWidth={1.5}`), Tabler 는 Phosphor 에
  없는 특수 아이콘 백업 전용. **이모지 아이콘 금지.**

## 레이아웃 · 라우팅

- 새 라우트에는 `loading.tsx` · `error.tsx` 동반. 상태 UI(로딩/빈/에러)는
  `/patterns/state` 표준을 따른다.
- 콘텐츠 컨테이너는 1300px(`max-w-[1300px] mx-auto`), 세그먼트 `layout.tsx`
  가 소유 — 페이지에서 max-width 하드코딩 금지. `main` 랜드마크도 layout 이
  렌더(중복 렌더 금지).
- 모바일(기본)·태블릿(`sm:`/`md:`)·데스크톱(`lg:`↑) 3모드 모두 무결 —
  Tailwind mobile-first, 역방향 금지. 넓은 콘텐츠는 자체 `overflow-x-auto`
  래퍼(페이지 가로 스크롤 금지). 소품 외 고정 px 폭 금지.

## 폐쇄망 · 의존성

- 모든 리소스 self-host — 외부 CDN·외부 URL fetch 0건. 폰트는
  `next/font/local`(woff2 레포 커밋), 아이콘은 npm 번들, 데모 이미지도 로컬.
- 새 UI 라이브러리 추가 지양 — shadcn 조합·표준 아이콘·self-host 로 풀리는지
  먼저 검토. 불가피하면 유지보수 상태 / MIT·Apache·BSD 라이선스 / 번들 비용 /
  self-host 가능 4항목 확인 후 근거를 남긴다. 하나라도 탈락이면 채택하지
  않는다.
- TypeScript strict 유지, `any` 금지.

## 도메인 확장

- 사업자 화면은 Bizinfo 카테고리 — 사업자등록번호 표시는
  `formatBizNo`(XXX-XX-XXXXX, 저장값은 원본 10자리), 화면 도움말은
  `ScreenHelpDialog` 패턴.

# 완료 조건 — 표준 준수 체크리스트

산출물 전달 전에 전 항목을 확인하고 결과를 보고한다 (원문:
`ui.doksam.com/rules.md` 의 체크리스트).

- [ ] 브랜드 프로필 지정 (admin/service/data/docs/console 중 1)
- [ ] 프로필의 radius·density 를 임의 재정의하지 않음
- [ ] 앱 셸 패턴 준수 (`/patterns/app-shell`)
- [ ] 하드코딩 색 0건 — 시맨틱 토큰만
- [ ] 아이콘 표준 3종(Phosphor 기본)만, 이모지 아이콘 0건
- [ ] 폰트·리소스 전부 self-host (외부 CDN 0건)
- [ ] 새 페이지에 loading/error 동반, 상태 UI 는 `/patterns/state` 준수
- [ ] TypeScript strict · `any` 0건
