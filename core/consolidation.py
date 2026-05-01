from __future__ import annotations

import math

import pandas as pd


def _select_candidates(asset_metrics: pd.DataFrame) -> pd.DataFrame:
    if asset_metrics.empty:
        return asset_metrics.copy()

    candidate_mask = (
        asset_metrics["is_zombie"]
        & asset_metrics["is_migratable"]
        & (~asset_metrics["is_business_protected"])
    )

    candidates = asset_metrics[candidate_mask].copy()

    if "risk_score" in candidates.columns:
        candidates = candidates.sort_values(
            ["risk_score", "avg_utilization", "energy_kwh"],
            ascending=[False, True, False],
        )
    else:
        candidates = candidates.sort_values(
            ["avg_utilization", "energy_kwh"],
            ascending=[True, False],
        )

    return candidates.reset_index(drop=True)


def calculate_consolidation(
    asset_metrics: pd.DataFrame,
    consolidation_ratio: float,
    safe_util_limit: float,
    electricity_price: float,
    cooling_factor: float,
    annualization_factor: float,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    if asset_metrics.empty:
        return pd.DataFrame(), pd.DataFrame(), {}

    work = asset_metrics.copy()
    candidates = _select_candidates(work)

    target_shutdown = int(math.floor(len(candidates) * consolidation_ratio / 100))

    total_capacity = work["capacity"].sum()
    total_load = (work["avg_utilization"] / 100 * work["capacity"]).sum()

    selected_rows = []

    for _, row in candidates.iterrows():
        if len(selected_rows) >= target_shutdown:
            break

        trial_capacity_removed = sum(item["capacity"] for item in selected_rows) + row["capacity"]
        trial_remaining_capacity = max(total_capacity - trial_capacity_removed, 0.0001)
        trial_post_util = total_load / trial_remaining_capacity * 100

        if trial_post_util <= safe_util_limit:
            selected_rows.append(row.to_dict())

    shutdown_assets = pd.DataFrame(selected_rows)

    selected_ids = set(shutdown_assets["asset_id"].tolist()) if not shutdown_assets.empty else set()
    work["selected_for_shutdown_assessment"] = work["asset_id"].isin(selected_ids)

    removed_capacity = shutdown_assets["capacity"].sum() if not shutdown_assets.empty else 0.0
    remaining_capacity = max(total_capacity - removed_capacity, 0.0001)
    post_avg_utilization = total_load / remaining_capacity * 100

    saving_energy_kwh = shutdown_assets["energy_kwh"].sum() if not shutdown_assets.empty else 0.0
    saving_cost = saving_energy_kwh * electricity_price

    cooling_saving_kwh = saving_energy_kwh * cooling_factor
    cooling_saving_cost = cooling_saving_kwh * electricity_price

    migration_cost = shutdown_assets["migration_cost"].sum() if not shutdown_assets.empty else 0.0
    restart_risk_cost = shutdown_assets["restart_risk_cost"].sum() if not shutdown_assets.empty else 0.0

    gross_saving_cost = saving_cost + cooling_saving_cost
    net_saving_cost = gross_saving_cost - migration_cost - restart_risk_cost

    annual_gross_saving = gross_saving_cost * annualization_factor
    annual_net_saving = net_saving_cost * annualization_factor

    summary = {
        "candidate_assets": int(len(candidates)),
        "estimated_shutdown_assets": int(len(shutdown_assets)),
        "post_avg_utilization": float(post_avg_utilization),
        "saving_energy_kwh": float(saving_energy_kwh),
        "saving_cost": float(saving_cost),
        "cooling_saving_kwh": float(cooling_saving_kwh),
        "cooling_saving_cost": float(cooling_saving_cost),
        "migration_cost": float(migration_cost),
        "restart_risk_cost": float(restart_risk_cost),
        "gross_saving_cost": float(gross_saving_cost),
        "net_saving_cost": float(net_saving_cost),
        "annual_gross_saving": float(annual_gross_saving),
        "annual_net_saving": float(annual_net_saving),
        "safe_util_limit": float(safe_util_limit),
        "total_capacity": float(total_capacity),
        "remaining_capacity": float(remaining_capacity),
    }

    group_result = calculate_group_consolidation(
        asset_metrics=work,
        consolidation_ratio=consolidation_ratio,
        safe_util_limit=safe_util_limit,
        electricity_price=electricity_price,
        cooling_factor=cooling_factor,
        annualization_factor=annualization_factor,
    )

    return work, group_result, summary


def calculate_group_consolidation(
    asset_metrics: pd.DataFrame,
    consolidation_ratio: float,
    safe_util_limit: float,
    electricity_price: float,
    cooling_factor: float,
    annualization_factor: float,
) -> pd.DataFrame:
    rows = []

    for group_name, group_df in asset_metrics.groupby("group"):
        candidates = _select_candidates(group_df)
        target_shutdown = int(math.floor(len(candidates) * consolidation_ratio / 100))

        total_capacity = group_df["capacity"].sum()
        total_load = (group_df["avg_utilization"] / 100 * group_df["capacity"]).sum()

        selected_rows = []

        for _, row in candidates.iterrows():
            if len(selected_rows) >= target_shutdown:
                break

            trial_removed_capacity = sum(item["capacity"] for item in selected_rows) + row["capacity"]
            trial_remaining_capacity = max(total_capacity - trial_removed_capacity, 0.0001)
            trial_post_util = total_load / trial_remaining_capacity * 100

            if trial_post_util <= safe_util_limit:
                selected_rows.append(row.to_dict())

        selected = pd.DataFrame(selected_rows)

        removed_capacity = selected["capacity"].sum() if not selected.empty else 0.0
        remaining_capacity = max(total_capacity - removed_capacity, 0.0001)
        post_util = total_load / remaining_capacity * 100

        saving_energy = selected["energy_kwh"].sum() if not selected.empty else 0.0
        saving_cost = saving_energy * electricity_price
        cooling_saving = saving_energy * cooling_factor
        cooling_saving_cost = cooling_saving * electricity_price
        migration_cost = selected["migration_cost"].sum() if not selected.empty else 0.0
        restart_risk_cost = selected["restart_risk_cost"].sum() if not selected.empty else 0.0

        gross_saving = saving_cost + cooling_saving_cost
        net_saving = gross_saving - migration_cost - restart_risk_cost

        rows.append(
            {
                "group": group_name,
                "asset_count": int(len(group_df)),
                "candidate_assets": int(len(candidates)),
                "estimated_shutdown": int(len(selected)),
                "avg_utilization": float(group_df["avg_utilization"].mean()),
                "post_avg_utilization": float(post_util),
                "zombie_assets": int(group_df["is_zombie"].sum()),
                "protected_assets": int(group_df["is_business_protected"].sum()),
                "saving_energy_kwh": float(saving_energy),
                "saving_cost": float(saving_cost),
                "cooling_saving_kwh": float(cooling_saving),
                "cooling_saving_cost": float(cooling_saving_cost),
                "migration_cost": float(migration_cost),
                "restart_risk_cost": float(restart_risk_cost),
                "gross_saving_cost": float(gross_saving),
                "net_saving_cost": float(net_saving),
                "annual_net_saving": float(net_saving * annualization_factor),
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    return result.sort_values("net_saving_cost", ascending=False).reset_index(drop=True)