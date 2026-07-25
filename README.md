# Mobile Web Planner Agent Skill 📱

Google Antigravity (`agy`) 환경에서 범용 AI 에이전트를 **'모바일 웹/앱 UX/UI 수석 기획자'**로 변신시켜주는 범용 스킬입니다.
뉴스뿐만 아니라 쇼핑몰, 커뮤니티, O2O 예약 서비스 등 **모든 도메인의 모바일 기획**을 완벽하게 수행할 수 있도록 설계되었습니다.

## 🚀 사용 방법 (How to Use)

1. 이 저장소(Repository)를 클론하거나 다운로드합니다.
2. 다운로드한 `skills` 폴더 내부의 `mobile_web_planner` 폴더를 프로젝트 작업 공간(Workspace)의 `.antigravity/skills/` 디렉토리 하위로 복사합니다.
   (또는 Antigravity 전역 설정 폴더인 `~/.gemini/antigravity/skills/`에 넣어도 됩니다.)
3. `agy` 또는 Antigravity IDE를 열고 에이전트에게 다음과 같이 요청합니다:
   > *"새로운 반려동물 용품 쇼핑몰 모바일웹 기획해줘"*
   > *"동네 맛집 리뷰 커뮤니티 앱 화면 기획서 작성해볼래?"*
4. 범용 에이전트가 이 스킬(`SKILL.md`)을 자동으로 감지하고, 해당 도메인에 맞는 완벽한 IA와 화면 기획서를 작성해 줍니다!

## 📁 구조 (Structure)

```text
📦 mobile-web-planner-agent
 ┣ 📂 skills
 ┃ ┗ 📂 mobile_web_planner
 ┃   ┣ 📜 SKILL.md (범용 기획자 페르소나, 워크플로우, 템플릿 정의 파일)
 ┃   ┗ 📂 resources
 ┃     ┗ 📜 template.html (기획서 HTML/CSS 스켈레톤)
 ┣ 📂 examples
 ┃ ┣ 📜 doksam_news_storyboard.html (스킬로 생성한 화면설계서 예시)
 ┃ ┣ 📜 mobile_news_plan.md (뉴스 앱 기획 예시)
 ┃ ┗ 📂 images (목업 이미지)
 ┣ 📜 generate_doksam.py (예시 스토리보드 HTML 생성 스크립트)
 ┗ 📜 README.md
```

`generate_doksam.py`는 저장소 루트 기준 상대경로로 동작하므로, 클론 후 아래와 같이 바로 실행할 수 있습니다.

```bash
python generate_doksam.py
```

## 🛠️ 커스터마이징
이 스킬은 템플릿 형태로 제공됩니다. 본인 회사만의 고유한 기획 양식이나 필수 정책(예: "모든 기획서에는 관리자 페이지 플로우도 포함할 것")이 있다면 `SKILL.md` 파일을 열어 언제든지 커스텀하세요!
