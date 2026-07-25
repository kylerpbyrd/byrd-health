#!/usr/bin/with-contenv bashio

export PYTHONPATH="/app/packages/fertility_engine/src:/app/packages/data_service/src:/app/packages/web_api/src:/app/packages/ha_bridge/src:${PYTHONPATH:-}"
export PATH="/opt/venv/bin:${PATH}"
export DATA_PATH="/data"

# Read add-on configuration via bashio
TEMP_UNIT=$(bashio::config 'temp_unit' 'F')
HA_SENSOR_ENTITY=$(bashio::config 'ha_sensor_entity' '')
POLL_INTERVAL=$(bashio::config 'poll_interval_minutes' '15')

export BBT_TEMP_UNIT="${TEMP_UNIT}"
export BBT_HA_SENSOR_ENTITY="${HA_SENSOR_ENTITY}"
export BBT_POLL_INTERVAL="${POLL_INTERVAL}"
export BYRD_SECRET_KEY="${BYRD_SECRET_KEY:-byrd-health-dev-key-change-me}"
export BYRD_DATABASE_URL="sqlite+aiosqlite:///data/byrd_health.db"

bashio::log.info "Starting Byrd Health Fertility Tracker v2.0.0"
bashio::log.info "  Temperature unit : ${TEMP_UNIT}"
bashio::log.info "  Poll interval    : ${POLL_INTERVAL} min"
if [ -n "${HA_SENSOR_ENTITY}" ]; then
    bashio::log.info "  HA sensor entity : ${HA_SENSOR_ENTITY}"
fi

# Start the FastAPI app with uvicorn
exec uvicorn web_api.app:create_app --factory --host 0.0.0.0 --port 8000
