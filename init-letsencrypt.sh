#!/bin/sh
# Первое получение сертификата Let's Encrypt для jam.secsoc.tech
# Запуск: ./init-letsencrypt.sh your@email.com

set -e

EMAIL="${1:?Укажите email для Let's Encrypt: ./init-letsencrypt.sh your@email.com}"
DOMAIN="jam.secsoc.tech"

echo "Получение сертификата для $DOMAIN (email: $EMAIL)..."

docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d "$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --non-interactive

echo "Сертификат получен. Переключаем nginx на HTTPS..."
cp nginx/nginx-ssl.conf nginx/nginx.conf
docker compose restart nginx

echo "Готово. Откройте https://$DOMAIN"
