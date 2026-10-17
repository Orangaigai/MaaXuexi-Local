# 安装与配置

## 支持范围

- Windows 10/11 x64，Python 3.12 x64，Windows PowerShell 5.1 或以上。
- 主要测试环境为 MuMu、学习强国 2.74.0；不承诺其他版本兼容。
- 模拟器设置按上游的 1280×720、DPI 240 平板模式。应用旋转后的截图应为 720×1280；识别坐标依赖此尺寸。先允许应用自行旋转，仍不匹配时调整模拟器方向，勿强行运行不匹配画面。
- 安装 [Microsoft VC++ x64 运行库](https://aka.ms/vs/17/release/vc_redist.x64.exe)。

请把源码放在可写目录，保留完整目录结构。不要把它解压进另一份正在运行的安装目录，也不要复用别人的 `.venv`、密钥或配置数据库。

## 首次安装

在项目根目录打开 PowerShell：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Install-MaaXuexi.ps1 -MuMuDirectory "D:\Apps\MuMuPlayer"
```

MuMu 可位于任意目录，示例路径没有特殊意义。安装器查找该目录或其 `nx_main` 下的 `mumu-cli.exe`、`adb.exe`。多个实例可添加 `-VmIndex 1`。无法使用 `py -3.12` 时，加 `-PythonPath "C:\Python312\python.exe"` 指定 Python。

安装器会：验证 MuMu 路径和 Python、创建 `.venv`、安装固定版本依赖、首次生成 `config/emulator.json` 与 `config/local-task-plan.json`，创建无黑窗快捷方式。已有配置保留；不会自动执行任务、启用评论或注册定时任务。

需要更换 MuMu 路径或实例时，先停止后台，再按 `config/emulator.example.json` 编辑本机 `config/emulator.json`。安装器再次执行不会覆盖它。

## 首次启动和模型

1. 在 MuMu 安装应用并本人登录，处理首次权限和引导。
2. 双击 `MaaXuexi-Local.lnk`。也可运行 `启动MaaXuexi.cmd`。
3. 浏览器打开 <http://127.0.0.1:8000/>，选择任务后点击执行；启动器只准备后台和模拟器。
4. 需要模型任务时打开 `配置答题密钥.cmd` 或控制页的配置入口，输入 **DeepSeek 官网** API Key。密钥由当前 Windows 用户使用 DPAPI 加密保存；不要发到 Issue 或聊天。
5. “保存并验证”会发送一张程序生成的小图片，产生一次小额接口费用。这里的验证是 API 连通测试，不是应用的访问验证。

模型固定走 `https://api.deepseek.com`；网页的模型显示不表示可任意配置其他服务商。读屏完整时使用文字请求；跨屏、含图或识别不完整时保留图片请求。截图可能含账号信息，详情见 [隐私说明](PRIVACY.md)。

## 定时启动

先完成一次手动运行，在控制页保存定时清单，然后运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Register-DailyTask.ps1
```

默认名称 `MaaXuexi-Local-Daily`、Windows 当前时区 09:00，可用 `-Hour 10 -Minute 30` 调整。同名计划已存在时脚本拒绝覆盖。查看预期设置而不注册：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Register-DailyTask.ps1 -CheckOnly
```

当前用户必须已登录，电脑开机、联网、未休眠。定时脚本使用 `pythonw.exe`，不需要一直打开终端；浏览器可以关闭，后台继续运行。电脑关机或错过触发时间时不保证补跑。暂停、验证、网络异常会影响完成度。

控制页展示 `config/schedule-status.json` 的本机登记信息，不实时查询 Windows 调度器。若自行在任务计划程序中修改或删除任务，以 Windows 中的实际状态为准。

删除定时任务（只删除该名称）：

```powershell
Unregister-ScheduledTask -TaskName 'MaaXuexi-Local-Daily' -Confirm:$false
```

## 可选的公开评论

默认关闭，默认定时清单不包含此项。启用意味着允许工具以账号公开发言，应由账号本人了解文案规则后主动配置：复制 `config/comment-policy.example.json` 为 `config/comment-policy.json`，将 `enabled` 改为 `true`，再在网页勾选并保存。

范围固定为“科普中国/生活百科”，根据正文生成 8–20 字，经结构规则与模型复核，每天最多一次发表尝试。模型审核可能漏判。发表结果不明也计入当日尝试，**不要通过删除 `comments.sqlite3` 重复发布**。工具不会取消用户原有订阅。

## 更新与卸载

更新前停止后台，备份 `config`，再拉取代码并重新运行安装器。DPAPI 密钥通常只能由原 Windows 用户解密，不应跨机器直接复制使用。数据库记录影响订阅清理和评论次数，务必保留。

卸载时先删除该项目的计划任务，运行 `停止MaaXuexi.cmd`，自行备份需要的 `config` 与 `logs` 后再删除整个项目目录。本项目不修改系统代理或 VPN 设置。
