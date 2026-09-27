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

# Три службы банка держит systemd: ib-atlas-api (8041), ib-drill (8042) и
# ib-physics-api (8043). До 27 сентября их пускала эта выкатка -- nohup плюс
# pid-файл, без юнита и без супервизора, -- и SIGTERM гасил службу навсегда:
# снаружи это 502 на ib.archik.tech, а внутри Knowy -- «пустой банк», то есть
# поломка выглядела чужой. Заодно ушла причина аварии 2026-09-15: pid-файл врал,
# старая служба оставалась на порту, новая падала с «address already in use», а
# проверка здоровья отвечала старой -- выкатка зелёная, работает прошлый релиз.
# У порта теперь один владелец, и pid-файлы не нужны.
services=(ib-atlas-api.service ib-drill.service ib-physics-api.service)

deployment_failure() {
  status=$?
  printf 'Bank services failed. State and recent journal:\n' >&2
  sudo -n /usr/bin/systemctl is-active "${services[@]}" >&2 || true
  for unit in "${services[@]}"; do
    printf -- '--- %s\n' "$unit" >&2
    journalctl -u "$unit" -n 40 --no-pager >&2 || true
  done
  exit "$status"
}
trap deployment_failure ERR

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
test -f "$release/vendor/ib-physics/api/practice.py"
test -f "$release/vendor/ib-physics/api/widget/practice.html"
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


drill_runtime="$remote_root/drill-runtime"
drill_venv="$drill_runtime/venv"
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


# API банка физики. Пускает только по ключу, и файл ключей живёт вне
# релизов: в нём SHA-256 ключей, а сами ключи на машине не хранятся. Кладёт
# его root, один раз; нет файла — служба не поднимется, и выкатка остановится
# здесь, а не выставит банк наружу без замка.
physics_runtime="$remote_root/physics-api"
physics_keys="$physics_runtime/keys"
if [[ ! -f "$physics_keys" ]]; then
  printf 'Physics API keys file is missing: %s\n' "$physics_keys" >&2
  exit 1
fi
# Секрет подписи временных ссылок на файлы (рисунок, рендер без ключа).
# Создаётся один раз и живёт вне релизов рядом с ключами; если его сменить,
# перестанут открываться только уже выданные ссылки.
physics_signing="$physics_runtime/signing-key"
if [[ ! -s "$physics_signing" ]]; then
  ( umask 077; od -An -N32 -tx1 /dev/urandom | tr -d ' \n' > "$physics_signing.tmp" )
  mv -f -- "$physics_signing.tmp" "$physics_signing"
fi
"$api_venv/bin/pip" install --disable-pip-version-check --quiet \
  -r "$release/vendor/ib-physics/api/requirements.txt"



# Ссылку переключаем ДО перезапуска: службы читают код по пути current, поэтому
# порядок обратный прежнему. У прежнего порядка была своя цена -- проверка могла
# отвечать от прошлого релиза. Если проверка здоровья здесь не пройдёт,
# rollback() вернёт ссылку и перезапустит службы: наружу снова пойдёт прошлый
# релиз, как и раньше.
ln -s -- "$release" "$next"
mv -Tf -- "$next" "$current"

printf 'Restarting bank services.\n'
sudo -n /usr/bin/systemctl restart "${services[@]}"

printf 'Waiting for Question Atlas API health check.\n'
for _ in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8041/health >/dev/null; then
    break
  fi
  sleep 0.5
done
curl --fail --silent --show-error http://127.0.0.1:8041/health >/dev/null

printf 'Waiting for drill health check.\n'
for _ in {1..60}; do
  if curl --fail --silent http://127.0.0.1:8042/api/drill/health >/dev/null; then
    break
  fi
  sleep 0.5
done
curl --fail --silent --show-error http://127.0.0.1:8042/api/drill/health >/dev/null

# Банк и приёмы физики грузятся при старте, до первого запроса: это секунды.
printf 'Waiting for physics API health check.\n'
for _ in {1..120}; do
  if curl --fail --silent http://127.0.0.1:8043/health >/dev/null; then
    break
  fi
  sleep 0.25
done
curl --fail --silent --show-error http://127.0.0.1:8043/health >/dev/null

# Наружу банк только за ключом: без ключа обязан быть 401.
anonymous=$(curl --silent --output /dev/null --write-out '%{http_code}' \
  http://127.0.0.1:8043/api/physics/v1/questions)
if [[ "$anonymous" != "401" ]]; then
  printf 'Physics API answered %s without a key.\n' "$anonymous" >&2
  exit 1
fi
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

# Вернуть ссылку недостаточно: службы читают код по пути current уже при
# запуске, поэтому без перезапуска они продолжат работать на том релизе,
# который только что не прошёл проверку.
sudo -n /usr/bin/systemctl restart \
  ib-atlas-api.service ib-drill.service ib-physics-api.service || true
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
# Практика в ChatGPT (MCP) — третья дверь; без ключа тоже отказ.
physics_mcp=$(curl --silent --output /dev/null --write-out '%{http_code}' --max-time 20 \
  -X POST -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  --data '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  'https://ib.archik.tech/api/physics/mcp')
if [[ "$physics_mcp" != "401" ]]; then
  printf 'Physics practice MCP answered %s without a key.\n' "$physics_mcp" >&2
  rollback
  exit 1
fi
# Подписанная ссылка — вторая дверь без ключа; поддельная обязана получить отказ.
physics_forged=$(curl --silent --output /dev/null --write-out '%{http_code}' \
  --max-time 20 "https://ib.archik.tech/api/physics/s/$(( $(date +%s) + 600 )).000000000000.$(printf 'A%.0s' {1..43})/v1/questions/19M.2.HL.TZ1.2/render/question.png")
if [[ "$physics_forged" != "403" ]]; then
  printf 'Physics API answered %s to a forged signed link.\n' "$physics_forged" >&2
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

# Каждая выкатка оставляет на диске свой каталог, и никто их не убирал: к
# 17 сентября их накопилось 116 на 2.2 ГБ. Этого хватило, чтобы заполнить
# диск, и Postgres Life OS ушёл в бесконечный цикл восстановления — ему
# негде было записать контрольную точку. Держим последние KEEP, плюс тот,
# на который смотрит current, плюс предыдущий: откат должен остаться
# возможным. Релизы связаны жёсткими ссылками, поэтому старые стоят только
# тем, что в них изменилось, — но счёт всё равно не должен расти без края.
ssh "${ssh_args[@]}" "$remote" bash -s -- "$remote_root" "$current" "$previous" <<'REMOTE'
set -euo pipefail

root=$1
current=$2
previous=$3
keep=5

case "$root" in
  /var/www/math.archik.tech) ;;
  *) printf 'Unsafe root for pruning.\n' >&2; exit 64 ;;
esac

live=$(readlink -f -- "$current" || true)
cd -- "$root/releases" || exit 0
# Через подстановку процесса, а не через конвейер: под pipefail пустой
# каталог уронил бы выкатку уже после того, как она прошла.
mapfile -t all < <(ls -1dt -- */ 2>/dev/null | sed 's|/$||')
for name in "${all[@]:keep}"; do
  case "$name" in
    */*|''|.|..) continue ;;
  esac
  path="$root/releases/$name"
  if [[ "$path" == "$live" || "$path" == "$previous" ]]; then
    continue
  fi
  rm -rf -- "$path"
done
REMOTE

printf 'Deployed %s\n' "$release_id"
