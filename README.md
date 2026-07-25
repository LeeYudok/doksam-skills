# Mobile Web Planner Agent Skill 📱

Claude Code, Codex, Gemini CLI / Antigravity 등 범용 AI 에이전트를 **'모바일 웹/앱 UX/UI 수석 기획자'**로 변신시켜주는 범용 스킬입니다.
뉴스뿐만 아니라 쇼핑몰, 커뮤니티, O2O 예약 서비스 등 **모든 도메인의 모바일 기획**을 완벽하게 수행할 수 있도록 설계되었습니다.

## 🚀 사용 방법 (How to Use)

1. 이 저장소를 클론합니다.
2. 설치 스크립트를 실행합니다. 기본은 심링크이므로, 이후 저장소에서 `SKILL.md` 를 수정하면 세 런타임에 즉시 반영됩니다.

   ```bash
   ./install.sh
   ```

   | 런타임 | 설치 경로 |
   |---|---|
   | Codex, Gemini CLI | `~/.agents/skills/mobile-web-planner` |
   | Claude Code | `~/.claude/skills/mobile-web-planner` |
   | Antigravity (`agy`) | `~/.gemini/config/skills/mobile-web-planner` |

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

## 📁 구조 (Structure)

```text
📦 mobile-web-planner-agent
 ┣ 📂 skills
 ┃ ┗ 📂 mobile-web-planner
 ┃   ┣ 📜 SKILL.md (기획자 페르소나, 워크플로우, 클래스 Quick Reference)
 ┃   ┗ 📂 resources
 ┃     ┗ 📜 template.html (기획서 HTML/CSS 스켈레톤 · CSS 클래스 정의처)
 ┣ 📂 examples
 ┃ ┣ 📜 doksam_news_storyboard.html (생성 산출물 예시 · 슬라이드 7장)
 ┃ ┣ 📜 mobile_news_plan.md (뉴스 앱 기획 예시)
 ┃ ┗ 📂 images (목업 이미지)
 ┣ 📂 scripts
 ┃ ┣ 📜 check_output.py (생성된 기획서의 계약 준수 판정)
 ┃ ┣ 📜 build_multimock_probe.py (목업 복수 배치 기하 검증 프로브 생성)
 ┃ ┗ 📜 multimock-probe.html (프로브 · 브라우저로 열면 자체 채점)
 ┣ 📂 tests
 ┃ ┣ 📜 test_generate.py (검증기 단위 테스트)
 ┃ ┗ 📜 test_install.sh (install.sh 동작 테스트)
 ┣ 📂 docs
 ┃ ┗ 📂 superpowers (설계 · 구현 계획 문서)
 ┣ 📜 install.sh (3개 런타임 설치)
 ┣ 📜 generate_doksam.py (예시 재생성 + 클래스 계약 검증)
 ┗ 📜 README.md
```

`generate_doksam.py` 는 예시 스토리보드를 재생성하면서, 생성된 HTML 이 `template.html` 에 정의되지 않은 CSS 클래스를 쓰고 있으면 exit 1 로 막습니다. 저장소 루트 기준 상대경로로 동작하므로 클론 후 바로 실행할 수 있습니다.

```bash
python3 generate_doksam.py
```

`examples/doksam_news_storyboard.html` 은 이 스크립트의 산출물이므로 직접 편집하지 않습니다.

## 🛠️ 커스터마이징
이 스킬은 템플릿 형태로 제공됩니다. 본인 회사만의 고유한 기획 양식이나 필수 정책(예: "모든 기획서에는 관리자 페이지 플로우도 포함할 것")이 있다면 `SKILL.md` 파일을 열어 언제든지 커스텀하세요!


## 📝 기획서 생성 방법

세 런타임 모두 **같은 문장**으로 동작합니다. 필요한 기능을 나열하고 서비스명을 붙이면 됩니다.

```text
게시판, 공지, 운동 참석투표, 입상소식, 코트예약, 회원목록 넣어서
덕삼테니스클럽(동호회) 모바일 웹 화면설계서 만들어줘
```

```bash
# Claude Code
claude "위 문장"

# Codex
codex exec --sandbox workspace-write "위 문장"

# Antigravity
agy -p "위 문장"
```

### 산출물 저장 위치가 런타임마다 다릅니다

| 런타임 | 저장 위치 |
|---|---|
| Claude Code · Codex | 현재 작업 디렉터리 |
| Antigravity (`agy`) | `~/.gemini/antigravity-cli/scratch/<주제>/` 에 저장하고 링크를 반환 |

`agy` 에서 특정 위치에 받으려면 프롬프트에 경로를 명시하세요.

```text
... 만들어줘. 산출물 HTML 은 현재 작업 디렉터리에 저장해줘.
```

### 결과물

`01 Cover` / `02 Document History` / `03 Index` / `04 IA` / `05 General Rule` + 화면당 `06.x` 슬라이드 한 장으로 구성된 **단일 HTML 파일**이 나옵니다. 브라우저로 열면 16:9 슬라이드가 세로로 나열됩니다.

- **화면 순서는 나열한 순서를 따릅니다.** 진입 화면(메인 홈)이 `06.1`, 나열한 기능이 `06.2` 부터입니다.
- **강조색은 도메인에 맞게 에이전트가 고릅니다.** 테니스 동호회면 코트 그린, 뉴스면 뉴트럴 블루 식입니다. 브랜드 컬러를 지정하려면 프롬프트에 적으세요.
- **목록·상세, 입력 전후처럼 비교가 필요한 화면은 목업 2개**가 나란히 배치됩니다.

### 결과 검증

생성된 문서가 스킬의 계약을 지켰는지 기계적으로 확인할 수 있습니다.

```bash
python3 scripts/check_output.py <생성된파일.html>
```

미정의 CSS 클래스 · 이모지 · 배지 좌표 · 배지와 설명 항목의 1:1 대응 · mermaid 런타임 · 치환 안 된 플레이스홀더를 검사하고, 위반이 있으면 목록과 함께 exit 1 로 끝납니다. 화면 순서와 목업 개수는 요청 맥락에 따라 정답이 달라지므로 수치만 함께 보고합니다.
