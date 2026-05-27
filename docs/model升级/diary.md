## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
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

### 当前工程判断
- 先做最小闭环：`idle / companion_1 / companion_2 -> ContextBuilder -> HacksonOrchestrator -> model_runtime -> 保存消息`。
- V1 不做 streaming，不做搜索 UI，不做文件工具，不做代码沙盒，不展示原始 thinking。
- 先用 fake runtime 和 fixture JSON 做单元测试，再接真实 Responses API。
- 目标机验证必须开新端口和新数据库，不暂停现有服务。

### 下一步
- 目标机开新端口和新数据库做 smoke。
- 验证 register/login、idle tick、idle say、join companion_1、companion_1 follow-up、companion_2 message。
- 验证保存的 assistant message metadata 包含 orchestration 字段。
- 目标机 smoke 通过后再更新 `api.md`。

### 风险
- 如果一次性加入 streaming、web search、memory、citation，问题会混在一起，难以定位。
- `idle` 自动生成如果开高 reasoning 或搜索，会带来成本和循环失败风险。
- reasoning summary 可以产品化展示，但原始 chain-of-thought 不能展示或依赖。
