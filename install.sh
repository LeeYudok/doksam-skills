#!/usr/bin/env bash
# mobile-web-planner 스킬을 Claude Code / Codex / Gemini(Antigravity) 가
# 인식하는 경로에 노출한다. 기본은 심링크이므로 이 레포에서 SKILL.md 를
# 수정하면 세 런타임에 즉시 반영된다.
set -uo pipefail

SKILL_NAME="mobile-web-planner"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_ROOT/skills/$SKILL_NAME"
CLAUDE_AGENT_SRC="$REPO_ROOT/.claude/agents/mobile-web-planner.md"
CODEX_AGENT_SRC="$REPO_ROOT/.codex/agents/mobile_web_planner.toml"
ANTIGRAVITY_AGENT_SRC="$REPO_ROOT/adapters/antigravity/AGENTS.md"

MODE="symlink"     # symlink | copy
ACTION="install"   # install | uninstall
WITH_AGENT=0
SELECTION=""
DRY_RUN=0
FORCE=0
PROJECT=""

ok=0
skipped=0
failed=0

usage() {
  cat <<'USAGE'
사용법: ./install.sh [옵션]

옵션:
  (없음)              전역 3경로에 심링크를 만든다
                        ~/.agents/skills/                (Codex, Gemini CLI)
                        ~/.claude/skills/                (Claude Code)
                        ~/.gemini/config/skills/         (Antigravity, agy)
  --copy              심링크 대신 복사한다
  --project <dir>     전역 대신 해당 레포의 프로젝트 스킬 경로에 설치한다
                        <dir>/.claude/skills/            (Claude Code)
                        <dir>/.agents/skills/            (Codex, Antigravity)
  --skill-only        Skill 만 설치한다 (기본값)
  --with-agent        Skill 과 이름 있는 Agent Adapter 를 함께 설치한다
                        Claude: .claude/agents/
                        Codex:  .codex/agents/
                        Antigravity Managed Agent 등록 원본은 경로를 안내한다
  --dry-run           수행할 작업만 출력하고 파일시스템은 바꾸지 않는다
  --uninstall         이 레포를 가리키는 심링크를 제거한다
  --force             충돌하는 기존 항목을 교체한다
  -h, --help          이 도움말

동작 규칙:
  - 이미 이 레포를 가리키는 심링크면 skip 한다 (멱등)
  - 다른 것을 가리키는 심링크나 실제 디렉터리가 있으면 덮어쓰지 않고
    exit 1 한다. --force 를 준 경우에만 교체한다
  - --uninstall 은 이 레포를 가리키는 심링크만 제거한다. 실제 디렉터리
    (--copy 설치분 등)는 경로를 안내하고 손대지 않는다
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy)      MODE="copy"; shift ;;
    --skill-only)
      if [[ "$SELECTION" == "agent" ]]; then
        echo "오류: --skill-only 와 --with-agent 는 함께 쓸 수 없다" >&2
        exit 1
      fi
      SELECTION="skill"; WITH_AGENT=0; shift ;;
    --with-agent)
      if [[ "$SELECTION" == "skill" ]]; then
        echo "오류: --skill-only 와 --with-agent 는 함께 쓸 수 없다" >&2
        exit 1
      fi
      SELECTION="agent"; WITH_AGENT=1; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    --uninstall) ACTION="uninstall"; shift ;;
    --force)     FORCE=1; shift ;;
    --project)
      if [[ $# -lt 2 ]]; then
        echo "오류: --project 에 디렉터리 인자가 필요하다" >&2
        exit 1
      fi
      PROJECT="$2"; shift 2 ;;
    -h|--help)   usage; exit 0 ;;
    *)
      echo "오류: 알 수 없는 옵션 '$1'" >&2
      usage >&2
      exit 1 ;;
  esac
done

if [[ ! -d "$SRC" ]]; then
  echo "오류: 스킬 원본이 없다 — $SRC" >&2
  exit 1
fi

# 타깃 목록 구성
targets=()
agent_sources=()
agent_targets=()
if [[ -n "$PROJECT" ]]; then
  if [[ ! -d "$PROJECT" ]]; then
    echo "오류: --project 대상이 디렉터리가 아니다 — $PROJECT" >&2
    exit 1
  fi
  if ! project_abs="$(cd "$PROJECT" && pwd)"; then
    echo "오류: --project 경로로 이동 실패 — $PROJECT" >&2
    exit 1
  fi
  # Antigravity 의 프로젝트 customization root 는 .agents/ 이고 Codex 와 같은
  # 경로이므로, 두 타깃으로 세 런타임을 모두 커버한다.
  targets+=("$project_abs/.claude/skills/$SKILL_NAME")
  targets+=("$project_abs/.agents/skills/$SKILL_NAME")
  if [[ $WITH_AGENT -eq 1 ]]; then
    agent_sources+=("$CLAUDE_AGENT_SRC" "$CODEX_AGENT_SRC")
    agent_targets+=(
      "$project_abs/.claude/agents/mobile-web-planner.md"
      "$project_abs/.codex/agents/mobile_web_planner.toml"
    )
  fi
