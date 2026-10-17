# MaaXuexi Local

[![CI](https://github.com/Orangaigai/MaaXuexi-Local/actions/workflows/ci.yml/badge.svg)](https://github.com/Orangaigai/MaaXuexi-Local/actions/workflows/ci.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Windows_x64-0078D4)
![Python](https://img.shields.io/badge/python-3.12-3776AB)

基于 [ravizhan/MaaXuexi](https://github.com/ravizhan/MaaXuexi) 的本地维护版本，使用 MaaFramework、MuMu 与 OCR 完成界面操作，提供浏览器控制台和 Windows 定时启动。

**当前为预发布源码版。** 主要在 Windows + MuMu + 学习强国 2.74.0 环境验证；界面变化可能导致识别失败。遇到真实访问验证，需要本人在模拟器完成，程序观察页面恢复后继续。不能保证每天无人值守完成、答题全对或账号不受限制。请先确认平台规则，再决定是否使用。

English: A Windows-first, locally maintained derivative of MaaXuexi. Human verification is required; no CAPTCHA solving or bypass is included. See [installation](docs/INSTALLATION.md), [privacy](docs/PRIVACY.md), and [validation limits](docs/VALIDATION.md).

## 功能

| 任务 | 当前实现 |
| --- | --- |
| 登录与核分 | 先读当日积分，已完成任务跳过；运行后记录实际结果 |
| 选读文章 | 按缺额分批阅读、核分，达到面板目标后结束 |
| 视听学习 | 识别视频进度；读不到进度时不虚记已播放时间 |
| 本地频道 | 导航到本地内容，返回积分页核对 |
| 每日答题 | 选择、输入填空、点选填空；完整提示优先，否则请求模型；自动提交和返回 |
| 趣味答题 | 识别当天计分入口；保留单人、双人、四人流程与结算处理 |
| 订阅 | 逐个订阅并核分；数据库记录轮次、次数和待清理项；取消本工具新增订阅 |
| 发表观点 | 可选且默认关闭；仅限科普中国/生活百科，正文生成与复核、8–20 字、每天最多一次尝试 |
| 本地控制 | 启动、进度、停止、待处理报告、密钥配置、定时清单；重复启动复用后台 |

默认顺序：登录 → 文章 → 视听 → 本地 → 趣味 → 订阅 → 观点（启用时）→ 每日答题。依据本机观察安排常见少验证任务在前；**验证频率没有保证**。积分上限以应用当日面板为准，不作为永久规则。

## 快速开始

前提：Windows 10/11 x64、[Python 3.12 x64](https://www.python.org/downloads/)、[MuMu](https://mumu.163.com/)、[VC++ x64 运行库](https://aka.ms/vs/17/release/vc_redist.x64.exe)。模拟器按上游要求设为 1280×720、DPI 240 平板模式；应用内页面应呈现 720×1280 的竖屏截图。不同 MuMu 版本如有方向差异，先对照 [安装说明](docs/INSTALLATION.md) 检查。

```powershell
git clone https://github.com/Orangaigai/MaaXuexi-Local.git
cd MaaXuexi-Local
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Install-MaaXuexi.ps1 -MuMuDirectory "C:\Program Files\Netease\MuMuPlayer"
```

上面的 MuMu 路径是示例，替换为实际安装位置；也可以直接指向 `nx_main`。安装器创建独立 `.venv` 和本机配置，保留已有配置，不执行学习任务。

1. 在模拟器安装应用、本人登录，并处理首次引导。
2. 双击 `MaaXuexi-Local.lnk` 或 `启动MaaXuexi.cmd`，打开控制页 <http://127.0.0.1:8000/>。
3. 需要模型答题时，在“配置答题密钥”页面填写自己的 DeepSeek 官网 API Key；保存并验证会产生一次小额接口调用。
4. 勾选任务，点击一次“执行所选任务”。遇访问验证只在模拟器亲自完成，通常无需再点网页“执行”或“继续”。

文章、视听等任务不需要模型。模型答题可能发送题干、选项、提示及完整截图；接口按服务商规则收费。当前模型配置为 `deepseek-flash`，请以 [DeepSeek 官方文档](https://api-docs.deepseek.com/quick_start/pricing/) 和本机验证结果为准。

## 每天自动运行

先在网页保存定时清单，再手动执行并确认环境可用，最后按需注册计划任务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Register-DailyTask.ps1
```

默认在 **Windows 当前时区每天 09:00** 启动；不会在仅下载源码时自动注册。电脑须开机、未休眠、联网且当前用户已登录。定时运行遇验证最多等待十分钟，超时记录未完成项目；不会自动验证，也不保证所有分数完成。删除计划任务见 [安装说明](docs/INSTALLATION.md)。

## 测试与排错

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -q
.\.venv\Scripts\python.exe scripts\Check-Publication.py
```

离线测试不操作模拟器、不调用付费 API；不等于完整的线上积分验收。更详细的设备自检、网络错误、端口占用、验证恢复和已知限制见 [故障排查](docs/TROUBLESHOOTING.md) 与 [验收范围](docs/VALIDATION.md)。

## 项目文档

- [安装与配置](docs/INSTALLATION.md)
- [隐私与数据](docs/PRIVACY.md)
- [架构与维护](docs/ARCHITECTURE.md)
- [变更记录](CHANGELOG.md)
- [贡献指南](CONTRIBUTING.md)、[行为准则](CODE_OF_CONDUCT.md)、[安全报告](SECURITY.md)
- [上游归属与第三方资源](NOTICE.md)、[公开规范参考](docs/REFERENCES.md)

## 来源与许可证

基于上游 v1.7.1，固定基线提交 [`ff6a0d5`](https://github.com/ravizhan/MaaXuexi/commit/ff6a0d5a811c5fc987a0c0ae77ea9abaf55fa073)。保留原始 [AGPL-3.0 许可证](LICENSE) 和上游署名。上游 README 另有“禁止倒卖或用于商业用途”的声明，原文与归属见 [NOTICE](NOTICE.md)。本仓库不代表官方平台，不承诺使用获得平台许可。
