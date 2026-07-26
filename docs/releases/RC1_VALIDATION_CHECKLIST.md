# RC1 Validation Checklist — Session 1
## Startup, Ingress, Core UI, API, Entities

> **Release Engineer:** Independent certification
> **Date:** 2026-07-26
> **HA Instance:** 192.168.1.44:8123
> **Status:** READY — AWAITING USER EVIDENCE

---

## Prerequisites

Before beginning, ensure:

- [ ] HA instance at `192.168.1.44:8123` is running and accessible
- [ ] You can access HA Supervisor (Settings → Add-ons → Add-on Store)
- [ ] You have terminal access to the HA host (for `docker logs`)
- [ ] The repository is up-to-date: `git pull origin main`
- [ ] No prior `byrd_health_fertility` add-on is installed (or you're OK with a fresh install)

---

## Step 1: Rebuild the Docker Image

### 1.1 Pull latest code and rebuild

```bash
cd /path/to/byrd-health
git pull origin main
docker build -t byrd-health:rc1 .
```

**Expected output:**
- 15 Dockerfile steps complete successfully
- Frontend build: TypeScript compilation passes, Vite produces output chunks
- Final image tagged as `byrd-health:rc1`
- No errors at any step

**Evidence to capture:**
- Screenshot of the final `docker build` output showing "Successfully tagged byrd-health:rc1"

PS C:\Users\kyler\OneDrive\Documents\Code\projects\byrd-health> docker build -t byrd-health:rc1 .
[+] Building 80.2s (21/21) FINISHED                                                                                                                                                                                                                                              docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                                             0.1s
 => => transferring dockerfile: 1.26kB                                                                                                                                                                                                                                                           0.0s
 => [internal] load metadata for ghcr.io/home-assistant/base:latest                                                                                                                                                                                                                              1.2s
 => [internal] load .dockerignore                                                                                                                                                                                                                                                                0.1s
 => => transferring context: 2B                                                                                                                                                                                                                                                                  0.0s
 => [ 1/17] FROM ghcr.io/home-assistant/base:latest@sha256:94ff231402a5e7ad2a82e261ad5fa4ffae7d7bb095c3febb2edbdf309c9b6aca                                                                                                                                                                      0.2s
 => => resolve ghcr.io/home-assistant/base:latest@sha256:94ff231402a5e7ad2a82e261ad5fa4ffae7d7bb095c3febb2edbdf309c9b6aca                                                                                                                                                                        0.2s
 => [internal] load build context                                                                                                                                                                                                                                                                0.8s
 => => transferring context: 1.41MB                                                                                                                                                                                                                                                              0.6s
 => CACHED [ 2/17] RUN apk add --no-cache python3 py3-pip nodejs npm                                                                                                                                                                                                                             0.0s
 => CACHED [ 3/17] RUN python3 -m venv /opt/venv                                                                                                                                                                                                                                                 0.0s
 => [ 4/17] COPY packages/ /app/packages/                                                                                                                                                                                                                                                        0.5s
 => [ 5/17] RUN pip install --no-cache-dir /app/packages/fertility_engine                                                                                                                                                                                                                        7.0s
 => [ 6/17] RUN pip install --no-cache-dir /app/packages/data_service                                                                                                                                                                                                                           10.1s 
 => [ 7/17] RUN pip install --no-cache-dir /app/packages/ha_bridge                                                                                                                                                                                                                               6.4s 
 => [ 8/17] RUN pip install --no-cache-dir /app/packages/device_adapters                                                                                                                                                                                                                         3.4s 
 => [ 9/17] RUN pip install --no-cache-dir /app/packages/web_api                                                                                                                                                                                                                                12.5s 
 => [10/17] COPY frontend/ /app/frontend/                                                                                                                                                                                                                                                        4.6s 
 => [11/17] WORKDIR /app/frontend                                                                                                                                                                                                                                                                0.7s 
 => [12/17] RUN npm install && npm run build                                                                                                                                                                                                                                                     9.3s 
 => [13/17] RUN mkdir -p /app/static && cp -r /app/frontend/dist/* /app/static/                                                                                                                                                                                                                  1.1s 
 => [14/17] COPY packages/ha_bridge/src/ha_bridge/card/ha-card.js /app/static/ha-card.js                                                                                                                                                                                                         0.7s 
 => [15/17] COPY run.sh /run.sh                                                                                                                                                                                                                                                                  0.6s 
 => [16/17] RUN chmod a+x /run.sh                                                                                                                                                                                                                                                                1.6s 
 => exporting to image                                                                                                                                                                                                                                                                          17.4s 
 => => exporting layers                                                                                                                                                                                                                                                                         10.8s 
 => => exporting manifest sha256:2390f1dac9ce46c3eb279238b6e35093cdd13b4938a3e739217787a34d195f2b                                                                                                                                                                                                0.2s
 => => exporting config sha256:d9c88b9988efee8a0572fbffd5392d686687597df09bdb7e0515adc40fd6ad08                                                                                                                                                                                                  0.2s
 => => exporting attestation manifest sha256:e59bbbb31d8baf61364780da9d5a462c52785d725a6f358e209b1288a738eb9b                                                                                                                                                                                    0.4s
 => => exporting manifest list sha256:1907c4cddb746a92aa0ab2ba53377c6f10da8c783be601bb9da326c09f64c7c6                                                                                                                                                                                           0.2s
 => => naming to docker.io/library/byrd-health:rc1                                                                                                                                                                                                                                               0.0s
 => => unpacking to docker.io/library/byrd-health:rc1   

### 1.2 Verify image exists

```bash
docker images byrd-health:rc1
```

**Expected:** Image listed with size and creation time.

PS C:\Users\kyler\OneDrive\Documents\Code\projects\byrd-health> docker images byrd-health:rc1
>> 
                                                                                                                                                                                                                                                                                  i Info →   U  In Use
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
byrd-health:rc1   1907c4cddb74        637MB          135MB     

---

## Step 2: Install on Home Assistant

### 2.1 Load the add-on

If using a local add-on repository:
1. In HA, go to **Settings → Add-ons → Add-on Store**
2. Click the three-dot menu → **Repositories**
3. Add your local repository URL
4. Find "Byrd Health — Fertility Tracker" in the store
5. Click it, then click **INSTALL**

**Evidence to capture:**
- Screenshot of the add-on appearing in the store
- Screenshot of the installation completing (green checkmark)
 
 Appears in store and installs.

### 2.2 Review Configuration

Before starting, go to the **Configuration** tab of the add-on.

**Default values should show:**
```
temp_unit: F
ha_sensor_entity: ""
poll_interval_minutes: 15
notify_temp_reminder: true
notify_temp_reminder_time: "07:00"
notify_fertile_window: true
notify_period_prediction: true
notify_ovulation_detected: true
```

**Evidence to capture:**
- Screenshot of the Configuration tab with default values

  all default values and options present.
---

## Step 3: Start the Add-on

### 3.1 Click START

Go to the **Info** tab, click **START**.

### 3.2 Watch the logs

Click the **Log** tab immediately after starting.

**Expected logs (in order):**

```
[s6-init] making user provided files available at /var/run/s6/etc...
[s6-init] ensuring user provided files have correct perms...
[cont-init.d] executing container initialization scripts...
[cont-init.d] done.
[services.d] starting services
[services.d] done.
INFO: Starting Byrd Health Fertility Tracker v2.0.0
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**If encryption key is being generated for the first time:**
- No explicit log line, but check that no error about missing key appears

**If profiles exist and have cycle data:**
- Log lines showing entity publishing (may appear as debug or info)

**Evidence to capture:**
- **Full log output** — scroll to capture the entire startup sequence
- Screenshot of the log tab showing all startup messages
- **IMPORTANT:** Note any ERROR or WARNING lines

### 3.3 Verify add-on status

The add-on should show a **green circle** with "Running" status.

---

## Step 4: Open the Web UI via Ingress

### 4.1 Click "OPEN WEB UI"

From the add-on Info tab, click **OPEN WEB UI**.

Alternatively, find "Fertility Tracker" in the HA sidebar and click it.

**Expected:**
- The Byrd Health dashboard loads
- URL shows something like: `http://192.168.1.44:8123/api/hassio_ingress/<token>/`
- The purple "Byrd Health" header with the Activity icon
- Navigation bar with: Dashboard, Calendar, Log Entry, History, Profiles, Settings

**Evidence to capture:**
- Screenshot of the full dashboard page
- The browser URL bar (showing the ingress path)

### 4.2 Check browser console

Open browser DevTools (F12) → Console tab.

**Expected:** No errors. Look specifically for:
- `window.__INGRESS_PATH__` value
- Any 404 errors on asset loading
- Any React errors or warnings

**Evidence to capture:**
- Screenshot of the Console tab (filter to "All levels")
- If errors present, screenshot each one expanded

---

## Step 5: First-Run Dashboard

If no profiles or data exist yet:

### 5.1 Dashboard empty state

**Expected:**
- A page with a thermometer icon
- "No data yet" or similar empty-state message
- "Profile Required" or prompt to create one

**Evidence to capture:**
- Screenshot of the empty state

### 5.2 Navigate to Profiles

Click **Profiles** in the nav bar.

**Expected:**
- "No profiles yet" message with a users icon
- An input field to create a new profile
- "Create" button

### 5.3 Create a profile

1. Type a name (e.g., "Test User")
2. Click **Create**

**Expected:**
- Profile appears in the list
- Shows `°F / standard` as defaults
- "Active" badge appears next to it

**Evidence to capture:**
- Screenshot of the profile list after creation

### 5.4 Return to Dashboard

Click **Dashboard** in the nav bar.

**Expected:**
- Phase banner appears (likely "Unknown" phase since no data)
- Stat tiles show zeros/dashes
- Chart area shows "No data yet" or empty chart
- "Log Today's Entry" button visible
- "View Cycle History" button visible

**Evidence to capture:**
- Screenshot of the dashboard with the new profile active

---

## Step 6: Verify All Pages Load

Click each navigation item and verify the page renders without errors.

### 6.1 Dashboard (`/`)
- Already verified — use screenshot from Step 5.4

### 6.2 Calendar (`/calendar`)
- Month grid should appear with day headers (S M T W Th F S)
- Today should be highlighted
- Month navigation arrows visible
- "Today" button visible
- Legend at bottom with color swatches

**Evidence to capture:**
- Screenshot of the Calendar page

### 6.3 Log Entry (`/entry`)
- Form should appear with:
  - Date field (pre-filled with today)
  - Large temperature input
  - Menstrual Flow radio buttons
  - Cervical Mucus radio buttons
  - OPK radio buttons
  - Collapsible "Cervical Position" section
  - Symptoms checkboxes
  - Notes textarea
  - "First day of period" toggle
  - Submit button

**Evidence to capture:**
- Screenshot of the Entry page (full form)

### 6.4 History (`/history`)
- "Cycle History" card with table
- Should show at least one cycle row (auto-created on profile creation)
- Table columns: Cycle #, Start Date, Length, Ovulation, Luteal, Status
- Status should show "Active" badge

**Evidence to capture:**
- Screenshot of the History page

### 6.5 Profiles (`/profiles`)
- Already verified in Step 5.2-5.3

### 6.6 Settings (`/settings`)
- Temperature Unit section with °F / °C toggle
- Interpretation Method dropdown (Standard / Conservative)
- Data Export button
- "Start New Cycle" card in danger zone
- "Save Settings" button at bottom

**Evidence to capture:**
- Screenshot of the Settings page

---

## Step 7: Verify API Endpoints

### 7.1 Discover the Ingress Token

Find the ingress token. It's visible in the browser URL bar from Step 4:
```
http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/
```

Copy the full `<TOKEN>` value.

### 7.2 Health Check

Run from any machine that can reach the HA instance:

```bash
curl -s http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/api/health
```

**Expected response:**
```json
{"status": "ok"}
```

**Evidence to capture:**
- Terminal output showing the curl command and response

### 7.3 List Profiles

```bash
curl -s http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/api/v1/fertility/profiles/
```

**Expected response:**
```json
[{
  "id": "<UUID>",
  "name": "Test User",
  "slug": "test_user",
  "temp_unit": "F",
  "interpretation_method": "standard",
  "is_active": true,
  "created_at": "<ISO8601>"
}]
```

**Evidence to capture:**
- Terminal output with the full JSON response

### 7.4 Get Insights

```bash
curl -s http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/api/v1/fertility/insights/
```

**Expected response** (with no data):
```json
{
  "cycle_day": 1,
  "phase": "unknown",
  "coverline": null,
  "ovulation_date": null,
  "ovulation_confirmed": false,
  ...
  "warnings": []
}
```

**Evidence to capture:**
- Terminal output with the full JSON response

### 7.5 OpenAPI Docs

Navigate in browser to:
```
http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/docs
```

**Expected:**
- Swagger UI loads
- Shows "Byrd Health API" title
- All endpoints listed under profiles, entries, cycles, insights, devices, calendar tags
- "Authorize" button available for token input

**Evidence to capture:**
- Screenshot of the Swagger UI page

---

## Step 8: Verify HA Entities

### 8.1 Open Developer Tools → States

In HA, go to **Developer Tools** → **STATES**.

### 8.2 Filter for Byrd entities

In the filter box, type: `bbt_`

**Expected entities** (for slug `test_user`):

| Entity ID | Expected State |
|-----------|---------------|
| `sensor.bbt_test_user_cycle_day` | `"1"` |
| `sensor.bbt_test_user_cycle_phase` | `"unknown"` (or `"menstruation"` if day 1) |
| `sensor.bbt_test_user_ovulation_date` | `"none"` |
| `sensor.bbt_test_user_next_period_date` | `"none"` |
| `binary_sensor.bbt_test_user_fertile_window` | `"off"` |
| `binary_sensor.bbt_test_user_ovulation_confirmed` | `"off"` |

**Conditional entities (may not appear if values are null):**
| Entity ID | Note |
|-----------|------|
| `sensor.bbt_test_user_last_temp` | Only if last_temp is not None |
| `sensor.bbt_test_user_luteal_length` | Only if luteal_length is not None |
| `sensor.bbt_test_user_avg_cycle_length` | Only if avg_cycle_length is not None |

**Evidence to capture:**
- **Screenshot of the States page** with `bbt_` filter applied, showing all entities
- Expand each entity and screenshot its attributes (or list them in text)

### 8.3 Verify entity attributes

For `sensor.bbt_test_user_cycle_day`, check attributes include:
- `friendly_name: "BBT Test User Cycle Day"`
- `unit_of_measurement: "days"`
- `icon: "mdi:calendar-today"`

**Evidence to capture:**
- Screenshot of the expanded entity showing all attributes

---

## Step 9: Collect Logs

### 9.1 Add-on logs (full startup)

From the HA Add-on Log tab, copy the **entire** log output from startup to current.

### 9.2 Docker logs (if accessible)

If you have terminal access to the HA host:

```bash
docker logs addon_local_byrd_health_fertility --tail 100
```

(Container name may vary — check with `docker ps | grep byrd`)

**Evidence to capture:**
- Full log output from either source

---

## PASS/FAIL Criteria — Session 1

### CRITICAL Gates (any FAIL → entire session FAILS)

| # | Criterion | PASS Condition |
|---|-----------|---------------|
| C1 | Docker build | `docker build` completes without errors |
| C2 | Add-on installs | HA Supervisor shows successful install |
| C3 | Add-on starts | Status shows green "Running" |
| C4 | No startup errors | Zero ERROR lines in logs |
| C5 | UI loads via Ingress | Dashboard renders when clicking OPEN WEB UI |
| C6 | API responds | Health check returns `{"status":"ok"}` |
| C7 | Entities published | At least 6 `bbt_*` entities visible in HA States |
| C8 | All 7 pages load | Each navigation item renders without errors or white screens |

### HIGH Gates (FAIL → note as deficiency but does not block session)

| # | Criterion | PASS Condition |
|---|-----------|---------------|
| H1 | Encryption key auto-generated | `/data/.byrd_key` exists OR no key error in logs |
| H2 | All API endpoints accessible | Profiles, insights, cycles endpoints return valid JSON |
| H3 | OpenAPI docs render | Swagger UI loads at `/docs` |
| H4 | Asset loading | No 404 errors in browser console for JS/CSS |
| H5 | Browser console clean | No React errors or unhandled exceptions |

---

## Evidence Package Checklist

When submitting Session 1 evidence, include:

- [ ] `01-docker-build.png` — Docker build success
- [ ] `02-addon-install.png` — Add-on installed in store
- [ ] `03-addon-config.png` — Configuration tab
- [ ] `04-startup-logs.txt` — Full log output from startup
- [ ] `05-addon-running.png` — Green "Running" status
- [ ] `06-dashboard.png` — Dashboard page via Ingress
- [ ] `07-browser-console.png` — DevTools console
- [ ] `08-calendar.png` — Calendar page
- [ ] `09-entry-form.png` — Entry form page
- [ ] `10-history.png` — History page
- [ ] `11-settings.png` — Settings page
- [ ] `12-api-health.txt` — curl health check output
- [ ] `13-api-profiles.txt` — curl profiles list output
- [ ] `14-api-insights.txt` — curl insights output
- [ ] `15-swagger-ui.png` — OpenAPI docs page
- [ ] `16-ha-entities.png` — HA States filtered to `bbt_`
- [ ] `17-ha-entity-detail.png` — Expanded entity showing attributes

---

## How to Submit Evidence

1. Collect all screenshots and log files listed above.
2. Provide them along with any notes about unexpected behavior.
3. The Release Engineer will analyze each item and produce a PASS/FAIL verdict.
4. If PASS: we advance to Validation Session 2.
5. If FAIL: the Release Engineer will identify remediation steps.

---

**Ready for user evidence. The release gate will not advance until this checklist is completed and verified.**