else
  targets+=("$HOME/.agents/skills/$SKILL_NAME")
  targets+=("$HOME/.claude/skills/$SKILL_NAME")
  # Antigravity 의 전역 customization root 는 ~/.gemini/config/ 다.
  # ~/.gemini/antigravity/skills/ 는 agy 가 탐색하지 않는다 (이슈 #5).
  targets+=("$HOME/.gemini/config/skills/$SKILL_NAME")
  if [[ $WITH_AGENT -eq 1 ]]; then
    agent_sources+=("$CLAUDE_AGENT_SRC" "$CODEX_AGENT_SRC")
    agent_targets+=(
      "$HOME/.claude/agents/mobile-web-planner.md"
      "$HOME/.codex/agents/mobile_web_planner.toml"
    )
  fi
fi

points_at_src() {
  [[ -L "$1" ]] && [[ "$(readlink "$1")" == "$2" ]]
}

do_uninstall() {
  local target="$1" source="$2"
  if points_at_src "$target" "$source"; then
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "remove    $target"
    else
      if ! rm "$target"; then
        echo "fail      $target (심링크 제거 실패)" >&2
        failed=$((failed + 1))
        return 0
      fi
      echo "remove    $target"
    fi
    ok=$((ok + 1))
  elif [[ -L "$target" ]]; then
    echo "skip      $target (다른 곳을 가리키는 심링크: $(readlink "$target"))"
    skipped=$((skipped + 1))
  elif [[ -e "$target" ]]; then
    echo "skip      $target (실제 디렉터리 — 직접 확인 후 제거할 것)"
    skipped=$((skipped + 1))
  else
    echo "skip      $target (없음)"
    skipped=$((skipped + 1))
  fi
}

do_install() {
  local target="$1" source="$2"

  if points_at_src "$target" "$source"; then
    echo "skip      $target (이미 설치됨)"
    skipped=$((skipped + 1))
    return 0
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    if [[ $FORCE -eq 0 ]]; then
      local what="실제 디렉터리"
      [[ -L "$target" ]] && what="다른 곳을 가리키는 심링크: $(readlink "$target")"
      echo "conflict  $target ($what) — 덮어쓰지 않는다. 교체하려면 --force" >&2
      failed=$((failed + 1))
      return 0
    fi
    if [[ $DRY_RUN -eq 0 ]]; then
      if ! rm -rf "$target"; then
        echo "fail      $target (기존 항목 제거 실패)" >&2
        failed=$((failed + 1))
        return 0
      fi
    fi
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "$MODE   $target -> $source"
    ok=$((ok + 1))
    return 0
  fi

  if ! mkdir -p "$(dirname "$target")"; then
    echo "fail      $target (부모 디렉토리 생성 실패)" >&2
    failed=$((failed + 1))
    return 0
  fi
  if [[ "$MODE" == "copy" ]]; then
    if ! cp -R "$source" "$target"; then
      echo "fail      $target (복사 실패)" >&2
      failed=$((failed + 1))
      return 0
    fi
    echo "copy      $target"
  else
    if ! ln -s "$source" "$target"; then
      echo "fail      $target (심링크 생성 실패)" >&2
      failed=$((failed + 1))
      return 0
    fi
    echo "symlink   $target -> $source"
  fi
  ok=$((ok + 1))
}

if [[ $DRY_RUN -eq 1 ]]; then
  echo "(dry-run — 파일시스템을 바꾸지 않는다)"
fi

for target in "${targets[@]}"; do
  if [[ "$ACTION" == "uninstall" ]]; then
    do_uninstall "$target" "$SRC"
  else
    do_install "$target" "$SRC"
  fi
done

if [[ $WITH_AGENT -eq 1 ]]; then
  for ((i = 0; i < ${#agent_targets[@]}; i++)); do
    if [[ ! -f "${agent_sources[$i]}" ]]; then
      echo "fail      ${agent_sources[$i]} (Agent 원본 없음)" >&2
      failed=$((failed + 1))
      continue
    fi
    if [[ "$ACTION" == "uninstall" ]]; then
      do_uninstall "${agent_targets[$i]}" "${agent_sources[$i]}"
    else
      do_install "${agent_targets[$i]}" "${agent_sources[$i]}"
    fi
  done
  echo "info      Antigravity Managed Agent 등록 원본: $ANTIGRAVITY_AGENT_SRC"
fi

echo
echo "완료: ok=$ok skip=$skipped conflict=$failed"
[[ $failed -eq 0 ]]
