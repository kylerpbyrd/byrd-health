# Repair Plan — White Page on HA Add-on Load

| Key | Value |
|---|---|
| **Based on** | `docs/DEBUG_REPORT.md` |
| **Date** | 2026-07-24 |

---

## Fix Order

Fixes are listed in dependency order. Fix 1 must be applied before Fix 2 can be verified.

---

## Fix 1: Inject Ingress Path as JavaScript Variable + Robust Base Tag

**Why:** The base tag injection uses `str.replace("<head>", ...)` which fails because the built HTML has indented `<head>` (two leading spaces). Vite preserves source HTML formatting in production builds. Without the base tag, all asset URLs resolve to HA root instead of the Ingress path.

Additionally, React Router needs the Ingress path as `basename` — this must be passed from the server to the client at runtime.

**Risk:** Low — changes only the HTML-serving logic, not the SPA itself.

**Files affected:**
- `packages/web_api/src/web_api/app.py` (lines 104-108)

**Change:** Replace the naive `str.replace()` with regex-based replacement that handles indentation, and inject a `window.__INGRESS_PATH__` global so the React app can read the Ingress path:

```python
import re

@app.get("/{full_path:path}")
async def serve_spa(full_path: str, request: Request) -> Response:
    if full_path.startswith(("api/", "docs", "openapi.json")):
        raise HTTPException(status_code=404)

    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_path):
        raise HTTPException(status_code=404)

    html = open(index_path).read()
    script_name = request.scope.get("script_name", "")

    # Inject base tag and ingress path global (handles indented <head>)
    if script_name:
        ingress_script = (
            f'<base href="{script_name}/">\n'
            f'<script>window.__INGRESS_PATH__ = "{script_name}";</script>'
        )
        html = re.sub(r"(\s*)<head>", rf"\1<head>\n\1  {ingress_script}", html)

    return HTMLResponse(content=html)
```

**Expected outcome:** Built HTML receives `<base>` tag and `window.__INGRESS_PATH__` global variable regardless of indentation.

---

## Fix 2: Pass basename to BrowserRouter

**Why:** `BrowserRouter` without `basename` cannot match routes when the browser URL includes the Ingress path prefix. The router reads `window.location.pathname` which is `/hassio/ingress/byrd_health_fertility/dashboard` but routes are defined as `/dashboard`. Without basename, React Router renders nothing — white page even after assets load.

For client-side navigation, `history.pushState("/history")` would push a URL without the Ingress prefix, navigating to the wrong domain.

**Risk:** Low — only changes the React Router initialization. Routes remain identical.

**Files affected:**
- `frontend/src/App.tsx` (line 15)

**Change:** Read `window.__INGRESS_PATH__` (injected by Fix 1) and pass it as `basename`:

```tsx
// At module level, read the ingress path from the global injected by the server
const BASENAME = (window as any).__INGRESS_PATH__ || "/";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename={BASENAME}>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/entry" element={<EntryPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/history/:cycleId" element={<CycleDetailPage />} />
            <Route path="/profiles" element={<ProfilesPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

**Expected outcome:** React Router correctly matches routes regardless of Ingress path. Client-side navigation stays within the Ingress prefix.

---

## Fix 3: Align DATABASE_URL Environment Variable

**Why:** `config.py` uses env prefix `BYRD_` (so it reads `BYRD_DATABASE_URL`) but `run.sh` exports `DATABASE_URL` (no prefix). The setting falls back to default `sqlite+aiosqlite:///./byrd_health.db` which creates the database in the container's ephemeral root filesystem instead of the persistent `/data` volume. All user data is lost on container restart.

**Risk:** Low — simple naming fix.

**Files affected:**
- `run.sh:15` — change export name

**Change — Option A (preferred, minimal):**
```bash
# run.sh line 15 — use the BYRD_ prefix
export BYRD_DATABASE_URL="sqlite+aiosqlite:///data/byrd_health.db"
```

**Change — Option B (if prefix is undesirable):**
Remove the prefix from `config.py`:
```python
model_config = {"extra": "ignore"}  # Remove "env_prefix": "BYRD_"
```

**Expected outcome:** Database is created at `/data/byrd_health.db` which persists across container restarts.

---

## 4. Verification Steps

After all fixes are applied and the add-on is rebuilt:

1. **Check server logs** — confirm `Uvicorn running on http://0.0.0.0:8000`
2. **Open Web UI** — page should render with purple Byrd Health UI
3. **Check browser dev tools Network tab** — verify asset requests return 200 (not 404)
4. **Check browser dev tools Console** — no JavaScript errors about missing modules
5. **Navigate to different pages** — `/history`, `/entry`, etc. should render
6. **Check `/data/byrd_health.db` exists** — verify database is in persistent storage
7. **Create an entry** — verify data persists across add-on restart

---

## 5. Files Summary

| # | File | Change | Risk |
|---|---|---|---|
| 1 | `packages/web_api/src/web_api/app.py:104-108` | Regex-based base tag injection + `__INGRESS_PATH__` global | Low |
| 2 | `frontend/src/App.tsx:1,15` | Read `__INGRESS_PATH__` and pass to `BrowserRouter basename` | Low |
| 3 | `run.sh:15` | Change `DATABASE_URL` → `BYRD_DATABASE_URL` | Low |

---

## 6. Implementation Results

| Fix | Status | File | Change |
|---|---|---|---|
| Fix 1 | ✅ Implemented | `app.py:107` | `str.replace` → `re.sub` with whitespace capture. Injects `<base>` and `window.__INGRESS_PATH__`. 42/42 tests pass. |
| Fix 2 | ✅ Implemented | `App.tsx:15-23` | `BrowserRouter basename={BASENAME}` from `window.__INGRESS_PATH__`. TypeScript global declared. `npm build` succeeds, 21/21 tests pass. |
| Fix 3 | ✅ Implemented | `run.sh:15` | `DATABASE_URL` → `BYRD_DATABASE_URL`. Matches config prefix `BYRD_`. |

**Backend tests:** 159/160 pass (1 pre-existing `test_delete_profile` failure — profile ownership guard, unrelated).  
**Frontend tests:** 21/21 pass.
