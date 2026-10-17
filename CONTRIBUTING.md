# 贡献指南

欢迎提交可复现的问题、文档修改和范围清晰的代码改进。请先阅读 [安装说明](docs/INSTALLATION.md) 和 [验收边界](docs/VALIDATION.md)。

1. 从 `main` 创建工作分支；一个 PR 解决一类问题。
2. 保留 AGPL-3.0 许可证和原作者归属；新增外部代码、模型或图片须说明出处和许可证。
3. 不提交账号数据、密钥、数据库、日志、原始用户截图或 `.venv`。新增测试尽量使用合成数据。
4. 修改任务判断、答案匹配、恢复或发布次数时，补充能重现原问题的离线回归；文档排版不必为了数量添加测试。
5. 运行下面的检查，并在 PR 说明实际验证范围。线上验证需由账号本人参与；CI 不登录账号、不控制模拟器、不调用付费接口。

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -q
.\.venv\Scripts\python.exe scripts\Check-Publication.py
```

修改公开文件后，用 `python scripts/Check-Publication.py --write-manifest` 更新源码摘要，再重新检查。不要更新摘要来掩盖没有解释的文件变化。提交说明建议使用具体动词，如 `Fix daily completion detection`；不强制为格式重写历史。

模型对比工具默认只校验样本；显式 `--run` 才会付费请求。仓库自带图片为合成契约样本，不能用来宣传真实答题准确率。要评测模型，请自备有合法来源、去身份化且独立标注的样本。

不接受自动解验证码、跳过访问验证、伪造积分、关闭公开发言次数限制，或隐藏第三方数据传输的改动。对结构重构，应说明行为保持依据，避免同时改动模型、超时和任务顺序。
