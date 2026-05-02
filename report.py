from __future__ import annotations

from typing import Any


def build_utilization_report(
    summary: dict,
    thresholds: dict,
    mode: str = "standard",
    lang: str = "en",
    currency: str = "¥",
    action_counts: Any | None = None,
) -> dict:
    if lang == "zh":
        return _build_zh(summary, thresholds, mode, currency, action_counts)

    return _build_en(summary, thresholds, mode, currency, action_counts)


def _fmt(value, digits: int = 2) -> str:
    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return str(value)


def _money(value, currency: str, digits: int = 0) -> str:
    return f"{currency}{_fmt(value, digits)}"


def _shared_values(summary: dict) -> dict:
    total_assets = int(summary.get("total_assets", 0))
    low_util_assets = int(summary.get("low_util_assets", 0))
    zombie_assets = int(summary.get("zombie_assets", 0))
    protected_assets = int(summary.get("protected_assets", 0))
    migratable_assets = int(summary.get("migratable_assets", 0))
    candidate_assets = int(summary.get("candidate_assets", 0))

    return {
        "total_assets": total_assets,
        "low_util_assets": low_util_assets,
        "zombie_assets": zombie_assets,
        "candidate_assets": candidate_assets,
        "shutdown_assets": int(summary.get("estimated_shutdown_assets", 0)),
        "protected_assets": protected_assets,
        "migratable_assets": migratable_assets,
        "non_migratable_assets": max(total_assets - migratable_assets, 0),
        "non_candidate_assets": max(total_assets - candidate_assets, 0),
        "period_days": summary.get("period_days", 0),
        "total_energy": summary.get("total_energy_kwh", 0),
        "waste_energy": summary.get("waste_energy_kwh", 0),
        "waste_cost": summary.get("waste_cost", 0),
        "cost_saving_ratio": summary.get("cost_saving_ratio", 0),
        "annual_operating_saving": summary.get("annual_operating_saving", 0),
        "one_time_cost": summary.get("one_time_consolidation_cost", 0),
        "first_year_net": summary.get("first_year_net_benefit", 0),
        "migration_cost": summary.get("migration_cost", 0),
        "restart_risk_cost": summary.get("restart_risk_cost", 0),
        "post_util": summary.get("post_avg_utilization", 0),
        "avg_util": summary.get("avg_utilization", 0),
        "top_group": summary.get("top_waste_group", "N/A"),
    }


def _action_count_map(action_counts: Any | None) -> dict[str, int]:
    if action_counts is None:
        return {}

    try:
        if getattr(action_counts, "empty", True):
            return {}
        return {
            str(row["action_category"]): int(row["asset_count"])
            for _, row in action_counts.iterrows()
            if "action_category" in action_counts.columns and "asset_count" in action_counts.columns
        }
    except Exception:
        return {}


def _sections(summary_tab: str, sections: list[dict]) -> dict:
    # Keep the old keys out of the rendering path and expose one clean, mode-aware section list.
    return {
        "sections": sections,
        "summary_title": sections[0]["title"] if sections else summary_tab,
        "summary": "",
        "savings_summary": "",
        "advanced_title": "",
        "insights": [],
        "economic_title": "",
        "economic_items": [],
        "decision_title": "",
        "decision_items": [],
        "risk_title": "",
        "risk_text": "",
        "risk_items": [],
    }


