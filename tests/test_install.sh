#!/usr/bin/env bash
# install.sh 동작 테스트. 임시 HOME 으로 격리하므로 실제 홈 디렉터리를 건드리지 않는다.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="$REPO_ROOT/install.sh"
SRC="$REPO_ROOT/skills/mobile-web-planner"
CLAUDE_AGENT_SRC="$REPO_ROOT/.claude/agents/mobile-web-planner.md"
CODEX_AGENT_SRC="$REPO_ROOT/.codex/agents/mobile_web_planner.toml"

pass=0
fail=0

check() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  ok   $label"
    pass=$((pass + 1))
  else
    echo "  FAIL $label — expected '$expected', got '$actual'"
    fail=$((fail + 1))
  fi
}

new_sandbox() {
  SANDBOX="$(mktemp -d)"
  export HOME="$SANDBOX"
}

drop_sandbox() {
  rm -rf "$SANDBOX"
}

echo "test: --dry-run 은 파일시스템을 바꾸지 않는다"
new_sandbox
"$INSTALL" --dry-run >/dev/null 2>&1
check "exit code" "0" "$?"
check "심링크 미생성" "absent" "$([[ -e "$HOME/.claude/skills/mobile-web-planner" ]] && echo present || echo absent)"
drop_sandbox

echo "test: 기본 설치는 전역 3경로에 심링크를 만든다"
new_sandbox
"$INSTALL" >/dev/null 2>&1
check "exit code" "0" "$?"
for t in ".agents/skills" ".claude/skills" ".gemini/config/skills"; do
  link="$HOME/$t/mobile-web-planner"
  check "$t 심링크" "$SRC" "$(readlink "$link" 2>/dev/null)"
done
drop_sandbox

echo "test: --skill-only 는 기본 설치와 같다"
new_sandbox
"$INSTALL" --skill-only >/dev/null 2>&1
check "exit code" "0" "$?"
check "Skill 설치" "$SRC" "$(readlink "$HOME/.agents/skills/mobile-web-planner" 2>/dev/null)"
check "Claude Agent 미설치" "absent" "$([[ -e "$HOME/.claude/agents/mobile-web-planner.md" ]] && echo present || echo absent)"
check "Codex Agent 미설치" "absent" "$([[ -e "$HOME/.codex/agents/mobile_web_planner.toml" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --with-agent 는 Skill 과 Claude/Codex Agent 를 설치한다"
new_sandbox
out="$("$INSTALL" --with-agent 2>&1)"
check "exit code" "0" "$?"
check "Claude Agent" "$CLAUDE_AGENT_SRC" "$(readlink "$HOME/.claude/agents/mobile-web-planner.md" 2>/dev/null)"
check "Codex Agent" "$CODEX_AGENT_SRC" "$(readlink "$HOME/.codex/agents/mobile_web_planner.toml" 2>/dev/null)"
check "Antigravity 원본 안내" "1" "$(grep -c '^info.*Antigravity Managed Agent 등록 원본:' <<<"$out")"
drop_sandbox

echo "test: --skill-only 와 --with-agent 를 함께 쓰면 실패한다"
new_sandbox
"$INSTALL" --skill-only --with-agent >/dev/null 2>&1
check "exit code" "1" "$?"
drop_sandbox

echo "test: 재실행은 멱등하다 (skip)"
new_sandbox
"$INSTALL" >/dev/null 2>&1
out="$("$INSTALL" 2>&1)"
check "exit code" "0" "$?"
check "skip 3건" "3" "$(grep -c '^skip' <<<"$out")"
drop_sandbox

echo "test: 남의 디렉터리가 있으면 덮어쓰지 않고 실패한다"
new_sandbox
mkdir -p "$HOME/.claude/skills/mobile-web-planner"
touch "$HOME/.claude/skills/mobile-web-planner/SKILL.md"
"$INSTALL" >/dev/null 2>&1
check "exit code" "1" "$?"
check "기존 파일 보존" "present" "$([[ -f "$HOME/.claude/skills/mobile-web-planner/SKILL.md" ]] && echo present || echo absent)"
drop_sandbox

echo "test: 남의 심링크가 있으면 덮어쓰지 않고 실패한다"
new_sandbox
decoy="$SANDBOX/decoy"
mkdir -p "$decoy"
mkdir -p "$HOME/.claude/skills"
ln -s "$decoy" "$HOME/.claude/skills/mobile-web-planner"
"$INSTALL" >/dev/null 2>&1
check "exit code" "1" "$?"
check "기존 심링크 보존" "$decoy" "$(readlink "$HOME/.claude/skills/mobile-web-planner" 2>/dev/null)"
drop_sandbox

