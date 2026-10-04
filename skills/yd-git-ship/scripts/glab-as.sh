#!/bin/sh
# Run glab as an agent's GitLab account without printing its token.
#
# Usage: glab-as.sh <claude|codex|agy> <glab args...>
#   glab-as.sh claude api user                      # -> "username": "claude-ai"
#   glab-as.sh claude mr create -R gitlab.doksam.com/<ns>/<repo> ...
# The token comes from ~/workspace/.env.toml [gitlab_<agent>_ai].token and only
# lives in this process's environment.
set -eu

agent="${1:-}"
case "$agent" in
  claude|codex|agy) shift ;;
  *) echo "usage: $0 <claude|codex|agy> <glab args...>" >&2; exit 2 ;;
esac

GITLAB_TOKEN=$(python3 - "$agent" <<'PY'
import os, sys, tomllib
with open(os.path.expanduser("~/workspace/.env.toml"), "rb") as f:
    print(tomllib.load(f)[f"gitlab_{sys.argv[1]}_ai"]["token"])
PY
)
export GITLAB_TOKEN
export GITLAB_HOST="${GITLAB_HOST:-gitlab.doksam.com}"
exec glab "$@"
