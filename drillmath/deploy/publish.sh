#!/usr/bin/env bash
# Выкатка тренажёра на drillmath.archik.tech.
#
# Сайт статический: собранная страница плюс проксирование /api/drill в
# службу ib-drill, которая уже работает на машине. Поэтому выкатка — это
# сборка и подмена символической ссылки, без служб и миграций.
#
# Запускается на самой машине от root (а не из CI): токен подмодулей в
# GitHub протух 2026-10-08, и прогон падает на checkout. Когда секрет
# обновят, этот скрипт станет шагом workflow — он уже написан так, чтобы
# ничего, кроме путей, у него не было.
#
#   sudo bash drillmath/deploy/publish.sh
set -euo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
root=/var/www/drillmath.archik.tech
release="$root/releases/$(git -C "$here" rev-parse --short HEAD)-$(date +%Y%m%d%H%M)"

if [[ $EUID -ne 0 ]]; then
  printf 'Нужен root: релизы лежат в /var/www.\n' >&2
  exit 1
fi

printf 'Сборка страницы.\n'
npm --prefix "$here" ci --silent
npm --prefix "$here" run build --silent

test -f "$here/dist/index.html"
test -d "$here/dist/assets"

printf 'Релиз %s\n' "$release"
install -d -m 755 "$root/releases" "$release"
rsync -rlpt --delete "$here/dist/" "$release/"
chown -R mathdeploy:nginx "$root"

# Ссылка переключается одним mv: полуготового состояния наружу не видно.
ln -s -- "$release" "$root/current.next"
mv -Tf -- "$root/current.next" "$root/current"

# Конфигурация nginx правится только руками от root и живёт в
# /etc/archik-sites; здесь лежит её копия, чтобы в git было видно, что
# стоит на машине. Если копия разошлась — предупреждаем, но не трогаем.
live=/etc/archik-sites/drillmath.archik.tech.conf
if ! diff -q "$here/deploy/drillmath.archik.tech.conf" "$live" >/dev/null 2>&1; then
  printf 'Внимание: %s разошёлся с копией в репозитории.\n' "$live" >&2
fi

printf 'Проверка.\n'
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 https://drillmath.archik.tech/ || true)
printf 'https://drillmath.archik.tech/ → %s\n' "$code"
