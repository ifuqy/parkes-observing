"""Build two Parkes automation requests without creating them or touching websites."""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BEIJING = timezone(timedelta(hours=8), "Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]


def parse_time(value):
    dt = datetime.fromisoformat(value)
    return dt.replace(tzinfo=BEIJING) if dt.tzinfo is None else dt.astimezone(BEIJING)


def build_plan(start, end, project, page, plan, sources, now=None, *, username, oic_display_name, phone, email):
    start, end = parse_time(start), parse_time(end)
    now = now or datetime.now(BEIJING)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if end <= start:
        raise ValueError("End must be later than start; give explicit dates across midnight.")
    if end - start <= timedelta(minutes=7):
        raise ValueError("Slot must exceed seven minutes so the two preparation tasks do not overlap.")
    if start - timedelta(minutes=12) <= now:
        raise ValueError("Preparation time is past. Obtain explicit user direction for immediate execution.")
    if not re.fullmatch(r"P[0-9]+", project):
        raise ValueError("Use an exact project code such as P1365.")
    if page < 1 or not plan.strip():
        raise ValueError("Supply a positive page number and nonempty plan Alias.")
    if not sources or any(not x.strip() for x in sources):
        raise ValueError("Supply ordered source names.")
    if len(set(sources)) != len(sources):
        raise ValueError("Repeated sources need user clarification before scheduling.")
    if any("\n" in x or "\r" in x for x in [plan, *sources]):
        raise ValueError("Plan and source names must be single-line values.")
    points = {
        "prepare_start": start - timedelta(minutes=12),
        "announce": start - timedelta(minutes=5),
        "start": start,
        "no_reply_takeover": start + timedelta(minutes=2),
        "prepare_end": end - timedelta(minutes=5),
        "abort": end - timedelta(minutes=2),
        "end": end,
    }
    spec = {
        "timezone": "Asia/Shanghai",
        "project": project,
        "plan_page": page,
        "plan_alias": plan,
        "sources_in_order": list(sources),
        "times": {k: v.isoformat() for k, v in points.items()},
        "username": username,
        "oic_display_name": oic_display_name,
        "phone": phone,
        "email": email,
    }
    workflow = (ROOT / "references" / "workflow.md").read_text(encoding="utf-8-sig")
    workflow = workflow.split("## 历史案例")[0].replace("{PROJECT}", project)
    for key, value in [("USERNAME", username), ("OIC_DISPLAY_NAME", oic_display_name), ("PHONE", phone), ("EMAIL", email)]:
        workflow = workflow.replace("{" + key + "}", value)
    spec_text = json.dumps(spec, ensure_ascii=False, indent=2)
    common = (
        "使用 $parkes-observing。技能路径：" + str(ROOT / "SKILL.md") +
        "\n本次参数与北京时间节点：\n" + spec_text +
        "\n此任务仅针对上述绝对日期与时段，不得挪到次日。首次触发核对日期并删除自身定时器，"
        "然后继续本次运行；删除不表示观测完成。每次有新消息恢复时先核对进度，避免重复提交。"
        "凭据只使用本聊天用户直接提供或已登录的会话，不写出密码。"
        "用户已授权本次时段的标准流程，普通步骤不反复确认；遵守平台强制审批。"
        "遇实际冲突或工具错误才请求协助。静默处理无变化等待，只通知完成、故障或需要用户行动。"
        "\n完整执行流程：\n" + workflow
    )
    tasks = []
    for phase, trigger in [("start", points["prepare_start"]), ("end", points["prepare_end"])]:
        phase_instruction = (
            "只执行交接与启动部分：提前12分钟准备两站登录、提前5分钟到场消息、交接/OIC；已代启则保留并确认OIC，未启动才按顺序逐源Schedule和一次Start，"
            "核实运行后保持网页打开。另一结束任务独立负责停止；不得删除它。"
            if phase == "start" else
            "只执行停止与交接部分：提前准备，在指定Abort时刻停止本项目，"
            "先截图记录停止后的Observing状态，再发门户交接消息、核实并关闭两个任务标签。"
            "最后在本聊天发送截图与状态，不声称完成全部积分。"
        )
        anchored = trigger.date() != now.astimezone(BEIJING).date()
        rule = (f"DTSTART;TZID=Asia/Shanghai:{trigger:%Y%m%dT%H%M%S}\nRRULE:FREQ=DAILY;COUNT=1"
                if anchored else
                f"RRULE:FREQ=DAILY;BYHOUR={trigger.hour};BYMINUTE={trigger.minute};BYSECOND=0;COUNT=1")
        tasks.append({
            "mode": "suggested_create" if anchored else "create",
            "kind": "heartbeat",
            "destination": "thread",
            "name": f"Parkes {project} {start:%Y-%m-%d %H:%M} " +
                    ("交接与启动" if phase == "start" else "结束记录与交接"),
            "status": "ACTIVE",
            "rrule": rule,
            "prompt": phase_instruction + "\n" + common,
        })
    return {
        "spec": spec,
        "trigger_dates_must_be_verified": [points["prepare_start"].isoformat(), points["prepare_end"].isoformat()],
        "tasks": tasks,
        "note": "Only call automation_update after verifying each next-run absolute date in Asia/Shanghai. "
                "RRULE wall-clock values alone do not encode the requested future date. "
                "If the tool cannot anchor that date, do not activate an earlier repeating run; "
                "use its supported one-off/anchored schedule or explain the scheduling limitation."
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--start", required=True, help="Full ISO date/time; naive time means Beijing")
    p.add_argument("--end", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--page", required=True, type=int)
    p.add_argument("--plan", required=True)
    p.add_argument("--source", required=True, action="append", help="Repeat in observing order")
    p.add_argument("--username", required=True)
    p.add_argument("--oic-display-name", required=True)
    p.add_argument("--phone", required=True)
    p.add_argument("--email", required=True)
    args = p.parse_args()
    try:
        result = build_plan(args.start, args.end, args.project, args.page, args.plan, args.source, username=args.username, oic_display_name=args.oic_display_name, phone=args.phone, email=args.email)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

