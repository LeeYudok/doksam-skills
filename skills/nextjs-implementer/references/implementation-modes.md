# 구현 모드별 실행 계약

`SKILL.md`에서 구현 프로필을 정한 뒤 선택한 절만 적용한다. 기존 프로젝트에는
새 스캐폴드를 덮지 않고 현재 package manager와 명령을 따른다.

## Next.js App Router

새 프로젝트는 TypeScript, App Router, ESLint를 켠 `create-next-app`으로 만든다.
기본 확인 명령은 프로젝트 scripts에 맞춰 다음 의미를 모두 충족해야 한다.

```sh
pnpm lint
pnpm test
pnpm build
pnpm dev
```

기본 URL은 `http://localhost:3000`이지만 실제 포트를 기록한다. Next.js 풀스택은
Server Actions/Route Handlers를 사용하고, Java 모드는 타입 있는 API client와
rewrite를 사용한다.

## Vite + React SPA

새 프로젝트는 pnpm + Vite + React + TypeScript로 만들고 `react-router`를
추가한다. 기존 프로젝트의 router major를 보존한다.

```sh
pnpm lint
pnpm exec tsc --noEmit
pnpm test
pnpm build
python3 <frontend-build-스킬>/scripts/check_bundle.py dist
pnpm dev
```

기본 URL은 `http://localhost:5173`이지만 실제 포트를 기록한다. SPA fallback은
호스팅 환경에도 설정해 직접 URL 진입이 404가 되지 않게 한다. API가 있으면
`server.proxy`를 사용하고, 배포 시 API base URL은 공개 설정과 비밀 설정을
분리한다.

## traceability.json

저장소의 `docs/traceability.json`을 기본 경로로 쓰되 기존 문서 디렉터리 규약이
있으면 따른다. JSON은 기계가 읽을 수 있어야 하며 주석을 넣지 않는다.

```json
{
  "documentVersion": "1.0.0",
  "frontendMode": "vite-react-spa",
  "screens": [
    {
      "screenId": "DTC-BOARD-001",
      "route": "/board",
      "implementation": ["src/routes/board.tsx"],
      "rules": [
        {
          "ruleId": "DTC-BOARD-001.IN-01",
          "tests": ["src/routes/board.test.tsx"]
        }
      ]
    }
  ]
}
```

규칙 ID 형식은 `<화면ID>.<구분>-<2자리 번호>`다. 구분은 `IN`(입력 검증),
`OUT`(출력 규칙), `INT`(인터랙션), `EDGE`(엣지케이스)다. 같은 ID를 두 번 쓰지
않고, 한 규칙이 여러 파일에 걸리면 배열에 모두 기록한다. 구문서의 임시 키는
원문을 수정하지 않고 manifest에만 `legacy: true`로 표시한다.

규칙 ID가 있는 최신 문서는 구현 완료 전에 다음을 실행한다.

```sh
python3 <스킬경로>/scripts/validate_traceability.py \
  docs/traceability.json docs/<프로젝트>_business-rules.md --repo-root .
```

화면·규칙 ID의 누락/중복/잘못된 연결, 구현·테스트 파일의 부재를 모두
검사하며 위반이 있으면 exit 1이다.
