FROM matrixdotorg/synapse:sha-1841ded

# 1. Copy all custom modules from the local 'modules' folder
COPY modules/ /usr/local/lib/python3.13/site-packages/

# 2. Fix permissions for all files in that directory
RUN chmod 644 /usr/local/lib/python3.13/site-packages/*.py

# 3. Copy your local homeserver.yaml.template OUTSIDE /data
COPY homeserver.yaml /homeserver.yaml.template

# 4. Add entrypoint script to perform variable substitution
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY nginx-entrypoint.sh /nginx-entrypoint.sh
RUN chmod +x /nginx-entrypoint.sh

RUN apt-get update && apt-get install -y libmagic1 && pip install python-magic

ENTRYPOINT ["/entrypoint.sh"]
