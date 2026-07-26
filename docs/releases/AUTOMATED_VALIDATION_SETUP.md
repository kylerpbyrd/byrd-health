# Automated VS-1 Validation — Setup Guide

> **Audience:** Release Engineer
> **Requires:** Node.js 20+, running HA instance with Byrd Health add-on installed
> **Script:** `tools/validate-vs1.ts`

---

## Prerequisites

1. **Node.js 20+** installed on the machine running the tests
2. **Home Assistant** instance running, reachable from the test machine
3. **Byrd Health Fertility Tracker** add-on installed and running on HA
4. The add-on's Web UI is accessible via Ingress (OPEN WEB UI works in browser)

---

## Getting the Ingress URL

1. In Home Assistant, navigate to **Settings → Add-ons → Byrd Health Fertility Tracker**
2. Click **OPEN WEB UI**
3. Copy the full URL from your browser's address bar. It will look like:

   ```
   http://192.168.1.44:8123/api/hassio_ingress/hIMAL9ekLW2VPDZSV3Pf_F-7hYvNuALxPdihfAcCQ24/
   ```

   The token changes each time the add-on restarts. You must use the current token.

---

## Installing Dependencies

From the repository root:

```bash
npm install playwright @playwright/test
npx playwright install chromium
```

If you only need API checks and no browser UI checks, skip `npx playwright install chromium`.

---

## Running the Validation

### Quick run (headless browser, console output)

```bash
# PowerShell
$env:BYRD_INGRESS_URL="http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/"
npx playwright test tools/validate-vs1.ts

# Bash / WSL
BYRD_INGRESS_URL="http://192.168.1.44:8123/api/hassio_ingress/<TOKEN>/" \
  npx playwright test tools/validate-vs1.ts
```

Replace `<TOKEN>` with the actual token from your ingress URL.

### Run with headed browser (see what's happening)

```bash
BYRD_INGRESS_URL="http://..." npx playwright test tools/validate-vs1.ts --headed
```

### Run a single check

```bash
BYRD_INGRESS_URL="http://..." npx playwright test tools/validate-vs1.ts -g "C3"
```

---

## Expected Output

All checks pass:

```
Running X tests using 1 worker

PASS: C1 — Dashboard loads via ingress
PASS: C2 — Dashboard page loaded
PASS: C2 — Calendar page loaded
PASS: C2 — Log Entry page loaded
PASS: C2 — History page loaded
PASS: C2 — Profiles page loaded
PASS: C2 — Settings page loaded
PASS: C3 — API health check returns ok
PASS: C4 — Profiles endpoint: 2 profile(s)
PASS: C5 — Created test profile: <UUID>
PASS: C6 — Profile activated
PASS: C7 — Temperature entry submitted
PASS: C8 — Insights returned (phase: unknown)
PASS: C9 — Cleanup: deleted profile <UUID>

X passed (Xs)
```

If any check fails, you'll see `FAIL: <check> — <reason>` with details, and the test run will exit with a non-zero code.

---

## Checks Performed

| # | Check | Type |
|---|-------|------|
| C1 | Dashboard loads via Ingress | Browser |
| C2 | All 6 nav pages render without errors or white screens | Browser |
| C3 | `GET /api/health` returns `{"status":"ok"}` | API |
| C4 | `GET /api/v1/fertility/profiles/` returns valid JSON array | API |
| C5 | `POST /api/v1/fertility/profiles/` with `{name:"VS1-Test"}` returns 201 | API |
| C6 | `POST /api/v1/fertility/profiles/{id}/activate` returns 200 | API |
| C7 | `POST /api/v1/fertility/entries/` with temperature data returns 201 | API |
| C8 | `GET /api/v1/fertility/insights/` returns valid insights object | API |
| C9 | Cleanup — delete the VS1-Test profile (best-effort) | API |

**C9 cleanup note:** Profile deletion requires (a) at least one other profile exists and (b) the VS1-Test profile is not the active one. The script handles activation switching automatically. If no other profiles exist, delete will fail and a warning is logged — the test profile must be removed manually through the UI.

---

## Running via MCP Playwright Server

If you have set up an MCP Playwright server (a separate Playwright instance accessible over MCP protocol), you can point the test at it by setting the `PW_SERVER_URL` environment variable:

```bash
PW_SERVER_URL="ws://localhost:4444" BYRD_INGRESS_URL="http://..." \
  npx playwright test tools/validate-vs1.ts
```

See your MCP Playwright server documentation for setup details.

---

## Troubleshooting

| Symptom | Likely Cause |
|---------|-------------|
| All C1-C2 browser tests time out | BYRD_INGRESS_URL is wrong, HA is unreachable, or the add-on is not running |
| C3-C9 API tests fail but C1 passes | Token in URL is expired (add-on restarted) — get a fresh URL |
| C7 fails with 422 | Profile ID mismatch or missing `profile_id` in request body |
| C9 cleanup fails | No other profiles exist to activate before delete — clean up manually |
| `Error: BYRD_INGRESS_URL env var is required` | You forgot to set the environment variable |
