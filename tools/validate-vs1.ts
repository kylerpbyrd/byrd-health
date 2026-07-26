import { test, expect } from "@playwright/test";

const RAW_URL = process.env.BYRD_INGRESS_URL;
if (!RAW_URL) throw new Error("BYRD_INGRESS_URL env var is required");
const BASE_URL = RAW_URL.endsWith("/") ? RAW_URL : RAW_URL + "/";
const API_BASE = `${BASE_URL}api/`;

const NAV_PAGES = [
  { label: "Dashboard", segment: "" },
  { label: "Calendar", segment: "calendar" },
  { label: "Log Entry", segment: "entry" },
  { label: "History", segment: "history" },
  { label: "Profiles", segment: "profiles" },
  { label: "Settings", segment: "settings" },
];

let profileId: string | null = null;

test.describe("VS-1 Automated Validation", () => {

  test("C1: Dashboard loads via ingress", async ({ page }) => {
    try {
      await page.goto(BASE_URL, { waitUntil: "networkidle" });
      await expect(page.locator("nav")).toBeVisible({ timeout: 15000 });
      await expect(page.getByText("Byrd Health").first()).toBeVisible();
      console.log("PASS: C1 — Dashboard loads via ingress");
    } catch (e: any) {
      console.log(`FAIL: C1 — ${e.message}`);
      throw e;
    }
  });

  test("C2: All 6 nav pages load without errors", async ({ page }) => {
    for (const { label, segment } of NAV_PAGES) {
      try {
        const url = segment ? `${BASE_URL}${segment}` : BASE_URL;
        await page.goto(url, { waitUntil: "networkidle" });
        await page.waitForSelector("#main-content", { timeout: 10000 });
        const visible = page.locator("#main-content *:visible");
        expect(await visible.count()).toBeGreaterThan(0);
        console.log(`PASS: C2 — ${label} page loaded`);
      } catch (e: any) {
        console.log(`FAIL: C2 — ${label} page: ${e.message}`);
      }
    }
  });

  test.describe.serial("API workflow (C3-C9)", () => {

    test("C3: API health check", async ({ request }) => {
      try {
        const resp = await request.get(`${API_BASE}health`);
        expect(resp.status()).toBe(200);
        const body = await resp.json();
        expect(body.status).toBe("ok");
        console.log("PASS: C3 — API health check returns ok");
      } catch (e: any) {
        console.log(`FAIL: C3 — ${e.message}`);
        throw e;
      }
    });

    test("C4: API profiles endpoint returns array", async ({ request }) => {
      try {
        const resp = await request.get(`${API_BASE}v1/fertility/profiles/`);
        expect(resp.status()).toBe(200);
        const body = await resp.json();
        expect(Array.isArray(body)).toBe(true);
        console.log(`PASS: C4 — Profiles endpoint: ${body.length} profile(s)`);
      } catch (e: any) {
        console.log(`FAIL: C4 — ${e.message}`);
        throw e;
      }
    });

    test("C5: Create test profile", async ({ request }) => {
      try {
        const resp = await request.post(`${API_BASE}v1/fertility/profiles/`, {
          data: { name: "VS1-Test" },
        });
        expect(resp.status()).toBe(201);
        const body = await resp.json();
        profileId = body.id;
        expect(profileId).toBeTruthy();
        console.log(`PASS: C5 — Created test profile: ${profileId}`);
      } catch (e: any) {
        console.log(`FAIL: C5 — ${e.message}`);
        throw e;
      }
    });

    test("C6: Activate test profile", async ({ request }) => {
      try {
        expect(profileId).toBeTruthy();
        const resp = await request.post(
          `${API_BASE}v1/fertility/profiles/${profileId}/activate`
        );
        expect(resp.status()).toBe(200);
        console.log("PASS: C6 — Profile activated");
      } catch (e: any) {
        console.log(`FAIL: C6 — ${e.message}`);
        throw e;
      }
    });

    test("C7: Submit temperature entry", async ({ request }) => {
      try {
        expect(profileId).toBeTruthy();
        const today = new Date().toISOString().split("T")[0];
        const resp = await request.post(`${API_BASE}v1/fertility/entries/`, {
          data: {
            date: today,
            temp_value: 98.2,
          },
        });
        expect(resp.status()).toBe(201);
        console.log("PASS: C7 — Temperature entry submitted");
      } catch (e: any) {
        console.log(`FAIL: C7 — ${e.message}`);
        throw e;
      }
    });

    test("C8: Insights returned after entry", async ({ request }) => {
      try {
        expect(profileId).toBeTruthy();
        const resp = await request.get(`${API_BASE}v1/fertility/insights/`);
        expect(resp.status()).toBe(200);
        const body = await resp.json();
        expect(typeof body).toBe("object");
        console.log(`PASS: C8 — Insights returned (phase: ${body.phase || "unknown"})`);
      } catch (e: any) {
        console.log(`FAIL: C8 — ${e.message}`);
        throw e;
      }
    });

    test.afterAll(async ({ request }) => {
      if (!profileId) return;
      try {
        const listResp = await request.get(`${API_BASE}v1/fertility/profiles/`);
        const profiles: any[] = await listResp.json();
        const other = profiles.find((p: any) => p.id !== profileId);

        if (other) {
          await request.post(`${API_BASE}v1/fertility/profiles/${other.id}/activate`);
        }

        const del = await request.delete(`${API_BASE}v1/fertility/profiles/${profileId}`);
        if (del.ok()) {
          console.log(`PASS: C9 — Cleanup: deleted profile ${profileId}`);
        } else {
          const msg = await del.text();
          console.log(`FAIL: C9 — Cleanup: delete returned ${del.status()} — ${msg}`);
        }
      } catch (e: any) {
        console.log(`FAIL: C9 — Cleanup error: ${e.message}`);
      }
    });
  });
});
