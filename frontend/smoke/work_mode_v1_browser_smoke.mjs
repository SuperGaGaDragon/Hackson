/*
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/

import { chromium } from "playwright";

const frontendUrl = process.env.HACKSON_SMOKE_FRONTEND_URL || "http://127.0.0.1:4173";
const screenshotPath = process.env.HACKSON_SMOKE_SCREENSHOT || "../scripts/artifacts/work_mode_v1_browser_smoke.png";

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(15000);

  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await register(page);
  await page.getByTitle("Work").click();
  await page.getByLabel("Project name").fill("Browser Smoke Project");
  await page.getByRole("button", { name: /Create/ }).click();
  await page.getByLabel("Mission title").fill("写一个8000字小说");
  await page.getByLabel("Mission goal").fill("写一个8000字中文小说，题材自定，要求分章节，有大纲，有最终成稿。");
  await page.getByRole("button", { name: /Create/ }).last().click();
  await page.getByRole("button", { name: /Start/ }).click();

  await page.getByText("completed").first().waitFor({ timeout: 20000 });
  await assertVisible(page, "Progress");
  await assertVisible(page, "Windows");
  await assertVisible(page, "Product");
  await assertVisible(page, "8000字小说计划");
  await assertVisible(page, "第一章草稿");
  await assertVisible(page, "第二章草稿");
  await assertVisible(page, "最终成稿");
  await assertVisible(page, "Final");

  const windows = page.locator(".window-row");
  const windowCount = await windows.count();
  if (windowCount < 2) {
    throw new Error(`expected_at_least_two_windows:${windowCount}`);
  }
  const firstWindow = windows.first();
  const isOpenBefore = await firstWindow.evaluate((node) => node.open);
  if (isOpenBefore) {
    throw new Error("window_should_be_collapsed_by_default");
  }
  await firstWindow.locator("summary").click();
  await assertVisible(page, "雨夜车站里");

  const productText = await page.locator(".artifact-content").innerText();
  const cjkCount = (productText.match(/[\u4e00-\u9fff]/g) || []).length;
  if (cjkCount < 8000) {
    throw new Error(`final_product_too_short:${cjkCount}`);
  }

  await page.screenshot({ path: screenshotPath, fullPage: true });
  await browser.close();
  console.log(`work_mode_v1_browser_smoke=ok windows=${windowCount} final_cjk=${cjkCount} screenshot=${screenshotPath}`);
}

async function register(page) {
  await page.getByRole("button", { name: "Register" }).click();
  await page.getByLabel("User").fill(`worksmoke${Date.now()}`);
  await page.getByLabel("Email").fill(`worksmoke${Date.now()}@example.com`);
  await page.getByLabel("Pass").fill("smokepass123");
  await page.getByRole("button", { name: "Enter" }).click();
}

async function assertVisible(page, text) {
  await page.getByText(text, { exact: false }).first().waitFor();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
