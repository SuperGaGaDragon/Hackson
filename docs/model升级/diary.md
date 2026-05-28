## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Model 升级工程日志

## 2026-05-27

### 已完成
- 阅读 `agents/` 约束，确认本次必须先落文档，再进入代码。
- 阅读项目 README、后端架构、上下文、交互、模型运行时、前端功能文档。
- 判断 `goal.md` 方向可行，但它不是简单换模型，而是统一 Orchestrator 产品迭代。
- 写入 `version.md`：
  - V1：质量升级，三种模式统一走 Hackson Orchestrator，同步返回。
  - V1.1：体验升级，加 streaming、Thinking/Search 状态、citation。
  - V1.2：工具和 memory 升级。
  - V2：更完整的 ChatGPT-like 产品层。
- 写入 `plan.md`，明确产品目标、非目标、模块边界、文件计划、测试矩阵、目标机 smoke、回滚策略。
- 写入 `eval.md`，固定 idle、companion_1、companion_2 的质量样本和评分口径。
- 新增 `backend/orchestration/`，实现 V1 mode policy 和 Hackson Orchestrator service。
- 扩展 `model_runtime`：
  - 保留默认 chat-completions fallback。
  - 增加 `HACKSON_MODEL_API_MODE=responses` 配置路径。
  - 增加非 streaming Responses client。
  - 标准化 provider response id、reasoning summary、tool events metadata。
- 将 `interactions` 接入 Hackson Orchestrator，`idle`、`companion_1`、`companion_2` 的生成路径统一经过 mode policy。
- Assistant message metadata 现在记录 `orchestration_policy`、`reasoning_effort`、`tool_policy`、`provider` 等审计字段。
- 本地测试通过：
  - `backend/orchestration/tests`: 5 passed.
  - `backend/model_runtime/tests`: 17 passed.
  - `backend/context/tests`: 9 passed.
  - `backend/interactions/tests`: 21 passed.
  - backend 全模块逐目录 unittest: all passed.
  - `npm --prefix frontend run build`: passed.
- 目标机 smoke 通过：
  - 新目录：`~/hackson_orchestrator_v1_8148`。
  - 新端口：`127.0.0.1:8148`。
  - 新数据库：`hackson_orchestrator_v1_8148_fake`。
  - Fake OpenAI-compatible relay：`127.0.0.1:18148`。
  - 验证 `register`、`idle tick`、`idle say`、`idle join`、`companion_1 follow-up`、`companion_2 message`。
  - 验证 Responses mode 下 assistant message metadata 包含 `orchestration_policy`、`reasoning_effort`、`tool_policy`、`provider`、`provider_response_id`、`reasoning_summary`。
  - 上游真实 provider smoke 遇到稳定 `429 {"detail":"model_rate_limited"}`，后端未崩溃。
  - 临时 `8148` 和 `18148` 进程已清理，未触碰 `8145`、`8147`、`8130`。
- Public `8145` 已推广：
  - 同步 HEAD 到 `~/hackson_domain_8145`，保留目标机 `.env` 和 `.venv`。
  - 目标机 public 目录测试通过：orchestration `5`、model_runtime `17`、interactions `21`。
  - 目标机 frontend 用 Node `20.19.6` 构建通过。
  - 已重启 `hackson-domain-8145.service`。
  - `127.0.0.1:8145/health` 和 `https://hackson.catachess.com/health` 返回 `{"status":"ok"}`。
  - Public API smoke 验证 register、conversation creation；模型 backed routes 当前受上游 provider rate limit，稳定返回 `429 {"detail":"model_rate_limited"}`。
  - Public 代码已包含 `backend/orchestration/` 和 `InteractionService -> HacksonOrchestrator` 路径。
- 追加 Codex CLI provider：
  - 新增 `HACKSON_MODEL_PROVIDER=codex_cli` 路径，后端通过目标机自己的 `codex exec` 调用模型。
  - 目标机安装 `@openai/codex` CLI，版本 `0.134.0`。
  - 目标机直接验证 `codex exec -m gpt-5.4` 返回 `OK`。
  - 目标机后端 `ModelRuntime.generate` 直接验证返回 `HACKSON_OK`，provider 为 `codex_cli`。
  - 目标机 public `8145` API smoke 通过：`register`、`conversation`、`idle tick`、`companion_1 join` 均成功，assistant metadata 中 `provider=codex_cli`。
  - Public service 已恢复并运行：`hackson-domain-8145.service` active，`127.0.0.1:8145/health` 与 `https://hackson.catachess.com/health` 均正常。
