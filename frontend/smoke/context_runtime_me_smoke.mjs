/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/

import { chromium } from "playwright";

const frontendUrl = process.env.HACKSON_SMOKE_FRONTEND_URL || "http://127.0.0.1:8166";
const screenshotPath = process.env.HACKSON_SMOKE_SCREENSHOT || "../scripts/artifacts/context_runtime_me_memory_smoke.png";

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1360, height: 960 } });
  page.setDefaultTimeout(15000);

  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await register(page);
  await page.locator('nav[aria-label="Main"]').waitFor();
  await page.getByTitle("Me").click();

  await page.getByRole("heading", { name: "Nora & Vale" }).waitFor();
  await page.getByRole("heading", { name: "Context" }).waitFor();
  await page.getByText(/Memory/).waitFor();
  const debug = page.locator(".debug-panel");
  await debug.waitFor();
  if (await debug.evaluate((node) => node.open)) {
    throw new Error("debug_should_default_closed");
  }
  const firstLogVisibleBeforeOpen = await page.locator(".prompt-log-item").first().isVisible().catch(() => false);
  if (firstLogVisibleBeforeOpen) {
    throw new Error("prompt_logs_should_not_dominate_first_view");
  }
  const promptChecked = await page.locator("label", { hasText: "Prompt log" }).locator("input").isChecked();
  const backgroundChecked = await page.locator("label", { hasText: "Away idle" }).locator("input").isChecked();
  if (!promptChecked) throw new Error("prompt_log_should_default_on");
  if (backgroundChecked) throw new Error("background_idle_should_default_off");
  await debug.locator("summary").click();
  await page.getByText(/Prompt logs/).waitFor();
  const firstLog = page.locator(".prompt-log-item").first();
  if (await firstLog.count()) {
    await firstLog.locator("summary").click();
    await firstLog.locator("pre").waitFor();
  }
  await page.evaluate(() => {
    document.querySelector(".settings-view")?.scrollTo(0, 0);
    window.scrollTo(0, 0);
  });

  await page.screenshot({ path: screenshotPath, fullPage: true });
  await browser.close();
  console.log(`context_runtime_me_smoke=ok screenshot=${screenshotPath}`);
}

async function register(page) {
  const stamp = Date.now();
  await page.getByRole("button", { name: "Register" }).click();
  await page.getByLabel("User").fill(`ctxme${stamp}`);
  await page.getByLabel("Email").fill(`ctxme${stamp}@example.com`);
  await page.getByLabel("Pass").fill("smokepass123");
  await page.getByRole("button", { name: "Enter" }).click();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
