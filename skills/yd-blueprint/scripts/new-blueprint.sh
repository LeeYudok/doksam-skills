#!/usr/bin/env bash
# 청사진 뼈대(bun + Vite + React + JSONL)를 저장소에 만든다.
#
#   new-blueprint.sh [--root <dir>] [--dir <name>] [--pm bun|pnpm|npm] [--no-install]
#
#   --root        뼈대를 둘 기준 폴더. 기본은 현재 git 저장소 루트
#   --dir         기준 폴더 아래 이름. 기본 frontend
#   --pm          패키지 매니저. 기본은 PATH 에서 bun → pnpm → npm 순으로 처음 찾은 것
#                 (뼈대는 어느 쪽으로 깔아도 수정 없이 같다)
#   --no-install  패키지 설치를 건너뛴다
#
# 이미 있는 폴더는 덮어쓰지 않는다. 기존 프론트가 있는 곳은 --dir frontend/blueprint 처럼 비켜 만든다.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$SKILL_DIR/assets/template"
ROOT=""
DIR="frontend"
INSTALL=1
PM=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="${2:-}"; shift 2 ;;
    --dir) DIR="${2:-}"; shift 2 ;;
    --pm) PM="${2:-}"; shift 2 ;;
    --no-install) INSTALL=0; shift ;;
    -h|--help) sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "오류: 알 수 없는 옵션 — $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$ROOT" ]]; then
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "오류: git 저장소 안이 아니다 — --root <dir> 로 기준 폴더를 준다" >&2
    exit 1
  }
fi
if [[ -z "$DIR" || "$DIR" == /* || "$DIR" == *..* ]]; then
  echo "오류: --dir 은 기준 폴더 아래의 상대 경로여야 한다 — $DIR" >&2
  exit 1
fi
if [[ ! -d "$ROOT" ]]; then
  echo "오류: 기준 폴더가 없다 — $ROOT" >&2
  exit 1
fi
ROOT="$(cd "$ROOT" && pwd)"
TARGET="$ROOT/$DIR"

if [[ -e "$TARGET" && -n "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  echo "오류: 이미 있고 비어 있지 않다 — $TARGET (덮어쓰지 않는다)" >&2
  echo "      기존 프론트와 겹치면 --dir $DIR/blueprint 처럼 비켜서 만든다" >&2
  exit 1
fi
if [[ -z "$PM" ]]; then
  for candidate in bun pnpm npm; do
    if command -v "$candidate" >/dev/null 2>&1; then PM="$candidate"; break; fi
  done
fi
if [[ -n "$PM" && ! "$PM" =~ ^(bun|pnpm|npm)$ ]]; then
  echo "오류: --pm 은 bun·pnpm·npm 중 하나여야 한다 — $PM" >&2
  exit 1
fi
if [[ "$INSTALL" -eq 1 ]] && { [[ -z "$PM" ]] || ! command -v "$PM" >/dev/null 2>&1; }; then
  echo "오류: 패키지 매니저가 없다 — brew install oven-sh/bun/bun (pnpm·npm 도 된다)" >&2
  exit 1
fi

mkdir -p "$TARGET"
cp -R "$TEMPLATE/." "$TARGET/"

NAME="$(basename "$ROOT" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9\n-' '-')-blueprint"
sed "s/__NAME__/$NAME/" "$TARGET/package.json" > "$TARGET/package.json.tmp" && mv "$TARGET/package.json.tmp" "$TARGET/package.json"

if [[ "$INSTALL" -eq 1 ]]; then
  (cd "$TARGET" && "$PM" install) || { echo "오류: $PM install 실패" >&2; exit 1; }
fi

echo "만들었다: $TARGET"
echo "  데이터   $TARGET/data/*.jsonl  (줄마다 JSON 한 개)"
RUN="${PM:-bun} run"
echo "  띄우기   cd $TARGET && $RUN dev    → http://localhost:5173/blueprint/"
echo "  검사     cd $TARGET && $RUN check"
