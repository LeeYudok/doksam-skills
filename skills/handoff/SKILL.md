---
name: handoff
description: 세션을 끊고 다음 세션에 넘긴다 — 재개 가능한 상태를 HANDOFF.md 에 적고 같은 내용으로 핸드오프 이슈를 만들어 URL 하나로 건넨다. 그 URL 을 받으면 적힌 단언을 실제와 대조한 뒤 이어서 착수하고, 끝나면 결과를 남기고 닫는다. 컨텍스트가 40~50% 에 닿았을 때, "여기서 끊자 / 상태 남겨 / 이어받아 / 재개" 라고 하거나 핸드오프 이슈 URL 만 붙여넣었을 때 쓴다.
---

# 세션 핸드오프

핸드오프는 **요약이 아니라 재개 가능한 상태**다. 다음 세션이 이 문서만 읽고 같은
자리에서 다음 명령을 칠 수 있어야 한다. "뭘 했는지" 보다 **"지금 어디에 서 있고
다음에 뭘 치는지"** 가 본체다.

컨텍스트 사용량이 40~50% 에 닿으면 하던 걸 멈추고 이 스킬을 부른다. compaction 은
모델이 뭘 버릴지 스스로 고르므로 안전망일 뿐이다.

## 모드

| 호출 | 하는 일 |
| --- | --- |
| `/handoff` (인자 없음) | **작성** — `HANDOFF.md` 작성 + 핸드오프 이슈 생성 → 전체 URL 출력 |
| `/handoff <URL 또는 #N>` | **재개** — 이슈 본문·코멘트를 읽고 상태를 검증한 뒤 이어서 착수 |
| `/handoff done` | **종료** — 이어받은 작업 결과를 핸드오프 이슈에 남기고 닫는다 |

사용자가 핸드오프 이슈 URL 만 붙여넣어도(설명 없이) 재개 모드로 본다.

## 포지 판별 (첫 단계, 추측 금지)

레포마다 트래커가 다르다. **명령을 고르기 전에 리모트를 본다.**

```bash
git remote get-url origin
```

| 리모트 | CLI | 프로젝트 지정 |
| --- | --- | --- |
| `github.com/<owner>/<repo>` | `gh` | `--repo <owner>/<repo>` |
| GitLab (self-hosted 포함) | `glab` | `projects/<owner>%2F<repo>` (슬래시는 `%2F`) |
| Forgejo/Gitea | `curl` + API 토큰 | `/api/v1/repos/<owner>/<repo>` |

아래 예시는 두 갈래를 나란히 적는다. **자기 레포에 없는 쪽은 쓰지 않는다.**

---

## 1. 작성

### 1-1. 상태를 모은다 (추측 금지, 전부 실측)

```bash
git branch --show-current && git status --short
git log --oneline -5
git worktree list

# GitHub
gh pr list && gh issue list --label handoff --state open
# GitLab
glab mr list -P 10 && glab issue list --label handoff -P 5

# 띄워 둔 로컬 서버 — 포트는 이 레포 것으로 바꿔 적는다
lsof -nP -iTCP -sTCP:LISTEN | grep -E '<앱이름>|<포트>' || true
```

검증 게이트를 돌렸다면 **결과 원문**(통과/실패 줄)을 그대로 옮긴다. 안 돌렸으면
"안 돌림" 이라고 적는다 — 돌린 척이 제일 위험하다.

### 1-2. `HANDOFF.md` 를 쓴다 (레포 루트, 템플릿은 아래)

이미 있으면 **덮어쓴다**. 핸드오프는 항상 "지금 상태" 한 장이고, 과거 이력은
이슈와 그 레포의 작업 로그 파일(`CURRENT_TASK.md` 등)이 갖는다.

### 1-3. 핸드오프 이슈를 만든다

본문은 인라인 `jq --arg` 나 `--body "$(...)"` 말고 **파일 경유** — fenced code·표·
백슬래시가 들어가면 control char escape 에 걸리고, 큰 본문은 ARG_MAX 를 넘겨
빈 요청이 된다.

```bash
# GitHub
gh issue create --title "핸드오프: <한 줄 요약> (<YYYY-MM-DD>)" \
  --label handoff --body-file HANDOFF.md

# GitLab
glab api --method POST "projects/<owner>%2F<repo>/issues" \
  -F "title=핸드오프: <한 줄 요약> (<YYYY-MM-DD>)" \
  -F "labels=handoff" \
  -F "description=@HANDOFF.md" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['iid'], d['web_url'])"
```

`handoff` 라벨이 없으면 먼저 만든다(`gh label create handoff` / GitLab 은 라벨
자동 생성). 라벨이 있어야 다음 세션이 "열린 핸드오프" 를 한 번에 찾는다.

`HANDOFF.md` 첫 줄에 그 URL 을 적어 넣고(이슈 ↔ 파일 상호 참조), 레포에 작업
로그 파일이 있으면 맨 위에도 한 줄 남긴다. 그 다음 커밋한다.

```bash
git add HANDOFF.md && git commit -m "docs: 세션 핸드오프 (#<N>)"
```

