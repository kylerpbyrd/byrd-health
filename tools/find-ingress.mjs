import { chromium } from "playwright";

const HA_URL = process.env.BYRD_HA_URL || "http://192.168.1.44:8123";

const browser = await chromium.launch();
const ctx = await browser.newContext();
const page = await ctx.newPage();

// Navigate to the add-on panel page
await page.goto(`${HA_URL}/hassio/addon/local_byrd_health_fertility`, {
  waitUntil: "domcontentloaded",
  timeout: 20000,
});
await page.waitForTimeout(3000);

// Look for ingress-related URLs in the page content
const html = await page.content();

// Search for ingress patterns
const patterns = [
  /api\/hassio_ingress\/[A-Za-z0-9_\-]+\//g,
  /"ingress_url"\s*:\s*"[^"]+"/g,
  /"ingress_entry"\s*:\s*"[^"]+"/g,
];

for (const pattern of patterns) {
  const matches = html.match(pattern);
  if (matches) {
    console.log(`Pattern ${pattern}:`, matches);
  }
}

// Also check if there are iframes
const iframes = await page.locator("iframe").all();
console.log(`Found ${iframes.length} iframe(s)`);
for (const f of iframes) {
  const src = await f.getAttribute("src");
  console.log("  iframe src:", src);
}

// Check the page URL after any redirects
console.log("Current page URL:", page.url());

await browser.close();
