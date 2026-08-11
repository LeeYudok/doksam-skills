#!/usr/bin/env bash
# 레이아웃 규약대로 새 스킬 뼈대를 만든다.
#
#   ./scripts/new_skill.sh <skill-name> ["한 줄 설명"]
#
# 만들어지는 것:
#   skills/<name>/SKILL.md              세 런타임 공통 행동 계약 (유일 원본)
#   skills/<name>/agents/claude.md      Claude Code Agent Adapter
#   skills/<name>/agents/codex.toml     Codex custom agent
#   skills/<name>/agents/antigravity.md Antigravity Managed Agent 등록 원본
#   .claude/agents/<name>.md            위 원본을 가리키는 심링크
#   .codex/agents/<name_underscored>.toml
#
# scripts/ 와 tests/ 는 빈 채로 만들지 않는다 — git 이 빈 디렉터리를 추적하지
# 않아 커밋에 안 남고, 내용이 생길 때 직접 만들면 된다.
# 규약 위반은 tests/test_skill_layout.py 가 잡는다. 생성 후 반드시 돌린다.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "사용법: ./scripts/new_skill.sh <skill-name> [\"한 줄 설명\"]" >&2
  exit 1
fi

NAME="$1"
DESC="${2:-이 스킬이 언제 쓰이는지 한 줄로 적는다.}"

if [[ ! "$NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "오류: 스킬명은 kebab-case 소문자여야 한다 — $NAME" >&2
  exit 1
fi

DIR="$REPO_ROOT/skills/$NAME"
if [[ -e "$DIR" ]]; then
  echo "오류: 이미 존재한다 — skills/$NAME" >&2
  exit 1
fi

UNDERSCORED="${NAME//-/_}"

mkdir -p "$DIR/agents"

cat > "$DIR/SKILL.md" <<EOF
---
name: $NAME
description: $DESC
---

# $NAME

## 역할

(이 스킬이 에이전트에게 어떤 역할을 부여하는지 적는다.)

## 워크플로

1. (입력에서 무엇을 확정하는지)
2. (무엇을 만드는지)
3. (무엇으로 검증하는지)

## 완료 조건

(무엇이 충족되어야 산출물을 전달할 수 있는지 적는다.)
EOF

cat > "$DIR/agents/claude.md" <<EOF
---
name: $NAME
description: $DESC
skills:
  - $NAME
---

\`$NAME\` Skill 을 작업 계약의 단일 원본으로 사용한다.

역할·절차·산출물 형식은 Skill 에 있는 것을 따르고, 이 파일에 복제하지 않는다.
EOF

cat > "$DIR/agents/codex.toml" <<EOF
name = "$UNDERSCORED"
description = "$DESC"
developer_instructions = """
Use the $NAME skill as the single source of truth for the task.
Follow its workflow and deliverable contract; do not restate them here.
"""
EOF

# frontmatter 는 필수다. agy 는 frontmatter 가 없는 agent md 를 오류도 경고도
# 없이 무시한다 (2026-08-11 agy 1.1.11 실측 — 이슈 #110).
cat > "$DIR/agents/antigravity.md" <<EOF
---
name: $NAME
description: $DESC
---

# $NAME

$DESC

\`$NAME\` Skill 을 작업 계약의 단일 원본으로 사용한다. Antigravity Managed Agent
등록 시 이 파일의 내용을 역할 정의로 넣는다.
EOF

ln -s "../../skills/$NAME/agents/claude.md" \
  "$REPO_ROOT/.claude/agents/$NAME.md"
ln -s "../../skills/$NAME/agents/codex.toml" \
  "$REPO_ROOT/.codex/agents/$UNDERSCORED.toml"

echo "생성됨: skills/$NAME"
echo "  .claude/agents/$NAME.md -> skills/$NAME/agents/claude.md"
echo "  .codex/agents/$UNDERSCORED.toml -> skills/$NAME/agents/codex.toml"
echo
echo "다음: SKILL.md 를 채우고 ./scripts/run_tests.sh 로 규약을 확인한다"
