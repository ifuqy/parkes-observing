# Parkes Observing Skill

用于 Codex 的 Parkes/Murriyang 观测交接助手。依据观测时段、项目、计划 Alias 和有序源列表，生成启动与停止两项定时任务。

## 安装

将本仓库复制到 `~/.codex/skills/parkes-observing`，重启或刷新 Codex 的 skill 列表，然后调用 `$parkes-observing`。需要可用的浏览器/电脑操作工具和 Codex 定时任务工具。

## 使用

提供完整观测日期、开始和结束时间（默认 Asia/Shanghai）、项目编号、计划页数、计划 Alias、源顺序，以及登录名、OIC 显示名、电话和邮箱。密码仅在当前受授权会话提供，或复用已登录的浏览器，不写入仓库或任务提示。

默认在开始前12分钟准备两站登录、前5分钟发到场消息；结束前5分钟准备、前2分钟停止。用户可明确覆盖节点。实际执行须取得有权观测者的授权，并遵守平台审批与望远镜保护。

`scripts/make_plan.py` 仅计算时间与生成任务参数，不会连接望远镜或创建任务。运行 `python scripts/make_plan.py --help` 查看全部参数；生成后仍须通过 Codex 的任务工具创建并核对两项任务。

界面经验和工具行为来自2026年10月的实际操作，可能随网站或客户端更新而变化。详见 [SKILL.md](SKILL.md) 和 [执行流程](references/workflow.md)。本项目为独立工作流，不代表台站官方软件。
