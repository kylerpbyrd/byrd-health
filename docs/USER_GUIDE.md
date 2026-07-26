# Byrd Health — User Guide

## Installation

1. Add the Byrd Health repository to your Home Assistant Add-on Store
2. Install the "Byrd Health — Fertility Tracker" add-on
3. Configure options (temperature unit, sensor entity)
4. Start the add-on
5. Open the Web UI from the sidebar

## First-Time Setup

1. Create a profile (name + temperature unit F/C)
2. Log your first temperature reading
3. The dashboard will show your cycle day, phase, and predictions

## Features

- Basal body temperature tracking
- Cycle phase detection (menstrual, fertile, luteal)
- Ovulation detection and confirmation
- Fertile window prediction
- Cycle history and charts
- Multi-profile support
- Home Assistant entity publishing (9 sensors per profile)
- Data export (JSON)
- Privacy-first: all data stored locally, encrypted at rest

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| temp_unit | F | Temperature display unit (F or C) |
| ha_sensor_entity | (none) | HA entity ID for automatic temperature reading |
| poll_interval_minutes | 15 | How often to poll the HA sensor |

## Data & Privacy

All health data is stored locally in an encrypted SQLite database.
Data never leaves your Home Assistant device.
You can export your data at any time from Settings.
