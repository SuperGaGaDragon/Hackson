/*
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/

import { chromium } from "playwright";

const frontendUrl = process.env.HACKSON_SMOKE_FRONTEND_URL || "http://127.0.0.1:4173";
const screenshotPath = process.env.HACKSON_SMOKE_SCREENSHOT || "../scripts/artifacts/work_mode_v1_browser_smoke.png";
const mobileScreenshotPath =
  process.env.HACKSON_SMOKE_MOBILE_SCREENSHOT || "../scripts/artifacts/work_mode_v1_browser_smoke_mobile.png";
const completionTimeoutMs = Number(process.env.HACKSON_SMOKE_COMPLETION_TIMEOUT_MS || "20000");
const expectFixtureText = process.env.HACKSON_SMOKE_EXPECT_FIXTURE_TEXT !== "false";

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(15000);

  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await register(page);
  await page.getByTitle("Work").click();
  await page.getByLabel("Project name").fill("Browser Smoke Project");
  await page.getByRole("button", { name: /Create/ }).click();
  await page.getByTitle("New Mission").click();
  await page.getByLabel("Mission title").fill("写一个8000字小说");
  await page.getByLabel("Mission goal").fill("写一个8000字中文小说，题材自定，要求分章节，有大纲，有最终成稿。");
  await page.locator(".mission-create-modal").getByRole("button", { name: /Create/ }).click();
  await page.locator(".mission-create-modal").waitFor({ state: "detached" });
  if ((await page.getByLabel("Mission title").count()) !== 0) {
    throw new Error("mission_create_form_should_not_remain_in_rail");
  }
  await page.getByRole("button", { name: /Start/ }).click();

  await page.locator(".mission-head .chip", { hasText: "completed" }).waitFor({ timeout: completionTimeoutMs });
  await page.getByRole("button", { name: /Check/ }).click();
  await page.locator(".reliability-panel").waitFor();
  await assertVisible(page, "Reliability");
  await assertReliabilityPanel(page);
  await assertVisible(page, "Progress");
  await page.locator(".activity-strip").waitFor();
  await assertVisible(page, "Windows");
  await assertVisible(page, "Product");
  await assertVisible(page, "Diagnostics");
  await assertVisible(page, "Final");
  if (expectFixtureText) {
    await assertVisible(page, "8000字小说计划");
    await assertVisible(page, "第一章草稿");
    await assertVisible(page, "第二章草稿");
    await assertVisible(page, "最终成稿");
  }

  const windows = page.locator(".window-row");
  const windowCount = await windows.count();
  if (windowCount < 2) {
    throw new Error(`expected_at_least_two_windows:${windowCount}`);
  }
  const missionOrder = await page.locator(".mission-content > *").evaluateAll((nodes) =>
    nodes.map((node) => {
      if (node.classList.contains("activity-strip")) return "activity";
      if (node.classList.contains("reliability-panel")) return "reliability";
      if (node.classList.contains("window-panel")) return "windows";
      if (node.classList.contains("product-panel")) return "product";
      if (node.classList.contains("timeline-card")) return "progress";
      if (node.classList.contains("raw-log-panel")) return "diagnostics";
      return "unknown";
    }),
  );
  const expectedOrder = ["activity", "reliability", "windows", "product", "progress", "diagnostics"];
  if (expectedOrder.some((item, index) => missionOrder[index] !== item)) {
    throw new Error(`mission_order_invalid:${missionOrder.join(",")}`);
  }
  const diagnosticOpen = await page.locator(".raw-log-panel").evaluate((node) => node.open);
  if (diagnosticOpen) {
    throw new Error("diagnostics_should_be_collapsed_by_default");
  }
  const lineageCount = await page.locator(".artifact-nav-row").count();
  if (lineageCount < 3) {
    throw new Error(`expected_artifact_lineage:${lineageCount}`);
  }
  const desktopReaderColumns = await page
    .locator(".product-reader-shell")
    .evaluate((node) => getComputedStyle(node).gridTemplateColumns.trim().split(/\s+/).length);
  if (desktopReaderColumns < 2) {
    throw new Error(`product_reader_should_split_on_desktop:${desktopReaderColumns}`);
  }
  const navRowHeights = await page
    .locator(".artifact-nav-row")
    .evaluateAll((rows) => rows.map((row) => Math.round(row.getBoundingClientRect().height)));
  const maxNavRowHeight = Math.max(...navRowHeights);
  const minNavRowHeight = Math.min(...navRowHeights);
  if (minNavRowHeight < 52 || maxNavRowHeight > 92) {
    throw new Error(`artifact_nav_unstable_height:${minNavRowHeight}-${maxNavRowHeight}`);
  }
  await page.locator(".event-time").first().waitFor();
  const planRows = await page.locator(".mission_plan_updated").count();
  if (planRows < 1) {
    throw new Error("expected_plan_progress_row");
  }
  await page.locator(".mission_plan_updated").first().click();
  await assertVisible(page, "Steps");
  const productRows = await page.locator(".product_updated").count();
  if (productRows < 1) {
    throw new Error("expected_product_progress_row");
  }
  await page.locator(".product_updated").first().click();
  const expandedRows = await page.locator(".progress-row[aria-expanded='true']").count();
  if (expandedRows !== 1) {
    throw new Error(`expected_one_expanded_progress_row:${expandedRows}`);
  }
  await assertVisible(page, "Product");

  const firstWindow = windows.first();
  const isOpenBefore = await firstWindow.evaluate((node) => node.open);
  if (isOpenBefore) {
    throw new Error("window_should_be_collapsed_by_default");
  }
  await firstWindow.locator("summary").click();
  const windowPreviewText = await firstWindow.locator(".window-artifact-preview, p").last().innerText();
  if ((windowPreviewText.match(/[\u4e00-\u9fff]/g) || []).length < 20) {
    throw new Error("window_preview_missing_content");
  }
  await firstWindow.locator("summary").click();

  const productText = await page.locator(".artifact-content").innerText();
  if (expectFixtureText) {
    for (const expectedProductSection of ["故事大纲", "第一章草稿", "第二章草稿", "最终成稿"]) {
      if (!productText.includes(expectedProductSection)) {
        throw new Error(`product_reader_missing_section:${expectedProductSection}`);
      }
    }
  }
  const outlineButton = page.locator(".artifact-navigator .artifact-nav-row", { hasText: /outline|大纲/i }).first();
  await outlineButton.click();
  const outlineOnlyText = await page.locator(".artifact-content").innerText();
  if ((outlineOnlyText.match(/[\u4e00-\u9fff]/g) || []).length < 20 || /最终成稿|final/i.test(outlineOnlyText)) {
    throw new Error("artifact_single_select_failed");
  }
  const finalButton = page.locator(".artifact-navigator .artifact-nav-row", { hasText: /final|最终|成稿/i }).last();
  await finalButton.click();
  const finalOnlyText = await page.locator(".artifact-content").innerText();
  const finalOnlyCjk = (finalOnlyText.match(/[\u4e00-\u9fff]/g) || []).length;
  if (finalOnlyCjk < 8000) {
    throw new Error(`final_artifact_too_short:${finalOnlyCjk}`);
  }
  await page.locator(".artifact-navigator").getByRole("button", { name: /All artifacts|All/ }).click();
  const restoredProductText = await page.locator(".artifact-content").innerText();
  const restoredCjk = (restoredProductText.match(/[\u4e00-\u9fff]/g) || []).length;
  if (restoredCjk <= finalOnlyCjk) {
    throw new Error("artifact_all_restore_failed");
  }
  const cjkCount = restoredCjk;
  if (cjkCount < 8000) {
    throw new Error(`final_product_too_short:${cjkCount}`);
  }

  await page.screenshot({ path: screenshotPath, fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator(".product-panel").scrollIntoViewIfNeeded();
  const hasHorizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  );
  if (hasHorizontalOverflow) {
    throw new Error("mobile_horizontal_overflow");
  }
  await page.screenshot({ path: mobileScreenshotPath, fullPage: true });
  await browser.close();
  console.log(
    `work_mode_v1_browser_smoke=ok windows=${windowCount} final_cjk=${cjkCount} screenshot=${screenshotPath} mobile=${mobileScreenshotPath}`,
  );
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

async function assertReliabilityPanel(page) {
  const panelText = await page.locator(".reliability-panel").innerText();
  if (!/\d+\s*\/\s*100/.test(panelText)) {
    throw new Error(`reliability_score_missing:${panelText}`);
  }
  if (!/(Ship-ready|Minor review|Needs review|Unsafe)/.test(panelText)) {
    throw new Error(`reliability_status_missing:${panelText}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