def _build_zh(summary: dict, thresholds: dict, mode: str, currency: str, action_counts: Any | None) -> dict:
    v = _shared_values(summary)
    actions = _action_count_map(action_counts)

    low_threshold = thresholds.get("low_util_threshold", 10)
    active_threshold = thresholds.get("high_util_threshold", 40)
    active_duty_limit = thresholds.get("high_duty_threshold", 5)
    safe_util_limit = thresholds.get("safe_util_limit", 70)

    summary_items = [
        f"本次分析覆盖 {v['total_assets']} 台/套资产，样本周期约 {_fmt(v['period_days'], 2)} 天，平均利用率约 {_fmt(v['avg_util'])}%。",
        f"系统识别出低利用率资产 {v['low_util_assets']} 台/套、疑似僵尸资产 {v['zombie_assets']} 台/套、可评估整合资产 {v['candidate_assets']} 台/套。",
        f"样本周期总耗电量约 {_fmt(v['total_energy'])} kWh，潜在浪费电量约 {_fmt(v['waste_energy'])} kWh；浪费最集中的分组为 {v['top_group']}。",
    ]

    if mode == "basic":
        sections = [
            {
                "tab": "摘要",
                "title": "基础筛查摘要",
                "body": "基础模式只基于利用率、活跃时段占比和统一功率/电价假设，适合在字段较少时快速识别资产利用率问题。",
                "items": summary_items,
            },
            {
                "tab": "决策建议",
                "title": "下一步排查建议",
                "body": "本模式不生成整合经济性结论，也不引用业务保护、可迁移性、迁移成本或风险成本等高级参数。",
                "items": [
                    f"优先排查平均利用率低于 {low_threshold}%、且活跃时段占比较低的资产。",
                    f"疑似僵尸资产的判断还会参考是否存在超过 {active_threshold}% 的明显活跃时段；活跃时段占比上限为 {active_duty_limit}%。",
                    f"建议优先从 {v['top_group']} 分组开始做资产盘点，确认是否存在测试机、闲置实例、废弃服务或长期低负载任务。",
                    "如需判断整合后能省多少钱，应补充整合比例、目标利用率上限和冷却节能假设后切换到标准模式。",
                ],
            },
            {
                "tab": "风险提示",
                "title": "基础模式风险提示",
                "warning": "基础模式是低门槛初筛，不是下线指令。它不能判断业务保护、迁移可行性、隐藏 IO 活动或迁移风险。",
                "items": [
                    "低利用率资产可能承担备份、监控、容灾、低频批处理或业务保活任务。",
                    "在缺少内存、磁盘 IO、网络 IO 和业务标签时，结果应被理解为优先排查名单。",
                    "进入真实整合前，仍需由业务负责人确认资产归属、SLA 和关停窗口。",
                ],
            },
        ]
        return _sections("摘要", sections)

    common_economic_items = [
        f"整合后电费节省比例约为 {_fmt(v['cost_saving_ratio'])}%。",
        f"若当前样本能代表长期运行状态，折算年度运营节省约为 {_money(v['annual_operating_saving'], currency)}。",
        f"一次性整合成本约为 {_money(v['one_time_cost'], currency)}，该成本只在首年扣除一次，不进行年度化放大。",
        f"扣除一次性整合成本后，首年净收益约为 {_money(v['first_year_net'], currency)}。",
    ]

    if mode == "standard":
        sections = [
            {
                "tab": "摘要",
                "title": "标准模式摘要",
                "body": "标准模式在基础筛查上加入候选资产整合比例、整合后目标利用率上限和冷却节能折算，用于形成年度化经济性判断。",
                "items": summary_items + [
                    f"在当前整合假设下，理论可下线或迁移评估资产为 {v['shutdown_assets']} 台/套，整合后平均利用率约 {_fmt(v['post_util'])}%。",
                ],
            },
            {
                "tab": "经济性",
                "title": "标准经济性结论",
                "body": "本部分只使用标准模式参数，不引用业务保护、可迁移性、迁移成本情景或风险评分等增强模式参数。",
                "items": common_economic_items,
            },
            {
                "tab": "决策建议",
                "title": "标准模式决策建议",
                "items": [
                    f"若整合后平均利用率 {_fmt(v['post_util'])}% 仍低于目标利用率上限 {_fmt(safe_util_limit)}%，说明还有一定资源整合空间。",
                    f"建议将 {v['shutdown_assets']} 台/套理论可下线资产作为试点清单，先进行业务归属和运行必要性核验。",
                    "如果首年净收益为正，可优先开展小范围整合试点；如果为负，应降低一次性成本假设或缩小整合范围。",
                ],
            },
            {
                "tab": "风险提示",
                "title": "标准模式风险提示",
                "warning": "标准模式已经能估算年度化收益，但尚未充分过滤业务保护、可迁移性和隐藏 IO 活动。",
                "items": [
                    "低利用率不等于可以立即关停，标准模式输出的是整合评估清单，不是自动执行清单。",
                    "实际整合前仍需补充业务标签、迁移窗口、SLA、备份/容灾要求和回滚预案。",
                    "如果数据中存在内存、磁盘 IO、网络 IO、业务保护或可迁移字段，建议切换到增强模式进行更稳妥的筛选。",
                ],
            },
        ]
        return _sections("摘要", sections)

    immediate_count = actions.get("Immediate Shutdown Assessment", 0)
    migration_count = actions.get("Migration / Consolidation Candidate", 0)
    validation_count = actions.get("Business Validation Required", 0)
    protected_validate_count = actions.get("Protected / Validate Only", 0)
    watchlist_count = actions.get("Utilization Watchlist", 0)

    enhanced_summary_extra = [
        f"增强模式额外参考内存利用率、磁盘 IO、网络 IO、业务保护、可迁移性、迁移成本和重启/业务风险成本。",
        f"当前业务保护资产约 {v['protected_assets']} 台/套，不可迁移或未标记可迁移资产约 {v['non_migratable_assets']} 台/套；这些资产不会被简单视为可直接整合对象。",
    ]
    if actions:
        enhanced_summary_extra.append(
            f"管理动作分类中：立即下线评估 {immediate_count} 台/套，迁移/整合候选 {migration_count} 台/套，需业务核验 {validation_count} 台/套，保护/仅核验 {protected_validate_count} 台/套，持续观察 {watchlist_count} 台/套。"
        )

    sections = [
        {
            "tab": "摘要",
            "title": "增强模式摘要",
            "body": "增强模式不是单纯按低利用率排序，而是在利用率结果上叠加隐藏活动、业务保护、可迁移性和成本风险过滤。",
            "items": summary_items + enhanced_summary_extra,
        },
        {
            "tab": "经济性",
            "title": "增强经济性结论",
            "body": "增强模式下的一次性整合成本由迁移成本和重启/业务风险成本组成，并作为首年净收益的扣减项。",
            "items": common_economic_items + [
                f"其中迁移成本约为 {_money(v['migration_cost'], currency)}，重启/业务风险成本约为 {_money(v['restart_risk_cost'], currency)}。",
                "如果风险成本占比较高，建议优先选择低风险、可迁移、非业务保护资产开展试点，而不是追求一次性最大整合比例。",
            ],
        },
        {
            "tab": "决策建议",
            "title": "增强模式决策建议",
            "items": [
                "优先处理同时满足低利用率、低活跃时段、无明显内存/磁盘/网络 IO 活动、可迁移且非业务保护的资产。",
                "对低利用率但存在明显 IO 活动、业务保护标签或不可迁移属性的资产，应进入业务核验或持续观察，而不是直接纳入下线评估。",
                f"理论可下线或迁移评估资产为 {v['shutdown_assets']} 台/套，建议先从风险评分高、浪费成本高且迁移成本较低的资产开始试点。",
                "如果首年净收益为正，可推进小范围验证；如果首年净收益为负，应先复核迁移成本、风险成本和候选资产范围。",
            ],
        },
        {
            "tab": "风险提示",
            "title": "增强模式风险提示",
            "warning": "增强模式降低了误判概率，但仍然不能替代真实运维审批、业务负责人确认和迁移演练。",
            "items": [
                "内存、磁盘 IO 和网络 IO 只能提示隐藏活动，不能完整识别业务重要性。",
                "业务保护字段和可迁移字段依赖输入数据质量；如果原始 CSV 标注不完整，增强模式也可能低估风险。",
                "迁移成本和重启/业务风险成本是情景估算参数，适合做投资展示和试点筛选，真实执行前需要由运维与业务团队复核。",
            ],
        },
    ]
    return _sections("摘要", sections)