- 修复 Work Mode Codex 链路：
  - 复现用户失败：旧 Mission 报 `model_codex_cli_unavailable`，而 idle/comp 正常。
  - 根因：idle/comp 的 `interactions` 已注入 `CodexCliClient`；Work Mode 的 `ModelMissionRunner` 只注入 OpenAI-compatible client，provider 配成 `codex_cli` 时找不到客户端。
  - 第一次修复后继续 smoke，错误变为 `model_timeout`，说明已进入真实 Codex 调用，但 8000 字小说单次生成超过 180 秒。
  - 产品级收束：V0.5 Work Mission 定义为单次有界 first-pass artifact。长篇任务先生成可用样章/大纲，不在一个后台请求里写完整 8000 字。
  - 工程修复：Work Mode 注入 `CodexCliClient`；V0.5 prompt 限定 600-1200 中文字；Codex reasoning effort 降到 `low`；模型失败时同时把 active Step 标记为 `failed`。
  - 本地测试通过：逐个运行 backend 所有 `*/tests` 目录；Work Mode `18`、model_runtime `23`、interactions `21` 均通过。
  - 目标机 public `8145` 测试通过：Work Mode `18`、model_runtime `23`、interactions `21`。
  - 目标机 public smoke 通过：`撰写一个8000字小说` Mission `6a17428e1c922129e72e8968` 完成，事件链到 `MISSION_COMPLETED`，生成 1 个 text Artifact，长度 `1055`，metadata 为 `provider=codex_cli`、`modelName=gpt-5.4`。
- 实施 Work Mode V1 model-driven loop：
  - 先落 `docs/work_mode/final_version.md` 文档群，废弃 legacy 文档作为执行源。
  - Loop 1：实现严格 JSON Action tool protocol，拒绝普通文本、未知工具、多工具调用和 schema 错误。
  - Loop 2：新增 Product / Artifact lineage / Work Window 持久化，Mission detail 返回 `products`、`workWindows`、`artifacts`。
  - Loop 3：新增 Lead/Delegate context builder 和 JSON Action model client。
  - Loop 4：新增 `WorkModeToolExecutor` 和 `MissionLoopRunner`，工具顺序由模型返回的 tool action 决定，后端不写死流程。
  - Loop 5：实现 V1 工具：`mission_plan`、`work_product`、`inspect_product`、`delegate_agent`、`ask_user`、`finish_mission`、`block_mission`。
  - Loop 6：后端 start route 接入 V1 runner；frontend Work UI 增加 Timeline、Work Windows、Product Panel，窗口默认折叠，Product 以持久化数据为事实源。
  - Loop 7：新增 deterministic full smoke `scripts/work_mode_v1_full_smoke.py`，目标是完整 8000 CJK 验收，不依赖真实模型波动。
  - Loop 8：目标机新隔离服务 `hackson-work-v1-8150.service`，新目录 `~/hackson_work_v1_8150`，新库 `hackson_work_v1_8150`，未触碰 public `8145`、Idle `8147`、Work V0.5 `8148`、legacy `8130`。
  - 本地测试通过：Work Mode `46`、model_runtime `24`、interactions `21`、frontend build、deterministic full smoke `final_cjk=9936`。
  - 目标机测试通过：Work Mode `46`、model_runtime `24`、frontend build、deterministic full smoke `events=12/windows=2/products=1/artifacts=4/final_cjk=9936`。
  - 目标机真实 Codex HTTP smoke：真实模型能自动调用 `mission_plan` 和 `work_product`，持久化真实大纲 Product；长模型调用 timeout 后进入 `paused_retryable`，没有 fake artifact。
  - 修复 `codex_cli` timeout 清理：超时后 kill 整个 process group，目标机验证没有 orphan `codex exec`。
  - 修复 `paused_retryable` resume：公开 `POST /api/work/missions/{missionId}/start` 可对同一 Mission 创建新 run 并继续；目标机 resume smoke 最终 `MISSION_COMPLETED`。
