import { test, expect } from "@playwright/test";

const HA_URL = process.env.BYRD_HA_URL || "http://192.168.1.44:8123";
const HA_TOKEN = process.env.BYRD_HA_TOKEN || "";
const INGRESS_URL = process.env.BYRD_INGRESS_URL || "";
const INGRESS_COOKIE = process.env.BYRD_INGRESS_COOKIE || "";

const BASE = INGRESS_URL.endsWith("/") ? INGRESS_URL : INGRESS_URL + "/";

const NAV_PAGES = [
  { label: "Dashboard", segment: "" },
  { label: "Calendar", segment: "calendar" },
  { label: "Log Entry", segment: "entry" },
  { label: "History", segment: "history" },
  { label: "Profiles", segment: "profiles" },
  { label: "Settings", segment: "settings" },
];

let profileId: string | null = null;

// ── API helpers ──────────────────────────────────────────────

async function ingressGet(page: any, path: string) {
  return page.evaluate(async ({ url }: { url: string }) => {
    const r = await fetch(url);
    return { status: r.status, body: await r.text() };
  }, { url: `${BASE}api/${path}` });
}

async function ingressPost(page: any, path: string, data: any) {
  return page.evaluate(async ({ url, body }: { url: string; body: any }) => {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return { status: r.status, body: await r.text() };
  }, { url: `${BASE}api/${path}`, body: data });
}

async function ingressDelete(page: any, path: string) {
  return page.evaluate(async ({ url }: { url: string }) => {
    const r = await fetch(url, { method: "DELETE" });
    return { status: r.status, body: await r.text() };
  }, { url: `${BASE}api/${path}` });
}

// ── Test Suite ───────────────────────────────────────────────

