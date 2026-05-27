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

### 当前工程判断
- 先做最小闭环：`idle / companion_1 / companion_2 -> ContextBuilder -> HacksonOrchestrator -> model_runtime -> 保存消息`。
- V1 不做 streaming，不做搜索 UI，不做文件工具，不做代码沙盒，不展示原始 thinking。
- 先用 fake runtime 和 fixture JSON 做单元测试，再接真实 Responses API。
- 目标机验证必须开新端口和新数据库，不暂停现有服务。

### 下一步
- 补 `eval.md`，准备固定质量样本，避免只靠主观感觉判断模型升级效果。
- 新增 `backend/orchestration/`，先实现纯 policy 和 fake runtime 测试。
- 扩展 `model_runtime` 的可选 schema 字段，保持旧 chat-completions fallback 不破。
- 加 Responses API 非 streaming 路径，测试通过后再接入 `interactions`。

### 风险
- 如果一次性加入 streaming、web search、memory、citation，问题会混在一起，难以定位。
- `idle` 自动生成如果开高 reasoning 或搜索，会带来成本和循环失败风险。
- reasoning summary 可以产品化展示，但原始 chain-of-thought 不能展示或依赖。
