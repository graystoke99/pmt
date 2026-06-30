#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR/.."

docker compose up --build -d

printf '%s\n' "Frontend: http://localhost:3000"
printf '%s\n' "Backend:  http://localhost:8000"