def _build_en(summary: dict, thresholds: dict, mode: str, currency: str, action_counts: Any | None) -> dict:
    v = _shared_values(summary)
    actions = _action_count_map(action_counts)

    low_threshold = thresholds.get("low_util_threshold", 10)
    active_threshold = thresholds.get("high_util_threshold", 40)
    active_duty_limit = thresholds.get("high_duty_threshold", 5)
    safe_util_limit = thresholds.get("safe_util_limit", 70)

    summary_items = [
        f"This analysis covers {v['total_assets']} assets over approximately {_fmt(v['period_days'], 2)} days, with average utilization of {_fmt(v['avg_util'])}%.",
        f"The system identifies {v['low_util_assets']} low-utilization assets, {v['zombie_assets']} suspected zombie assets, and {v['candidate_assets']} consolidation review candidates.",
        f"Sample-period total energy consumption is approximately {_fmt(v['total_energy'])} kWh, with potential waste energy of {_fmt(v['waste_energy'])} kWh. The largest waste concentration is observed in {v['top_group']}.",
    ]

    if mode == "basic":
        sections = [
            {
                "tab": "Summary",
                "title": "Basic Screening Summary",
                "body": "Basic Mode only uses utilization, active-time ratio, and unified power/tariff assumptions. It is designed for quick screening when input fields are limited.",
                "items": summary_items,
            },
            {
                "tab": "Decision",
                "title": "Next-step Review Suggestions",
                "body": "This mode does not generate consolidation economics and does not reference business protection, migratability, migration cost, or risk cost assumptions.",
                "items": [
                    f"Prioritize assets with average utilization below {low_threshold}% and low active-time ratio.",
                    f"Suspected zombie identification also checks whether assets show clear activity above {active_threshold}%; the active-time ratio limit is {active_duty_limit}%.",
                    f"Start asset review from the highest-waste group: {v['top_group']}.",
                    "To estimate consolidation economics, add consolidation ratio, target utilization limit, and cooling-saving assumptions, then switch to Standard Mode.",
                ],
            },
            {
                "tab": "Risk",
                "title": "Basic Mode Risk Notices",
                "warning": "Basic Mode is a low-barrier screening view, not a shutdown command. It cannot judge business protection, migration feasibility, hidden IO activity, or migration risk.",
                "items": [
                    "Low-utilization assets may support backup, monitoring, disaster recovery, batch jobs, or business continuity.",
                    "Without memory, disk IO, network IO, and business tags, results should be treated as a priority review list.",
                    "Before real consolidation, business ownership, SLA, and shutdown windows still need confirmation.",
                ],
            },
        ]
        return _sections("Summary", sections)

    common_economic_items = [
        f"Estimated electricity cost saving ratio after consolidation: {_fmt(v['cost_saving_ratio'])}%.",
        f"If the current sample is representative of long-term operation, annual operating saving is approximately {_money(v['annual_operating_saving'], currency)}.",
        f"One-time consolidation cost is approximately {_money(v['one_time_cost'], currency)}. This cost is deducted once in the first year and is not annualized.",
        f"After deducting one-time consolidation cost, first-year net benefit is approximately {_money(v['first_year_net'], currency)}.",
    ]

    if mode == "standard":
        sections = [
            {
                "tab": "Summary",
                "title": "Standard Mode Summary",
                "body": "Standard Mode adds candidate consolidation ratio, post-consolidation target utilization limit, and cooling-saving conversion to support annualized economics.",
                "items": summary_items + [
                    f"Under the current consolidation assumptions, {v['shutdown_assets']} assets are theoretically selected for shutdown or migration assessment, with post-consolidation average utilization of {_fmt(v['post_util'])}%.",
                ],
            },
            {
                "tab": "Economics",
                "title": "Standard Economic Conclusions",
                "body": "This section only uses Standard Mode parameters and does not reference business protection, migratability, migration-cost scenarios, or risk scoring.",
                "items": common_economic_items,
            },
            {
                "tab": "Decision",
                "title": "Standard Mode Decision Suggestions",
                "items": [
                    f"If post-consolidation utilization {_fmt(v['post_util'])}% remains below the target limit of {_fmt(safe_util_limit)}%, further consolidation potential may exist.",
                    f"Use the {v['shutdown_assets']} theoretically selected assets as a pilot review list and validate business ownership and operational necessity first.",
                    "If first-year net benefit is positive, consider a small pilot. If negative, reduce one-time cost assumptions or narrow the consolidation scope.",
                ],
            },
            {
                "tab": "Risk",
                "title": "Standard Mode Risk Notices",
                "warning": "Standard Mode can estimate annualized value, but it has not fully filtered business protection, migratability, or hidden IO activity.",
                "items": [
                    "Low utilization does not automatically mean an asset can be shut down. The output is a consolidation review list, not an execution list.",
                    "Before real consolidation, business tags, migration windows, SLA, backup/disaster-recovery requirements, and rollback plans should be validated.",
                    "If memory, disk IO, network IO, business protection, or migratability fields are available, switch to Enhanced Mode for a more conservative review.",
                ],
            },
        ]
        return _sections("Summary", sections)

    immediate_count = actions.get("Immediate Shutdown Assessment", 0)
    migration_count = actions.get("Migration / Consolidation Candidate", 0)
    validation_count = actions.get("Business Validation Required", 0)
    protected_validate_count = actions.get("Protected / Validate Only", 0)
    watchlist_count = actions.get("Utilization Watchlist", 0)

    enhanced_summary_extra = [
        "Enhanced Mode additionally references memory utilization, disk IO, network IO, business protection, migratability, migration cost, and restart/business risk cost.",
        f"Current business-protected assets: {v['protected_assets']}; non-migratable or unmarked assets: {v['non_migratable_assets']}. These assets should not be treated as directly consolidatable.",
    ]
    if actions:
        enhanced_summary_extra.append(
            f"Action classification: immediate shutdown assessment {immediate_count}, migration/consolidation candidates {migration_count}, business validation required {validation_count}, protected/validate only {protected_validate_count}, utilization watchlist {watchlist_count}."
        )

    sections = [
        {
            "tab": "Summary",
            "title": "Enhanced Mode Summary",
            "body": "Enhanced Mode is not simple low-utilization sorting. It overlays hidden-activity signals, business protection, migratability, and cost-risk filters on top of utilization results.",
            "items": summary_items + enhanced_summary_extra,
        },
        {
            "tab": "Economics",
            "title": "Enhanced Economic Conclusions",
            "body": "In Enhanced Mode, one-time consolidation cost is composed of migration cost and restart/business risk cost, and is deducted from first-year net benefit.",
            "items": common_economic_items + [
                f"Migration cost is approximately {_money(v['migration_cost'], currency)}, and restart/business risk cost is approximately {_money(v['restart_risk_cost'], currency)}.",
                "If risk cost is material, prioritize low-risk, migratable, non-business-protected assets rather than maximizing consolidation ratio immediately.",
            ],
        },
        {
            "tab": "Decision",
            "title": "Enhanced Mode Decision Suggestions",
            "items": [
                "Prioritize assets that are low-utilization, low-active-time, show no clear memory/disk/network IO activity, are migratable, and are not business-protected.",
                "Assets with low utilization but visible IO activity, business protection, or non-migratable attributes should be routed to business validation or watchlist instead of direct shutdown assessment.",
                f"Theoretical shutdown or migration assessment assets: {v['shutdown_assets']}. Start with assets that have high priority score, high waste cost, and low migration cost.",
                "If first-year net benefit is positive, run a small validation pilot. If negative, review migration cost, risk cost, and candidate scope first.",
            ],
        },
        {
            "tab": "Risk",
            "title": "Enhanced Mode Risk Notices",
            "warning": "Enhanced Mode reduces false positives, but it still cannot replace real operation approval, business-owner confirmation, or migration rehearsal.",
            "items": [
                "Memory, disk IO, and network IO indicate hidden activity but cannot fully determine business criticality.",
                "Business-protection and migratability fields depend on input data quality; incomplete CSV labels may still underestimate risk.",
                "Migration cost and restart/business risk cost are scenario assumptions for portfolio analysis and pilot selection; they should be validated by operations and business teams before execution.",
            ],
        },
    ]
    return _sections("Summary", sections)