- 强化 Work Mode V1 产品门禁：
  - `finish_mission` 现在先校验 final Product 和 final Artifact 都属于当前 Mission，再标记 Product final 和 Mission completed。
  - `MISSION_COMPLETED` 事件 payload 记录 `finalProductIds` 和 `finalArtifactIds`，方便 smoke、UI 和后续审计。
  - 抽出 deterministic smoke helper，保留 in-process full smoke，同时新增 authenticated HTTP full smoke。
  - 新增 Playwright browser smoke：通过真实 React UI 注册、进入 Work、创建项目和 Mission、启动 V1 loop，验证 Timeline、Windows、Product、Final 状态、窗口默认折叠、窗口可展开、最终正文 CJK 字数 `>=8000`。
  - 本地通过：Work Mode `48`、model_runtime `24`、interactions `21`、frontend build、in-process full smoke、HTTP full smoke、browser smoke。
  - 目标机新隔离服务 `hackson-work-v1-8160.service`，新目录 `~/hackson_work_v1_8160`，新库 `hackson_work_v1_8160`，绑定 `127.0.0.1:8160`。
  - 目标机通过：Work Mode `48`、model_runtime `24`、interactions `21`、frontend build、in-process full smoke `final_cjk=9936`、HTTP full smoke `final_cjk=9936`、browser smoke `windows=2/final_cjk=9936`。
  - 目标机 `127.0.0.1:8160/health` 返回 `{"status":"ok"}`，静态首页返回 `200`，未停止 `8145/8147/8148/8150/8130` 等现有服务。
- 推广 Work Mode V1 hardening 到公网：
  - 用户确认“切公网”后，同步当前 HEAD 到 `~/hackson_domain_8145`，保留 `backend/.env`、`backend/.venv` 和运行态配置。
  - Public 目录验证通过：Work Mode `48`、model_runtime `24`、interactions `21`、frontend build。
  - 重启 `hackson-domain-8145.service`，服务 active。
  - `127.0.0.1:8145/health` 和 `https://hackson.catachess.com/health` 返回 `{"status":"ok"}`，公网首页返回 `200`。
  - Public deterministic full smoke 和 HTTP full smoke 均通过，`final_cjk=9936`。
  - Public 真实浏览器触发的 Codex Work V1 Mission `6a17978c519166b7a2582db0` 没有假完成，真实链路产生 `MISSION_PLAN_UPDATED`、`PRODUCT_UPDATED` 后按 timeout 进入 `paused_retryable model_timeout`，没有 orphan `codex exec`。
- 定位并修复 Work V1 长模型轮次体验问题：
  - 结论：`paused_retryable` 是正确安全底线，但正常长写作任务直接 pause 不是产品级体验。
  - 补充 `docs/work_mode/issues/issue7-long-turn-progress.md`，明确当前 `docs/work_mode` 未完全完成，真实公网 8000 字 Codex smoke 未完成，且 V1.0 需要非 streaming 进度层。
  - 后端新增安全 lifecycle events：`MODEL_TURN_STARTED`、`MODEL_TURN_HEARTBEAT`、`MODEL_TURN_COMPLETED`、`MODEL_TURN_RETRYING`、`MODEL_TURN_INVALID`、`TOOL_CALLED`、`WORK_WINDOW_FAILED`。
  - Lead turn 对 retryable provider error 先做有限自动 retry，耗尽后才进入 `paused_retryable`。
  - Delegate window 打开后若模型超时/失败，会标记窗口 `failed` 并发 `WORK_WINDOW_FAILED`，不再让 UI 看起来还在后台跑。
  - 前端新增 `ActivityStrip`，展示最近一次安全运行状态，用户能看到 Thinking、Tool、Retry、Done 等进度。
  - 新增 `HACKSON_WORK_MODE_V1_RETRYABLE_RETRIES` 和 `HACKSON_WORK_MODE_V1_HEARTBEAT_SECONDS`，让 retry 和 heartbeat 节奏可运维配置。
  - 本地验证通过：backend 全目录 unittest、Work Mode `52`、model_runtime `24`、interactions `21`、frontend build、in-process full smoke、HTTP full smoke、browser smoke，最终 `final_cjk=9936`。
  - 目标机新隔离服务 `hackson-work-v1-progress-8161.service`，新目录 `~/hackson_work_v1_progress_8161`，新库 `hackson_work_v1_progress_8161`，绑定 `127.0.0.1:8161`。
  - 目标机通过：Work Mode `52`、model_runtime `24`、interactions `21`、frontend build、in-process full smoke `events=30/final_cjk=9936`、HTTP full smoke `events=30/final_cjk=9936`、browser smoke `windows=2/final_cjk=9936`。
  - 目标机 `127.0.0.1:8161/health` 返回 `{"status":"ok"}`，静态首页包含 React root 和 assets，未停止 `8145/8147/8148/8150/8160/8130` 等现有服务。
  - 推广到 public `8145`：public 目录 Work Mode `52`、model_runtime `24`、interactions `21`、frontend build、full smoke、HTTP smoke 全部通过后，重启 `hackson-domain-8145.service`。
  - 公网验证：`https://hackson.catachess.com/health` 和 `/` 返回 `200`，新 assets 为 `index-HYSRYan8.js` / `index-cInveBCH.css`。
  - 真实 Codex 小任务 Mission `6a17a145f01aad81f13bca71` 完成，事件链包含每轮 `MODEL_TURN_STARTED`、`MODEL_TURN_COMPLETED`、`TOOL_CALLED`，最终 `MISSION_COMPLETED`，没有 orphan Codex 进程。
