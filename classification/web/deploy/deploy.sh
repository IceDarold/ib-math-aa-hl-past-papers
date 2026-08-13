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
remote_root=/var/www/math.archik.tech
release_id="${GITHUB_SHA}-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
release="$remote_root/releases/$release_id"
current="$remote_root/current"
remote="${DEPLOY_USER}@${DEPLOY_HOST}"

if [[ ! -f "$web_dist/index.html" || ! -d "$archive" || ! -d "$practicum" ]]; then
  printf 'Build output, AA_HL archive, or practicum directory is missing.\n' >&2
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

ssh "${ssh_args[@]}" "$remote" bash -s -- "$release" "$current" "$release_id" <<'REMOTE'
set -euo pipefail

release=$1
current=$2
release_id=$3
next="${current}.next.${release_id}"

test -f "$release/index.html"
test -d "$release/assets"
test -d "$release/AA_HL"
test -f "$release/practicum/calculus/practicum-e7-differential-equations.ipynb"

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

if ! curl --fail --silent --show-error --head \
  --retry 5 --retry-delay 2 --max-time 20 \
  'https://math.archik.tech/practicum/calculus/practicum-e7-differential-equations.ipynb' >/dev/null; then
  rollback
  exit 1
fi

printf 'Deployed %s\n' "$release_id"
