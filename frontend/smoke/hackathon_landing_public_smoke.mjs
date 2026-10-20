/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-10-20
Last Modified by: Codex
*/
import { chromium } from "playwright";

const baseUrl = process.env.HACKSON_PUBLIC_URL || "https://hackson.catachess.com";
const screenshot = process.env.HACKSON_HACKATHON_SCREENSHOT || "../scripts/artifacts/hackathon_landing_public.png";
const mobileScreenshot =
  process.env.HACKSON_HACKATHON_MOBILE_SCREENSHOT || "../scripts/artifacts/hackathon_landing_public_mobile.png";

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(15000);
  await installLocalMocks(page);
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  const pageTitle = await page.title();
  if (pageTitle !== "Parallax") throw new Error(`unexpected_title:${pageTitle}`);
  await page.getByText("Parallax", { exact: true }).first().waitFor();
  await page.getByRole("heading", { name: /Think with AI.*Work with agents/ }).waitFor();
  await page.getByText("With your personalized agents,", { exact: true }).waitFor();
  await page.getByText("talk things through, get things done.", { exact: true }).waitFor();
  await page.getByText("Open workspace", { exact: true }).waitFor();
  await page.getByText("Try first", { exact: true }).waitFor();
  await page.getByText("Create account", { exact: true }).waitFor();
  await page.getByRole("heading", { name: "Work", exact: true }).waitFor();
  await page.getByText("Two agents handle your task, with steps you can review.", { exact: true }).waitFor();
  await page.getByRole("heading", { name: "Idle", exact: true }).waitFor();
  await page.getByText("Sort out your thoughts and explore ideas before acting.", { exact: true }).waitFor();
  await page.getByRole("heading", { name: "Chat", exact: true }).waitFor();
  await page.getByText("Talk with an AI companion, or simply think out loud.", { exact: true }).waitFor();
  await page.getByText("Customize your agents", { exact: true }).waitFor();
  await page.getByText("Try Desktop Pet", { exact: true }).waitFor();
  await page.getByText("Work. Idle. Chat.", { exact: true }).waitFor();
  const catImageCount = await page.locator('img[src="/assets/companion-cat-preview.png"]').count();
  if (catImageCount !== 0) throw new Error("landing_cat_image_should_not_render");
  await assertNoHorizontalOverflow(page, "desktop_landing");
  await page.screenshot({ path: screenshot, fullPage: true });
  await page.getByRole("button", { name: "Create account" }).click();
  await page.getByRole("heading", { name: "Create Account" }).waitFor();
  await page.getByRole("button", { name: "Back to intro" }).click();
  await page.getByRole("heading", { name: /Think with AI.*Work with agents/ }).waitFor();
  await page.getByText("Try first", { exact: true }).click();
  await page.locator(".work-workspace-view").waitFor();
  await page.getByText("Workspace", { exact: true }).first().waitFor();
  await page.getByLabel("Project name").waitFor();
  await page.getByTitle("Pet").waitFor();
  await page.getByRole("button", { name: "Back to intro" }).waitFor();
  const tokenStored = await page.evaluate(() => Boolean(window.sessionStorage.getItem("hackson_quick_access_token")));
  if (!tokenStored) throw new Error("quick_try_token_not_session_scoped");
  await assertNoHorizontalOverflow(page, "desktop_work");
  await page.getByRole("button", { name: "Back to intro" }).click();
  await page.getByRole("heading", { name: /Think with AI.*Work with agents/ }).waitFor();
  const tokenCleared = await page.evaluate(() => !window.sessionStorage.getItem("hackson_quick_access_token"));
  if (!tokenCleared) throw new Error("quick_try_back_to_intro_should_clear_session");

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  mobile.setDefaultTimeout(15000);
  await installLocalMocks(mobile);
  await mobile.goto(baseUrl, { waitUntil: "networkidle" });
  await mobile.getByRole("heading", { name: /Think with AI.*Work with agents/ }).waitFor();
  await mobile.getByText("Try first", { exact: true }).waitFor();
  await mobile.getByText("Try Desktop Pet", { exact: true }).waitFor();
  await assertNoHorizontalOverflow(mobile, "mobile");
  await mobile.screenshot({ path: mobileScreenshot, fullPage: true });

  await assertProductEntry(browser, baseUrl, "Open Idle", "/idle", "Live timeline");
  await assertProductEntry(browser, baseUrl, "Open Chat", "/companion", "Companion");
  await assertProductEntry(browser, baseUrl, "Customize your agents", "/me", "Settings");
  await assertProductEntry(browser, baseUrl, "Try Desktop Pet", "/download/companion", "Desktop Companion", false);

  await browser.close();
  console.log(`hackathon_landing_public_smoke=ok screenshot=${screenshot} mobile=${mobileScreenshot}`);
}

