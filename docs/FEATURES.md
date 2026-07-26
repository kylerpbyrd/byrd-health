# Feature Guide — Sympto-Thermal Method

## Temperature Tracking

Record your basal body temperature (BBT) every morning before getting out of bed.
Consistent timing improves accuracy. The app supports both Fahrenheit and Celsius.

## Cycle Phases

- **Menstruation** — Cycle days 1-5 (typically). Period tracking.
- **Pre-Ovulatory** — Follicular phase. Temps are lower.
- **Fertile Window** — Days leading to ovulation. Highest conception probability.
- **Ovulation** — Confirmed after 3 consecutive elevated temperatures.
- **Luteal Phase** — Post-ovulation. Temps stay elevated until next period.

## Signs You Can Track

- **Cervical Mucus** — Dry, Sticky, Creamy, Watery, Egg-white
- **OPK Results** — Negative, Positive, Peak
- **Menstrual Flow** — Spotting, Light, Medium, Heavy
- **Symptoms** — Cramps, headache, bloating, fatigue, etc.

## Charts

The BBT chart shows your temperature curve with:
- Coverline (horizontal line indicating temperature shift threshold)
- Fertile window shading
- Ovulation day marker
- Discarded readings (shown in gray)

## Home Assistant Integration

9 entities per profile:

| Entity | Type | Description |
|--------|------|-------------|
| sensor.bbt_{slug}_cycle_day | sensor | Current cycle day |
| sensor.bbt_{slug}_cycle_phase | sensor | Current phase |
| sensor.bbt_{slug}_last_temp | sensor | Most recent temperature |
| binary_sensor.bbt_{slug}_fertile_window | binary_sensor | In fertile window |
| binary_sensor.bbt_{slug}_ovulation_confirmed | binary_sensor | Ovulation confirmed |
| sensor.bbt_{slug}_ovulation_date | sensor | Estimated ovulation date |
| sensor.bbt_{slug}_next_period_date | sensor | Predicted next period |
| sensor.bbt_{slug}_luteal_length | sensor | Luteal phase length |
| sensor.bbt_{slug}_avg_cycle_length | sensor | Average cycle length |
