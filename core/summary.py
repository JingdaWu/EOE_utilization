from __future__ import annotations

import pandas as pd


def calculate_summary(
    asset_metrics: pd.DataFrame,
    group_metrics: pd.DataFrame,
    consolidation_summary: dict,
    period_days: float,
) -> dict:
    if asset_metrics.empty:
        return {}

    total_assets = int(len(asset_metrics))
    low_util_assets = int(asset_metrics["is_low_util"].sum())
    zombie_assets = int(asset_metrics["is_zombie"].sum())
    protected_assets = int(asset_metrics["is_business_protected"].sum())
    migratable_assets = int(asset_metrics["is_migratable"].sum())

    total_energy = float(asset_metrics["energy_kwh"].sum())
    total_cost = float(asset_metrics["cost"].sum())
    waste_energy = float(asset_metrics["waste_energy_kwh"].sum())
    waste_cost = float(asset_metrics["waste_cost"].sum())

    avg_utilization = float(asset_metrics["avg_utilization"].mean())
    p95_utilization = float(asset_metrics["p95_utilization"].mean())

    annualization_factor = 365 / max(period_days, 1 / 24)

    gross_saving = float(consolidation_summary.get("gross_saving_cost", waste_cost))
    net_saving = float(consolidation_summary.get("net_saving_cost", gross_saving))

    summary = {
        "period_days": float(period_days),
        "annualization_factor": float(annualization_factor),

        "total_assets": total_assets,
        "low_util_assets": low_util_assets,
        "zombie_assets": zombie_assets,
        "protected_assets": protected_assets,
        "migratable_assets": migratable_assets,

        "low_util_ratio": low_util_assets / total_assets * 100 if total_assets else 0,
        "zombie_ratio": zombie_assets / total_assets * 100 if total_assets else 0,

        "avg_utilization": avg_utilization,
        "p95_utilization": p95_utilization,

        "total_energy_kwh": total_energy,
        "total_cost": total_cost,
        "waste_energy_kwh": waste_energy,
        "waste_cost": waste_cost,

        "candidate_assets": int(consolidation_summary.get("candidate_assets", 0)),
        "estimated_shutdown_assets": int(consolidation_summary.get("estimated_shutdown_assets", 0)),
        "post_avg_utilization": float(consolidation_summary.get("post_avg_utilization", avg_utilization)),

        "saving_energy_kwh": float(consolidation_summary.get("saving_energy_kwh", waste_energy)),
        "saving_cost": float(consolidation_summary.get("saving_cost", waste_cost)),
        "cooling_saving_kwh": float(consolidation_summary.get("cooling_saving_kwh", 0)),
        "cooling_saving_cost": float(consolidation_summary.get("cooling_saving_cost", 0)),

        "migration_cost": float(consolidation_summary.get("migration_cost", 0)),
        "restart_risk_cost": float(consolidation_summary.get("restart_risk_cost", 0)),
        "gross_saving_cost": gross_saving,
        "net_saving_cost": net_saving,

        "annual_gross_saving": float(consolidation_summary.get("annual_gross_saving", gross_saving * annualization_factor)),
        "annual_net_saving": float(consolidation_summary.get("annual_net_saving", net_saving * annualization_factor)),
    }

    if group_metrics is not None and not group_metrics.empty:
        top_group = group_metrics.sort_values("waste_cost", ascending=False).iloc[0]
        summary["top_waste_group"] = str(top_group["group"])
        summary["top_waste_group_cost"] = float(top_group["waste_cost"])
    else:
        summary["top_waste_group"] = "N/A"
        summary["top_waste_group_cost"] = 0.0

    return summary


def build_summary_dataframe(summary: dict) -> pd.DataFrame:
    return pd.DataFrame([summary])


def build_priority_asset_list(asset_metrics: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    if asset_metrics.empty:
        return asset_metrics.copy()

    sort_cols = []
    ascending = []

    if "risk_score" in asset_metrics.columns:
        sort_cols.append("risk_score")
        ascending.append(False)

    sort_cols.extend(["waste_cost", "avg_utilization"])
    ascending.extend([False, True])

    return asset_metrics.sort_values(sort_cols, ascending=ascending).head(limit).reset_index(drop=True)


def build_management_action_counts(asset_metrics: pd.DataFrame) -> pd.DataFrame:
    if asset_metrics.empty or "action_category" not in asset_metrics.columns:
        return pd.DataFrame()

    result = asset_metrics.groupby("action_category", as_index=False).agg(
        asset_count=("asset_id", "count"),
        avg_risk_score=("risk_score", "mean"),
        total_waste_cost=("waste_cost", "sum"),
        total_energy_kwh=("energy_kwh", "sum"),
    )

    return result.sort_values("total_waste_cost", ascending=False).reset_index(drop=True)