#!/bin/sh
set -e

# Replace ${DOMAIN} and ${POSTGRES_PASSWORD} in /homeserver.yaml.template and output to /data/homeserver.yaml
sed "s/\${DOMAIN}/$DOMAIN/g; s/\${POSTGRES_PASSWORD}/$POSTGRES_PASSWORD/g" /homeserver.yaml.template > /data/homeserver.yaml

# Start Synapse with explicit config file
exec python -m synapse.app.homeserver -c /data/homeserver.yaml
