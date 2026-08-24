#!/usr/bin/env bash

set -euo pipefail

required_variables=(
  DEPLOY_HOST
  DEPLOY_USER
  DEPLOY_KEY_PATH
  DEPLOY_KNOWN_HOSTS
  GITHUB_SHA
  GITHUB_RUN_ID
  GITHUB_RUN_ATTEMPT
  HTPASSWD_FILE
  BASIC_AUTH_USER
  BASIC_AUTH_PASSWORD
  GRADER_KEY_FILE
)

for variable in "${required_variables[@]}"; do
  if [[ -z "${!variable:-}" ]]; then
    printf 'Missing required variable: %s\n' "$variable" >&2
    exit 64
  fi
done

if [[ ! "$GITHUB_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  printf 'GITHUB_SHA must be a full commit SHA.\n' >&2
  exit 64
fi

if [[ ! "$GITHUB_RUN_ID" =~ ^[0-9]+$ || ! "$GITHUB_RUN_ATTEMPT" =~ ^[0-9]+$ ]]; then
  printf 'GitHub run identifiers must be numeric.\n' >&2
  exit 64
fi

repository_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
web_dist="$repository_root/classification/web/dist"
archive="$repository_root/AA_HL"
practicum="$repository_root/practicum"
api_source="$repository_root/classification/api"
api_database="$api_source/data/questions.sqlite"
drill_source="$repository_root/practicum/drill"
remote_root=/var/www/math.archik.tech
release_id="${GITHUB_SHA}-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
release="$remote_root/releases/$release_id"
current="$remote_root/current"
remote="${DEPLOY_USER}@${DEPLOY_HOST}"

if [[ ! -f "$web_dist/index.html" || ! -d "$archive" || ! -d "$practicum" || ! -f "$api_database" ]]; then
  printf 'Build output, archive, practicum, or API index is missing.\n' >&2
  exit 66
fi

if [[ ! -f "$drill_source/bank.json" || ! -f "$HTPASSWD_FILE" ]]; then
  printf 'Drill bank or the htpasswd file is missing.\n' >&2
  exit 66
fi

ssh_args=(
  -i "$DEPLOY_KEY_PATH"
  -o "UserKnownHostsFile=$DEPLOY_KNOWN_HOSTS"
  -o StrictHostKeyChecking=yes
  -o IdentitiesOnly=yes
  -o BatchMode=yes
)

printf -v rsync_ssh 'ssh -i %q -o UserKnownHostsFile=%q -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o BatchMode=yes' \
  "$DEPLOY_KEY_PATH" "$DEPLOY_KNOWN_HOSTS"

previous=$(ssh "${ssh_args[@]}" "$remote" readlink -f -- "$current" || true)

ssh "${ssh_args[@]}" "$remote" install -d -m 755 \
  /var/www/math.archik.tech/drill-runtime /var/www/math.archik.tech/drill-data

ssh "${ssh_args[@]}" "$remote" bash -s -- "$release" "$previous" <<'REMOTE'
set -euo pipefail

release=$1
previous=$2

case "$release" in
  /var/www/math.archik.tech/releases/[0-9a-f]*-[0-9]*-[0-9]*) ;;
  *) printf 'Unsafe release path.\n' >&2; exit 64 ;;
esac

if [[ -e "$release" ]]; then
  printf 'Release already exists: %s\n' "$release" >&2
  exit 73
fi

