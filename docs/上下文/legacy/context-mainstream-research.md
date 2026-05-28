# 上下文处理主流方案与论文综述

版本：v0.1  
日期：2026-05-25  
作者：Codex research draft

## 1. 本文目的

本文总结当前大模型应用、长期陪伴型 Agent、多 Agent 系统、RAG、长上下文与 Agent 记忆方向的主流上下文处理方法。目标不是做论文罗列，而是为 Hackson 的上下文系统设计提供可落地的技术判断。

Hackson 的核心难点不是“把聊天记录塞进 prompt”，而是让两个具有不同人格的 Agent 在三种模式中稳定运行：

- Idle Life Mode：两个 Agent 自主互动、形成经历、写日记、成长。
- Companion Mode：用户随时插入或新开对话，Agent 必须围绕用户且不丢失必要上下文。
- Work Mode：Agent 协作推进任务，并能调用 Codex CLI 等工具。

这要求上下文系统同时解决：长期记忆、短期对话、人格一致性、多 Agent 共享事实、用户隐私、工具状态、成本控制、延迟控制和幻觉控制。

## 2. 当前主流上下文处理范式

### 2.1 直接长上下文

做法：把更多历史消息、文档、工具结果直接放进模型上下文窗口。

优点：

- 架构简单，第一版开发最快。
- 对短期对话最稳定，减少检索遗漏。
- 适合 Companion Mode 中最近几十轮的连续聊天。

缺点：

- 成本随历史长度线性上升。
- 延迟上升。
- 模型并不能等价地使用所有上下文。
- 容易发生“重要信息在中间被忽略”的问题。

关键论文：Lost in the Middle: How Language Models Use Long Contexts。该论文发现，长上下文模型在相关信息位于输入开头或结尾时表现更好，相关信息位于中间时性能会明显下降。这意味着“上下文窗口变大”不等于“记忆系统解决”。来源：https://arxiv.org/abs/2307.03172

工程结论：

- 不能把 Hackson 的长期 idle 记录直接全部塞进 prompt。
- 重要人格、当前目标、用户指令、最近事件应放在上下文的前部或后部。
- 中间区域只适合放可丢失的背景材料，不适合放核心事实。

### 2.2 摘要压缩

做法：对历史对话进行滚动总结，把很长的聊天压缩成短摘要。

常见策略：

- rolling summary：每 N 轮更新一次会话摘要。
- hierarchical summary：短摘要聚合成长摘要，再聚合成长期档案。
- event summary：只提取事件、承诺、偏好、关系变化。
- persona summary：把对人格有影响的经历写入人格状态。

优点：

- 成本低，适合持续运行。
- 对陪伴类产品非常必要。
- 可以把 idle 中的经历转化成 Agent 的“人生轨迹”。

缺点：

- 摘要会丢失细节。
- 摘要模型可能引入幻觉。
- 多次摘要会产生漂移。
- 如果摘要直接改人格，可能造成 Agent 性格失控。

工程结论：

- 摘要不能只有一份。Hackson 至少需要会话摘要、事件摘要、关系摘要、人格候选更新、事实记忆五类产物。
- 摘要写入必须有 schema 和置信度，不能让 Agent 随意改自己的核心人格。
- 原始消息仍要入库，摘要只是索引和压缩层。

### 2.3 RAG：检索增强生成

做法：把历史消息、文档、日记、工具结果切块后存入数据库或向量库。每次生成前根据当前问题检索相关内容，再拼入 prompt。

优点：

- 能处理远超上下文窗口的历史。
- 可按用户、Agent、模式、时间、主题进行检索。
- 适合用户突然问“你还记得上次我们说过什么吗？”

缺点：

- 检索质量决定回答质量。
- 向量相似度不等于真正相关。
- 对多跳关系、长期关系变化、人格演化不够强。
- RAG 会引入延迟和工程复杂度。

主流增强方向：

