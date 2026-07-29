# doksam-skills

Claude Code, Codex, Antigravity 에서 쓰는 Agent Skill 모음입니다. `install.sh` 가 `skills/` 아래 모든 스킬을 세 런타임 경로에 노출합니다.

| 스킬 | 설명 |
|---|---|
| [mobile-web-planner](skills/mobile-web-planner/SKILL.md) | 모바일 웹/앱 UX/UI 수석 기획자 — 모든 도메인의 화면설계서(스토리보드)와 Business Rules 를 생성. 플랫폼별 Agent Adapter 포함 |
| [memory-factcheck](skills/memory-factcheck/SKILL.md) | 에이전트 영속 메모리를 코드·DB·이슈 등 실제 근거와 대조해 낡은 기억을 교정하는 감사 스킬 |
| [nextjs-implementer](skills/nextjs-implementer/SKILL.md) | mobile-web-planner 의 화면설계서·Business Rules 한 쌍을 받아 구현으로 이어가는 후속 스킬 — 프론트는 Next.js + React, 백엔드는 Next.js 풀스택 또는 Java 1.8 API 서버 중 선택 |

## Mobile Web Planner

뉴스뿐만 아니라 쇼핑몰, 커뮤니티, O2O 예약 서비스 등 **모든 도메인의 모바일 기획**을 완벽하게 수행할 수 있도록 설계되었습니다.

## 설치 (Install)

