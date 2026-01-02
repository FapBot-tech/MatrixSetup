FROM matrixdotorg/synapse:v1.114.0@sha256:3c07255ec6e9f81e005f948913a500f0cdf3e0f3673c41839266d2de4a1ae2ab

# 1. Copy all custom modules from the local 'modules' folder
# This will put room_restrict.py at /usr/local/lib/python3.11/site-packages/room_restrict.py
COPY modules/ /usr/local/lib/python3.13/site-packages/

# 2. Fix permissions for all files in that directory
RUN chmod 644 /usr/local/lib/python3.13/site-packages/*.py

# 3. Copy your local homeserver.yaml
COPY homeserver.yaml /data/homeserver.yaml

RUN apt-get update && apt-get install -y libmagic1
RUN pip install python-magic