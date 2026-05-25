
数据库需要如下表格，存储如下：

username 
display_name 
email 
password 

设置的信息：

idle_on (true/false)

V1 demo 模型配置说明：

- 用户表不存 endpoint、api key、本地模型路径。
- web 设置页不提供用户自选模型入口。
- 模型 endpoint 由后端平台侧统一配置。
- 平台 API key 应存 secret ref 或环境变量，不进入用户数据表。
