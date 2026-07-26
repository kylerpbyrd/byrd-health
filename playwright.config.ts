import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tools",
  testMatch: "validate-vs1.ts",
  timeout: 90000,
  use: {
    baseURL: process.env.BYRD_HA_URL || "http://192.168.1.44:8123",
  },
});
