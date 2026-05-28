/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/

import { chromium } from "playwright";

const frontendUrl = process.env.HACKSON_SMOKE_FRONTEND_URL || "https://hackson.catachess.com/";
const screenshotPath =
  process.env.HACKSON_PRODUCT_READER_SCREENSHOT || "../scripts/artifacts/work_mode_product_reader_public_ui_smoke.png";
const mobileScreenshotPath =
  process.env.HACKSON_PRODUCT_READER_MOBILE_SCREENSHOT ||
  "../scripts/artifacts/work_mode_product_reader_public_ui_smoke_mobile.png";

const project = {
  id: "project_product_reader",
  name: "Product Reader Polish",
  status: "active",
};
const mission = {
  id: "mission_product_reader",
  projectId: project.id,
  title: "长篇爽文《我能看见万物价格》",
  goal: "验证 Product reader 长短标题混排时的产品级阅读体验。",
  status: "completed",
};
const createdAt = "2026-05-28T13:00:00.000Z";
const productId = "product_reader";
const artifacts = [
  artifact("artifact_outline", "爽文故事大纲与人物设定", "outline", "outline", outlineContent()),
  artifact(
    "artifact_chapter_1",
    "《我能看见万物价格》正文第一部分：谷底觉醒与第一次反杀",
    "chapter",
    "chapter",
    chapterContent("第一章草稿", 90),
  ),
  artifact(
    "artifact_chapter_2",
    "《我能看见万物价格》中段正文：捡漏起飞，连环反打",
    "chapter",
    "chapter",
    chapterContent("第二章草稿", 95),
  ),
  artifact(
    "artifact_final",
    "《我能看见万物价格》后段与结局正文：三线崩盘，终局反杀",
    "chapter",
    "final",
    chapterContent("最终成稿", 420),
  ),
  artifact("artifact_review", "《我能看见万物价格》成稿审查", "review", "review", reviewContent()),
];
const product = {
  id: productId,
  title: "长篇爽文《我能看见万物价格》",
  summary: "大纲、前段、中段与后段已形成完整闭环，可进入任务完成。",
  status: "final",
  artifactIds: artifacts.map((item) => item.id),
  latestArtifactId: "artifact_review",
  deliverableArtifactId: "artifact_final",
  deliveryStatus: "verified_final",
};

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(15000);
  await installApiMocks(page);
  await page.addInitScript(() => {
    window.localStorage.setItem("hackson_access_token", "product-reader-smoke-token");
  });
  await page.goto(frontendUrl, { waitUntil: "networkidle" });
  await page.getByTitle("Work").click();
  await page.getByText(project.name, { exact: true }).click();
  await page.locator(".history-list .history-item", { hasText: mission.title }).first().click();
  await page.locator(".product-panel").waitFor();
  await page.locator(".deliverable-surface").waitFor();

  const deliverableText = await page.locator(".deliverable-surface").innerText();
  if (!deliverableText.includes("Verified final") || !deliverableText.includes("最终成稿")) {
    throw new Error(`deliverable_missing_final:${deliverableText}`);
  }
  if (deliverableText.includes("成稿审查")) {
    throw new Error("review_artifact_replaced_deliverable");
  }

  const navRows = page.locator(".artifact-nav-row");
  const rowCount = await navRows.count();
  if (rowCount !== artifacts.length + 1) {
    throw new Error(`unexpected_artifact_nav_count:${rowCount}`);
  }
  const desktopColumns = await page
    .locator(".product-reader-shell")
    .evaluate((node) => getComputedStyle(node).gridTemplateColumns.trim().split(/\s+/).length);
  if (desktopColumns < 2) {
    throw new Error(`product_reader_not_split:${desktopColumns}`);
  }
  const navHeights = await navRows.evaluateAll((rows) =>
    rows.map((row) => Math.round(row.getBoundingClientRect().height)),
  );
  const maxHeight = Math.max(...navHeights);
  const minHeight = Math.min(...navHeights);
  if (minHeight < 52 || maxHeight > 92) {
    throw new Error(`artifact_nav_height_unstable:${minHeight}-${maxHeight}`);
  }
  const titleClamp = await navRows
    .nth(2)
    .locator(".artifact-nav-copy strong")
    .evaluate((node) => {
      const style = getComputedStyle(node);
      return {
        display: style.display,
        lineClamp: style.webkitLineClamp,
        overflow: style.overflow,
      };
    });
  if (titleClamp.lineClamp !== "2" || titleClamp.overflow !== "hidden") {
    throw new Error(`artifact_title_not_clamped:${JSON.stringify(titleClamp)}`);
  }

  await page.locator(".artifact-navigator").getByRole("button", { name: /All artifacts/ }).click();
  const allText = await page.locator(".artifact-content").innerText();
  if (!allText.includes("故事大纲") || !allText.includes("最终成稿") || !allText.includes("成稿审查")) {
    throw new Error("all_artifacts_reader_missing_sections");
  }
  await page.locator(".artifact-navigator .artifact-nav-row", { hasText: /成稿审查/ }).click();
  const reviewText = await page.locator(".artifact-content").innerText();
  if (!reviewText.includes("成稿审查") || reviewText.includes("第一章草稿")) {
    throw new Error("single_artifact_reader_failed");
  }
  await page.locator(".artifact-navigator").getByRole("button", { name: /All artifacts/ }).click();
  await assertNoHorizontalOverflow(page, "desktop");
  await page.screenshot({ path: screenshotPath, fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator(".product-panel").scrollIntoViewIfNeeded();
  await assertNoHorizontalOverflow(page, "mobile");
  await page.screenshot({ path: mobileScreenshotPath, fullPage: true });
  await browser.close();
  console.log(`work_mode_product_reader_public_ui_smoke=ok screenshot=${screenshotPath} mobile=${mobileScreenshotPath}`);
}

async function installApiMocks(page) {
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    if (!url.pathname.startsWith("/api/")) {
      await route.continue();
      return;
    }
    const method = route.request().method();
    if (method === "OPTIONS") {
      await route.fulfill({ status: 204, headers: corsHeaders() });
      return;
    }
    if (url.pathname === "/api/users/me") {
      await json(route, {
        id: "user_product_reader",
        username: "product-reader-smoke",
        lang: "zh",
        settings: {},
        agentProfiles: [
          { slot: "agent_1", short: "A1", name: "Nora", color: "teal", voice: "precise" },
          { slot: "agent_2", short: "A2", name: "Vale", color: "amber", voice: "sharp" },
        ],
      });
      return;
    }
    if (url.pathname === "/api/agents") {
      await json(route, []);
      return;
    }
    if (url.pathname === "/api/conversations" || url.pathname === "/api/idle/conversations") {
      await json(route, []);
      return;
    }
    if (url.pathname === "/api/work/projects") {
      await json(route, [project]);
      return;
    }
    if (url.pathname === `/api/work/projects/${project.id}/missions`) {
      await json(route, [mission]);
      return;
    }
    if (url.pathname === `/api/work/missions/${mission.id}`) {
      await json(route, missionDetail());
      return;
    }
    if (url.pathname === `/api/work/missions/${mission.id}/events`) {
      await json(route, []);
      return;
    }
    await json(route, { detail: "not mocked" }, 404);
  });
}

