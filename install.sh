#!/usr/bin/env bash
# 이 레포의 skills/ 아래 모든 스킬을 Claude Code / Codex / Gemini(Antigravity)
# 가 인식하는 경로에 노출한다. 기본은 심링크이므로 이 레포에서 SKILL.md 를
# 수정하면 세 런타임에 즉시 반영된다.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAMES=()
for d in "$REPO_ROOT"/skills/*/; do
  [[ -f "$d/SKILL.md" ]] && SKILL_NAMES+=("$(basename "$d")")
done
# Agent Adapter 원본은 각 스킬이 소유한다: skills/<skill>/agents/{claude.md,
# codex.toml, antigravity.md}. 스킬명은 여기서 하드코딩하지 않는다.

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
                      원본은 skills/<skill>/agents/ 가 소유한다
                        claude.md      -> .claude/agents/<skill>.md
                        codex.toml     -> .codex/agents/<skill_underscored>.toml
                        antigravity.md -> agy 플러그인으로 등록 (전역 설치 시)
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

if [[ ${#SKILL_NAMES[@]} -eq 0 ]]; then
  echo "오류: skills/ 아래에 SKILL.md 를 가진 스킬이 없다" >&2
  exit 1
fi

# 타깃 목록 구성
target_bases=()
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
  target_bases=("$project_abs/.claude/skills" "$project_abs/.agents/skills")
  claude_agents_base="$project_abs/.claude/agents"
  codex_agents_base="$project_abs/.codex/agents"
else
  # Antigravity 의 전역 customization root 는 ~/.gemini/config/ 다.
  # ~/.gemini/antigravity/skills/ 는 agy 가 탐색하지 않는다 (이슈 #5).
  target_bases=("$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.gemini/config/skills")
  claude_agents_base="$HOME/.claude/agents"
  codex_agents_base="$HOME/.codex/agents"
fi

# 스킬별 Agent Adapter 를 런타임이 탐색하는 이름으로 매핑한다.
#   skills/<skill>/agents/claude.md   -> <claude agents>/<skill>.md
#   skills/<skill>/agents/codex.toml  -> <codex agents>/<skill_underscored>.toml
# antigravity.md 는 agy 가 파일시스템 에이전트 디렉터리를 탐색하지 않으므로
# (2026-08-02 agy 1.1.8 실측: ~/.gemini/config/agents/ 의 md 는 CLI 를 행 상태로
# 만든다 — 이슈 #78) 플러그인 메커니즘으로 등록한다: agents/ 를 담은 플러그인을
# 스테이징해 `agy plugin install` → ~/.gemini/config/plugins/<name>/ 에 복사된다.
antigravity_sources=()
if [[ $WITH_AGENT -eq 1 ]]; then
  for skill in "${SKILL_NAMES[@]}"; do
    agents_dir="$REPO_ROOT/skills/$skill/agents"
    if [[ -f "$agents_dir/claude.md" ]]; then
      agent_sources+=("$agents_dir/claude.md")
      agent_targets+=("$claude_agents_base/$skill.md")
    fi
    if [[ -f "$agents_dir/codex.toml" ]]; then
      agent_sources+=("$agents_dir/codex.toml")
      agent_targets+=("$codex_agents_base/${skill//-/_}.toml")
    fi
    if [[ -f "$agents_dir/antigravity.md" ]]; then
      antigravity_sources+=("$agents_dir/antigravity.md")
    fi
  done
  if [[ ${#agent_sources[@]} -eq 0 ]]; then
    echo "오류: --with-agent 를 줬지만 skills/*/agents/ 에 Adapter 가 없다" >&2
    exit 1
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

