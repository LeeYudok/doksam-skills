#!/usr/bin/env bash
# install.sh 동작 테스트. 임시 HOME 으로 격리하므로 실제 홈 디렉터리를 건드리지 않는다.
#
# 스킬명을 하드코딩하지 않는다. skills/ 를 훑어 프로브(probe) 스킬을 고르므로
# 스킬이 늘거나 이름이 바뀌어도 이 파일은 그대로 둔다.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="$REPO_ROOT/install.sh"

SKILLS=()
for d in "$REPO_ROOT"/skills/*/; do
  [[ -f "$d/SKILL.md" ]] && SKILLS+=("$(basename "$d")")
done
if [[ ${#SKILLS[@]} -eq 0 ]]; then
  echo "오류: skills/ 아래에 SKILL.md 를 가진 스킬이 없다" >&2
  exit 1
fi

# 스킬 설치 동작을 확인할 대표 스킬
SKILL="${SKILLS[0]}"
SRC="$REPO_ROOT/skills/$SKILL"

# agy CLI 스텁 — 실제 agy 를 호출하지 않고 인자만 기록한다 (이슈 #78).
# PATH 맨 앞에 두어 install.sh 의 `command -v agy` 와 호출을 가로챈다.
STUB_BIN="$(mktemp -d)"
AGY_LOG="$STUB_BIN/agy.log"
cat > "$STUB_BIN/agy" <<STUB
#!/usr/bin/env bash
echo "\$@" >> "$AGY_LOG"
exit 0
STUB
chmod +x "$STUB_BIN/agy"
export PATH="$STUB_BIN:$PATH"

# Agent Adapter 동작을 확인할 대표 스킬 (claude.md 를 가진 첫 스킬)
AGENT_SKILL=""
for s in "${SKILLS[@]}"; do
  if [[ -f "$REPO_ROOT/skills/$s/agents/claude.md" ]]; then
    AGENT_SKILL="$s"
    break
  fi
done
if [[ -z "$AGENT_SKILL" ]]; then
  echo "오류: agents/claude.md 를 가진 스킬이 없어 Agent 테스트를 할 수 없다" >&2
  exit 1
fi
CLAUDE_AGENT_SRC="$REPO_ROOT/skills/$AGENT_SKILL/agents/claude.md"
CODEX_AGENT_SRC="$REPO_ROOT/skills/$AGENT_SKILL/agents/codex.toml"
CLAUDE_AGENT_LINK=".claude/agents/$AGENT_SKILL.md"
CODEX_AGENT_LINK=".codex/agents/${AGENT_SKILL//-/_}.toml"

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
check "심링크 미생성" "absent" "$([[ -e "$HOME/.claude/skills/$SKILL" ]] && echo present || echo absent)"
drop_sandbox

echo "test: 기본 설치는 전역 3경로에 모든 스킬 심링크를 만든다"
new_sandbox
"$INSTALL" >/dev/null 2>&1
check "exit code" "0" "$?"
for t in ".agents/skills" ".claude/skills" ".gemini/config/skills"; do
  for s in "${SKILLS[@]}"; do
    check "$t/$s 심링크" "$REPO_ROOT/skills/$s" "$(readlink "$HOME/$t/$s" 2>/dev/null)"
  done
done
drop_sandbox

echo "test: --skill-only 는 기본 설치와 같다"
new_sandbox
"$INSTALL" --skill-only >/dev/null 2>&1
check "exit code" "0" "$?"
check "Skill 설치" "$SRC" "$(readlink "$HOME/.agents/skills/$SKILL" 2>/dev/null)"
check "Claude Agent 미설치" "absent" "$([[ -e "$HOME/$CLAUDE_AGENT_LINK" ]] && echo present || echo absent)"
check "Codex Agent 미설치" "absent" "$([[ -e "$HOME/$CODEX_AGENT_LINK" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --with-agent 는 Skill 과 Claude/Codex Agent 를 설치한다"
new_sandbox
out="$("$INSTALL" --with-agent 2>&1)"
check "exit code" "0" "$?"
check "Claude Agent" "$CLAUDE_AGENT_SRC" "$(readlink "$HOME/$CLAUDE_AGENT_LINK" 2>/dev/null)"
check "Codex Agent" "$CODEX_AGENT_SRC" "$(readlink "$HOME/$CODEX_AGENT_LINK" 2>/dev/null)"
check "Agent 원본은 스킬 소유" "present" "$([[ "$CLAUDE_AGENT_SRC" == "$REPO_ROOT/skills/"* ]] && echo present || echo absent)"
check "agy 스텁이 plugin install 을 받음" "present" "$(grep -q '^plugin install ' "$AGY_LOG" && echo present || echo absent)"
check "런타임별 요약에 Antigravity 등록" "present" "$(grep -q '^런타임별 에이전트: .*Antigravity=플러그인' <<<"$out" && echo present || echo absent)"
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
check "스킬 수 × 3경로 만큼 skip" "$((${#SKILLS[@]} * 3))" "$(grep -c '^skip' <<<"$out")"
drop_sandbox

echo "test: 남의 디렉터리가 있으면 덮어쓰지 않고 실패한다"
new_sandbox
mkdir -p "$HOME/.claude/skills/$SKILL"
touch "$HOME/.claude/skills/$SKILL/SKILL.md"
"$INSTALL" >/dev/null 2>&1
check "exit code" "1" "$?"
check "기존 파일 보존" "present" "$([[ -f "$HOME/.claude/skills/$SKILL/SKILL.md" ]] && echo present || echo absent)"
drop_sandbox

echo "test: 남의 심링크가 있으면 덮어쓰지 않고 실패한다"
new_sandbox
decoy="$SANDBOX/decoy"
mkdir -p "$decoy"
mkdir -p "$HOME/.claude/skills"
ln -s "$decoy" "$HOME/.claude/skills/$SKILL"
"$INSTALL" >/dev/null 2>&1
check "exit code" "1" "$?"
check "기존 심링크 보존" "$decoy" "$(readlink "$HOME/.claude/skills/$SKILL" 2>/dev/null)"
drop_sandbox

echo "test: --force 는 충돌 항목을 교체한다"
new_sandbox
mkdir -p "$HOME/.claude/skills/$SKILL"
"$INSTALL" --force >/dev/null 2>&1
check "exit code" "0" "$?"
check "심링크로 교체" "$SRC" "$(readlink "$HOME/.claude/skills/$SKILL" 2>/dev/null)"
drop_sandbox

echo "test: --copy 는 심링크 대신 복사한다"
new_sandbox
"$INSTALL" --copy >/dev/null 2>&1
check "exit code" "0" "$?"
target="$HOME/.claude/skills/$SKILL"
check "심링크 아님" "notlink" "$([[ -L "$target" ]] && echo link || echo notlink)"
check "SKILL.md 복사됨" "present" "$([[ -f "$target/SKILL.md" ]] && echo present || echo absent)"
check "하위 디렉터리까지 복사됨" "present" \
  "$([[ -f "$HOME/.claude/skills/$AGENT_SKILL/agents/claude.md" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --project 는 프로젝트 스킬 경로에 설치한다"
new_sandbox
proj="$SANDBOX/myrepo"
mkdir -p "$proj"
"$INSTALL" --project "$proj" >/dev/null 2>&1
check "exit code" "0" "$?"
check ".claude/skills" "$SRC" "$(readlink "$proj/.claude/skills/$SKILL" 2>/dev/null)"
check ".agents/skills" "$SRC" "$(readlink "$proj/.agents/skills/$SKILL" 2>/dev/null)"
check "전역 미설치" "absent" "$([[ -e "$HOME/.claude/skills/$SKILL" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --project --with-agent 는 프로젝트 Agent 경로에도 설치한다"
new_sandbox
proj="$SANDBOX/myrepo"
mkdir -p "$proj"
"$INSTALL" --project "$proj" --with-agent >/dev/null 2>&1
check "exit code" "0" "$?"
check "프로젝트 Claude Agent" "$CLAUDE_AGENT_SRC" "$(readlink "$proj/$CLAUDE_AGENT_LINK" 2>/dev/null)"
check "프로젝트 Codex Agent" "$CODEX_AGENT_SRC" "$(readlink "$proj/$CODEX_AGENT_LINK" 2>/dev/null)"
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
  for s in "${SKILLS[@]}"; do
    check "$t/$s 제거" "absent" "$([[ -e "$HOME/$t/$s" ]] && echo present || echo absent)"
  done
done
drop_sandbox

echo "test: --uninstall --with-agent 는 Agent 심링크도 제거한다"
new_sandbox
"$INSTALL" --with-agent >/dev/null 2>&1
: > "$AGY_LOG"
"$INSTALL" --uninstall --with-agent >/dev/null 2>&1
check "agy 스텁이 plugin uninstall 을 받음" "present" "$(grep -q '^plugin uninstall ' "$AGY_LOG" && echo present || echo absent)"
check "exit code" "0" "$?"
check "Claude Agent 제거" "absent" "$([[ -e "$HOME/$CLAUDE_AGENT_LINK" ]] && echo present || echo absent)"
check "Codex Agent 제거" "absent" "$([[ -e "$HOME/$CODEX_AGENT_LINK" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --uninstall 은 실제 디렉터리를 삭제하지 않는다"
new_sandbox
"$INSTALL" --copy >/dev/null 2>&1
"$INSTALL" --uninstall >/dev/null 2>&1
check "복사본 보존" "present" "$([[ -f "$HOME/.claude/skills/$SKILL/SKILL.md" ]] && echo present || echo absent)"
drop_sandbox

echo "test: --vendor 는 사본을 파일 단위로 갱신하고 orphan 은 지우지 않는다"
reset_home
vproj="$(mktemp -d)"
git -C "$vproj" init -q
mkdir -p "$vproj/.agents/skills/$SKILL"
cp -R "$SRC/." "$vproj/.agents/skills/$SKILL/"
echo "낡은 내용" > "$vproj/.agents/skills/$SKILL/SKILL.md"          # 뒤처진 파일
echo "로컬 전용" > "$vproj/.agents/skills/$SKILL/local-note.md"      # orphan
mkdir -p "$REPO_ROOT/skills/$SKILL/__pycache__"
echo x > "$REPO_ROOT/skills/$SKILL/__pycache__/t.pyc"                # 제외 대상
"$INSTALL" --vendor "$vproj" --check >/dev/null 2>&1
check "--check 는 뒤처지면 exit 1" "1" "$?"
out="$("$INSTALL" --vendor "$vproj" --dry-run 2>&1)"
check "dry-run 이 update 를 예고" "present" "$(grep -q "^update    $SKILL/SKILL.md" <<<"$out" && echo present || echo absent)"
check "dry-run 후에도 사본은 그대로" "낡은 내용" "$(cat "$vproj/.agents/skills/$SKILL/SKILL.md")"
out="$("$INSTALL" --vendor "$vproj" 2>&1)"
check "vendor 갱신 exit 0" "0" "$?"
check "사본이 원본과 동일해짐" "same" "$(cmp -s "$SRC/SKILL.md" "$vproj/.agents/skills/$SKILL/SKILL.md" && echo same || echo diff)"
check "orphan 보존" "로컬 전용" "$(cat "$vproj/.agents/skills/$SKILL/local-note.md")"
check "orphan 보고" "present" "$(grep -q "^orphan    $SKILL/local-note.md" <<<"$out" && echo present || echo absent)"
check "__pycache__ 미복사" "absent" "$([[ -e "$vproj/.agents/skills/$SKILL/__pycache__" ]] && echo present || echo absent)"
check "git status 요약 출력" "present" "$(grep -q '^-- git status' <<<"$out" && echo present || echo absent)"
"$INSTALL" --vendor "$vproj" --check >/dev/null 2>&1
check "--check 는 최신이면 exit 0" "0" "$?"
rm -rf "$REPO_ROOT/skills/$SKILL/__pycache__" "$vproj"

echo "test: --vendor 는 설치 플래그와 배타적이다"
reset_home
vproj2="$(mktemp -d)"; mkdir -p "$vproj2/.agents/skills/$SKILL"
"$INSTALL" --vendor "$vproj2" --with-agent >/dev/null 2>&1
check "--vendor --with-agent 거부" "1" "$?"
rm -rf "$vproj2"

echo "test: --uninstall 은 남의 심링크를 건드리지 않는다"
new_sandbox
decoy="$SANDBOX/decoy"
mkdir -p "$decoy"
mkdir -p "$HOME/.claude/skills"
ln -s "$decoy" "$HOME/.claude/skills/$SKILL"
"$INSTALL" --uninstall >/dev/null 2>&1
check "exit code" "0" "$?"
check "남의 심링크 보존" "$decoy" "$(readlink "$HOME/.claude/skills/$SKILL" 2>/dev/null)"
drop_sandbox

echo
echo "pass=$pass fail=$fail"
[[ $fail -eq 0 ]]
