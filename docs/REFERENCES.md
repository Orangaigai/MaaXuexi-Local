# 公开规范与直接用户反馈

查阅日期：2026-10-18。采用对小型 Windows 项目有实际帮助的规范，没有为了凑清单引入无用框架。

| 参考来源 | 本仓库采用方式 |
| --- | --- |
| [GitHub 仓库最佳实践](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories) | README、许可证、清楚的用途、安装、限制和安全说明 |
| [社区健康文件](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories) | 贡献、安全、行为准则、支持说明、问题与 PR 模板 |
| [Actions 安全使用](https://docs.github.com/en/actions/reference/security/secure-use) | Action 固定完整提交 SHA、只读权限、不向测试提供账号或 API 密钥 |
| [清除敏感数据](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) | 上传前检查当前文件及公开历史；私人开发历史不混入公开快照 |
| [上游 README](https://github.com/ravizhan/MaaXuexi) | 保留 AGPL、原作者归属和上游使用声明；如实说明模拟器条件与人工验证 |
| [上游 Issue #16](https://github.com/ravizhan/MaaXuexi/issues/16) | 用户反馈视频滑动、答题失败与版本启动问题，后确认 v1.7.1 解决其案例；因此记录版本、复现与诊断类型 |
| [上游 Issue #12](https://github.com/ravizhan/MaaXuexi/issues/12) | 用户反馈识别到文章但不进入；因此区分“识别”“执行”“核分”三个阶段 |
| [上游 Issue #14](https://github.com/ravizhan/MaaXuexi/issues/14) | 提示 OCR 与题型流程讨论；采用完整、唯一匹配时优先提示，避免模糊匹配误点 |

这些 Issue 是直接用户个案，不能推断所有人都可运行、某种验证概率或账号安全保证。没有把项目 Star 数当作可靠性证据。
