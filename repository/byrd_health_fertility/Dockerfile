# -------------------------------------------------------------------
# Byrd Health — Fertility Tracker  v2.0.0
# Home Assistant Add-on Dockerfile
#
# NOTE: This Dockerfile is designed to be built from the repository
# root, not from this directory. Use the build script:
#   docker build -f repository/byrd_health_fertility/Dockerfile -t byrd-health:rc1 .
#
# For HA Supervisor local add-on use:
#   1. Build image manually: docker build -t byrd-health:rc1 .
#   2. Update config.yaml in this directory to use 'image: byrd-health:rc1'
#   3. Install via HA Supervisor
# -------------------------------------------------------------------

FROM ghcr.io/home-assistant/base:latest

LABEL \
  io.hass.version="2.0.0" \
  io.hass.type="addon" \
  io.hass.arch="aarch64|amd64|armhf|armv7"

RUN apk add --no-cache python3 py3-pip nodejs npm

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY packages/ /app/packages/

RUN pip install --no-cache-dir /app/packages/fertility_engine
RUN pip install --no-cache-dir /app/packages/data_service
RUN pip install --no-cache-dir /app/packages/ha_bridge
RUN pip install --no-cache-dir /app/packages/device_adapters
RUN pip install --no-cache-dir /app/packages/web_api

COPY frontend/ /app/frontend/
WORKDIR /app/frontend
RUN npm install && npm run build
RUN mkdir -p /app/static && cp -r /app/frontend/dist/* /app/static/

COPY packages/ha_bridge/src/ha_bridge/card/ha-card.js /app/static/ha-card.js

COPY run.sh /run.sh
RUN chmod a+x /run.sh

WORKDIR /
CMD ["/run.sh"]