- query rewriting：把用户问题改写成更适合检索的问题。
- hybrid search：向量检索 + 关键词检索 + 时间过滤。
- reranking：先召回多条，再用模型或 reranker 重排。
- multi-hop retrieval：分多步找相关事实。
- self-rag：模型判断是否需要检索、检索结果是否足够、回答是否被证据支持。

关键论文：

- Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection。提出模型在生成过程中学习何时检索、如何批判检索结果和自身输出。来源：https://arxiv.org/abs/2310.11511
- LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs。提出使用更长的检索单元，并结合长上下文模型改善检索增强生成。来源：https://arxiv.org/abs/2406.15319
- LongRAG: A Dual-Perspective Retrieval-Augmented Generation Paradigm for Long-Context Question Answering。强调从全局信息和局部事实两个视角处理长上下文问答。来源：https://arxiv.org/abs/2410.18050

工程结论：

- Hackson 不应该只做普通向量 RAG。普通 RAG 适合“找资料”，不够适合“长期人格与关系”。
- 检索结果必须按类型进入上下文：事实、事件、关系、人格、目标、工具状态分开处理。
- 需要 retrieval policy：不同模式下决定检索什么，而不是每次都查所有记忆。

### 2.4 OS 式分层记忆：MemGPT

做法：把 LLM 的上下文当成 RAM，把外部数据库当成磁盘。Agent 通过工具调用主动把信息从长期存储调入当前上下文，或把当前信息写入长期存储。

关键论文：MemGPT: Towards LLMs as Operating Systems。该论文提出 virtual context management，用 OS 内存层级的方式管理有限上下文，并应用在文档分析和多会话聊天。来源：https://arxiv.org/abs/2310.08560

核心思想：

- main context：当前必须在 prompt 中的短期上下文。
- archival memory：长期外部记忆。
- recall memory：历史对话回忆。
- memory tools：模型可以主动读写记忆。

优点：

- 非常适合长期陪伴类 Agent。
- 能让 Agent 主动管理记忆，而不是完全依赖后端硬拼 prompt。
- 对多会话聊天有直接参考价值。

缺点：

- 如果完全交给模型读写，容易写入错误记忆。
- 工具调用成本高。
- 需要复杂的权限、审计和回滚机制。

工程结论：

- Hackson 可以借鉴 MemGPT 的“分层上下文”，但不能完全让 Agent 自由改记忆。
- 应采用“Agent 提议，系统审核，分层写入”的机制。
- 用户可见的日记和不可见的系统记忆要分离。

### 2.5 生成式 Agent 架构：Observation、Reflection、Planning

关键论文：Generative Agents: Interactive Simulacra of Human Behavior。该论文构建了一个类似模拟小镇的 Agent 系统，核心模块是 observation、reflection、planning，Agent 会记录经历、反思、制定计划，并产生可信的社会行为。来源：https://arxiv.org/abs/2304.03442

核心机制：

- observation：Agent 观察到事件并写入 memory stream。
- reflection：当记忆重要性累积到阈值时，生成高层反思。
- planning：根据记忆和当前状态制定行动计划。

优点：

- 与 Hackson 的 Idle Life Mode 高度相关。
- 可以解释“AI 自己生活、闲聊、写日记、关系变化”。
- 证明反思和计划对可信行为很重要。

缺点：

- 论文场景偏模拟环境，不直接等于产品级聊天系统。
- 记忆重要性的评分和反思质量依赖模型。
- 用户隐私和可控性需要额外设计。

工程结论：

- Idle Mode 不应只是 while loop 聊天。它应该是“观察 - 反思 - 计划 - 行动 - 写入”的 Agent 生命周期。
- 每次 idle 对话都要产生结构化事件，而不是只存纯聊天。
- 反思不应每轮发生，应按时间、重要性、关系变化和平台设定的 demo 策略触发。V1 不依赖用户自定义模型配置。

### 2.6 反思式学习：Reflexion

关键论文：Reflexion: Language Agents with Verbal Reinforcement Learning。该框架不通过训练模型权重来学习，而是把反馈转化为语言反思，存入 episodic memory，影响之后的决策。来源：https://arxiv.org/abs/2303.11366