for skill in "${SKILL_NAMES[@]}"; do
  src="$REPO_ROOT/skills/$skill"
  for base in "${target_bases[@]}"; do
    if [[ "$ACTION" == "uninstall" ]]; then
      do_uninstall "$base/$skill" "$src"
    else
      do_install "$base/$skill" "$src"
    fi
  done
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
  # ---- Antigravity: 플러그인으로 에이전트 등록 (전역 설치에서만) ----
  # 설치 시점에 ~/.gemini/config/plugins/ 로 복사되므로 antigravity.md 를
  # 고친 뒤에는 --with-agent 재실행이 필요하다.
  AGY_PLUGIN_NAME="doksam-skills-agents"
  agy_status="원본 없음"
  # bash 3.2 는 set -u 아래에서 빈 배열 전개를 오류로 처리하므로 먼저 센다.
  if [[ ${#antigravity_sources[@]} -gt 0 ]]; then
    if [[ -n "$PROJECT" ]]; then
      agy_status="프로젝트 설치 미지원 — 전역(--project 없이)에서 플러그인으로 등록된다"
      echo "info      Antigravity 에이전트는 전역 플러그인 등록만 지원한다"
    elif ! command -v agy >/dev/null 2>&1; then
      agy_status="건너뜀 — agy CLI 없음"
      echo "info      agy CLI 가 없어 Antigravity 에이전트를 등록하지 못했다."
      echo "info      agy 설치 후 다시 실행하거나, 아래 원본으로 직접 플러그인을 만들면 된다:"
      for src in "${antigravity_sources[@]}"; do
        echo "info        $src"
      done
    elif [[ $DRY_RUN -eq 1 ]]; then
      agy_status="dry-run — 플러그인 '$AGY_PLUGIN_NAME' 등록 예정 (${#antigravity_sources[@]}개)"
      echo "plan      agy plugin install ($AGY_PLUGIN_NAME, 에이전트 ${#antigravity_sources[@]}개)"
    else
      staging="$(mktemp -d "${TMPDIR:-/tmp}/doksam-skills-agy.XXXXXX")"
      mkdir -p "$staging/agents"
      printf '{"name": "%s", "description": "doksam-skills Agent Adapter 모음 (install.sh 가 생성)", "version": "1.0.0"}\n' \
        "$AGY_PLUGIN_NAME" > "$staging/plugin.json"
      for skill in "${SKILL_NAMES[@]}"; do
        adapter="$REPO_ROOT/skills/$skill/agents/antigravity.md"
        [[ -f "$adapter" ]] && cp "$adapter" "$staging/agents/$skill.md"
      done
      if [[ "$ACTION" == "uninstall" ]]; then
        if agy plugin uninstall "$AGY_PLUGIN_NAME" >/dev/null 2>&1; then
          agy_status="플러그인 '$AGY_PLUGIN_NAME' 제거됨"
          echo "remove    agy plugin $AGY_PLUGIN_NAME"
          ok=$((ok + 1))
        else
          agy_status="플러그인 없음 (제거 생략)"
          echo "skip      agy plugin $AGY_PLUGIN_NAME (등록돼 있지 않음)"
          skipped=$((skipped + 1))
        fi
      else
        # 재실행 시 최신 원본으로 갱신되도록 기존 등록을 먼저 지운다.
        agy plugin uninstall "$AGY_PLUGIN_NAME" >/dev/null 2>&1 || true
        if agy plugin install "$staging" >/dev/null 2>&1; then
          agy_status="플러그인 '$AGY_PLUGIN_NAME' 등록 (에이전트 ${#antigravity_sources[@]}개 — 'agy agents' 로 확인)"
          echo "plugin    agy plugin $AGY_PLUGIN_NAME (에이전트 ${#antigravity_sources[@]}개)"
          ok=$((ok + 1))
        else
          agy_status="등록 실패 — 'agy plugin install $staging' 를 직접 실행해 오류를 확인할 것"
          echo "fail      agy plugin install (수동 확인 필요: $staging)" >&2
          failed=$((failed + 1))
        fi
      fi
      [[ "$agy_status" == 등록\ 실패* ]] || rm -rf "$staging"
    fi
  fi
fi

echo
if [[ $WITH_AGENT -eq 1 ]]; then
  echo "런타임별 에이전트: Claude=심링크 · Codex=심링크 · Antigravity=$agy_status"
fi
echo "완료: ok=$ok skip=$skipped conflict=$failed"
[[ $failed -eq 0 ]]
