
Step数字相同为同步进行。


V1: idle mode和companion mode1/2

准备工作
- Step1: 先写模型异步层/用户配置层。目标：用户自行提供模型路径，可以通过异步层成功打到模型。
- Step2: 科研上下文处理系统。阅读最新论文，找到最好方案（参考：chatgpt网页端跨对话机制）
- Step2: 模型调用工具对codex cli的调用处理 - 交流层。（参考openclaw）
- Step2: 数据库准备，数据库记录聊天记录等。（idle/companion2的设计）。可能数据库需要异步写入，不然爆炸。
- Step3: 两模型相互交流idle，以及对话进库。（暂时不做自我总结和自学习，留待step4）

性格处理
- Step3: 性格处理。用户编辑性格/故事（自带），如果是用户编辑性格/故事 ai自动整理成自己的文档（？或者有更好方案）
- Step4: idle 时的自学习功能实现。自我总结diary/自动清除prompt维持prompt字数限制 （？或者有更好方案）
- Step5: Companion（1）的上下文实现 - idle模式用户突然插入，怎么给ai做上下文？
- Step5: Companion（2）的上下文管理系统（compact？或者有更好方案？）


网站后端架构搭建

- Step6: 后端api。数据库送对话历史到前端。滚动加载对话历史。
- Step6: Companion1的 api借口，用户发的消息api送到后端，接库
- Step6: Companion2的api借口，用户发消息到后端，和数据库的连接。


网站前端

- domain/@username 设置页：1、编辑两个agent的性格（选择现成的/自编辑），上传照片，以及其他设置（打开关闭idle，idle频率）2、查看agents在idle自学习的时候的日记（Step4，或者有更好计划）
- domain/idle 两个agent的聊天记录，用户可以随时插入/观摩。
- domain/comp2 类似chatgpt的聊天框系统。





v2: 软件桌宠的加入


现成的软件桌宠
- Step1: 适配不同系统（先只适配macos）
- 看见ai在聊什么（最近对话框）
- llm 可以控制活动

用户上传图片
- Step1: 用户上传自己照片或者什么照片，ai像素化 （困在游戏机/任意场景的自己），并且可以自己编辑自己性格等。

其他
- 多个用户连接，拉群（很多用的agents相互交流）







v3: codex cli的work mode 

其他
- cata的桌宠想法（卖好看的桌宠）