[skills.sh](https://www.skills.sh) 생태계의 `skills` CLI 로 바로 설치할 수 있습니다.

```bash
npx skills add leeyudok/doksam-skills
```

저장소를 클론해 두고 쓰려면 `install.sh` 를 씁니다. 이쪽은 기본이 심링크
설치라 저장소에서 `SKILL.md` 를 고치면 런타임에 즉시 반영되고, 이름 있는
Agent Adapter 설치(`--with-agent`)와 프로젝트 단위 설치(`--project`)를
지원합니다. 자세한 내용은 아래 [사용 방법](#사용-방법-how-to-use) 을 보세요.

```bash
git clone https://github.com/leeyudok/doksam-skills.git
cd doksam-skills
./install.sh
```

## 쉽게 사용

```text
1. 이 저장소를 클론
2. cd [클론폴더]
3. claude
4. 입력창에 "주식스윙자동매매 모바일웹 버전으로 50-100장 (너가 필요하다고 생각하는 만큼) 내외로 기획서 만들어
병렬로 멀티llm 사용해서 해 ./output/yyyymmdd-[요약].html"
5. 저장된 ./output/yyyymmdd-[요약].html 파일을 열어서 디자인을 확인
```

## 사용 방법 (How to Use)

1. 이 저장소를 클론합니다.
2. 설치 스크립트를 실행합니다. 기본은 심링크이므로, 이후 저장소에서 `SKILL.md` 를 수정하면 세 런타임에 즉시 반영됩니다.

   ```bash
   ./install.sh
   ```

   기본값은 세 런타임에 공통 Skill만 설치합니다. Claude Code와 Codex의
   이름 있는 Agent Adapter까지 설치하려면 다음 옵션을 사용합니다.

   ```bash
   ./install.sh --with-agent
   ```

   설치 경로는 `skills/` 아래 **모든 스킬**에 대해 아래 패턴으로 생깁니다
   (`<skill>` 은 스킬 디렉터리명, `<skill_>` 은 `-` 를 `_` 로 바꾼 이름).

   | 런타임 | 설치 경로 |
   | --- | --- |
   | Codex, Gemini CLI | `~/.agents/skills/<skill>` |
   | Claude Code | `~/.claude/skills/<skill>` |
   | Antigravity (`agy`) | `~/.gemini/config/skills/<skill>` |
   | Claude Code Agent (`--with-agent`) | `~/.claude/agents/<skill>.md` |
   | Codex Agent (`--with-agent`) | `~/.codex/agents/<skill_>.toml` |

   Agent Adapter 원본은 각 스킬이 소유합니다(`skills/<skill>/agents/`).
   `--with-agent` 는 `claude.md` · `codex.toml` 이 있는 스킬만 설치합니다.

   Google Antigravity 로컬 제품군은 설치된 공통 Skill을 Agent에 장착합니다.
   Gemini API Managed Agent 등록용 역할 정의 원본은
   `skills/<skill>/agents/antigravity.md` 에 있으며, 인증이 필요한 원격 등록은
   설치 스크립트가 자동 수행하지 않습니다.

   특정 프로젝트에만 넣으려면 `--project` 를 씁니다. Antigravity 의 프로젝트 경로(`.agents/`)는 Codex 와 같으므로 두 경로로 세 런타임을 모두 커버합니다.

   ```bash
   ./install.sh --project ~/work/my-service
   # -> ~/work/my-service/.claude/skills/mobile-web-planner   (Claude Code)
   # -> ~/work/my-service/.agents/skills/mobile-web-planner    (Codex, Antigravity)
   ```

   Antigravity 의 프로젝트 경로는 `.git` 이 있는 **저장소 루트** 기준으로 해석되므로, `--project` 에는 하위 디렉터리가 아니라 저장소 루트를 넘기세요.

   심링크 대신 복사하려면 `--copy`, 미리 확인만 하려면 `--dry-run`, 제거는 `--uninstall` 입니다. 전체 옵션은 `./install.sh --help` 를 참고하세요.

3. 에이전트에게 요청합니다.

   > *"새로운 반려동물 용품 쇼핑몰 모바일웹 기획해줘"*
   > *"동네 맛집 리뷰 커뮤니티 앱 화면 기획서 작성해볼래?"*

4. 에이전트가 스킬을 감지하고, 해당 도메인의 IA와 화면 설계서를 단일 HTML 파일로 저장해 줍니다.

### 이름 있는 Agent 호출

`--with-agent`로 설치했다면 Claude Code에서는 전용 Agent를 메인 세션으로
실행할 수 있습니다.

```bash
claude --agent mobile-web-planner \
  "테니스 동호회 모바일 웹 화면설계서 만들어줘"
```

Codex에서는 custom agent 이름을 지정해 위임하도록 요청합니다.

```text
mobile_web_planner agent를 사용해서 테니스 동호회 모바일 웹 화면설계서를 만들어줘
```

Antigravity 로컬 환경에서는 같은 요청이 `mobile-web-planner` Skill을
자동 감지합니다. Managed Agent로 배포할 때는
`skills/mobile-web-planner/agents/antigravity.md` 와 공통 Skill을 등록 소스로
사용합니다.

## 구조 (Structure)

**스킬 하나가 자기 자산을 전부 소유합니다.** 행동 계약(`SKILL.md`), 리소스,
스크립트, 테스트, 세 런타임의 Agent Adapter 가 모두 `skills/<skill>/` 안에
있습니다. 저장소 루트에는 설치기와 공통 규약 검증만 둡니다.

```text
doksam-skills
├── skills
│   ├── memory-factcheck
│   │   └── SKILL.md                     메모리 팩트체크 감사 스킬
│   └── mobile-web-planner
│       ├── SKILL.md                     공통 Agent Workflow와 클래스 계약
│       ├── agents
│       │   ├── claude.md                Claude Code Agent Adapter
│       │   ├── codex.toml               Codex Agent Adapter
│       │   ├── antigravity.md           Gemini API Managed Agent 등록 원본
│       │   └── openai.yaml              Codex 스킬 UI 메타데이터
│       ├── resources
│       │   └── template.html            기획서 HTML/CSS 스켈레톤 · CSS 클래스 정의처
│       ├── scripts
│       │   ├── validate_storyboard.py   자체 완결형 산출물 검증기
│       │   └── check_badge_overflow.py  배지 좌표 오버플로 점검
│       └── tests
│           ├── test_validator.py        검증기 단위 테스트
│           ├── test_rules.py            Business Rules 판정 테스트
│           └── test_agents.py           이 스킬의 Adapter · 검증기 계약 테스트
├── .claude/agents                       skills/*/agents/claude.md 로의 심링크
├── .codex/agents                        skills/*/agents/codex.toml 로의 심링크
├── .agents
│   └── skills.json                      Antigravity 스킬 매니페스트
├── scripts
│   ├── new_skill.sh                     규약대로 새 스킬 뼈대 생성
│   └── run_tests.sh                     루트 + 모든 스킬 테스트 일괄 실행
├── tests
│   ├── test_skill_layout.py             모든 스킬의 레이아웃 · Adapter 규약 검증
│   └── test_install.sh                  install.sh 동작 테스트
├── install.sh                           3개 런타임 설치
└── README.md
```

## 새 스킬 추가

```bash
./scripts/new_skill.sh my-skill "이 스킬이 언제 쓰이는지 한 줄 설명"
```

`skills/my-skill/` 뼈대와 세 런타임 Adapter, 루트 심링크까지 한 번에 만듭니다.
`SKILL.md` 를 채운 뒤 규약을 확인합니다.

```bash
./scripts/run_tests.sh
```

`install.sh` 와 `tests/` 는 스킬을 순회하므로, 스킬을 추가할 때 손댈 필요가
없습니다.

## 커스터마이징

이 스킬은 템플릿 형태로 제공됩니다. 본인 회사만의 고유한 기획 양식이나 필수 정책(예: "모든 기획서에는 관리자 페이지 플로우도 포함할 것")이 있다면 `SKILL.md` 파일을 열어 언제든지 커스텀하세요!

## Agent로 기획서 생성하는 방법

```text
게시판, 공지, 운동 참석투표, 입상소식, 코트예약, 회원목록 넣어서 테니스 동호회 모바일 웹 화면설계서 만들어줘
```

```bash
# Antigravity (agy)
agy -p "게시판, 공지, 운동 참석투표, 입상소식, 코트예약, 회원목록 넣어서 테니스 동호회 모바일 웹 화면설계서 만들어줘"

# Claude Code
claude --agent mobile-web-planner "게시판, 공지, 운동 참석투표, 입상소식, 코트예약, 회원목록 넣어서 테니스 동호회 모바일 웹 화면설계서 만들어줘"

# Codex — custom agent를 지정해 위임하도록 요청
codex "mobile_web_planner agent를 사용해서 게시판, 공지, 운동 참석투표, 입상소식, 코트예약, 회원목록 넣어서 테니스 동호회 모바일 웹 화면설계서 만들어줘"
```

## Skill로 기획서 생성하는 방법

세 런타임 모두 **같은 문장**으로 동작합니다. 필요한 기능을 나열하고 서비스명을 붙이면 됩니다.

```text
게시판, 공지, 운동 참석투표, 입상소식, 코트예약, 회원목록 넣어서
테니스 동호회 모바일 웹 화면설계서 만들어줘
./output/agy/*.html 로
```

```bash
# Claude Code
claude "위 문장"

# Codex — 요청 내용과 Skill description을 바탕으로 자동 감지
codex exec --sandbox workspace-write "위 문장"

# Antigravity
agy -p "위 문장"
```

Codex에서 Skill을 확실하게 지정하려면 `$mobile-web-planner`를 프롬프트에
포함합니다. 셸의 변수 확장을 막기 위해 프롬프트 전체를 작은따옴표로
감싸세요.

```bash
codex exec --sandbox workspace-write \
  '$mobile-web-planner 스킬을 사용해서 서비스 기능과 요구사항을 바탕으로 화면설계서와 IA 초안을 만들어줘'
```

### 산출물 저장 위치가 런타임마다 다릅니다

| 런타임 | 저장 위치 |
| --- | --- |
| Claude Code · Codex | 현재 작업 디렉터리 |
| Antigravity (`agy`) | `~/.gemini/antigravity-cli/scratch/<주제>/` 에 저장하고 링크를 반환 |

`agy` 에서 특정 위치에 받으려면 프롬프트에 경로를 명시하세요.

```text
... 만들어줘. 산출물 HTML 은 현재 작업 디렉터리에 저장해줘.
```

### 결과물

두 파일이 한 쌍으로 나옵니다.

1. **`<프로젝트명>_storyboard.html`** — `01 Cover` / `02 Document History` / `03 Index` / `04 IA` / `05 Screen List`(화면 ID↔화면 매핑표) / `06 Service Flow`(정상 케이스 전체 흐름도) / `07.x Sequence Diagram`(상태 변경 트랜잭션당 1장) / `08 General Rule` + 화면당 `09.x` 슬라이드 한 장으로 구성된 단일 HTML 파일. 브라우저로 열면 16:9 슬라이드가 세로로 나열됩니다.
2. **`<프로젝트명>_business-rules.md`** — 화면 ID 를 키로 storyboard 와 연결되는 구현 명세. 화면마다 입력 검증(필드별 규칙·실패 시 UI) · 출력 규칙(로딩/빈 상태/오류 표시) · 인터랙션(트리거→조건→동작) · 엣지케이스(권한·동시성·네트워크)를 명세합니다. 개발자가 두 문서만 보고 구현에 착수할 수 있는 것이 목표입니다.

- **화면 순서는 나열한 순서를 따릅니다.** 진입 화면(메인 홈)이 `09.1`, 나열한 기능이 `09.2` 부터입니다.
- **강조색은 도메인에 맞게 에이전트가 고릅니다.** 테니스 동호회면 코트 그린, 뉴스면 뉴트럴 블루 식입니다. 브랜드 컬러를 지정하려면 프롬프트에 적으세요.
- **목록·상세, 입력 전후처럼 비교가 필요한 화면은 목업 2개**가 나란히 배치됩니다.

### 결과 검증

생성된 문서가 스킬의 계약을 지켰는지 기계적으로 확인할 수 있습니다.

```bash
python3 skills/mobile-web-planner/scripts/validate_storyboard.py <생성된파일.html>
```

검증기는 미정의 CSS 클래스 · 이모지 · 배지 좌표 · 배지와 설명 항목의 1:1 대응 ·
mermaid 런타임 · 치환 안 된 플레이스홀더를 검사하고, 짝을 이루는
`_business-rules.md` 문서에 대해서는 화면 ID 커버리지(모든 화면이 섹션을
갖는가) · 필수 헤딩 4종 존재와 내용 유무 · 끊어진 화면 ID 참조를
검사합니다. 위반이 있으면 목록과 함께 exit 1 로 끝납니다.

검증기는 스킬 안에 들어 있으므로, 설치된 스킬만 있는 환경에서는 설치 경로
기준으로 같은 명령을 실행합니다.

```bash
python3 ~/.claude/skills/mobile-web-planner/scripts/validate_storyboard.py <생성된파일.html>
```

## 라이선스

[MIT](LICENSE)