브랜치에 커밋 중이면 **푸시까지** 한다 — 새 세션이 다른 워크트리에서 이어받을 수 있어야 한다.

### 1-4. 사용자에게는 URL 한 줄

마지막 출력은 항상 **전체 URL**. `/clear` 후 그 URL 만 붙여넣으면 이어진다고 알린다.

---

## 2. 재개

### 2-1. 본문과 코멘트를 읽는다

```bash
# GitHub
gh issue view <N> --comments
# GitLab
glab issue view <N>
glab api "projects/<owner>%2F<repo>/issues/<N>/notes" | python3 -c "
import json,sys
for n in json.load(sys.stdin): print('---', n['author']['username'], n['created_at']); print(n['body'][:2000])"
```

코멘트가 본문보다 최신일 수 있다 — **항상 둘 다** 읽는다.

### 2-2. 단언을 검증한다 (이슈 본문도 decay 한다)

본문이 말하는 것 중 **행동을 바꾸는 단언 1~2개**는 실제와 대조한 뒤 움직인다.
실전에서 "열려 있다" 던 PR 이 이미 머지돼 있던 적이 있다.

| 본문이 말하는 것 | 확인 |
| --- | --- |
| 브랜치/워크트리 | `git worktree list`, `git branch -a --contains <sha>` |
| PR/MR 상태 | `gh pr view <N>` / `glab mr view <N>` — 이미 머지됐을 수 있다 |
| 이슈 상태 | `gh issue view <N>` / `glab issue view <N>` — 이미 닫혔을 수 있다 |
| 띄워 둔 서버 | `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:<port>/` |
| 배포된 버전 | 서비스의 `/version`·`/healthz` 를 직접 친다 |
| 다음 명령 | 경로·스크립트가 아직 있는지 (`ls`, `git show --stat`) |

충돌하면 **실제 상태를 믿고** 이슈에 코멘트로 교정한다.

### 2-3. 이어서 착수

- 워크트리가 남아 있으면 그 안에서, 없으면 `git worktree add ../<repo>-<n> <branch>`.
- 정식 클론에서는 `checkout`/`switch` 금지(pull·읽기만) — 다른 세션의 발밑이 바뀐다.
- 핸드오프 이슈는 **작업 이슈가 아니다** — 실제 작업 이슈 번호가 본문에 있으면 그걸
  브랜치/커밋/PR 에 박는다. 핸드오프 이슈는 세션 사이를 잇는 표식일 뿐이다.

---

## 3. 종료

이어받은 작업이 끝나면(또 다른 핸드오프를 쓰는 경우 포함) 핸드오프 이슈를 닫는다.

```bash
# GitHub
gh issue comment <N> --body-file <결과파일>.md && gh issue close <N>
# GitLab
glab api --method POST "projects/<owner>%2F<repo>/issues/<N>/notes" -F "body=@<결과파일>.md"
glab issue close <N>
```

닫을 때 한 줄: 무엇이 끝났고, 다음 핸드오프가 있으면 그 URL.
열린 핸드오프 이슈가 둘 이상 쌓이면 어느 게 최신인지 모른다 — **동시에 하나만** 연다.

---

## HANDOFF.md 템플릿

````markdown
# HANDOFF — <한 줄 요약>

- 이슈: <핸드오프 이슈 URL>  ·  작성: <YYYY-MM-DD HH:MM:SS.mmm>
- 작업 이슈/PR: #<N> · #<M> (<상태>)
- 브랜치: `<branch>`  ·  워크트리: `<path>` (없으면 "없음 — 새로 만들 것")
- HEAD: `<sha>` (<push 여부>)

## 지금 어디까지

<끝난 것 / 안 끝난 것을 사실로. "대체로 됨" 금지.>

## 검증 결과 (원문)

```
<테스트·빌드·게이트의 마지막 실행 결과 그대로. 안 돌렸으면 "안 돌림">
```

## 실행 중인 것

| 대상 | 주소 | 어떻게 띄웠나 |
| --- | --- | --- |
| <로컬 서버> | <http://127.0.0.1:포트> | <명령 + 실행 디렉터리> |
| <터널/프록시> | <127.0.0.1:포트> | <스크립트 경로, pid> |

## 미결 판단

<사람이 정해야 하는 것. 선택지와 각 선택의 결과까지.>

## 다음에 칠 명령

```bash
# 복붙 가능한 형태로, 실행 디렉터리 포함
cd <절대경로>
<command>
```

## 함정

<이번에 밟은 것. 도구·플랫폼 차이, 잘못 읽기 쉬운 신호 등.>
````

---

## 원칙

- **사실만**. 날짜·이슈번호·수치는 실측으로 채우고, 모르면 "모름" 이라고 쓴다.
- **명령은 복붙 가능하게**. 실행 디렉터리 포함, 상대경로 금지.
- **큰 tool output 은 붙여넣지 않는다** — 파일로 남기고 경로와 마지막 몇 줄만.
- 본문에 `.env` 값·토큰·비밀번호를 넣지 않는다. 키 **이름**까지만.
- 한 세션 = 한 작업 이슈. 핸드오프는 그 경계를 넘기는 장치지, 한 세션을 늘리는 장치가 아니다.