适用场景：

- Work Mode 中任务失败后的复盘。
- Companion Mode 中用户明确纠正 Agent 后的行为更新。
- Idle Mode 中 Agent 对自己发言风格或关系变化的反思。

优点：

- 不需要微调模型。
- 容易工程化。
- 对工具调用、代码任务、长期任务很适合。

缺点：

- 反思可能过拟合单次反馈。
- 如果没有冲突检测，旧反思和新反思会互相矛盾。

工程结论：

- Hackson 需要“反思记忆”，但必须带来源、触发原因、适用范围和过期策略。
- 用户反馈优先级高于 Agent 自我反思。
- 失败复盘适合进入 Work Mode 的 task memory，不应污染陪伴人格。

### 2.7 长期陪伴记忆：MemoryBank

关键论文：MemoryBank: Enhancing Large Language Models with Long-Term Memory。该工作面向长期 AI Companion，存储互动历史、总结事件，并借鉴遗忘曲线更新记忆强度。来源：https://arxiv.org/abs/2305.10250

核心价值：

- 陪伴产品需要长期用户建模。
- 记忆不是永久等权，应该有强度、时间衰减、重复强化。
- 用户偏好、共同经历、情感事件需要被长期保留。

工程结论：

- Hackson 的 Companion Mode 应有 memory strength。
- 被反复提到的偏好、名字、关系事件应强化。
- 低价值 idle 闲聊应自然衰减，不必永久进入高优先级上下文。

### 2.8 Agentic Memory：A-MEM

关键论文：A-MEM: Agentic Memory for LLM Agents。该论文借鉴 Zettelkasten，将记忆组织成动态互联的笔记网络，新记忆写入时生成描述、关键词、标签，并与历史记忆建立链接，甚至触发旧记忆的更新。来源：https://arxiv.org/abs/2502.12110

核心价值：

- 记忆不是静态 append-only 日志。
- 记忆之间应该有链接、主题、演化。
- 新经历会改变旧经历的解释。

优点：

- 很适合 Hackson 的“人格成长”和“关系变化”。
- 比普通向量库更适合多 Agent 关系网络。

风险：

- 记忆自我演化可能篡改事实。
- 如果没有版本历史，会丢失原始依据。
- 过度整理会让 Agent 看起来“被系统改写人生”。

工程结论：

- Hackson 可以采用“记忆卡片 + 链接图”的方式组织长期记忆。
- 旧记忆允许追加 interpretation，不允许覆盖 original event。
- 人格变化必须来自多次证据累积，而不是单条 idle 对话。

### 2.9 Skill Library 与长期能力成长

关键论文：Voyager: An Open-Ended Embodied Agent with Large Language Models。该系统在 Minecraft 中让 Agent 自动探索、形成课程、保存技能库，并在新世界复用技能。来源：https://arxiv.org/abs/2305.16291

对 Hackson 的意义：

- Work Mode 不应该只存聊天记录，还要沉淀“可复用技能”。
- Agent 调用 Codex CLI 完成任务后，可以把成功流程沉淀成 task pattern。
- 桌宠/硬件行为也可以沉淀成 interaction skill。

工程结论：

- Work Mode 需要 task memory 和 skill memory。
- 技能库不应混入陪伴记忆。
- 成功经验、失败经验、工具调用模板应结构化存储。

### 2.10 图谱化 RAG：GraphRAG

做法：把文档或记忆组织成实体、关系、社区摘要，检索时不仅返回相似文本，也返回相关实体网络和高层主题。

代表工程：Microsoft GraphRAG。来源：https://www.microsoft.com/en-us/research/project/graphrag/

适用场景：

- 多 Agent 关系。
- 用户、Agent、项目、任务、工具、记忆之间的复杂关联。
- 从长期历史中回答“他们之间关系怎么变化了？”

优点：

- 比纯向量检索更能处理关系和全局问题。
- 适合做可解释的记忆系统。

