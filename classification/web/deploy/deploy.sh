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
nginx_source="$repository_root/classification/web/deploy/math.archik.tech.conf"
remote_root=/var/www/math.archik.tech
release_id="${GITHUB_SHA}-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
release="$remote_root/releases/$release_id"
current="$remote_root/current"
remote="${DEPLOY_USER}@${DEPLOY_HOST}"

if [[ ! -f "$web_dist/index.html" || ! -d "$archive" || ! -d "$practicum" || ! -f "$api_database" || ! -f "$nginx_source" ]]; then
  printf 'Build output, archive, practicum, API index, or nginx configuration is missing.\n' >&2
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

rsync -rlptzc --delete --include='*/' --include='*.ipynb' --exclude='*' -e "$rsync_ssh" \
  "$practicum/" "$remote:$release/practicum/"

rsync -rlptzc --delete --exclude='__pycache__/' --exclude='*.pyc' -e "$rsync_ssh" \
  "$api_source/" "$remote:$release/api/"

rsync -rlptz -e "$rsync_ssh" \
  "$nginx_source" "$remote:$release/math.archik.tech.conf"

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

printf 'Updating nginx proxy configuration.\n'
if ! sudo -n true 2>&1; then
  printf 'The deploy user is not permitted to update nginx.\n' >&2
  exit 65
fi
nginx_target=$(sudo -n grep -rl --include='*.conf' 'server_name math.archik.tech' /etc/nginx /opt/hiddify-manager/nginx 2>/dev/null | head -n 1)
if [[ -z "$nginx_target" ]]; then
  printf 'Could not locate the nginx virtual host for math.archik.tech.\n' >&2
  exit 65
fi
sudo -n install -m 644 "$release/math.archik.tech.conf" "$nginx_target"
sudo -n nginx -t
sudo -n systemctl reload nginx

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

if ! curl --fail --silent --show-error --location \
  --retry 5 --retry-delay 2 --max-time 20 \
  https://math.archik.tech/ | grep -q 'Question Atlas'; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error --head \
  --retry 5 --retry-delay 2 --max-time 20 \
  'https://math.archik.tech/AA_HL/2022/May/TZ2/Paper%201/question-paper.pdf' >/dev/null; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error --max-time 20 \
  'https://math.archik.tech/api/health' | grep -q '"ok":true'; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error --head \
  --retry 5 --retry-delay 2 --max-time 20 \
  'https://math.archik.tech/practicum/calculus/practicum-e7-differential-equations.ipynb' >/dev/null; then
  rollback
  exit 1
fi

printf 'Deployed %s\n' "$release_id"