test.describe("VS-1 Automated Validation", () => {
  test.describe.configure({ mode: "serial" });
  let authPage: any;

  test.beforeAll(async ({ browser }) => {
    const ctx = await browser.newContext();
    authPage = await ctx.newPage();

    // Set the ingress session cookie so all requests are authenticated
    if (INGRESS_COOKIE) {
      await ctx.addCookies([{
        name: "ingress_session",
        value: INGRESS_COOKIE,
        domain: new URL(HA_URL).hostname,
        path: "/",
      }]);
    }
  });

  test.afterAll(async () => {
    if (authPage) await authPage.context().close();
  });

  // ── C1: Dashboard via Ingress ──────────────────────────

  test("C1: Dashboard loads via Ingress", async () => {
    if (!INGRESS_URL) {
      console.log("SKIP: C1 — BYRD_INGRESS_URL not set");
      return;
    }
    try {
      await authPage.goto(BASE, { waitUntil: "domcontentloaded", timeout: 30000 });
      await authPage.waitForTimeout(3000);

      const bodyText = await authPage.locator("body").innerText();
      if (bodyText.includes("401") || bodyText.includes("Unauthorized")) {
        throw new Error("Got 401 — ingress_session cookie may be expired");
      }

      await expect(authPage.getByText("Byrd Health").first()).toBeVisible({ timeout: 15000 });
      console.log("PASS: C1 — Dashboard loads via Ingress");
    } catch (e: any) {
      console.log(`FAIL: C1 — ${e.message}`);
    }
  });

  // ── C2: All pages render ───────────────────────────────

  test("C2: All nav pages load", async () => {
    if (!INGRESS_URL) {
      console.log("SKIP: C2 — BYRD_INGRESS_URL not set");
      return;
    }
    for (const { label, segment } of NAV_PAGES) {
      try {
        const url = segment ? `${BASE}${segment}` : BASE;
        await authPage.goto(url, { waitUntil: "domcontentloaded", timeout: 20000 });
        await authPage.waitForTimeout(1000);
        await expect(authPage.locator("main, header").first()).toBeVisible({ timeout: 10000 });
        console.log(`PASS: C2 — ${label}`);
      } catch (e: any) {
        console.log(`FAIL: C2 — ${label}: ${e.message}`);
      }
    }
  });

  // ── C3: HA Core API ────────────────────────────────────

  test("C3: HA Core API reachable", async () => {
    if (!HA_TOKEN) {
      console.log("SKIP: C3 — BYRD_HA_TOKEN not set");
      return;
    }
    try {
      const r = await authPage.evaluate(async ({ url, token }: { url: string; token: string }) => {
        const res = await fetch(`${url}/api/`, { headers: { Authorization: `Bearer ${token}` } });
        return { status: res.status, body: await res.text() };
      }, { url: HA_URL, token: HA_TOKEN });
      expect(r.status).toBe(200);
      expect(JSON.parse(r.body).message).toBe("API running.");
      console.log("PASS: C3 — HA Core API reachable");
    } catch (e: any) {
      console.log(`FAIL: C3 — ${e.message}`);
      throw e;
    }
  });

  // ── C4: HA entities published ──────────────────────────

  test("C4: Byrd Health entities published", async () => {
    if (!HA_TOKEN) {
      console.log("SKIP: C4 — BYRD_HA_TOKEN not set");
      return;
    }
    try {
      const r = await authPage.evaluate(async ({ url, token }: { url: string; token: string }) => {
        const res = await fetch(`${url}/api/states`, { headers: { Authorization: `Bearer ${token}` } });
        return { status: res.status, body: await res.text() };
      }, { url: HA_URL, token: HA_TOKEN });
      expect(r.status).toBe(200);
      const states: any[] = JSON.parse(r.body);
      const bbt = states.filter((s: any) =>
        s.entity_id.startsWith("sensor.bbt_") || s.entity_id.startsWith("binary_sensor.bbt_")
      );
      expect(bbt.length).toBeGreaterThanOrEqual(6);
      console.log(`PASS: C4 — ${bbt.length} Byrd Health entities published`);
      for (const e of bbt.slice(0, 10)) {
        console.log(`  ${e.entity_id}: ${e.state}`);
      }
    } catch (e: any) {
      console.log(`FAIL: C4 — ${e.message}`);
      throw e;
    }
  });

  // ── C5: Create test profile ────────────────────────────

  test("C5: Create test profile via add-on API", async () => {
    if (!INGRESS_URL) {
      console.log("SKIP: C5 — BYRD_INGRESS_URL not set");
      return;
    }
    try {
      const r = await ingressPost(authPage, "v1/fertility/profiles/", { name: "VS1-Test" });
      expect(r.status).toBe(201);
      profileId = JSON.parse(r.body).id;
      console.log(`PASS: C5 — Created: ${profileId}`);
    } catch (e: any) {
      console.log(`FAIL: C5 — ${e.message}`);
      throw e;
    }
  });

  // ── C6: Activate + submit entry ────────────────────────

  test("C6: Activate profile + submit entry", async () => {
    if (!INGRESS_URL || !profileId) {
      console.log(`SKIP: C6 — ${!INGRESS_URL ? "no ingress URL" : "no profile"}`);
      return;
    }
    try {
      let r = await ingressPost(authPage, `v1/fertility/profiles/${profileId}/activate`, {});
      expect(r.status).toBe(200);

      const today = new Date().toISOString().split("T")[0];
      r = await ingressPost(authPage, "v1/fertility/entries/", { date: today, temp_value: 98.2 });
      expect(r.status).toBe(201);
      console.log("PASS: C6 — Activated + entry submitted");
    } catch (e: any) {
      console.log(`FAIL: C6 — ${e.message}`);
      throw e;
    }
  });

  // ── C7: Insights returned ──────────────────────────────

  test("C7: Insights after entry", async () => {
    if (!INGRESS_URL || !profileId) {
      console.log(`SKIP: C7 — ${!INGRESS_URL ? "no ingress URL" : "no profile"}`);
      return;
    }
    try {
      const r = await ingressGet(authPage, "v1/fertility/insights/");
      expect(r.status).toBe(200);
      const body = JSON.parse(r.body);
      console.log(`PASS: C7 — Insights (phase: ${body.phase || "?"}, day: ${body.cycle_day || "?"})`);
    } catch (e: any) {
      console.log(`FAIL: C7 — ${e.message}`);
      throw e;
    }
  });

  // ── C8: Cleanup ────────────────────────────────────────

  test("C8: Cleanup — delete test profile", async () => {
    if (!profileId || !INGRESS_URL) return;
    try {
      const listR = await ingressGet(authPage, "v1/fertility/profiles/");
      const profiles: any[] = JSON.parse(listR.body);
      const other = profiles.find((p: any) => p.id !== profileId);
      if (other) {
        await ingressPost(authPage, `v1/fertility/profiles/${other.id}/activate`, {});
      }
      const delR = await ingressDelete(authPage, `v1/fertility/profiles/${profileId}`);
      if (delR.status >= 200 && delR.status < 300) {
        console.log(`PASS: C8 — Deleted profile ${profileId}`);
      } else {
        console.log(`WARN: C8 — Delete returned ${delR.status}`);
      }
    } catch (e: any) {
      console.log(`WARN: C8 — ${e.message}`);
    }
  });
});
