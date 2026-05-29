/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-29
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
  if (pageTitle !== "Parallex") throw new Error(`unexpected_title:${pageTitle}`);
  await page.getByText("Parallex", { exact: true }).first().waitFor();
  await page.getByText("Agentic work, made inspectable.", { exact: true }).waitFor();
  await page.getByText("Idle Mode", { exact: true }).waitFor();
  await page.getByText("Brainstorm with multiple AI agents.", { exact: true }).waitFor();
  await page.getByText("Work Mode", { exact: true }).waitFor();
  await page.getByText("Visualize missions, progress, windows, and products.", { exact: true }).waitFor();
  await page.getByText("Evaluator", { exact: true }).waitFor();
  await page.getByText("Reduce hallucination risk with evidence-gap checks.", { exact: true }).waitFor();
  await page.getByText("Visual workflow", { exact: true }).waitFor();
  await page.getByText("Brainstorm to final, visibly.", { exact: true }).waitFor();
  await page.getByText("Universal memory.", { exact: true }).waitFor();
  await page.getByText("Permanent agents", { exact: true }).waitFor();
  await page.getByText("Your two agents", { exact: true }).waitFor();
  await page.getByText("Approved memory", { exact: true }).waitFor();
  await page.getByText("Context you allow", { exact: true }).waitFor();
  await assertAbsent(page, "TMLS Agentic Hackathon");
  await assertAbsent(page, "Intent to product, with the trace intact.");
  await assertAbsent(page, "Temporary session. Close this browser session and the work may be gone.");
  await assertAbsent(page, "Nora / Vale");
  const catImageCount = await page.locator('img[src="/assets/companion-cat-preview.png"]').count();
  if (catImageCount !== 0) throw new Error("landing_cat_image_should_not_render");
  await assertNoHorizontalOverflow(page, "desktop_landing");
  await page.screenshot({ path: screenshot, fullPage: true });
  await page.getByRole("button", { name: "Create Account" }).first().click();
  await page.getByRole("heading", { name: "Create Account" }).waitFor();
  await page.getByRole("button", { name: "Back to intro" }).click();
  await page.getByRole("heading", { name: "Parallex" }).waitFor();
  await page.getByRole("button", { name: "Quick Try" }).first().click();
  await page.locator(".work-workspace-view").waitFor();
  await page.getByText("Workspace", { exact: true }).first().waitFor();
  await page.getByLabel("Project name").waitFor();
  await page.getByRole("button", { name: "Back to intro" }).waitFor();
  const tokenStored = await page.evaluate(() => Boolean(window.sessionStorage.getItem("hackson_quick_access_token")));
  if (!tokenStored) throw new Error("quick_try_token_not_session_scoped");
  await assertNoHorizontalOverflow(page, "desktop_work");
  await page.getByRole("button", { name: "Back to intro" }).click();
  await page.getByRole("heading", { name: "Parallex" }).waitFor();
  const tokenCleared = await page.evaluate(() => !window.sessionStorage.getItem("hackson_quick_access_token"));
  if (!tokenCleared) throw new Error("quick_try_back_to_intro_should_clear_session");

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  mobile.setDefaultTimeout(15000);
  await installLocalMocks(mobile);
  await mobile.goto(baseUrl, { waitUntil: "networkidle" });
  await mobile.getByText("Agentic work, made inspectable.", { exact: true }).waitFor();
  await mobile.getByText("Brainstorm to final, visibly.", { exact: true }).waitFor();
  await mobile.getByText("Quick Try", { exact: true }).first().waitFor();
  await assertNoHorizontalOverflow(mobile, "mobile");
  await mobile.screenshot({ path: mobileScreenshot, fullPage: true });

  await browser.close();
  console.log(`hackathon_landing_public_smoke=ok screenshot=${screenshot} mobile=${mobileScreenshot}`);
}

async function assertAbsent(page, text) {
  const count = await page.getByText(text, { exact: true }).count();
  if (count !== 0) throw new Error(`landing_text_should_be_absent:${text}`);
}

async function installLocalMocks(page) {
  if (process.env.HACKSON_USE_QUICK_TRY_MOCKS === "true") {
    await page.route("**/api/users/quick-try", async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          accessToken: "quick-try-smoke-token",
          tokenType: "bearer",
          user: {
            id: "quick_try_smoke",
            username: "quick-smoke",
            isTemporary: true,
            agentProfiles: [
              { slot: "agent_1", short: "A1", name: "Nora", color: "teal", voice: "precise" },
              { slot: "agent_2", short: "A2", name: "Vale", color: "amber", voice: "sharp" },
            ],
          },
        }),
      });
    });
  }
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
