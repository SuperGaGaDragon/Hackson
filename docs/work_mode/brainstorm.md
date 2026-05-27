## header
Created at: 2026-05-26
Created by: User
Last Modified at: 2026-05-26
Last Modified by: Codex

你要做的不是“让模型自己写前端 UI”，而是：

给模型一组已经设计好的 React 展示组件，让模型选择什么时候调用哪个组件、填什么内容。

也就是模型的工具箱分两类：

1. 展示工具：告诉用户现在发生了什么
2. 执行工具：调动 Codex CLI / shell / 文件系统干活

MVP 可以非常清晰。

一句话产品定义

用户可以同时创建多个 Project，每个 Project 里可以启动多个 Mission。每个 Mission 点开后，Agent 会持续循环执行，直到任务完成、失败、被阻塞、或者用户手动停止。过程中 Agent 通过固定 React 组件展示 warning、summary、product、raw logs、progress、approval。

这就是一个 Agent Mission Runtime + Web UI。

核心不是白板，而是“组件协议”

你可以把前端设计成一套固定组件：

WarningCard
SummaryCard
ProductPanel
RawConversationPanel
ProgressTimeline
LoopStatusCard
CodexRunPanel
DiffViewer
ApprovalCard
AgentThoughtSummary

模型不能随便写 UI，但它可以调用这些组件：

{
  "type": "ui.warning",
  "title": "测试失败",
  "message": "pytest 失败，原因是缺少 JWT_SECRET 环境变量。",
  "severity": "medium"
}

前端收到后渲染成漂亮 warning。

这就是关键：

模型负责决定“展示什么”
前端负责决定“怎么展示”
MVP：一个 Agent 版本

第一版不要做多 agent。就做一个：

User
 ↓
Supervisor Loop
 ↓
Single Agent
 ↓
Codex CLI

这个 Single Agent 有两个能力：

1. 展示 UI 状态
2. 调动 Codex 干活

用户流程：

1. 用户创建 Project
2. 绑定本地 repo
3. 新建 Mission
4. 输入目标
5. 选择自主等级
6. 点击 Start
7. Agent 开始循环
8. UI 实时显示进度
9. 用户可以 Pause / Stop / Approve / Continue
10. 任务完成后生成最终 Summary + Product + Diff
Mission 页面设计

页面可以这样分：

左侧：Project / Mission 列表
中间：当前 Mission 进度
右侧：Inspector / Approval
底部：Raw Logs / Codex Output / Diff

中间主区域最重要。

Mission: 修复 Google OAuth 登录
Status: Running
Loop: iteration 4
Current action: Running Codex
Last result: backend tests failed
Next action: ask Codex to fix missing env var

然后下面是 timeline：

[✓] 读取项目结构
[✓] 找到 auth 相关文件
[✓] 调用 Codex 修改 callback route
[✗] pytest failed
[!] Warning: 缺少 JWT_SECRET
[→] 正在让 Codex 修复测试环境
模型工具箱设计

你可以给 Agent 这些工具。

1. ui.warning

用于展示问题。

{
  "tool": "ui.warning",
  "payload": {
    "title": "检测到阻塞问题",
    "message": "Codex 修改后测试失败，错误来自 CORS preflight。",
    "severity": "high",
    "suggested_next_step": "继续让 Codex 修复 CORS middleware。"
  }
}

前端渲染成红/黄 warning 卡片。

2. ui.summary

用于展示阶段性总结。

{
  "tool": "ui.summary",
  "payload": {
    "title": "第 3 轮执行总结",
    "items": [
      "已添加 Google OAuth callback route",
      "已修改 frontend login button",
      "当前测试失败，原因是缺少测试环境变量"
    ]
  }
}
3. ui.product

用于展示真正产物。

如果任务是写文章，product 就是正文。

如果任务是 coding，product 可以是：

最终结果
改了哪些文件
测试结果
下一步建议

例如：

