/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/

import fs from "node:fs";
import { chromium } from "playwright";

const statePath = process.env.HACKSON_AGENTLENS_PUBLIC_SMOKE_STATE;
const screenshotPath =
  process.env.HACKSON_AGENTLENS_PUBLIC_UI_SCREENSHOT ||
  "../scripts/artifacts/work_mode_agentlens_public_ui_smoke.png";

if (!statePath) {
  throw new Error("missing_state_path");
}

const state = JSON.parse(fs.readFileSync(statePath, "utf8"));

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(15000);
  await page.goto(state.baseUrl, { waitUntil: "domcontentloaded" });
  await page.evaluate((token) => {
    window.localStorage.setItem("hackson_access_token", token);
  }, state.accessToken);
  await page.goto(state.baseUrl, { waitUntil: "networkidle" });
  await page.getByTitle("Work").click();
  await page.getByText("AgentLens Public Smoke", { exact: false }).click();
  await page
    .locator(".history-list .history-item", { hasText: "AgentLens Toronto AI reliability smoke" })
    .first()
    .click();
  const checkButton = page.getByRole("button", { name: "Check" });
  await checkButton.waitFor();
  if (!(await checkButton.isVisible())) {
    throw new Error("check_button_missing");
  }
  if (!(await checkButton.isEnabled())) {
    throw new Error("check_button_disabled");
  }
  await page.locator(".quality-panel").waitFor();
  const panelText = await page.locator(".quality-panel").innerText();
  if (!panelText.includes(`${state.score} / 100`)) {
    throw new Error(`score_missing:${panelText}`);
  }
  if (!/Quality|Risk|Needs review|Unsafe|Minor review|Ship-ready/.test(panelText)) {
    throw new Error(`panel_incomplete:${panelText}`);
  }
  const mainReliabilityCards = await page.locator(".mission-content > .reliability-panel").count();
  if (mainReliabilityCards !== 0) {
    throw new Error(`reliability_should_not_be_main_content:${mainReliabilityCards}`);
  }
  const qualityDetailsOpen = await page.locator(".quality-details").evaluate((node) => node.open);
  if (qualityDetailsOpen) {
    throw new Error("quality_details_should_be_collapsed");
  }
  await page.locator(".quality-details summary").click();
  const detailText = await page.locator(".reliability-panel.embedded").innerText();
  if (!/Reliability|Issues|Claims/.test(detailText)) {
    throw new Error(`details_incomplete:${detailText}`);
  }
  if (!detailText.includes("Unsupported claim")) {
    throw new Error(`unsupported_issue_missing:${detailText}`);
  }
  const hasHorizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  );
  if (hasHorizontalOverflow) {
    throw new Error("desktop_horizontal_overflow");
  }
  await page.screenshot({ path: screenshotPath, fullPage: true });
  await browser.close();
  console.log(`work_mode_agentlens_public_ui_smoke=ok screenshot=${screenshotPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
