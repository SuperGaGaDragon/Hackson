/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/

import { chromium } from "playwright";

const frontendUrl = process.env.HACKSON_SMOKE_FRONTEND_URL || "http://127.0.0.1:5173";
const screenshotPath = process.env.HACKSON_SMOKE_SCREENSHOT || "../scripts/artifacts/idle_interruption_smoke.png";
const smokeTimeoutMs = Number(process.env.HACKSON_SMOKE_TIMEOUT_MS || "60000");

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1360, height: 960 } });
  page.setDefaultTimeout(smokeTimeoutMs);

  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await register(page);
  await page.getByTitle("Idle").click();
  const say = page.getByLabel("Say");
  await say.waitFor();

  await page.getByRole("button", { name: "Tick" }).click();
  await page.getByText("Working").waitFor();
  if (!(await say.isEnabled())) {
    throw new Error("idle_say_should_stay_enabled_while_working");
  }
  await say.fill("我现在插一句。");
  await page.getByTitle("Send").click();
  await page.getByText("我现在插一句。").waitFor();
  await page.waitForFunction(() => document.querySelectorAll(".message-row").length >= 3);

  await page.screenshot({ path: screenshotPath, fullPage: true });
  await browser.close();
  console.log(`idle_interruption_smoke=ok screenshot=${screenshotPath}`);
}

async function register(page) {
  const stamp = Date.now();
  await page.getByRole("button", { name: "Register" }).click();
  await page.getByLabel("User").fill(`idleint${stamp}`);
  await page.getByLabel("Email").fill(`idleint${stamp}@example.com`);
  await page.getByLabel("Pass").fill("smokepass123");
  await page.getByRole("button", { name: "Enter" }).click();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
