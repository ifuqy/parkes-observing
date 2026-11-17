# Parkes Observing Skill

用于 Codex 的 Parkes/Murriyang 观测交接助手。依据观测时段、项目、计划 Alias 和有序源列表，生成预检、交接监测、备用复核和停止交接四项定时任务。

## 安装

将本仓库复制到 `~/.codex/skills/parkes-observing`，重启或刷新 Codex 的 skill 列表，然后调用 `$parkes-observing`。需要可用的浏览器/电脑操作工具和 Codex 定时任务工具。

## 使用

提供完整观测日期、开始和结束时间（默认 Asia/Shanghai）、项目编号、计划页数、计划 Alias、源顺序，以及登录名、OIC 显示名、电话和邮箱。密码仅在当前受授权会话提供，或复用已登录的浏览器，不写入仓库或任务提示。

默认在开班前 15 分钟预检，前 2 分钟启动交接监测；同一监测任务在开班时再查一次 jPORTAL，不刷新。开班后 2 分钟独立复核。结束前 5 分钟准备收尾，按本次批准的硬停止时间停止（默认结束前 3 分钟）。用户可明确覆盖节点。实际执行须取得有权观测者的授权，并遵守平台审批与望远镜保护。

`scripts/make_plan.py` 仅计算时间与生成任务参数，不会连接望远镜或创建任务。运行 `python scripts/make_plan.py --help` 查看全部参数；生成后仍须通过 Codex 的任务工具创建并核对四项任务。

界面经验和工具行为来自2026年10月起的实际操作，可能随网站或客户端更新而变化。详见 [SKILL.md](SKILL.md)、[执行流程](references/workflow.md) 和 [可复用执行清单](references/checklist.md)；清单包含 P1365 实操提炼的时间预算、会话检查、截止操作与 OIC 释放经验，不含私人运行资料。本项目为独立工作流，不代表台站官方软件。