{
  "tool": "ui.product",
  "payload": {
    "title": "最终交付结果",
    "kind": "code_result",
    "content": {
      "summary": "Google OAuth 登录流程已完成。",
      "changed_files": [
        "backend/auth.py",
        "frontend/LoginButton.tsx",
        "tests/test_auth.py"
      ],
      "tests": "pytest passed"
    }
  }
}
4. ui.raw_conversation

用于展示两个 AI 或 agent 的原始交流。

MVP 一个 agent 也可以先保留这个组件。

{
  "tool": "ui.raw_conversation",
  "payload": {
    "messages": [
      {
        "role": "agent",
        "content": "I need to inspect the auth routes first."
      },
      {
        "role": "codex",
        "content": "Found backend/auth.py and frontend/login.tsx."
      }
    ]
  }
}

这个默认折叠，不要占主界面。

5. loop.continue

这是最重要的。

模型可以说：

{
  "tool": "loop.continue",
  "payload": {
    "reason": "测试还没有通过，需要继续修复。",
    "next_goal": "Ask Codex to fix the failed pytest case.",
    "stop_condition": "All tests pass or max_iterations reached."
  }
}

但是注意：不能完全相信模型无限循环。

外层 Supervisor 必须硬编码限制：

max_iterations
max_runtime
max_cost
no_progress_limit
dangerous_action_gate
user_stop

所以模型可以“建议继续”，但系统决定是否真的继续。

6. codex.run

真正干活。

{
  "tool": "codex.run",
  "payload": {
    "goal": "Fix the failing pytest related to JWT_SECRET.",
    "repo_path": "/repos/cyber1924",
    "mode": "edit",
    "allowed_commands": ["pytest", "npm test", "python"],
    "forbidden_commands": ["rm -rf", "git push", "railway up"]
  }
}

后端收到后调 Codex CLI。

最重要的循环设计

你的核心 runtime 可以这么写：

while mission.status == "running":
    state = load_mission_state(mission_id)

    agent_output = call_agent(
        goal=mission.goal,
        state=state,
        recent_events=recent_events,
        available_tools=[
            "ui.warning",
            "ui.summary",
            "ui.product",
            "ui.raw_conversation",
            "codex.run",
            "loop.continue",
            "loop.stop",
            "ask_user"
        ]
    )

    for tool_call in agent_output.tool_calls:
        execute_tool(tool_call)

    save_events(agent_output)

    if should_stop(mission):
        break

重点是：

LLM 不是一直运行。
是外层 while loop 一直调它。

所以“点开一次，不停止就一直继续”的实现方式是：

用户点击 Start
↓
后端创建 mission loop
↓
每一轮调用 Agent
↓
Agent 调 Codex 或展示 UI
↓
保存结果
↓
判断是否继续
↓
继续下一轮
Stop Condition 要产品化

用户创建 Mission 时，可以选择：

一直循环直到：
1. Agent 判断任务完成
2. 所有测试通过
3. Reviewer 没有新问题
4. Product 生成完成
5. 用户手动停止
6. 达到最大轮数
7. 遇到需要审批的危险操作
8. 连续 N 轮没有进展

UI 上显示：

Loop Condition:
Run until tests pass or user stops.

Safety:
Max iterations: 20
Max runtime: 60 min
Dangerous commands: require approval

这个非常产品级。

多 Project 同时开

数据结构上要这样：

Workspace
  └── Project
        └── Mission
              └── Run
                    └── Step
                          └── Event

例如：

Workspace: Super
  Project: Cyber1924
    Mission: Fix OAuth
    Mission: Add planner UI

  Project: Catie Chess
    Mission: Add training dashboard
    Mission: Write NeurIPS rebuttal helper

每个 Mission 都是一个独立 loop。

每个 loop 有自己的：

status
agent state
codex thread
repo worktree
logs
events
diff
product

这样用户可以同时跑多个任务。

UI 组件和事件对应表

你可以这样设计：