echo "test: --force 는 충돌 항목을 교체한다"
new_sandbox
mkdir -p "$HOME/.claude/skills/mobile-web-planner"
"$INSTALL" --force >/dev/null 2>&1
check "exit code" "0" "$?"
check "심링크로 교체" "$SRC" "$(readlink "$HOME/.claude/skills/mobile-web-planner" 2>/dev/null)"
drop_sandbox

echo "test: --copy 는 심링크 대신 복사한다"
new_sandbox
"$INSTALL" --copy >/dev/null 2>&1
check "exit code" "0" "$?"
target="$HOME/.claude/skills/mobile-web-planner"
check "심링크 아님" "notlink" "$([[ -L "$target" ]] && echo link || echo notlink)"
check "SKILL.md 복사됨" "present" "$([[ -f "$target/SKILL.md" ]] && echo present || echo absent)"
check "template.html 복사됨" "present" "$([[ -f "$target/resources/template.html" ]] && echo present || echo absent)"
check "번들 검증기 복사됨" "present" "$([[ -f "$target/scripts/validate_storyboard.py" ]] && echo present || echo absent)"
check "Codex UI 메타데이터 복사됨" "present" "$([[ -f "$target/agents/openai.yaml" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --project 는 프로젝트 스킬 경로에 설치한다"
new_sandbox
proj="$SANDBOX/myrepo"
mkdir -p "$proj"
"$INSTALL" --project "$proj" >/dev/null 2>&1
check "exit code" "0" "$?"
check ".claude/skills" "$SRC" "$(readlink "$proj/.claude/skills/mobile-web-planner" 2>/dev/null)"
check ".agents/skills" "$SRC" "$(readlink "$proj/.agents/skills/mobile-web-planner" 2>/dev/null)"
check "전역 미설치" "absent" "$([[ -e "$HOME/.claude/skills/mobile-web-planner" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --project --with-agent 는 프로젝트 Agent 경로에도 설치한다"
new_sandbox
proj="$SANDBOX/myrepo"
mkdir -p "$proj"
"$INSTALL" --project "$proj" --with-agent >/dev/null 2>&1
check "exit code" "0" "$?"
check "프로젝트 Claude Agent" "$CLAUDE_AGENT_SRC" "$(readlink "$proj/.claude/agents/mobile-web-planner.md" 2>/dev/null)"
check "프로젝트 Codex Agent" "$CODEX_AGENT_SRC" "$(readlink "$proj/.codex/agents/mobile_web_planner.toml" 2>/dev/null)"
drop_sandbox

echo "test: --project 대상이 디렉터리가 아니면 실패한다"
new_sandbox
"$INSTALL" --project "$SANDBOX/nope" >/dev/null 2>&1
check "exit code" "1" "$?"
drop_sandbox

echo "test: --uninstall 은 우리 심링크만 제거한다"
new_sandbox
"$INSTALL" >/dev/null 2>&1
"$INSTALL" --uninstall >/dev/null 2>&1
check "exit code" "0" "$?"
for t in ".agents/skills" ".claude/skills" ".gemini/config/skills"; do
  check "$t 제거" "absent" "$([[ -e "$HOME/$t/mobile-web-planner" ]] && echo present || echo absent)"
done
drop_sandbox

echo "test: --uninstall --with-agent 는 Agent 심링크도 제거한다"
new_sandbox
"$INSTALL" --with-agent >/dev/null 2>&1
"$INSTALL" --uninstall --with-agent >/dev/null 2>&1
check "exit code" "0" "$?"
check "Claude Agent 제거" "absent" "$([[ -e "$HOME/.claude/agents/mobile-web-planner.md" ]] && echo present || echo absent)"
check "Codex Agent 제거" "absent" "$([[ -e "$HOME/.codex/agents/mobile_web_planner.toml" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --uninstall 은 실제 디렉터리를 삭제하지 않는다"
new_sandbox
"$INSTALL" --copy >/dev/null 2>&1
"$INSTALL" --uninstall >/dev/null 2>&1
check "복사본 보존" "present" "$([[ -f "$HOME/.claude/skills/mobile-web-planner/SKILL.md" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --uninstall 은 남의 심링크를 건드리지 않는다"
new_sandbox
decoy="$SANDBOX/decoy"
mkdir -p "$decoy"
mkdir -p "$HOME/.claude/skills"
ln -s "$decoy" "$HOME/.claude/skills/mobile-web-planner"
"$INSTALL" --uninstall >/dev/null 2>&1
check "exit code" "0" "$?"
check "남의 심링크 보존" "$decoy" "$(readlink "$HOME/.claude/skills/mobile-web-planner" 2>/dev/null)"
drop_sandbox

echo
echo "pass=$pass fail=$fail"
[[ $fail -eq 0 ]]
