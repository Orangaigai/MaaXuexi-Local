# 隐私与数据

## 数据去向

| 数据 | 保存或发送位置 |
| --- | --- |
| DeepSeek API Key | `config/deepseek-key.dpapi`，使用当前 Windows 用户 DPAPI 加密；调用时发送到 DeepSeek 官方 API |
| 题目、选项、提示 | 模型需要时发送给 DeepSeek；可包含完整截图 |
| 评论正文和原文 | 启用评论后，原文、草稿送模型生成及复核；实际发布内容会公开 |
| 订阅轮次、次数、待清理状态 | `config/subscriptions.sqlite3`，只在本机 |
| 评论尝试记录 | `config/comments.sqlite3`，防止重复发表 |
| 最近任务结果、诊断截图与日志 | `config`、`logs`、`debug`，可能含账号页面和题目 |

控制服务只绑定 `127.0.0.1:8000`，没有面向公网设计的用户认证。不要把它改成 `0.0.0.0`、端口转发到公网或接入不可信反向代理。同一台电脑上的其他程序可能访问本地服务；Windows 用户加密并不能隔离当前用户运行的所有软件。

公开源码不包含密钥、Windows 快捷方式、数据库、日志、私人报告或原始账号截图。公开测试图片为从布局契约重新生成的示意数据；OCR 文本中的玩家标识使用占位名称。资源目录保留上游识别素材，归属见 [NOTICE](../NOTICE.md)。

提交 Issue 前只摘取必要日志，删去昵称、手机号、组织信息、头像、完整个人路径、API Key、Cookie、二维码和访问验证画面。不要上传整个 `config`、`.venv`、`logs` 或 `debug` 压缩包。截图和日志在本机留存期间也应按个人数据管理。

怀疑密钥泄露时，先在服务商处撤销并重新创建，再排查本地与 Git 历史；仅删除当前文件不能清除已上传副本。参见 [GitHub 官方说明](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)。
