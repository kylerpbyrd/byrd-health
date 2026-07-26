#!/usr/bin/with-contenv bashio

export PYTHONPATH="/app/packages/fertility_engine/src:/app/packages/data_service/src:/app/packages/web_api/src:/app/packages/ha_bridge/src:${PYTHONPATH:-}"
export PATH="/opt/venv/bin:${PATH}"
export DATA_PATH="/data"

# Read add-on configuration via bashio
TEMP_UNIT=$(bashio::config 'temp_unit' 'F')
HA_SENSOR_ENTITY=$(bashio::config 'ha_sensor_entity' '')
POLL_INTERVAL=$(bashio::config 'poll_interval_minutes' '15')
NOTIFY_TEMP_REMINDER=$(bashio::config 'notify_temp_reminder' 'true')
NOTIFY_TEMP_REMINDER_TIME=$(bashio::config 'notify_temp_reminder_time' '07:00')
NOTIFY_FERTILE_WINDOW=$(bashio::config 'notify_fertile_window' 'true')
NOTIFY_PERIOD_PREDICTION=$(bashio::config 'notify_period_prediction' 'true')
NOTIFY_OVULATION_DETECTED=$(bashio::config 'notify_ovulation_detected' 'true')

export BBT_TEMP_UNIT="${TEMP_UNIT}"
export BBT_HA_SENSOR_ENTITY="${HA_SENSOR_ENTITY}"
export BBT_POLL_INTERVAL="${POLL_INTERVAL}"
export BBT_NOTIFY_TEMP="${NOTIFY_TEMP_REMINDER}"
export BBT_NOTIFY_TEMP_TIME="${NOTIFY_TEMP_REMINDER_TIME}"
export BBT_NOTIFY_FERTILE="${NOTIFY_FERTILE_WINDOW}"
export BBT_NOTIFY_PERIOD="${NOTIFY_PERIOD_PREDICTION}"
export BBT_NOTIFY_OVULATION="${NOTIFY_OVULATION_DETECTED}"
# Encryption key: use env var if set, otherwise read persisted key, otherwise generate
if [ -z "${BYRD_SECRET_KEY}" ]; then
    if [ -f /data/.byrd_key ]; then
        export BYRD_SECRET_KEY="$(cat /data/.byrd_key)"
    else
        export BYRD_SECRET_KEY="$(openssl rand -hex 32)"
        echo "${BYRD_SECRET_KEY}" > /data/.byrd_key
        bashio::log.info "Generated new encryption key in /data/.byrd_key"
    fi
fi
export BYRD_DATABASE_URL="sqlite+aiosqlite:///data/byrd_health.db"

bashio::log.info "Starting Byrd Health Fertility Tracker v2.0.0"
bashio::log.info "  Temperature unit : ${TEMP_UNIT}"
bashio::log.info "  Poll interval    : ${POLL_INTERVAL} min"
if [ -n "${HA_SENSOR_ENTITY}" ]; then
    bashio::log.info "  HA sensor entity : ${HA_SENSOR_ENTITY}"
fi

# Run database migrations
export DATABASE_URL="${BYRD_DATABASE_URL}"
cd /app/packages/data_service
python -m alembic upgrade head || bashio::log.warning "Database migration failed, continuing..."
cd /

# Start the FastAPI app with uvicorn
exec uvicorn web_api.app:create_app --factory --host 0.0.0.0 --port 8000
