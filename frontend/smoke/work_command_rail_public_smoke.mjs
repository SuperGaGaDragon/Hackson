/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { chromium } from 'playwright';

const baseUrl = process.env.HACKSON_PUBLIC_URL || 'https://hackson.catachess.com';
const screenshot = process.env.HACKSON_COMMAND_RAIL_SCREENSHOT || '../scripts/artifacts/work_command_rail_public.png';
const mobileScreenshot = process.env.HACKSON_COMMAND_RAIL_MOBILE_SCREENSHOT || '../scripts/artifacts/work_command_rail_public_mobile.png';
const createdAt = '2026-05-28T21:00:00.000Z';
const user = `rail${Date.now()}`;
const pass = 'railpass123';
const project = { id: 'project_command_rail', name: 'Command Rail Smoke', status: 'active' };
const mission = {
  id: 'mission_command_rail',
  projectId: project.id,
  title: 'Progress filter and composer smoke',
  goal: '写一个关于法国大革命的文献综述。'.repeat(24),
  status: 'running',
  leadEmployeeId: 'agent_1',
  leadEmployeeName: 'Nora',
  leadEmployeeRole: 'precise',
  currentStep: 'Instruction added',
};
const artifact = {
  id: 'artifact_command_rail',
  missionId: mission.id,
  runId: 'run_command_rail',
  kind: 'outline',
  title: '法国大革命文献综述大纲',
  content: '一、研究范围。二、史学脉络。三、争议问题。四、可靠性检查。',
  metadata: { artifactRole: 'outline', productId: 'product_command_rail', summary: '完成文献综述大纲。' },
  createdAt,
  updatedAt: createdAt,
};
const product = {
  id: 'product_command_rail',
  title: '法国大革命文献综述',
  summary: '形成可继续扩展的论文大纲。',
  status: 'active',
  artifactIds: [artifact.id],
  latestArtifactId: artifact.id,
  deliverableArtifactId: null,
  deliveryStatus: 'none',
};

async function api(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : null;
  if (!response.ok) throw new Error(`${path}:${response.status}:${text}`);
  return body;
}

async function main() {
  await assertPublicInstructionRoute();

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(15000);
  await installApiMocks(page);
  await page.addInitScript(() => {
    window.localStorage.setItem('hackson_access_token', 'command-rail-smoke-token');
  });
  await page.goto(`${baseUrl}/work_mission/${mission.id}`, { waitUntil: 'domcontentloaded' });
  await page.locator('.work-rail').waitFor();
  await page.locator('.rail-directory').waitFor();
  await page.locator('.mission-composer').waitFor();
  await page.locator('.rail-directory').getByText('Directory', { exact: true }).waitFor();
  await page.locator('.mission-composer').getByText('Command', { exact: true }).waitFor();
  await page.getByPlaceholder('Tell the lead what to adjust').waitFor();
  const headerStart = await page.locator('.mission-head').getByRole('button', { name: 'Start' }).count();
  if (headerStart !== 0) throw new Error(`header_start_should_not_exist:${headerStart}`);
  const composerText = await page.locator('.mission-composer').innerText();
  if (!composerText.includes('Add instruction')) throw new Error(`composer_mode_wrong:${composerText}`);
  await page.locator('.mission-composer textarea').fill('补一个可靠性检查视角。');
  await page.locator('.mission-composer').getByRole('button', { name: 'Send' }).click();
  await page.locator('.timeline-card .progress-row', { hasText: 'Instruction added through smoke' }).waitFor();
  await page.locator('.progress-filters').getByRole('button', { name: /Thinking/ }).click();
  const thinkingRows = await page.locator('.progress-row').count();
  if (thinkingRows < 1) throw new Error('thinking_filter_empty');
  const thinkingText = await page.locator('.timeline-card').innerText();
  if (thinkingText.includes('Reliability\\n80 / 100')) throw new Error(`thinking_filter_leaked_reliability:${thinkingText}`);
  await page.locator('.progress-filters').getByRole('button', { name: /Reliability/ }).click();
  const reliabilityText = await page.locator('.timeline-card').innerText();
  if (!/Reliability|Evaluation/.test(reliabilityText)) throw new Error(`reliability_filter_missing:${reliabilityText}`);
  await page.locator('.progress-filters').getByRole('button', { name: /Inputs/ }).click();
  const inputText = await page.locator('.timeline-card').innerText();
  if (!inputText.includes('Instruction')) throw new Error(`input_filter_missing_instruction:${inputText}`);
  await page.locator('.progress-filters').getByRole('button', { name: /All/ }).click();
  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (horizontalOverflow) throw new Error('desktop_horizontal_overflow');
  await page.screenshot({ path: screenshot, fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.locator('.mission-composer').waitFor();
  const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (mobileOverflow) throw new Error('mobile_horizontal_overflow');
  await page.screenshot({ path: mobileScreenshot, fullPage: true });
  await browser.close();
  console.log(`work_command_rail_public_smoke=ok screenshot=${screenshot} mobile=${mobileScreenshot}`);
}

async function assertPublicInstructionRoute() {
  const auth = await api('/api/users/register', {
    method: 'POST',
    body: JSON.stringify({ username: user, email: `${user}@example.com`, password: pass }),
  });
  const headers = { Authorization: `Bearer ${auth.accessToken}` };
  const project = await api('/api/work/projects', {
    method: 'POST',
    headers,
    body: JSON.stringify({ name: 'Command Rail Smoke' }),
  });
  const mission = await api('/api/work/missions', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      projectId: project.id,
      title: 'Progress filter route probe',
      goal: '只验证运行中指令接口存在，不启动模型。',
      leadEmployeeId: 'agent_1',
    }),
  });
  const response = await fetch(`${baseUrl}/api/work/missions/${mission.id}/instruction`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ instruction: 'route probe' }),
  });
  const text = await response.text();
  if (response.status !== 409 || !text.includes('mission_not_running')) {
    throw new Error(`instruction_route_probe_failed:${response.status}:${text}`);
  }
}