缺点：

- 构图成本高。
- 实时更新复杂。
- 对 V1 来说可能过重。

工程结论：

- V1 可以先做轻量 memory graph：实体、事件、关系三张表即可。
- 不需要一开始引入完整 GraphRAG 框架。
- 但数据模型要预留 graph 化能力。

## 3. 对 Hackson 的综合判断

Hackson 的上下文系统不能采用单一方案。产品需要的是混合架构：

- 最近聊天：直接长上下文。
- 长期经历：摘要压缩 + 原文索引。
- 用户偏好：长期 profile memory。
- Agent 人格：受控 persona memory。
- Idle 生活：事件流 + 反思 + 日记。
- 用户插入 idle：场景快照 + 最近事件 + 关系状态。
- Work Mode：任务状态 + 工具结果 + 反思复盘 + 技能库。
- 多 Agent：共享世界记忆 + 私有 Agent 记忆并存。

因此推荐的研究方向是：Context Operating System for Multi-Agent Companions，即“多 Agent 陪伴系统的上下文操作系统”。

## 4. 推荐基线架构

V1 不建议追求最复杂的 Agentic Memory，而应先实现稳定可验证的 Context OS v0：

1. Conversation Store：保存原始消息。
2. Event Store：结构化保存发生了什么。
3. Summary Store：保存会话摘要、日摘要、关系摘要。
4. Persona Store：保存核心人格、可变人格、用户编辑人格。
5. Memory Store：保存可检索的长期记忆卡片。
6. Context Builder：根据 mode 和当前输入组装 prompt。
7. Reflection Worker：异步生成日记、反思、记忆候选。
8. Memory Governor：决定什么能写入长期记忆，什么只能留在日志。

## 5. 关键原则

### 原则 1：原始历史不可丢，摘要可重建

所有对话、工具调用、用户插入都必须进入原始日志。摘要、记忆、人格变化都只是派生结果。如果摘要出错，可以重跑。

### 原则 2：人格变化必须慢

人格成长是产品亮点，但不能让 Agent 一天之内因为一次 idle 对话完全变样。人格更新应分为：

- core persona：用户明确设置，默认不可自动改。
- adaptive persona：系统根据长期行为缓慢调整。
- episode mood：短期情绪或状态，可快速变化。

### 原则 3：记忆要有权限

用户说的话、Agent 自己想的话、工具结果、系统推断，不能混为一谈。每条记忆必须有 source、visibility、confidence、owner。

### 原则 4：不同模式使用不同上下文配方

Idle、Companion 1、Companion 2、Work Mode 的上下文需求不同。不能用一个万能 prompt。

### 原则 5：上下文构建必须可解释

每次模型调用前，系统应能记录“为什么把这些记忆放进 prompt”。否则后期无法调试人格漂移、幻觉和用户隐私问题。

## 6. 参考资料

- Lost in the Middle: How Language Models Use Long Contexts：https://arxiv.org/abs/2307.03172
- MemGPT: Towards LLMs as Operating Systems：https://arxiv.org/abs/2310.08560
- Generative Agents: Interactive Simulacra of Human Behavior：https://arxiv.org/abs/2304.03442
- Reflexion: Language Agents with Verbal Reinforcement Learning：https://arxiv.org/abs/2303.11366
- MemoryBank: Enhancing Large Language Models with Long-Term Memory：https://arxiv.org/abs/2305.10250
- A-MEM: Agentic Memory for LLM Agents：https://arxiv.org/abs/2502.12110
- Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection：https://arxiv.org/abs/2310.11511
- LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs：https://arxiv.org/abs/2406.15319
- LongRAG: A Dual-Perspective Retrieval-Augmented Generation Paradigm for Long-Context Question Answering：https://arxiv.org/abs/2410.18050
- Voyager: An Open-Ended Embodied Agent with Large Language Models：https://arxiv.org/abs/2305.16291
- Microsoft GraphRAG：https://www.microsoft.com/en-us/research/project/graphrag/
