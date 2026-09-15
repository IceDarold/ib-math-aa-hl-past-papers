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
drill_source="$repository_root/practicum/aahl"
# Ядро тренажёра — отдельный репозиторий, подключённый подмодулем: релиз
# должен нести ровно ту версию ядра, на которой его проверяли, иначе
# откат назад откатит только половину.
drill_core="$repository_root/vendor/drill-core"
# Физика — тоже подмодуль: её банк это лицензионный материал IB, и
# репозиторий поэтому приватный, но версия предмета обязана ехать вместе
# с релизом наравне с ядром.
physics_subject="$repository_root/vendor/ib-physics"
# Дорога для предмета, которого в git нет вовсе: положить его каталог
# сюда на самой машине, и выкатка его подберёт.
extra_subjects_root="/var/www/math.archik.tech/subjects"
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

if [[ ! -f "$drill_core/drill/server.py" ]]; then
  printf 'Drill core is missing. Did the checkout include submodules?\n' >&2
  exit 66
fi

if [[ ! -f "$physics_subject/bank/2025/bank.json" ]]; then
  printf 'Physics bank is missing. Did the checkout include submodules?\n' >&2
  exit 66
fi

# Индекс атласа собирается в сборке, а не лежит в репозитории: он выводной
# и весит три мегабайта двоичного файла, который менялся бы каждой правкой
# карты приёмов.
if [[ ! -f "$physics_subject/bank/2025/atlas.sqlite" ]]; then
  printf 'Physics atlas index is missing. Run build_atlas.py before deploying.\n' >&2
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
  # kit.py разрезан на пакет practicum/kit/. Фильтр rsync старый файл больше
  # не берёт, а значит, и --delete его не тронет: убираем копию прошлого
  # релиза здесь, иначе сайт отдавал бы устаревший набор. Жёсткая ссылка —
  # прошлый релиз не меняется.
  rm -f -- "$release/practicum/kit.py"
else
  install -d -m 755 "$release"
fi

# Каталог страниц физики заводится здесь по той же причине, что и vendor/.
install -d -m 755 "$release/physics"

# rsync создаёт только последний каталог пути, а vendor/ в релизе ещё нет:
# ни в пустом, ни в жёстко слинкованном с прошлым, где подмодулей не было
# вовсе. Заводим его здесь, а не флагом --mkpath, чтобы не зависеть от
# версии rsync на обеих сторонах.
install -d -m 755 "$release/vendor"
REMOTE

# --delete здесь сносит из релиза всё, чего нет в сборке страницы, и
# каталоги, которые приезжают следующими, он тоже снёс бы. Архив исключён
# по этой причине давно; vendor/ — по той же, только его вдобавок некому
# создать заново: rsync заводит лишь последний каталог пути.
rsync -rlptz --delete --exclude='/AA_HL/' --exclude='/vendor/' --exclude='/physics/' -e "$rsync_ssh" \
  "$web_dist/" "$remote:$release/"

rsync -rlptzc --delete -e "$rsync_ssh" \
  "$archive/" "$remote:$release/AA_HL/"

rsync -rlptzc --delete --exclude='__pycache__/' --exclude='*.pyc' \
  --include='*/' --include='*.ipynb' --include='*.pdf' --include='kit/*.py' \
  --include='aahl/***' --include='map.yaml' \
  --exclude='*' -e "$rsync_ssh" \
  "$practicum/" "$remote:$release/practicum/"

rsync -rlptzc --delete --exclude='__pycache__/' --exclude='*.pyc' \
  --exclude='.venv/' --exclude='tests/' -e "$rsync_ssh" \
  "$drill_core/" "$remote:$release/vendor/drill-core/"

# У физики нужен предмет, банк и собранные страницы: по ним предмет и
# понимает, какие практикумы готовы.
# Рендеры задач (bank/2025/renders, 118 МБ) места почти не прибавляют: релиз
# заводится жёсткими ссылками на прошлый, а -c оставляет совпавшие файлы
# нетронутыми — копируется только то, что перерисовали.
rsync -rlptzc --delete --exclude='__pycache__/' --exclude='*.pyc' \
  --exclude='.git/' --exclude='.venv/' --exclude='tests/' -e "$rsync_ssh" \
  "$physics_subject/" "$remote:$release/vendor/ib-physics/"

# Те же страницы вторым экземпляром там, куда ведут ссылки: их отдаёт
# nginx как обычную статику, из корня релиза.
if [[ -d "$physics_subject/site" ]]; then
  rsync -rlptzc --delete -e "$rsync_ssh" \
    "$physics_subject/site/" "$remote:$release/physics/"
