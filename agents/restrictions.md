
1. Actively use skills in .agents/ 
2. For each folder(and subfolder), a README.md is required. 每次执行以前必须先落文档，然后严格按照文档落代码。代码架构必须非常清晰。The README.md must be in this format:

## header
Created at: 
Created by: 
Last Modified at: 
Lst Modified by: 

## brief intro
- goal for this folder. 
- 架构思路

## folder structure 
|-test.py intro to this file 
|-tests/ intro to this subfolder (and another READNE doc is necessary in this subfolder)
|......

## 代办
not finished stuff (or what should be done in the future)

3. For each file, there must be an header:

Created at:
Created by:
Last Modified at:
Last Modified by:

comments is necessary. 

4. We have a server at docs/数据库/machine.md Backend should be deployed at that machine. Be sure to test in that machine frequently. 

5. 每次开始工作前先检查工作区是否干净。如果不干净提交干净再继续。
6. 目标机上禁止暂停任何现有服务。必须开新的端口。如果要暂停服务，必须找我核实。
7. 后端用fastapi，前端用react+vite。
8. 根目录必须放一个api.md 也是包含header，实时更新所有的api端口和目的。要求：a. 没看过代码的程序员看到这个文档可以无缝开始 b. 出现在文档上的必须是检测好的。
9. 所有需要保密的环境变量，存.env 在本地，目标机都可以留档！（不允许出现任何占位，example之类）。记住放在gitignore不要上传到git即可。
10. 和前端相关的请仔细遵循frontend_restrictions.md
11. 你是非常有经验的工程师，用最工程化的实施计划。一圈一圈慢慢叠加：最小闭环，测试，debug，继续。
12. 循环逻辑：产品级别的实施，用大厂的工程化流程实行。直到用户的需求完成。