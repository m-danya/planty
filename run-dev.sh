#!/usr/bin/env bash

set -euo pipefail

project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
session_name=${PLANTY_TMUX_SESSION:-planty-dev}

if [[ ! $session_name =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "PLANTY_TMUX_SESSION may contain only letters, numbers, '_' and '-'." >&2
    exit 1
fi

for command_name in tmux uv npm; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Required command is not installed: $command_name" >&2
        exit 1
    fi
done

if [[ ! -f "$project_dir/.env.dev" ]]; then
    echo ".env.dev is missing. Complete the local setup from README.md first." >&2
    exit 1
fi

(
    cd "$project_dir"
    uv run alembic upgrade head
)

if ! tmux has-session -t "=$session_name" 2>/dev/null; then
    tmux new-session -d -s "$session_name" -n backend -c "$project_dir"
    tmux send-keys -t "=$session_name:backend" \
        "uv run uvicorn planty.main:app --reload" Enter

    tmux new-window -t "=$session_name" -n frontend -c "$project_dir/frontend"
    tmux send-keys -t "=$session_name:frontend" "npm run dev" Enter
    tmux select-window -t "=$session_name:backend"
fi

if [[ -n ${TMUX:-} ]]; then
    exec tmux switch-client -t "=$session_name"
else
    exec tmux attach-session -t "=$session_name"
fi