- 盯公网用户写小说 Mission `6a17a659f01aad81f13bca8a`：
  - 真实链路证明 Lead Agent 没有写死流程：先 `mission_plan`，再 `work_product` 建立大纲，然后连续选择 `delegate_agent`。
  - 第一至第二章、第三至第四章两个 Work Window 完成，说明 Codex provider 和窗口执行可用。
  - 第五至第六章窗口失败为 `delegate_result_invalid`，不是 429、不是 401、不是 HTTP 500；根因是 Delegate 返回结果没有通过严格 JSON wrapper 校验。
  - 新增 `docs/work_mode/issues/issue8-delegate-result-tolerance.md`，明确 Lead 仍严格 JSON tool action，但 Delegate 写作结果需要容错 ingestion。
  - 修复：Delegate 结果支持 fenced JSON、嵌入 JSON、可用非结构化正文 canonicalize 为 completed Artifact；真正空结果或破损 JSON-like 结果标记窗口 failed，并进入 `paused_retryable` 而不是 unrecoverable `failed`。
  - 本地验证通过：Work Mode `55`、model_runtime `24`、interactions `21`、frontend build、in-process full smoke、HTTP full smoke、browser smoke，最终 `final_cjk=9936`。
  - 目标机隔离服务 `hackson-work-v1-delegate-8162.service` 通过：Work Mode `55`、model_runtime `24`、interactions `21`、frontend build、full smoke、HTTP smoke、Delegate unstructured-prose HTTP regression、browser smoke。
  - 推广到 public `8145`：public 目录测试、build、full smoke、HTTP smoke、Delegate tolerance regression 全部通过后重启 `hackson-domain-8145.service`。
  - 公网验证：`https://hackson.catachess.com/health` 和 `/` 返回 `200`，runtime Delegate 纯文本解析返回 `completed/delegateStructured=false`，没有 orphan Codex 进程。

### 当前工程判断
- 先做最小闭环：`idle / companion_1 / companion_2 -> ContextBuilder -> HacksonOrchestrator -> model_runtime -> 保存消息`。
- V1 不做 streaming，不做搜索 UI，不做文件工具，不做代码沙盒，不展示原始 thinking。
- 先用 fake runtime 和 fixture JSON 做单元测试，再接真实 Responses API。
- 目标机验证必须开新端口和新数据库，不暂停现有服务。
- Work V0.5 只保证单次有界产物；完整 8000 字长文需要后续 V1 supervisor loop 拆成多步生成、续写、合并、验收。
- Work V1 核心闭环已经成立：模型自己选工具，后端只管 schema、权限、持久化、状态机、UI 合同。
- 真实 Codex CLI 可跑通 V1 loop，但长文本质量和时延仍不适合直接在 HTTP background task 里无限等待；当前先用 lifecycle events、bounded retry、failed window cleanup 改善产品体验，后续仍需要 durable queue 和 native API/tool calling。

### 下一步
- 继续观察 `codex_cli` 冷启动延迟；如需要，再做常驻 worker 或队列化。
- V1.1 再做 streaming、Thinking/Search 状态、citation UI。
- Work V1 hardening 已推广到 public `8145`；`8160` 可继续作为 isolated 对照 smoke 环境保留。
- Work V1 progress hardening 已推广到 public `8145`；`8161` 可继续作为 isolated 对照 smoke 环境保留。
- Work V1.1 增加 native tool calling adapter；V1.2 再加 streaming，不改变当前 ToolExecutor。
- Work V1.3 再加并行 Work Window；V2 才引入 Codex/file/browser/computer tools。

### 风险
- 如果一次性加入 streaming、web search、memory、citation，问题会混在一起，难以定位。
- `idle` 自动生成如果开高 reasoning 或搜索，会带来成本和循环失败风险。
- reasoning summary 可以产品化展示，但原始 chain-of-thought 不能展示或依赖。
- `codex_cli` 是进程级调用，稳定但比直接 HTTP relay 更重；当前先完成最小闭环，后续再优化性能。
- 真实 8000 字全量模型 smoke 成本高、时延长；当前已用 deterministic full smoke 固定产品验收，用真实模型 smoke 验证链路、暂停和恢复。
- 当前 `8150` 是 isolated smoke，不是 public product；推广 public 前需要用户确认。