async function assertProductEntry(browser, baseUrl, linkName, pathname, heading, expectsSession = true) {
  const page = await browser.newPage({ viewport: { width: 1180, height: 820 } });
  page.setDefaultTimeout(15000);
  await installLocalMocks(page);
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.getByText(linkName, { exact: true }).click();
  await page.waitForURL((url) => url.pathname === pathname);
  await page.getByRole("heading", { name: heading, exact: true, level: 1 }).waitFor();
  if (expectsSession) {
    const tokenStored = await page.evaluate(() => Boolean(window.sessionStorage.getItem("hackson_quick_access_token")));
    if (!tokenStored) throw new Error(`entry_token_missing:${pathname}`);
  }
  await assertNoHorizontalOverflow(page, `entry_${pathname}`);
  await page.close();
}

async function installLocalMocks(page) {
  if (process.env.HACKSON_USE_QUICK_TRY_MOCKS === "true") {
    await page.route("**/api/**", async (route) => {
      const url = new URL(route.request().url());
      if (!url.pathname.startsWith("/api/")) {
        await route.continue();
        return;
      }
      let body = {};
      if (url.pathname === "/api/users/quick-try") {
        body = {
          accessToken: "quick-try-smoke-token",
          tokenType: "bearer",
          user: smokeUser(),
        };
      } else if (url.pathname === "/api/agents") {
        body = smokeAgents();
      } else if (url.pathname === "/api/work/projects" || url.pathname === "/api/conversations") {
        body = [];
      } else if (url.pathname === "/api/idle/conversation") {
        body = {
          id: "idle_smoke",
          userId: "quick_try_smoke",
          mode: "idle",
          status: "active",
          title: "Idle",
          participantSlots: ["agent_1", "agent_2"],
          parentConversationId: null,
          messageCount: 0,
          metadata: {},
          createdAt: "2026-10-19T00:00:00Z",
          updatedAt: "2026-10-19T00:00:00Z",
        };
      } else if (url.pathname.endsWith("/messages")) {
        body = { items: [], nextBeforeSequence: null };
      } else if (url.pathname === "/api/memory/me") {
        body = { memoryCards: [] };
      } else if (url.pathname === "/api/users/me/prompt-logs") {
        body = { promptLogs: [] };
      } else if (url.pathname === "/api/users/me") {
        body = smokeUser();
      }
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
    });
  }
}

function smokeUser() {
  return {
    id: "quick_try_smoke",
    username: "quick-smoke",
    isTemporary: true,
    personality: "I am trying Parallax unlogged in; progress will not be saved.",
    agentProfiles: smokeAgents(),
  };
}

function smokeAgents() {
  return [
    { slot: "agent_1", short: "A1", name: "Nora", color: "teal", voice: "precise" },
    { slot: "agent_2", short: "A2", name: "Vale", color: "amber", voice: "sharp" },
  ];
}

async function assertNoHorizontalOverflow(page, label) {
  const hasOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  );
  if (hasOverflow) throw new Error(`${label}_horizontal_overflow`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
