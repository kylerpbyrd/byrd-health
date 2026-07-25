# Debug Report — White Page on HA Add-on Load

| Key | Value |
|---|---|
| **Symptom** | Web UI loads as white/blank page when accessed via HA Ingress |
| **Severity** | Critical — add-on UI completely unusable |
| **Date** | 2026-07-24 |

---

## 1. Symptoms

From the HA add-on logs (shared by user):
```
INFO: Started server process [80]
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: 172.30.32.2:59726 - "GET / HTTP/1.1" 200 OK
INFO: 172.30.32.2:37934 - "GET / HTTP/1.1" 200 OK
```

- **Uvicorn starts successfully** — no Python import errors after the `pydantic-settings` fix
- **GET / returns 200 OK** — the server is serving `index.html`
- **NO asset requests logged** — the browser never requests `/assets/*.js` or `/assets/*.css`
- **User sees white page** — HTML loads but JavaScript never executes

---

## 2. Root Causes

### Root Cause 1: Base Tag Injection Fails

**Severity:** Critical | **File:** `packages/web_api/src/web_api/app.py:107`

The IngressMiddleware correctly strips the HA Ingress path prefix and sets `script_name` in the ASGI scope. The `serve_spa` function attempts to inject a `<base>` tag into `index.html` so that absolute asset URLs resolve through the Ingress proxy.

**The bug:** The string replacement on line 107 uses an exact match that fails due to HTML indentation:

```python
# app.py line 107 — FAILS because source HTML has indented <head>
html = html.replace("<head>", f'<head><base href="{script_name}/">')
```

**Evidence — Source HTML** (`frontend/index.html` line 3):
```html
  <head>    ← Two leading spaces! Replace looks for "<head>" with no spaces
```

Vite preserves HTML structure in production builds (only replaces script tags). The built `index.html` retains the two-space indentation before `<head>`. The `str.replace()` call looks for the exact string `"<head>"` which does NOT match `"  <head>"`.

**Impact:**
1. No `<base>` tag is injected into the HTML
2. Asset references like `<script src="/assets/index-abc123.js">` remain absolute
3. Browser resolves `/assets/...` to the Home Assistant root domain (e.g., `https://homeassistant.local/assets/...`) instead of the Ingress path (`https://homeassistant.local/hassio/ingress/byrd_health_fertility/assets/...`)
4. Assets 404 on HA's main web server → JavaScript never loads → white page

---

### Root Cause 2: BrowserRouter Without basename

**Severity:** Critical | **File:** `frontend/src/App.tsx:15`

The React app uses `BrowserRouter` without a `basename` prop:

```tsx
// App.tsx line 15
<BrowserRouter>   ← No basename! Routes defined as "/", "/entry", etc.
```

**Impact — Even if Root Cause 1 is fixed (assets load):**

1. User accesses `https://homeassistant.local/hassio/ingress/byrd_health_fertility/`
2. IngressMiddleware strips prefix; server serves `index.html`
3. React Router reads `window.location.pathname` = `/hassio/ingress/byrd_health_fertility/`
4. Routes are defined as `/`, `/entry`, `/history` — none match the full Ingress path
5. React Router renders nothing → white page

**Additionally:**
- `<Link to="/history">` would navigate to `https://homeassistant.local/history` (wrong)
- `history.pushState()` operates on raw URLs unaffected by `<base>` tag

---

### Secondary Finding: Database URL Mismatch

**Severity:** Medium — causes data loss on restart | **Files:** `packages/web_api/src/web_api/config.py:9`, `run.sh:15`

The `Settings` class uses env prefix `BYRD_`:

```python
# config.py line 9
model_config = {"env_prefix": "BYRD_", "extra": "ignore"}
```

But `run.sh` exports the variable without the prefix:

```bash
# run.sh line 15
export DATABASE_URL="sqlite+aiosqlite:///data/byrd_health.db"
```

**Impact:**
- Pydantic Settings ignores `DATABASE_URL` (wrong prefix)
- Falls back to default: `sqlite+aiosqlite:///./byrd_health.db`
- Database is created at `/byrd_health.db` (container root) instead of `/data/byrd_health.db` (persistent volume)
- All data is lost on container restart

---

## 3. Evidence Summary

| # | Finding | File | Line(s) | Status |
|---|---|---|---|---|
| 1 | Base tag injection fails on indented HTML | `app.py` | 107 | Root Cause |
| 2 | BrowserRouter lacks basename | `App.tsx` | 15 | Root Cause |
| 3 | DATABASE_URL env prefix mismatch | `config.py` | 9 | Data Loss |
| 4 | No explicit JS MIME type | `app.py` | — | Not relevant (Starlette handles this) |

---

## 4. Log Evidence

From the user's HA add-on logs (last successful start):
```
[16:15:21] INFO: Starting Byrd Health Fertility Tracker v2.0.0
INFO:     Started server process [80]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     172.30.32.2:59726 - "GET / HTTP/1.1" 200 OK
INFO:     172.30.32.2:37934 - "GET / HTTP/1.1" 200 OK
```

Key observations:
- Server starts without errors — Python layer is healthy
- `GET /` returns 200 — HTML is being served
- **No subsequent requests for `/assets/*`** — browser never attempts to load JavaScript
- IP `172.30.32.2` is the HA Ingress proxy, confirming requests arrive through Ingress

---

## 5. Affected Files

| File | Issue | Fix Priority |
|---|---|---|
| `packages/web_api/src/web_api/app.py:107` | String replace fails on indented HTML | P0 |
| `frontend/src/App.tsx:15` | BrowserRouter without basename | P0 |
| `run.sh:15` + `config.py:9` | DATABASE_URL env prefix mismatch | P1 |
