FROM ghcr.io/home-assistant/base:latest

# Labels for HA Supervisor
LABEL \
  io.hass.version="2.0.0" \
  io.hass.type="addon" \
  io.hass.arch="aarch64|amd64|armhf|armv7"

# Install Python
RUN apk add --no-cache python3 py3-pip nodejs npm

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy Python packages
COPY packages/ /app/packages/

# Install Python packages in dependency order (fertility_engine has no internal deps)
RUN pip install --no-cache-dir /app/packages/fertility_engine
RUN pip install --no-cache-dir /app/packages/data_service
RUN pip install --no-cache-dir /app/packages/web_api
RUN pip install --no-cache-dir /app/packages/ha_bridge

# Copy and build frontend
COPY frontend/ /app/frontend/
WORKDIR /app/frontend
RUN npm install && npm run build

# Copy frontend build output to static serving location
RUN mkdir -p /app/static && cp -r /app/frontend/dist/* /app/static/

# Copy startup script
COPY run.sh /run.sh
RUN chmod a+x /run.sh

WORKDIR /
CMD ["/run.sh"]
