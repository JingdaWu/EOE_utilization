from __future__ import annotations

import pandas as pd


def apply_power_model(df: pd.DataFrame, time_step_hours: float) -> pd.DataFrame:
    work = df.copy()

    utilization_fraction = work["utilization"] / 100

    work["estimated_power_w"] = work["power_idle"] + (
        work["power_peak"] - work["power_idle"]
    ) * utilization_fraction

    work["estimated_power_kw"] = work["estimated_power_w"] / 100
    work["estimated_power_kw"] = work["estimated_power_kw"] / 10
    work["energy_kwh"] = work["estimated_power_kw"] * time_step_hours

    return work


def attach_energy_cost_to_asset_metrics(
    asset_metrics: pd.DataFrame,
    power_timeseries: pd.DataFrame,
    electricity_price: float,
) -> pd.DataFrame:
    energy_by_asset = power_timeseries.groupby("asset_id", as_index=False).agg(
        avg_power_kw=("estimated_power_kw", "mean"),
        peak_power_kw=("estimated_power_kw", "max"),
        min_power_kw=("estimated_power_kw", "min"),
        energy_kwh=("energy_kwh", "sum"),
    )

    result = asset_metrics.merge(energy_by_asset, on="asset_id", how="left")

    for col in ["avg_power_kw", "peak_power_kw", "min_power_kw", "energy_kwh"]:
        result[col] = result[col].fillna(0.0)

    result["cost"] = result["energy_kwh"] * electricity_price

    result["waste_energy_kwh"] = result["energy_kwh"].where(result["is_zombie"], 0.0)
    result["waste_cost"] = result["waste_energy_kwh"] * electricity_price

    result["idle_energy_ratio"] = 0.0
    valid_mask = result["power_peak"] > 0
    result.loc[valid_mask, "idle_energy_ratio"] = (
        result.loc[valid_mask, "power_idle"] / result.loc[valid_mask, "power_peak"] * 100
    )

    return result


def calculate_energy_by_time(
    power_timeseries: pd.DataFrame,
    electricity_price: float,
) -> pd.DataFrame:
    if power_timeseries.empty:
        return pd.DataFrame()

    hourly = power_timeseries.groupby("timestamp", as_index=False).agg(
        total_power_kw=("estimated_power_kw", "sum"),
        total_energy_kwh=("energy_kwh", "sum"),
    )

    hourly["total_cost"] = hourly["total_energy_kwh"] * electricity_price
    return hourly