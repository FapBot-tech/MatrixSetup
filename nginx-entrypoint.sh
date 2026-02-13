#!/bin/sh
set -e

CERT_PATH="/etc/nginx/certs/fullchain.pem"
KEY_PATH="/etc/nginx/certs/privkey.pem"

if [ -f "$CERT_PATH" ] && [ -f "$KEY_PATH" ]; then
  # Generate nginx.conf with SSL
  sed "s/\${DOMAIN}/$DOMAIN/g" /nginx.conf.template > /etc/nginx/nginx.conf
else
  # Generate nginx.conf without SSL for both server blocks
  sed \
    -e '/listen 443 ssl;/d' \
    -e '/listen \[::\]:443 ssl;/d' \
    -e '/ssl_certificate/d' \
    -e '/ssl_certificate_key/d' \
    -e 's/\${DOMAIN}/$DOMAIN/g' \
    /nginx.conf.template > /etc/nginx/nginx.conf
fi

exec nginx -g 'daemon off;'
