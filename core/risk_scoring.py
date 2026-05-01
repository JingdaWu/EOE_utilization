from __future__ import annotations

import pandas as pd


def calculate_risk_score(
    asset_metrics: pd.DataFrame,
    low_util_threshold: float,
    high_duty_threshold: float,
) -> pd.DataFrame:
    if asset_metrics.empty:
        return asset_metrics.copy()

    df = asset_metrics.copy()

    cpu_idle_score = (1 - df["avg_utilization"] / max(low_util_threshold, 1)).clip(0, 1)
    peak_inactive_score = (1 - df["high_load_duty"] / max(high_duty_threshold, 1)).clip(0, 1)

    memory_idle_score = (1 - df["avg_memory_utilization"] / 60).clip(0, 1)
    disk_idle_score = (1 - df["avg_disk_io"] / 50).clip(0, 1)
    network_idle_score = (1 - df["avg_network_io"] / 50).clip(0, 1)

    protection_penalty = df["is_business_protected"].astype(float) * 0.45
    migration_penalty = (~df["is_migratable"]).astype(float) * 0.25

    df["risk_score"] = (
        cpu_idle_score * 30
        + peak_inactive_score * 25
        + memory_idle_score * 15
        + disk_idle_score * 10
        + network_idle_score * 10
        - protection_penalty * 100
        - migration_penalty * 100
    ).clip(0, 100)

    df["priority_level"] = df["risk_score"].apply(_priority_level)

    df["action_category"] = df.apply(_action_category, axis=1)

    return df.sort_values(
        ["risk_score", "waste_cost", "avg_utilization"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def _priority_level(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 50:
        return "Medium"
    if score >= 25:
        return "Low"
    return "Watch"


def _action_category(row) -> str:
    if row.get("is_business_protected", False):
        return "Protected / Validate Only"

    if not row.get("is_migratable", True):
        return "Business Validation Required"

    if row.get("risk_score", 0) >= 75 and row.get("is_zombie", False):
        return "Immediate Shutdown Assessment"

    if row.get("risk_score", 0) >= 50:
        return "Migration / Consolidation Candidate"

    if row.get("is_low_util", False):
        return "Utilization Watchlist"

    return "Normal Operation"