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
        f"本次分析包含 {v['total_assets']} 台设备，利用率日志覆盖时间周期约 {_fmt(v['period_days'], 2)} 天，设备平均利用率约为 {_fmt(v['avg_util'])}%。",
        f"设备利用率评估识别出低利用率资产 {v['low_util_assets']} 台、疑似闲置设备 {v['zombie_assets']} 台、评估可整合设备 {v['candidate_assets']} 台。",
        f"利用率日志覆盖时间周期内总耗电量为 {_fmt(v['total_energy'])} kWh，潜在浪费电量约为 {_fmt(v['waste_energy'])} kWh；潜在浪费电量最高的设备为 {v['top_group']}。",
    ]

    if mode == "basic":
        sections = [
            {
                "tab": "摘要",
                "title": "设备利用率评估摘要",
                "body": "基础模式仅使用利用率、统一功率和阈值规则开展分析，适合小数据样本输入与快速初筛。",
                "items": summary_items,
            },
            {
                "tab": "整合建议",
                "title": "设备整合建议",
                "body": "基础模式只能提供设备整合建议，不包含设备整合后的经济性预测评估结果。",
                "items": [
                    f"建议优先排查平均利用率低于 {low_threshold}%且活跃时段占比较低的设备。",
                    f"疑似闲置设备的判断依据为设备活跃时段是否超过 {active_threshold}% 及活跃时段占比是否超过 {active_duty_limit}%。",
                    f"建议优先从 {v['top_group']} 设备开展利用率审核，确认设备是否存在长期闲置、废弃服务或长期低负载状况。",
                    "如需判断实施设备整合后的经济性收益，请切换至进阶或高级模式并补充设备整合阈值、目标利用率等分析所需参数",
                ],
            },
            {
                "tab": "风险提示",
                "title": "基础模式分析局限性提示",
                "warning": "基础模式是仅使用利用率、统一功率和阈值规则开展的初筛判断，不包含设备整合建议。",
                "items": [
                    "低利用率设备可能承担备份、监控、容灾、低频处理或业务保活等重要功能。",
                    "由于缺乏设备内存、磁盘 IO、网络 IO 和业务标签考量，分析结果仅应被理解为优先筛查建议。",
                    "在实际开展设备整合前，仍需由专业业务负责人确认设备归属、SLA 和关停风险性。",
                ],
            },
        ]
        return _sections("摘要", sections)

    common_economic_items = [
        f"设备整合后电费支出节省比率为 {_fmt(v['cost_saving_ratio'])}%。",
        f"如果按照设备整合后状态长期运行数据中心，每年电费支出将节省 {_money(v['annual_operating_saving'], currency)}。",
        f"设备整合成本为 {_money(v['one_time_cost'], currency)}，该成本仅在实施设备整合时消耗，且成本会随设备长期运行进一步稀释。",
        f"扣除设备整合成本后，实施设备整合后数据中心首年经济性净收益约为 {_money(v['first_year_net'], currency)}。",
    ]

    if mode == "standard":
        sections = [
            {
                "tab": "摘要",
                "title": "设备利用率评估摘要",
                "body": "进阶模式将结合设备目标整合比例、目标利用率和冷却收益开展，用于评估设备整合收益。",
                "items": summary_items + [
                    f"在当前设备整合参数设定下，存在 {v['shutdown_assets']} 台可下线或迁移设备，整合后设备利用率将提升至 {_fmt(v['post_util'])}%。",
                ],
            },
            {
                "tab": "经济性分析",
                "title": "设备整合的经济性分析结论",
                "body": "本部分只使用进阶模式输入的相关参数，不考虑业务保护、可迁移性、迁移成本系数及风险系数等高级模式参数。",
                "items": common_economic_items,
            },
            {
                "tab": "决策建议",
                "title": "与设备整合相关的决策建议",
                "items": [
                    f"如果设备整合后预估的平均利用率 {_fmt(v['post_util'])}% 仍大幅低于目标利用率阈值 {_fmt(safe_util_limit)}%，说明数据中心可能仍存在进一步资源整合的空间。",
                    f"建议优先将 {v['shutdown_assets']} 台理论可下线的闲置/低利用率设备作为设备整合试点和运行必要性核验的对象。",
                    "如果设备整合后首年经济性净收益可观，建议优先开展小范围设备整合试点；如果经济性收益预期较小或呈现负值，则建议谨慎考虑设备整合或进一步评估降低设备迁移成本的可行性。",
                ],
            },
            {
                "tab": "风险提示",
                "title": "进阶模式分析局限性提示",
                "warning": "进阶模式虽然已经包含设备整合的经济性收益评估，但尚未充分过滤业务保护、可迁移性和隐藏 IO 等参数。",
                "items": [
                    "低利用率设备可能承担备份、监控、容灾、低频处理或业务保活等重要功能。",
                    "实际开展设备整合前仍建议补充业务标签、迁移窗口、SLA、备份/容灾要求和回滚预案。",
                    "如果数据中存在内存、磁盘 IO、网络 IO、业务保护或可迁移字段，建议切换到高级模式开展更高精度的进一步评估。",
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
        f"高级模式在进阶模式的基础上还将额外考量设备内存利用率、磁盘 IO、网络 IO、业务保护、可迁移性、迁移成本和重启/业务风险成本等高级参数。",
        f"系统识别到 {v['protected_assets']} 台业务保护设备及 {v['non_migratable_assets']} 台不可迁移或未标记可迁移设备；这些设备不会被简单视为可直接整合对象。",
    ]
    if actions:
        enhanced_summary_extra.append(
            f"系统检测到预估可下线设备 {immediate_count} 台，预估可迁移/整合设备 {migration_count} 台，需业务核验设备 {validation_count} 台，处于业务保护及仅核验状态设备 {protected_validate_count} 台，处于持续核验状态设备 {watchlist_count} 台。"
        )

    sections = [
        {
            "tab": "摘要",
            "title": "设备利用率评估摘要",
            "body": "高级模式在进阶模式的基础上还将叠加隐藏活动、业务保护、可迁移性和成本风险过滤。",
            "items": summary_items + enhanced_summary_extra,
        },
        {
            "tab": "经济性分析",
            "title": "设备整合的经济性分析结论",
            "body": "高级模式下的设备整合成本将结合设备迁移成本系数和风险成本系数高精度计算设备整合的经济性收益。",
            "items": common_economic_items + [
                f"设备整合迁移成本为 {_money(v['migration_cost'], currency)}，设备重启/业务风险成本为 {_money(v['restart_risk_cost'], currency)}。",
                "如果设备整合的迁移和风险成本占比较高，建议优先选择低风险、可迁移、非业务保护设备开展整合试点，而不是追求一次性最大规模的设备整合。",
            ],
        },
        {
            "tab": "决策建议",
            "title": "与设备整合相关的决策建议",
            "items": [
                "建议优先整合同时满足低利用率、低活跃时段、无明显内存/磁盘/网络 IO 活动、可迁移且非业务保护的设备。",
                "对于利用率较低但存在明显 IO 活动、业务保护标签或不可迁移属性的设备，应充分开展业务核验或持续观察，不建议优先纳入整合评估。",
                f"系统检测到 {v['shutdown_assets']} 台理论可下线或迁移设备，建议优先从浪费电费成本高且迁移成本较低的设备开始试点整合。",
                "如果设备整合后首年经济性净收益可观，建议优先开展小范围设备整合试点；如果经济性收益预期较小或呈现负值，则建议谨慎考虑设备整合或进一步评估降低设备迁移成本的可行性。",
            ],
        },
        {
            "tab": "风险提示",
            "title": "高级分析模式分析局限性提示",
            "warning": "高级模式虽然提高了预测精度、降低了误判概率，但仍然不能替代真实运维审批、业务负责人确认和迁移演练。",
            "items": [
                "内存、磁盘 IO 和网络 IO 只能显示设备是否涉及隐藏活动，不能完整识别其对实际业务的重要性。",
                "业务保护字段和可迁移字段依赖输入数据质量；如果利用率日志CSV中年存在不完整标注，高级模式也可能低估设备整合风险。",
                "设备迁移成本系数和设备重启/风险成本系数为理论估算参数，仅适合作为整合试点和决策辅助建议，真实执行前仍然需要由运维与业务团队复核。",
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

    summary_items = [  # refined EN report wording
        f"This assessment covers {v['total_assets']} devices / assets over approximately {_fmt(v['period_days'], 2)} days, with average utilization of {_fmt(v['avg_util'])}%.",
        f"The screening identified {v['low_util_assets']} low-utilization assets, {v['zombie_assets']} suspected idle assets, and {v['candidate_assets']} assets eligible for consolidation review.",
        f"During the analyzed log period, total energy consumption was approximately {_fmt(v['total_energy'])} kWh, with potential waste energy of {_fmt(v['waste_energy'])} kWh. The largest waste contribution was observed in {v['top_group']}.",
    ]

    if mode == "basic":
        sections = [  # refined EN report wording
            {
                "tab": "Summary",
                "title": "Utilization Screening Summary",
                "body": "Basic Mode uses only utilization data, uniform power assumptions, and threshold rules. It is intended for quick preliminary screening when the available dataset is limited.",
                "items": summary_items,
            },
            {
                "tab": "Consolidation Review",
                "title": "Preliminary Consolidation Review Suggestions",
                "body": "Basic Mode can highlight potential review targets, but it does not generate post-consolidation economic forecasts.",
                "items": [
                    f"Prioritize review of assets with average utilization below {low_threshold}% and a low active-time share.",
                    f"Suspected idle assets are identified by checking whether utilization exceeds {active_threshold}% and whether the active-time share exceeds {active_duty_limit}%.",
                    f"Start the utilization review with {v['top_group']}, where potential waste is most concentrated.",
                    "To evaluate consolidation economics, switch to Standard or Enhanced Mode and provide the required consolidation ratio, target utilization limit, and cooling-saving assumptions.",
                ],
            },
            {
                "tab": "Risk Notes",
                "title": "Basic Mode Limitations",
                "warning": "Basic Mode is a preliminary screening view, not a shutdown or migration instruction.",
                "items": [
                    "Low-utilization assets may still support backup, monitoring, disaster recovery, low-frequency batch processing, or business-continuity functions.",
                    "Because memory utilization, disk IO, network IO, and business tags are not considered, results should only be treated as a priority review list.",
                    "Before any real consolidation action, asset ownership, SLA requirements, maintenance windows, and shutdown risk must be confirmed by the relevant business and operations teams.",
                ],
            },
        ]
        return _sections("Summary", sections)

    common_economic_items = [  # refined EN report wording
        f"The estimated electricity cost saving ratio after consolidation is {_fmt(v['cost_saving_ratio'])}%.",
        f"If the post-consolidation operating state is maintained over the long term, annual electricity-related operating saving is estimated at {_money(v['annual_operating_saving'], currency)}.",
        f"The one-time consolidation cost is estimated at {_money(v['one_time_cost'], currency)}. This cost is incurred during implementation and is not annualized across the sampled period.",
        f"After deducting the one-time consolidation cost, the estimated first-year net benefit is {_money(v['first_year_net'], currency)}.",
    ]

    if mode == "standard":
        sections = [  # refined EN report wording
            {
                "tab": "Summary",
                "title": "Utilization and Consolidation Summary",
                "body": "Standard Mode adds consolidation ratio, target utilization limit, and cooling-saving conversion to estimate resource-consolidation benefits.",
                "items": summary_items + [
                    f"Under the current consolidation assumptions, {v['shutdown_assets']} assets are flagged for shutdown or migration review, and post-consolidation average utilization is estimated at {_fmt(v['post_util'])}%.",
                ],
            },
            {
                "tab": "Economics",
                "title": "Consolidation Economics",
                "body": "This section uses only Standard Mode inputs. It does not account for business protection, migratability, migration-cost multipliers, risk-cost multipliers, or enhanced risk scoring.",
                "items": common_economic_items,
            },
            {
                "tab": "Recommendations",
                "title": "Management Recommendations for Consolidation",
                "items": [
                    f"If the estimated post-consolidation average utilization of {_fmt(v['post_util'])}% remains well below the target utilization limit of {_fmt(safe_util_limit)}%, additional consolidation potential may still exist.",
                    f"Use the {v['shutdown_assets']} assets flagged for shutdown or migration review as the first pilot pool, and validate their business ownership and operational necessity before implementation.",
                    "If the estimated first-year net benefit is meaningful, start with a small-scale consolidation pilot. If the benefit is limited or negative, reassess migration effort, operational constraints, and candidate selection before proceeding.",
                ],
            },
            {
                "tab": "Risk Notes",
                "title": "Standard Mode Limitations",
                "warning": "Standard Mode includes consolidation economics, but it does not fully filter business protection, migratability, or hidden IO activity.",
                "items": [
                    "Low utilization does not automatically mean an asset can be shut down or migrated.",
                    "Before real consolidation, business tags, migration windows, SLA requirements, backup / disaster-recovery requirements, and rollback plans should be validated.",
                    "If memory utilization, disk IO, network IO, business protection, or migratability fields are available, switch to Enhanced Mode for a more conservative review.",
                ],
            },
        ]
        return _sections("Summary", sections)

    immediate_count = actions.get("Immediate Shutdown Assessment", 0)
    migration_count = actions.get("Migration / Consolidation Candidate", 0)
    validation_count = actions.get("Business Validation Required", 0)
    protected_validate_count = actions.get("Protected / Validate Only", 0)
    watchlist_count = actions.get("Utilization Watchlist", 0)

    enhanced_summary_extra = [  # refined EN report wording
        "Enhanced Mode further considers memory utilization, disk IO, network IO, business protection, migratability, migration cost, and restart / business risk cost.",
        f"The dataset includes {v['protected_assets']} business-protected assets and {v['non_migratable_assets']} non-migratable or unmarked assets. These assets should not be treated as directly consolidatable without validation.",
    ]
    if actions:
        enhanced_summary_extra.append(  # refined EN report wording
            f"Recommended action classification: {immediate_count} assets for immediate shutdown assessment, {migration_count} migration / consolidation candidates, {validation_count} assets requiring business validation, {protected_validate_count} protected assets for validation only, and {watchlist_count} assets on the utilization watchlist."
        )

    sections = [  # refined EN report wording
        {
            "tab": "Summary",
            "title": "Enhanced Utilization and Risk-filtered Consolidation Summary",
            "body": "Enhanced Mode is not a simple low-utilization ranking. It overlays hidden-activity signals, business protection, migratability, and cost-risk filters on top of the utilization assessment.",
            "items": summary_items + enhanced_summary_extra,
        },
        {
            "tab": "Economics",
            "title": "Risk-adjusted Consolidation Economics",
            "body": "In Enhanced Mode, one-time consolidation cost includes both migration cost and restart / business risk cost, and this combined cost is deducted from first-year net benefit.",
            "items": common_economic_items + [
                f"Migration cost is estimated at {_money(v['migration_cost'], currency)}, while restart / business risk cost is estimated at {_money(v['restart_risk_cost'], currency)}.",
                "If migration or risk cost is material, prioritize low-risk, migratable, non-business-protected assets instead of maximizing the consolidation ratio in a single step.",
            ],
        },
        {
            "tab": "Recommendations",
            "title": "Risk-aware Management Recommendations",
            "items": [
                "Prioritize assets that are low-utilization, low-active-time, show no clear memory / disk / network IO activity, are migratable, and are not business-protected.",
                "Assets with low utilization but visible IO activity, business-protection labels, or non-migratable attributes should be routed to business validation or continued observation rather than immediate shutdown assessment.",
                f"The system flags {v['shutdown_assets']} assets for shutdown or migration review. Start with assets that combine high waste cost, low migration cost, and low business risk.",
                "If first-year net benefit is positive, proceed through a controlled pilot. If it is negative, first review migration cost, risk cost, and candidate scope before considering implementation.",
            ],
        },
        {
            "tab": "Risk Notes",
            "title": "Enhanced Mode Limitations",
            "warning": "Enhanced Mode lowers the probability of false positives, but it still cannot replace production approval, business-owner confirmation, or migration rehearsal.",
            "items": [
                "Memory utilization, disk IO, and network IO can reveal hidden activity, but they cannot fully determine business criticality.",
                "Business-protection and migratability fields depend on CSV data quality; incomplete or outdated labels may still underestimate consolidation risk.",
                "Migration cost and restart / business risk cost are scenario assumptions for portfolio analysis and pilot selection. They should be validated by operations and business teams before execution.",
            ],
        },
    ]
    return _sections("Summary", sections)