async function installApiMocks(page) {
  let detail = missionDetail();
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    if (!url.pathname.startsWith('/api/')) {
      await route.continue();
      return;
    }
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status: 204, headers: corsHeaders() });
      return;
    }
    if (url.pathname === '/api/users/me') {
      await json(route, {
        id: 'user_command_rail',
        username: 'command-rail-smoke',
        agentProfiles: [
          { slot: 'agent_1', short: 'A1', name: 'Nora', color: 'teal', voice: 'precise' },
          { slot: 'agent_2', short: 'A2', name: 'Vale', color: 'amber', voice: 'sharp' },
        ],
      });
      return;
    }
    if (url.pathname === '/api/agents') {
      await json(route, []);
      return;
    }
    if (url.pathname === '/api/work/projects') {
      await json(route, [project]);
      return;
    }
    if (url.pathname === `/api/work/projects/${project.id}/missions`) {
      await json(route, [detail.mission]);
      return;
    }
    if (url.pathname === `/api/work/missions/${mission.id}`) {
      await json(route, detail);
      return;
    }
    if (url.pathname === `/api/work/missions/${mission.id}/events`) {
      await json(route, []);
      return;
    }
    if (url.pathname === `/api/work/missions/${mission.id}/events/stream`) {
      await route.fulfill({ status: 204, headers: corsHeaders(), body: '' });
      return;
    }
    if (url.pathname === `/api/work/missions/${mission.id}/instruction`) {
      detail = addInstructionEvent(detail);
      await json(route, detail);
      return;
    }
    await json(route, { detail: 'not mocked' }, 404);
  });
}

function missionDetail() {
  return {
    mission,
    activeRun: { id: 'run_command_rail', missionId: mission.id, status: 'running' },
    latestRun: { id: 'run_command_rail', missionId: mission.id, status: 'running' },
    events: [
      event('event_created', 1, 'MISSION_CREATED', 'Mission created', mission.title),
      event('event_started', 2, 'MISSION_STARTED', 'Started', 'Mission started.'),
      event('event_thinking', 3, 'MODEL_TURN_STARTED', 'Thinking', 'Selecting next tool.'),
      event('event_tool', 4, 'TOOL_CALLED', 'Tool selected', 'mission_plan', { tool: 'mission_plan', reason: '需要先建立执行计划。' }),
      event('event_plan', 5, 'MISSION_PLAN_UPDATED', '法国大革命文献综述执行计划', '先拆分研究、结构、写作与质控阶段。', {
        planTitle: '法国大革命文献综述执行计划',
        steps: [
          { status: 'in_progress', title: '建立综述框架', notes: '界定研究范围。' },
          { status: 'pending', title: '可靠性检查', notes: '补证据台账。' },
        ],
      }),
      event('event_product', 6, 'PRODUCT_UPDATED', '法国大革命文献综述大纲', '形成可继续扩展的论文大纲。', {
        productId: product.id,
        artifactId: artifact.id,
        kind: artifact.kind,
        summary: product.summary,
      }),
      event('event_eval_start', 7, 'EVALUATION_STARTED', 'Evaluation started', 'research_reliability_v1 · live'),
      event('event_reliability', 8, 'RELIABILITY_REPORTED', 'Reliability', '80 / 100', {
        reportArtifactId: 'report_command_rail',
        score: 80,
        status: 'minor_review',
        issueCounts: { high: 0, medium: 1, low: 0 },
        objective: false,
        scoreMeaning: 'Trace-backed reliability risk score, not proof of correctness.',
        confidence: 'medium',
        confidenceReason: 'Smoke report has synthetic trace coverage.',
      }),
      event('event_instruction_initial', 9, 'USER_INSTRUCTION_ADDED', 'Instruction added', '先收束为三段结构。', {
        instruction: '先收束为三段结构。',
      }),
    ],
    artifacts: [artifact],
    products: [product],
    workWindows: [
      {
        id: 'window_command_rail',
        missionId: mission.id,
        runId: 'run_command_rail',
        agentSlot: 'agent_2',
        title: '补充史学脉络',
        brief: '为综述补充史学脉络。',
        expectedOutput: 'outline',
        status: 'completed',
        summary: '完成史学脉络补充。',
        resultArtifactId: artifact.id,
        metadata: { windowType: 'delegate' },
        createdAt,
        updatedAt: createdAt,
      },
    ],
    report: null,
  };
}

function addInstructionEvent(detail) {
  const nextEvent = event(
    'event_instruction_sent',
    10,
    'USER_INSTRUCTION_ADDED',
    'Instruction added',
    'Instruction added through smoke',
    { instruction: 'Instruction added through smoke' },
  );
  return {
    ...detail,
    mission: { ...detail.mission, currentStep: 'Instruction added' },
    events: [...detail.events, nextEvent],
  };
}

function event(id, sequence, type, title, message, payload = {}) {
  return {
    id,
    missionId: mission.id,
    runId: 'run_command_rail',
    sequence,
    type,
    title,
    message,
    payload,
    createdAt,
  };
}

async function json(route, body, status = 200) {
  await route.fulfill({
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders() },
    body: JSON.stringify(body),
  });
}

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'authorization,content-type',
  };
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