Event Type	React Component	用途
MISSION_STARTED	MissionHeader	显示任务开始
STEP_STARTED	ProgressTimeline	显示当前步骤
CODEX_RUNNING	CodexRunPanel	显示 Codex 正在干活
WARNING	WarningCard	显示问题
SUMMARY	SummaryCard	显示阶段总结
PRODUCT_UPDATED	ProductPanel	显示当前产物
RAW_MESSAGE	RawConversationPanel	显示原始对话
TEST_FAILED	TestPanel	显示测试失败
TEST_PASSED	TestPanel	显示测试通过
APPROVAL_REQUIRED	ApprovalCard	等用户批准
MISSION_COMPLETED	FinalReport	最终报告

这样前端非常稳定。

一个 Agent 的 Prompt 应该怎么写

你可以硬编码 system prompt：

You are a mission agent inside an autonomous coding workspace.

Your job is to:
1. Understand the user's mission.
2. Decide the next best action.
3. Use UI tools to report progress.
4. Use codex.run when code changes are needed.
5. Continue looping until the mission is complete, blocked, or unsafe.
6. Never hide problems. Use ui.warning when something is wrong.
7. Use ui.summary after major progress.
8. Use ui.product when there is a user-facing deliverable.
9. Use loop.continue if more work is needed.
10. Use loop.stop only when the mission is complete or blocked.

You must output structured tool calls only.

这样模型就像一个“任务驾驶员”。

MVP 的最小版本可以非常简单

不要一开始做很多复杂权限。

MVP 只做：

Project List
Mission List
Mission Detail
Start / Stop
Codex Run
Progress Timeline
Warning Card
Summary Card
Product Panel
Raw Log Panel

后端只需要：

POST /projects
POST /missions
POST /missions/:id/start
POST /missions/:id/stop
GET /missions/:id/events
WebSocket /missions/:id/stream

worker 只需要：

run_agent_loop(mission_id)
run_codex(goal, repo_path)
save_event(event)

这就能跑起来。

两个 Agent 版本怎么加

V2 再做：

Worker Agent
Reviewer Agent

流程：

User
 ↓
Supervisor Loop
 ↓
Worker Agent
 ↓
Codex CLI
 ↓
Reviewer Agent
 ↓
Supervisor decides continue or stop

执行逻辑：

1. Worker 用 Codex 干活
2. Reviewer 看 diff / logs / product
3. Reviewer 输出问题
4. 如果有问题，Supervisor 让 Worker 继续修
5. 如果没问题，任务完成

两个 agent 的 raw conversation 可以展示在：

Raw Conversation Panel

但默认折叠。

用户主要看：

Progress
Warnings
Product
Reviewer Comments

不要让用户被 agent 聊天淹没。

你的“硬编码调动”想法是对的

MVP 不要做太智能的 planner。

直接硬编码一个循环就够：

Start Mission
↓
Agent decides next action
↓
If needs code:
    run Codex
↓
If Codex returns error:
    show warning
    continue
↓
If Codex returns diff:
    run tests
↓
If tests fail:
    continue
↓
If tests pass:
    show summary/product
    stop

也就是：

智能在单步判断
流程由系统硬编码

这比完全交给模型稳定很多。

最终建议

你现在这个产品应该这样切：

V0：单 Agent + Codex CLI + UI 事件流
V1：循环执行 + stop condition + warning/summary/product/raw panels
V2：Worker + Reviewer 两 Agent
V3：用户自定义 agent graph
V4：多 Project 多 Mission 并行

第一版最小闭环：

用户输入任务
↓
Agent 选择展示 summary
↓
Agent 调 codex.run
↓
Codex 修改代码
↓
系统保存 logs/diff
↓
Agent 展示 warning 或 product
↓
如果没完成，loop.continue
↓
直到完成或用户停止

你的产品核心可以总结成一句：

模型不负责画 UI，模型负责发事件；前端用固定漂亮组件展示事件；后端用硬编码 loop 持续调动模型和 Codex，直到任务完成或被用户停止。