if [[ -n "$previous" && -d "$previous" ]]; then
  case "$previous" in
    /var/www/math.archik.tech/releases/*) ;;
    *) printf 'Unsafe previous release path.\n' >&2; exit 64 ;;
  esac
  cp -al -- "$previous" "$release"
else
  install -d -m 755 "$release"
fi
REMOTE

rsync -rlptz --delete --exclude='/AA_HL/' -e "$rsync_ssh" \
  "$web_dist/" "$remote:$release/"

rsync -rlptzc --delete -e "$rsync_ssh" \
  "$archive/" "$remote:$release/AA_HL/"

rsync -rlptzc --delete --exclude='__pycache__/' --exclude='*.pyc' \
  --include='*/' --include='*.ipynb' --include='kit.py' --include='drill/***' \
  --exclude='*' -e "$rsync_ssh" \
  "$practicum/" "$remote:$release/practicum/"

rsync -rlptzc --delete --exclude='__pycache__/' --exclude='*.pyc' -e "$rsync_ssh" \
  "$api_source/" "$remote:$release/api/"

rsync -rlptz --chmod=F644 -e "$rsync_ssh" \
  "$HTPASSWD_FILE" "$remote:$remote_root/htpasswd"

# Ключ проверяющей модели: вне релизов, только владельцу. В командную
# строку службы он не попадает — служба читает его из файла, иначе он был
# бы виден в ps любому на машине.
rsync -rlptz --chmod=F600 -e "$rsync_ssh" \
  "$GRADER_KEY_FILE" "$remote:$remote_root/drill-runtime/openai.env"

ssh "${ssh_args[@]}" "$remote" bash -s -- "$release" "$current" "$release_id" "$remote_root" <<'REMOTE'
set -euo pipefail

release=$1
current=$2
release_id=$3
remote_root=$4
next="${current}.next.${release_id}"
api_runtime="$remote_root/api-runtime"
api_venv="$api_runtime/venv"
api_pid="$api_runtime/question-atlas-api.pid"
api_log="$api_runtime/question-atlas-api.log"

api_failure() {
  status=$?
  printf 'Question Atlas API deployment failed. Recent service log:\n' >&2
  if [[ -f "$api_log" ]]; then
    tail -n 80 "$api_log" >&2 || true
  fi
  exit "$status"
}
trap api_failure ERR

test -f "$release/index.html"
test -d "$release/assets"
test -d "$release/AA_HL"
test -f "$release/practicum/calculus/practicum-e7-differential-equations.ipynb"
test -f "$release/api/data/questions.sqlite"
test -f "$release/practicum/drill/bank.json"
test -f "$release/practicum/kit.py"

install -d -m 755 "$api_runtime"
if [[ ! -x "$api_venv/bin/python" ]]; then
  printf 'Creating Question Atlas API virtual environment.\n'
  python3 -m venv "$api_venv"
fi
printf 'Installing Question Atlas API dependencies.\n'
"$api_venv/bin/pip" install --disable-pip-version-check --quiet -r "$release/api/requirements.txt"

if [[ -f "$api_pid" ]]; then
  old_pid=$(cat "$api_pid" || true)
  if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
    kill "$old_pid"
    for _ in {1..20}; do
      kill -0 "$old_pid" 2>/dev/null || break
      sleep 0.1
    done
  fi
fi

nohup env QUESTION_ATLAS_DB="$release/api/data/questions.sqlite" \
  "$api_venv/bin/uvicorn" --app-dir "$release/api" app:app --host 127.0.0.1 --port 8041 \
  >> "$api_log" 2>&1 &
api_process=$!
printf '%s\n' "$api_process" > "$api_pid"

printf 'Waiting for Question Atlas API health check.\n'
for _ in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8041/health >/dev/null; then
    break
  fi
  sleep 0.1
done
curl --fail --silent --show-error http://127.0.0.1:8041/health >/dev/null

drill_runtime="$remote_root/drill-runtime"
drill_venv="$drill_runtime/venv"
drill_pid="$drill_runtime/drill.pid"
drill_log="$drill_runtime/drill.log"
drill_data="$remote_root/drill-data"

install -d -m 755 "$drill_runtime" "$drill_data"
if [[ ! -x "$drill_venv/bin/python" ]]; then
  printf 'Creating drill virtual environment.\n'
  python3 -m venv "$drill_venv"
fi
printf 'Installing drill dependencies.\n'
"$drill_venv/bin/pip" install --disable-pip-version-check --quiet \
  -r "$release/practicum/drill/requirements.txt"

if [[ -f "$drill_pid" ]]; then
  old_drill=$(cat "$drill_pid" || true)
  if [[ "$old_drill" =~ ^[0-9]+$ ]] && kill -0 "$old_drill" 2>/dev/null; then
    kill "$old_drill"
    for _ in {1..20}; do
      kill -0 "$old_drill" 2>/dev/null || break
      sleep 0.1
    done
  fi
fi

nohup env DRILL_DB="$drill_data/drill.sqlite" \
  DRILL_GRADER_KEY_FILE="$drill_runtime/openai.env" \
  "$drill_venv/bin/python" "$release/practicum/drill/server.py" \
  --host 127.0.0.1 --port 8042 \
  >> "$drill_log" 2>&1 &
printf '%s\n' "$!" > "$drill_pid"

printf 'Waiting for drill health check.\n'
for _ in {1..60}; do
  if curl --fail --silent http://127.0.0.1:8042/api/drill/health >/dev/null; then
    break
  fi
  sleep 0.2
done
if ! curl --fail --silent --show-error http://127.0.0.1:8042/api/drill/health >/dev/null; then
  printf 'Drill service did not start. Recent log:\n' >&2
  tail -n 40 "$drill_log" >&2 || true
  exit 1
fi

ln -s -- "$release" "$next"
mv -Tf -- "$next" "$current"
REMOTE

rollback() {
  printf 'Health check failed; restoring the previous release.\n' >&2
  ssh "${ssh_args[@]}" "$remote" bash -s -- "$previous" "$current" "$release_id" <<'REMOTE'
set -euo pipefail

previous=$1
current=$2
release_id=$3
next="${current}.rollback.${release_id}"

if [[ -n "$previous" && -d "$previous" ]]; then
  ln -s -- "$previous" "$next"
  mv -Tf -- "$next" "$current"
else
  unlink -- "$current"
fi
REMOTE
}

auth=(--user "$BASIC_AUTH_USER:$BASIC_AUTH_PASSWORD")

if ! curl --fail --silent --show-error --location "${auth[@]}" \
  --retry 5 --retry-delay 2 --max-time 20 \
  https://math.archik.tech/ | grep -q 'Question Atlas'; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error --head "${auth[@]}" \
  --retry 5 --retry-delay 2 --max-time 20 \
  'https://math.archik.tech/AA_HL/2022/May/TZ2/Paper%201/question-paper.pdf' >/dev/null; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error "${auth[@]}" --max-time 20 \
  'https://math.archik.tech/api/health' | grep -q '"ok":true'; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error --head "${auth[@]}" \
  --retry 5 --retry-delay 2 --max-time 20 \
  'https://math.archik.tech/practicum/calculus/practicum-e7-differential-equations.ipynb' >/dev/null; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error "${auth[@]}" --max-time 20 \
  'https://math.archik.tech/api/drill/health' | grep -q '"ok": true'; then
  rollback
  exit 1
fi

if curl --fail --silent --head --max-time 20 \
  'https://math.archik.tech/AA_HL/2022/May/TZ2/Paper%201/question-paper.pdf' \
  >/dev/null; then
  printf 'Archive is reachable without a password.\n' >&2
  rollback
  exit 1
fi

printf 'Deployed %s\n' "$release_id"
