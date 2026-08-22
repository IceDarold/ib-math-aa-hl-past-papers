#!/usr/bin/env bash
# Ставит конфигурацию nginx для math.archik.tech. Запускать от root на самой
# машине — учётная запись деплоя (mathdeploy) прав sudo не имеет вовсе,
# поэтому в deploy.sh этот шаг не входит.
#
# Нужен после правки classification/web/deploy/math.archik.tech.conf:
# сам деплой конфигурацию не трогает, только выкладывает файлы и службы.
#
#   sudo practicum/drill/deploy/install-nginx.sh
#
# Конфигурация кладётся в оба места. /etc/archik-sites — постоянное:
# оттуда restore-archik-sites возвращает её в hiddify после обновлений,
# которые чистят conf.d. Без этого настройка живёт до первого обновления.

set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
source_conf="$root/classification/web/deploy/math.archik.tech.conf"
durable=/etc/archik-sites/math.archik.tech.conf
live=/opt/hiddify-manager/nginx/conf.d/math.archik.tech.conf
htpasswd=/var/www/math.archik.tech/htpasswd

test -f "$source_conf"

if [[ ! -f "$htpasswd" ]]; then
  printf 'Нет %s — сайт закрыт паролем, файл обязателен.\n' "$htpasswd" >&2
  printf 'Его кладёт деплой из секретов MATH_BASIC_AUTH_USER и ...PASSWORD.\n' >&2
  exit 1
fi

install -m 0644 -o root -g root "$source_conf" "$durable"
install -m 0644 -o root -g root "$source_conf" "$live"
nginx -t -c /opt/hiddify-manager/nginx/nginx.conf
systemctl reload hiddify-nginx.service

printf 'Конфигурация установлена и nginx перезагружен.\n'