fi

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
test -f "$release/practicum/aahl/bank.json"
# Карта практикумов: по ней страница строит список тем и ссылок.
test -f "$release/practicum/map.yaml"
test -f "$release/vendor/drill-core/drill/server.py"
test -f "$release/vendor/ib-physics/bank/2025/bank.json"
test -f "$release/vendor/ib-physics/bank/2025/atlas.sqlite"
test -f "$release/vendor/ib-physics/bank/2025/renders.json"
test -f "$release/vendor/ib-physics/api/app.py"
# Проверочный набор — пакет: тренажёр импортирует его отсюда.
test -f "$release/practicum/kit/__init__.py"
test -f "$release/practicum/kit/density.py"

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

# Индексы атласа: математика из своего каталога, физика из подмодуля.
# Первый в списке отвечает на запросы, где предмет не назвали.
atlas_dbs="math:$release/api/data/questions.sqlite"
if [[ -f "$release/vendor/ib-physics/bank/2025/atlas.sqlite" ]]; then
  atlas_dbs="$atlas_dbs,physics:$release/vendor/ib-physics/bank/2025/atlas.sqlite"
fi
printf 'Atlas indexes: %s\n' "$atlas_dbs"

nohup env QUESTION_ATLAS_DBS="$atlas_dbs" \
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
  -r "$release/vendor/drill-core/requirements.txt" \
  -r "$release/practicum/aahl/requirements.txt"

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

