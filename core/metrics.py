from __future__ import annotations

import pandas as pd


def calculate_asset_metrics(
    df: pd.DataFrame,
    high_util_threshold: float,
    low_util_threshold: float,
    high_duty_threshold: float,
) -> pd.DataFrame:
    work = df.copy()
    work["is_high_load_point"] = work["utilization"] >= high_util_threshold

    grouped = work.groupby("asset_id", as_index=False).agg(
        asset_type=("asset_type", "first"),
        group=("group", "first"),
        avg_utilization=("utilization", "mean"),
        max_utilization=("utilization", "max"),
        min_utilization=("utilization", "min"),
        p90_utilization=("utilization", lambda x: x.quantile(0.90)),
        p95_utilization=("utilization", lambda x: x.quantile(0.95)),
        high_load_duty=("is_high_load_point", "mean"),
        avg_memory_utilization=("memory_utilization", "mean"),
        max_memory_utilization=("memory_utilization", "max"),
        avg_disk_io=("disk_io", "mean"),
        max_disk_io=("disk_io", "max"),
        avg_network_io=("network_io", "mean"),
        max_network_io=("network_io", "max"),
        power_idle=("power_idle", "mean"),
        power_peak=("power_peak", "mean"),
        capacity=("capacity", "mean"),
        business_critical=("business_critical", "first"),
        migratable=("migratable", "first"),
        migration_cost=("migration_cost", "mean"),
        restart_risk_cost=("restart_risk_cost", "mean"),
        record_count=("utilization", "count"),
    )

    grouped["high_load_duty"] = grouped["high_load_duty"] * 100

    grouped["is_low_util"] = grouped["avg_utilization"] < low_util_threshold
    grouped["is_zombie_basic"] = (
        (grouped["avg_utilization"] < low_util_threshold)
        & (grouped["high_load_duty"] < high_duty_threshold)
    )

    grouped["has_hidden_activity"] = (
        (grouped["avg_memory_utilization"] >= 50)
        | (grouped["avg_disk_io"] >= 40)
        | (grouped["avg_network_io"] >= 40)
    )

    grouped["is_business_protected"] = grouped["business_critical"].astype(str).str.lower().eq("yes")
    grouped["is_migratable"] = grouped["migratable"].astype(str).str.lower().eq("yes")

    grouped["is_zombie"] = (
        grouped["is_zombie_basic"]
        & (~grouped["has_hidden_activity"])
        & (~grouped["is_business_protected"])
    )

    return grouped.sort_values("avg_utilization", ascending=True).reset_index(drop=True)


def calculate_group_metrics(asset_metrics: pd.DataFrame) -> pd.DataFrame:
    if asset_metrics.empty:
        return pd.DataFrame()

    grouped = asset_metrics.groupby("group", as_index=False).agg(
        asset_count=("asset_id", "count"),
        asset_type_count=("asset_type", "nunique"),
        avg_utilization=("avg_utilization", "mean"),
        p95_utilization=("p95_utilization", "mean"),
        max_utilization=("max_utilization", "max"),
        avg_memory_utilization=("avg_memory_utilization", "mean"),
        avg_disk_io=("avg_disk_io", "mean"),
        avg_network_io=("avg_network_io", "mean"),
        low_util_assets=("is_low_util", "sum"),
        zombie_assets=("is_zombie", "sum"),
        protected_assets=("is_business_protected", "sum"),
        migratable_assets=("is_migratable", "sum"),
        total_energy_kwh=("energy_kwh", "sum"),
        total_cost=("cost", "sum"),
        waste_energy_kwh=("waste_energy_kwh", "sum"),
        waste_cost=("waste_cost", "sum"),
        total_capacity=("capacity", "sum"),
    )

    grouped["low_util_ratio"] = grouped["low_util_assets"] / grouped["asset_count"] * 100
    grouped["zombie_ratio"] = grouped["zombie_assets"] / grouped["asset_count"] * 100

    return grouped.sort_values("waste_cost", ascending=False).reset_index(drop=True)


def calculate_type_metrics(asset_metrics: pd.DataFrame) -> pd.DataFrame:
    if asset_metrics.empty:
        return pd.DataFrame()

    grouped = asset_metrics.groupby("asset_type", as_index=False).agg(
        asset_count=("asset_id", "count"),
        avg_utilization=("avg_utilization", "mean"),
        p95_utilization=("p95_utilization", "mean"),
        low_util_assets=("is_low_util", "sum"),
        zombie_assets=("is_zombie", "sum"),
        total_energy_kwh=("energy_kwh", "sum"),
        total_cost=("cost", "sum"),
        waste_energy_kwh=("waste_energy_kwh", "sum"),
        waste_cost=("waste_cost", "sum"),
    )

    grouped["low_util_ratio"] = grouped["low_util_assets"] / grouped["asset_count"] * 100
    grouped["zombie_ratio"] = grouped["zombie_assets"] / grouped["asset_count"] * 100

    return grouped.sort_values("waste_cost", ascending=False).reset_index(drop=True)