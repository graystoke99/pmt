import { defineConfig, devices } from "@playwright/test";

const browserName = process.env.PLAYWRIGHT_BROWSER_NAME ?? "chromium";
const executablePath = process.env.PLAYWRIGHT_EXECUTABLE_PATH;

const projectDevice =
  browserName === "firefox" ? devices["Desktop Firefox"] : devices["Desktop Chrome"];

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run build && npm run serve:static",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: true,
    timeout: 120_000,
  },
  projects: [
    {
      name: browserName,
      use: {
        ...projectDevice,
        browserName: browserName as "chromium" | "firefox" | "webkit",
        ...(executablePath
          ? {
              launchOptions: {
                executablePath,
              },
            }
          : {}),
      },
    },
  ],
});