# Предметы: математика и физика из самого релиза, остальные — если они
# заведены на машине. Первый в списке отвечает на запросы, где предмет
# не назвали, и это математика: так работали все прежние ссылки.
drill_subjects="math:$release/practicum/aahl/subject.py"
drill_subjects="$drill_subjects,physics:$release/vendor/ib-physics/subject.py"
for candidate in "$remote_root"/subjects/*/subject.py; do
  [[ -f "$candidate" ]] || continue
  name=$(basename "$(dirname "$candidate")")
  [[ "$name" == "math" || "$name" == "physics" ]] && continue
  drill_subjects="$drill_subjects,$name:$candidate"
done
printf 'Drill subjects: %s\n' "$drill_subjects"

nohup env DRILL_DB="$drill_data/drill.sqlite" \
  DRILL_GRADER_KEY_FILE="$drill_runtime/openai.env" \
  DRILL_SUBJECTS="$drill_subjects" \
  PYTHONPATH="$release/vendor/drill-core:$release/practicum" \
  "$drill_venv/bin/python" -m drill.server \
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

# API банка физики. Пускает только по ключу, и файл ключей живёт вне
# релизов: в нём SHA-256 ключей, а сами ключи на машине не хранятся. Кладёт
# его root, один раз; нет файла — служба не поднимется, и выкатка остановится
# здесь, а не выставит банк наружу без замка.
physics_runtime="$remote_root/physics-api"
physics_keys="$physics_runtime/keys"
physics_pid="$physics_runtime/physics-api.pid"
physics_log="$physics_runtime/physics-api.log"
if [[ ! -f "$physics_keys" ]]; then
  printf 'Physics API keys file is missing: %s\n' "$physics_keys" >&2
  exit 1
fi
"$api_venv/bin/pip" install --disable-pip-version-check --quiet \
  -r "$release/vendor/ib-physics/api/requirements.txt"

if [[ -f "$physics_pid" ]]; then
  old_physics=$(cat "$physics_pid" || true)
  if [[ "$old_physics" =~ ^[0-9]+$ ]] && kill -0 "$old_physics" 2>/dev/null; then
    kill "$old_physics"
    for _ in {1..20}; do
      kill -0 "$old_physics" 2>/dev/null || break
      sleep 0.1
    done
  fi
fi

# Порт обязан освободиться до запуска. pid-файл может врать — например,
# после ручного перезапуска, — и тогда старая служба остаётся на порту, новая
# падает с «address already in use», а проверка здоровья отвечает старой:
# выкатка зелёная, а работает прошлый релиз. Так и было 2026-09-15.
# Под set -e и pipefail пустой grep — это ошибка всего скрипта, а пустой
# порт здесь нормальный ответ. Поэтому || true: так 2026-09-15 выкатка
# погасила старую службу и оборвалась, не запустив новую.
physics_listener() {
  { ss -ltnpH 'sport = :8043' 2>/dev/null | grep -o 'pid=[0-9]*' | head -n 1 | cut -d= -f2; } || true
}
for _ in {1..50}; do
  stale=$(physics_listener)
  [[ -z "$stale" ]] && break
  kill "$stale" 2>/dev/null || true
  sleep 0.1
done
if [[ -n "$(physics_listener)" ]] || { ss -ltnH 'sport = :8043' | grep -q . ; }; then
  printf 'Port 8043 is still taken by another process.\n' >&2
  exit 1
fi

nohup env PHYSICS_API_KEYS="$physics_keys" \
  "$api_venv/bin/uvicorn" --app-dir "$release/vendor/ib-physics/api" app:app \
  --host 127.0.0.1 --port 8043 --proxy-headers \
  >> "$physics_log" 2>&1 &
physics_process=$!
printf '%s\n' "$physics_process" > "$physics_pid"

# Банк и приёмы грузятся при старте, до первого запроса: это секунды.
printf 'Waiting for physics API health check.\n'
for _ in {1..120}; do
  if curl --fail --silent http://127.0.0.1:8043/health >/dev/null; then
    break
  fi
  sleep 0.25
done
if ! curl --fail --silent --show-error http://127.0.0.1:8043/health >/dev/null; then
  printf 'Physics API did not start. Recent log:\n' >&2
  tail -n 40 "$physics_log" >&2 || true
  exit 1
fi
# Отвечать должен именно тот процесс, который запустили сейчас.
if [[ "$(physics_listener)" != "$physics_process" ]]; then
  printf 'Port 8043 is served by pid %s, not by the new process %s.\n' \
    "$(physics_listener)" "$physics_process" >&2
  tail -n 20 "$physics_log" >&2 || true
  exit 1
fi
anonymous=$(curl --silent --output /dev/null --write-out '%{http_code}' \
  http://127.0.0.1:8043/api/physics/v1/questions)
if [[ "$anonymous" != "401" ]]; then
  printf 'Physics API answered %s without a key.\n' "$anonymous" >&2
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
  https://ib.archik.tech/ | grep -q 'Question Atlas'; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error --head "${auth[@]}" \
  --retry 5 --retry-delay 2 --max-time 20 \
  'https://ib.archik.tech/AA_HL/2022/May/TZ2/Paper%201/question-paper.pdf' >/dev/null; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error "${auth[@]}" --max-time 20 \
  'https://ib.archik.tech/api/health' | grep -q '"ok":true'; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error --head "${auth[@]}" \
  --retry 5 --retry-delay 2 --max-time 20 \
  'https://ib.archik.tech/practicum/calculus/practicum-e7-differential-equations.ipynb' >/dev/null; then
  rollback
  exit 1
fi

if ! curl --fail --silent --show-error "${auth[@]}" --max-time 20 \
  'https://ib.archik.tech/api/drill/health' | grep -q '"ok": true'; then
  rollback
  exit 1
fi

if curl --fail --silent --head --max-time 20 \
  'https://ib.archik.tech/AA_HL/2022/May/TZ2/Paper%201/question-paper.pdf' \
  >/dev/null; then
  printf 'Archive is reachable without a password.\n' >&2
  rollback
  exit 1
fi

# API физики идёт мимо пароля сайта, и замок у него один — ключ. Снаружи
# без ключа должен быть отказ, а не банк и не 502 от упавшей службы.
if ! curl --fail --silent --show-error --max-time 20 --retry 5 --retry-delay 2 \
  'https://ib.archik.tech/api/physics/v1/health' | grep -q '"ok":true'; then
  printf 'Physics API is not reachable.\n' >&2
  rollback
  exit 1
fi
physics_anonymous=$(curl --silent --output /dev/null --write-out '%{http_code}' \
  --max-time 20 'https://ib.archik.tech/api/physics/v1/questions')
if [[ "$physics_anonymous" != "401" ]]; then
  printf 'Physics API answered %s without a key.\n' "$physics_anonymous" >&2
  rollback
  exit 1
fi

# С 2026-09-15 сайт живёт на ib.archik.tech; старый адрес обязан вести
# туда же, с тем же путём, — на нём ссылки из заметок и программы у API.
moved=$(curl --silent --output /dev/null --max-time 20 \
  --write-out '%{http_code} %{redirect_url}' \
  'https://math.archik.tech/api/physics/v1/health?probe=1')
if [[ "$moved" != "308 https://ib.archik.tech/api/physics/v1/health?probe=1" ]]; then
  printf 'Old address does not move to the new one: %s\n' "$moved" >&2
  rollback
  exit 1
fi

printf 'Deployed %s\n' "$release_id"