function missionDetail() {
  return {
    mission,
    activeRun: null,
    latestRun: { id: "run_product_reader", missionId: mission.id, status: "completed" },
    events: [
      event("event_created", 1, "MISSION_CREATED", "Mission created"),
      event("event_product", 2, "PRODUCT_UPDATED", "Product updated", {
        productId: product.id,
        artifactId: "artifact_final",
        kind: "chapter",
        summary: product.summary,
      }),
      event("event_completed", 3, "MISSION_COMPLETED", "Mission completed"),
    ],
    artifacts,
    products: [product],
    workWindows: [
      {
        id: "window_1",
        missionId: mission.id,
        runId: "run_product_reader",
        agentSlot: "agent_2",
        title: "后段与结局正文",
        brief: "补齐后段正文并完成终局反杀。",
        expectedOutput: "chapter",
        status: "completed",
        summary: "后段与结局已完成。",
        resultArtifactId: "artifact_final",
        metadata: { windowType: "delegate" },
        createdAt,
        updatedAt: createdAt,
      },
    ],
    report: null,
  };
}

function artifact(id, title, kind, role, content) {
  return {
    id,
    missionId: mission.id,
    runId: "run_product_reader",
    kind,
    title,
    content,
    metadata: {
      artifactRole: role,
      productId,
      summary: content.slice(0, 80),
    },
    createdAt,
    updatedAt: createdAt,
  };
}

function event(id, sequence, type, message, payload = {}) {
  return {
    id,
    missionId: mission.id,
    runId: "run_product_reader",
    sequence,
    type,
    message,
    payload,
    createdAt,
  };
}

function outlineContent() {
  return [
    "故事大纲",
    "题材定位：都市异能逆袭爽文。",
    "主角在最低谷时获得万物估值能力，能看见人、物、项目与情报的真实价值。",
    "核心成长线：从被动捡漏，到主动布局，再到拆穿资本局和伪善联盟。",
  ].join("\n\n");
}

function chapterContent(title, repeatCount) {
  const sentence =
    "主角看见价格背后的真实风险，避开陷阱，反手买下被低估的筹码，把对手精心设计的局变成自己的台阶。";
  return `${title}\n\n${Array.from({ length: repeatCount }, () => sentence).join("\n")}`;
}

function reviewContent() {
  return "成稿审查\n\n大纲、章节、反派升级与终局反杀齐备。标题很长但只能影响导航文字，不应该撑乱 Product reader。";
}

async function assertNoHorizontalOverflow(page, label) {
  const hasOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  );
  if (hasOverflow) {
    throw new Error(`${label}_horizontal_overflow`);
  }
}

async function json(route, payload, status = 200) {
  await route.fulfill({
    status,
    headers: corsHeaders({ "content-type": "application/json" }),
    body: JSON.stringify(payload),
  });
}

function corsHeaders(extra = {}) {
  return {
    "access-control-allow-origin": "*",
    "access-control-allow-headers": "authorization,content-type",
    "access-control-allow-methods": "GET,POST,PATCH,DELETE,OPTIONS",
    ...extra,
  };
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
