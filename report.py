from __future__ import annotations


def build_utilization_report(
    summary: dict,
    thresholds: dict,
    lang: str = "en",
    currency: str = "¥",
) -> dict:
    if lang == "zh":
        return _build_zh(summary, thresholds, currency)

    return _build_en(summary, thresholds, currency)


def _fmt(value, digits: int = 2) -> str:
    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return str(value)


def _build_zh(summary: dict, thresholds: dict, currency: str) -> dict:
    total_assets = int(summary.get("total_assets", 0))
    low_util_assets = int(summary.get("low_util_assets", 0))
    zombie_assets = int(summary.get("zombie_assets", 0))
    candidate_assets = int(summary.get("candidate_assets", 0))
    shutdown_assets = int(summary.get("estimated_shutdown_assets", 0))

    period_days = summary.get("period_days", 0)
    avg_util = summary.get("avg_utilization", 0)
    zombie_ratio = summary.get("zombie_ratio", 0)

    total_energy = summary.get("total_energy_kwh", 0)
    waste_energy = summary.get("waste_energy_kwh", 0)
    waste_cost = summary.get("waste_cost", 0)

    gross_saving = summary.get("gross_saving_cost", 0)
    net_saving = summary.get("net_saving_cost", 0)
    annual_net_saving = summary.get("annual_net_saving", 0)
    cooling_saving = summary.get("cooling_saving_cost", 0)
    migration_cost = summary.get("migration_cost", 0)
    restart_risk_cost = summary.get("restart_risk_cost", 0)
    post_util = summary.get("post_avg_utilization", 0)
    top_group = summary.get("top_waste_group", "N/A")

    low_threshold = thresholds.get("low_util_threshold", 10)
    high_duty_threshold = thresholds.get("high_duty_threshold", 5)
    safe_util_limit = thresholds.get("safe_util_limit", 65)

    summary_text = (
        f"本次分析覆盖 {total_assets} 台/套资产，分析周期约 {_fmt(period_days, 2)} 天。"
        f"整体平均利用率为 {_fmt(avg_util)}%，其中低利用率资产 {low_util_assets} 台/套，"
        f"疑似僵尸资产 {zombie_assets} 台/套，占比约 {_fmt(zombie_ratio)}%。"
    )

    savings_summary = (
        f"本周期总耗电量约 {_fmt(total_energy)} kWh，疑似低利用率资产对应的潜在浪费电量约 "
        f"{_fmt(waste_energy)} kWh，对应浪费电费约 {currency}{_fmt(waste_cost)}。"
    )

    insights = [
        f"当前浪费最集中的分组为 {top_group}，建议优先进行业务核验和资产盘点。",
        f"在当前整合假设下，可纳入整合或下线评估的资产约 {candidate_assets} 台/套，其中理论可下线或迁移评估 {shutdown_assets} 台/套。",
        f"整合后平均利用率约为 {_fmt(post_util)}%，安全上限为 {_fmt(safe_util_limit)}%。若低于安全上限，说明仍存在资源整合空间。",
    ]

    economic_items = [
        f"本周期设备侧节省与冷却联动节省合计约 {currency}{_fmt(gross_saving)}。",
        f"扣除迁移成本约 {currency}{_fmt(migration_cost)} 和重启风险成本约 {currency}{_fmt(restart_risk_cost)} 后，理论净节省约 {currency}{_fmt(net_saving)}。",
        f"若按当前周期结果折算全年，理论年度净节省约 {currency}{_fmt(annual_net_saving)}。",
        f"其中冷却侧联动收益约 {currency}{_fmt(cooling_saving)}，体现出低利用率资产不仅浪费 IT/设备侧电力，也会间接抬高冷却负荷。",
    ]

    decision_items = [
        f"建议优先排查平均利用率低于 {low_threshold}% 且高负载时段占比低于 {high_duty_threshold}% 的资产。",
        "建议将资产分为“可立即评估下线”“需业务核验”“业务保护资产”“持续观察”四类，而不是直接批量关停。",
        "对于低利用率但内存、磁盘 IO 或网络 IO 较高的资产，应优先标记为需业务核验，避免误判。",
        "若整合后平均利用率仍明显低于安全上限，可继续扩大试点整合范围。"
    ]

    risk_text = (
        "低利用率不等于可以立即关停。本模块输出的是管理决策辅助结果，"
        "更适合作为资产盘点、节能评估和投资展示材料，而不是自动运维指令。"
    )

    risk_items = [
        "部分低利用率设备可能承担备份、容灾、低频任务或业务保活功能。",
        "如果缺少业务标签、网络 IO、存储 IO 或监控上下文，应将结果理解为优先排查名单。",
        "实际整合前仍需确认迁移窗口、SLA、业务归属和冗余要求。",
    ]

    return {
        "summary_title": "摘要结论",
        "summary": summary_text,
        "savings_summary": savings_summary,
        "advanced_title": "关键洞察",
        "insights": insights,
        "economic_title": "经济性结论",
        "economic_items": economic_items,
        "decision_title": "管理建议",
        "decision_items": decision_items,
        "risk_title": "风险提示",
        "risk_text": risk_text,
        "risk_items": risk_items,
    }


