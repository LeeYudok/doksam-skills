#!/usr/bin/env bash
# 저장소 전체 테스트를 한 번에 돌린다.
#   1) tests/            저장소 공통 규약 (레이아웃·설치기)
#   2) skills/*/tests/   각 스킬이 소유한 테스트
# 스킬을 순회하므로 새 스킬을 추가해도 이 파일은 그대로 둔다.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"
failed=0

run() {
  local label="$1"
  shift
  echo "=== $label"
  if "$@"; then
    echo "--- ok: $label"
  else
    echo "--- FAIL: $label" >&2
    failed=$((failed + 1))
  fi
  echo
}

run "repo tests" "$PY" -m unittest discover -s "$REPO_ROOT/tests" -t "$REPO_ROOT/tests" -v

for dir in "$REPO_ROOT"/skills/*/tests/; do
  [[ -d "$dir" ]] || continue
  # 테스트 파일이 없는 디렉터리는 건너뛴다 — unittest discover 는 0건을
  # 실패(exit 5)로 처리하므로, 뼈대만 있는 새 스킬이 전체를 깨뜨리게 된다.
  compgen -G "$dir/test_*.py" >/dev/null || continue
  skill="$(basename "$(dirname "$dir")")"
  run "skill tests: $skill" "$PY" -m unittest discover -s "$dir" -t "$dir" -v
done

run "install.sh" "$REPO_ROOT/tests/test_install.sh"

if [[ $failed -gt 0 ]]; then
  echo "실패한 묶음: $failed" >&2
  exit 1
fi
echo "전부 통과"
