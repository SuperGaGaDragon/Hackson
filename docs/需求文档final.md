2026.5.25 1pm 
editted by: Quanhao Li, Jorlanda Chen 

- 两个不同性格agents。



## 总难点
- 模型异步系统，并发设计。
- ai 性格设计，不能只是简单的soul.md，需要技术创新。
- 什么时候ai要看什么文档（尤其是我们可能只用一个ai，只是用文档形成不同性格）
- ai自己修改自己性格文档。

## 注意点
- V1 demo 不做用户自行配置 env / endpoint / api key / 本地模型路径。
- 模型 endpoint 由我们在后端统一配置；web 只提供产品功能入口，不提供模型配置入口。后续版本可以再开放用户自选模型配置。

## 三种模式
1.  Mode1: idle mode 
- 两个agents相互做philosophy debate。
- 用户可以选择开/关（节约token）
- web ui上有一个页面展示这个内容。
- 用户可以随时加入，如果用户加入，进入 companion mode (1)。此时agents 必须围绕用户说话，需要维持上下文联系。

难点：
- 上下文拼接系统（core）。需要结合最新论文进行技术革新
- 数据库存储聊天内容


2. Companion mode(2)
- 用户主动开话题，类似于chatgpt web新建窗口。不需要上下文，群聊聊天，必须围绕用户展开。

3. Work mode
- 两个ai进行分工合作，相当于领导调动codex cli。他们可以要求codex cli返回什么东西。并且在网站上实施显示进度，可以24x7后台跑。
- 桌宠的结合。桌宠出现进度。

Work Mode 新产品定义：
- Work Mode 不是普通聊天，而是 Project / Mission / Employee Runtime。
- 用户可以在网站里创建和编辑 AI 员工。员工有名字、性格、工作风格、经历、项目经验和显示形象。
- 每个 Project 可以选择自己的员工列表。
- 用户创建 Mission 时，可以选择哪些员工加入，并指定一个主员工。
- 主员工负责推进 Mission，调动工具箱，整理对用户可见的进度。
- 工具箱包括：React 展示工具、shell/Codex CLI 执行工具、调动其他员工的 brainstorm/review 工具。
- 员工之间的 brainstorm 过程可以展示，但默认不淹没主界面；主界面主要显示 progress、warning、summary、product、approval、diff、test result。