def _build_en(summary: dict, thresholds: dict, currency: str) -> dict:
    total_assets = int(summary.get("total_assets", 0))
    low_util_assets = int(summary.get("low_util_assets", 0))
    zombie_assets = int(summary.get("zombie_assets", 0))
    candidate_assets = int(summary.get("candidate_assets", 0))
    shutdown_assets = int(summary.get("estimated_shutdown_assets", 0))

    period_days = summary.get("period_days", 0)
    avg_util = summary.get("avg_utilization", 0)
    zombie_ratio = summary.get("zombie_ratio", 0)

    total_energy = summary.get("total_energy_kwh", 0)
    waste_energy = summary.get("waste_energy_kwh", 0)
    waste_cost = summary.get("waste_cost", 0)

    gross_saving = summary.get("gross_saving_cost", 0)
    net_saving = summary.get("net_saving_cost", 0)
    annual_net_saving = summary.get("annual_net_saving", 0)
    cooling_saving = summary.get("cooling_saving_cost", 0)
    migration_cost = summary.get("migration_cost", 0)
    restart_risk_cost = summary.get("restart_risk_cost", 0)
    post_util = summary.get("post_avg_utilization", 0)
    top_group = summary.get("top_waste_group", "N/A")

    low_threshold = thresholds.get("low_util_threshold", 10)
    high_duty_threshold = thresholds.get("high_duty_threshold", 5)
    safe_util_limit = thresholds.get("safe_util_limit", 65)

    summary_text = (
        f"This analysis covers {total_assets} assets over approximately {_fmt(period_days, 2)} days. "
        f"The average utilization is {_fmt(avg_util)}%, with {low_util_assets} low-utilization assets "
        f"and {zombie_assets} suspected zombie assets, representing {_fmt(zombie_ratio)}% of the portfolio."
    )

    savings_summary = (
        f"The estimated total energy consumption is {_fmt(total_energy)} kWh during the analysis period. "
        f"Potential waste energy associated with underutilized assets is approximately {_fmt(waste_energy)} kWh, "
        f"equivalent to {currency}{_fmt(waste_cost)} in electricity cost."
    )

    insights = [
        f"The largest waste concentration is observed in {top_group}, which should be prioritized for business validation and asset review.",
        f"Under the current consolidation assumptions, {candidate_assets} assets are eligible for consolidation review, and {shutdown_assets} assets are theoretically selected for shutdown or migration assessment.",
        f"The post-consolidation average utilization is approximately {_fmt(post_util)}%, compared with a safe limit of {_fmt(safe_util_limit)}%. If it remains below the limit, further consolidation potential may exist.",
    ]

    economic_items = [
        f"The combined device-side and cooling-linked saving is approximately {currency}{_fmt(gross_saving)} for the analysis period.",
        f"After deducting migration cost of {currency}{_fmt(migration_cost)} and restart risk cost of {currency}{_fmt(restart_risk_cost)}, the theoretical net saving is {currency}{_fmt(net_saving)}.",
        f"Annualized net saving is approximately {currency}{_fmt(annual_net_saving)} if the current pattern remains stable.",
        f"Cooling-linked saving contributes approximately {currency}{_fmt(cooling_saving)}, indicating that underutilized assets also increase cooling-side energy demand.",
    ]

    decision_items = [
        f"Priority review is recommended for assets with average utilization below {low_threshold}% and high-load duty ratio below {high_duty_threshold}%.",
        "Assets should be classified into immediate shutdown assessment, business validation required, business protected, and watchlist categories.",
        "Assets with low CPU/device utilization but high memory, disk IO, or network IO should be validated carefully to avoid false positives.",
        "If post-consolidation utilization remains well below the safe limit, the pilot consolidation scope can be expanded."
    ]

    risk_text = (
        "Low utilization does not automatically mean an asset can be shut down. "
        "This module provides decision-support outputs for asset review, energy saving analysis, and portfolio demonstration, not automated operation commands."
    )

    risk_items = [
        "Some low-utilization assets may support backup, disaster recovery, low-frequency jobs, or business continuity.",
        "If business tags, network IO, storage IO, or monitoring context are missing, the output should be treated as a priority review list.",
        "Before actual consolidation, migration windows, SLA, business ownership, and redundancy requirements must be confirmed.",
    ]

    return {
        "summary_title": "Summary",
        "summary": summary_text,
        "savings_summary": savings_summary,
        "advanced_title": "Key Insights",
        "insights": insights,
        "economic_title": "Economic Conclusions",
        "economic_items": economic_items,
        "decision_title": "Management Suggestions",
        "decision_items": decision_items,
        "risk_title": "Risk Notices",
        "risk_text": risk_text,
        "risk_items": risk_items,
    }