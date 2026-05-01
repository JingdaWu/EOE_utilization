from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "asset_id", "utilization"]

OPTIONAL_COLUMNS = [
    "asset_type",
    "group",
    "power_idle",
    "power_peak",
    "capacity",
    "memory_utilization",
    "disk_io",
    "network_io",
    "business_critical",
    "migratable",
    "migration_cost",
    "restart_risk_cost",
]


COLUMN_ALIASES = {
    "timestamp": [
        "timestamp", "time", "datetime", "date_time", "date", "时间", "时间戳"
    ],
    "asset_id": [
        "asset_id", "device_id", "server_id", "id", "asset", "device", "server",
        "设备id", "资产id", "设备编号", "资产编号"
    ],
    "utilization": [
        "utilization", "cpu_utilization", "gpu_utilization", "usage", "load", "util",
        "core_utilization", "设备利用率", "利用率", "cpu利用率", "负载率", "稼动率"
    ],
    "asset_type": [
        "asset_type", "type", "device_type", "server_type", "equipment_type",
        "资产类型", "设备类型"
    ],
    "group": [
        "group", "zone", "rack", "room", "line", "area", "cluster", "business",
        "分组", "区域", "机柜", "产线", "业务线"
    ],
    "power_idle": [
        "power_idle", "idle_power", "p_idle", "standby_power", "空闲功率", "待机功率"
    ],
    "power_peak": [
        "power_peak", "peak_power", "rated_power", "p_peak", "full_power",
        "满载功率", "额定功率"
    ],
    "capacity": [
        "capacity", "resource_capacity", "rated_capacity", "容量", "资源容量"
    ],
    "memory_utilization": [
        "memory_utilization", "memory_usage", "mem_util", "memory", "内存利用率"
    ],
    "disk_io": [
        "disk_io", "storage_io", "io_disk", "disk", "磁盘io", "存储io"
    ],
    "network_io": [
        "network_io", "net_io", "network", "bandwidth", "网络io", "网络利用率"
    ],
    "business_critical": [
        "business_critical", "critical", "reserved", "protected",
        "关键业务", "业务保留", "保护资产"
    ],
    "migratable": [
        "migratable", "can_migrate", "migration_allowed", "movable",
        "可迁移", "支持迁移"
    ],
    "migration_cost": [
        "migration_cost", "migrate_cost", "迁移成本"
    ],
    "restart_risk_cost": [
        "restart_risk_cost", "restart_cost", "risk_cost", "重启风险成本", "风险成本"
    ],
}


def get_sample_csv_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sample" / "sample_utilization_template.csv"


def read_sample_csv() -> pd.DataFrame:
    return pd.read_csv(get_sample_csv_path())


def read_sample_csv_bytes() -> bytes:
    return get_sample_csv_path().read_bytes()


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(uploaded_file)

    raise ValueError("Unsupported file type")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    original_columns = list(df.columns)
    lookup = {str(col).strip().lower(): col for col in original_columns}

    rename_map = {}

    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            alias_lower = alias.strip().lower()
            if alias_lower in lookup:
                rename_map[lookup[alias_lower]] = standard_name
                break

    return df.rename(columns=rename_map)


def _normalize_yes_no(value, default: str) -> str:
    if pd.isna(value):
        return default

    text = str(value).strip().lower()

    yes_values = {"yes", "y", "true", "1", "是", "可", "可以", "支持", "critical"}
    no_values = {"no", "n", "false", "0", "否", "不可", "不支持", "non-critical"}

    if text in yes_values:
        return "Yes"

    if text in no_values:
        return "No"

    return default


def clean_utilization_data(
    df: pd.DataFrame,
    default_idle_power: float,
    default_peak_power: float,
) -> pd.DataFrame:
    df = normalize_columns(df).copy()

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["asset_id"] = df["asset_id"].astype(str).str.strip()
    df["utilization"] = pd.to_numeric(df["utilization"], errors="coerce")

    df = df.dropna(subset=["timestamp", "asset_id", "utilization"])
    df = df.drop_duplicates(subset=["timestamp", "asset_id"], keep="last")

    if df.empty:
        raise ValueError("No valid records after data cleaning.")

    if df["utilization"].max() <= 1.2:
        df["utilization"] = df["utilization"] * 100

    df["utilization"] = df["utilization"].clip(0, 100)

    if "asset_type" not in df.columns:
        df["asset_type"] = "Generic Asset"
    df["asset_type"] = df["asset_type"].fillna("Generic Asset").astype(str)

    if "group" not in df.columns:
        df["group"] = "Default Group"
    df["group"] = df["group"].fillna("Default Group").astype(str)

    if "power_idle" not in df.columns:
        df["power_idle"] = default_idle_power
    df["power_idle"] = pd.to_numeric(df["power_idle"], errors="coerce").fillna(default_idle_power).clip(lower=0)

    if "power_peak" not in df.columns:
        df["power_peak"] = default_peak_power
    df["power_peak"] = pd.to_numeric(df["power_peak"], errors="coerce").fillna(default_peak_power).clip(lower=0)

    wrong_power_mask = df["power_peak"] < df["power_idle"]
    df.loc[wrong_power_mask, "power_peak"] = df.loc[wrong_power_mask, "power_idle"]

    if "capacity" not in df.columns:
        df["capacity"] = 1.0
    df["capacity"] = pd.to_numeric(df["capacity"], errors="coerce").fillna(1.0).clip(lower=0.0001)

    for col in ["memory_utilization", "disk_io", "network_io"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        if df[col].max() <= 1.2:
            df[col] = df[col] * 100

        df[col] = df[col].clip(0, 100)

    if "business_critical" not in df.columns:
        df["business_critical"] = "No"
    df["business_critical"] = df["business_critical"].apply(lambda x: _normalize_yes_no(x, "No"))

    if "migratable" not in df.columns:
        df["migratable"] = "Yes"
    df["migratable"] = df["migratable"].apply(lambda x: _normalize_yes_no(x, "Yes"))

    if "migration_cost" not in df.columns:
        df["migration_cost"] = 0.0
    df["migration_cost"] = pd.to_numeric(df["migration_cost"], errors="coerce").fillna(0.0).clip(lower=0)

    if "restart_risk_cost" not in df.columns:
        df["restart_risk_cost"] = 0.0
    df["restart_risk_cost"] = pd.to_numeric(df["restart_risk_cost"], errors="coerce").fillna(0.0).clip(lower=0)

    df = df.sort_values(["asset_id", "timestamp"]).reset_index(drop=True)
    return df


def estimate_time_step_hours(df: pd.DataFrame) -> float:
    timestamps = (
        df["timestamp"]
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    if len(timestamps) < 2:
        return 1.0

    diffs = timestamps.diff().dropna().dt.total_seconds() / 3600
    median_diff = diffs.median()

    if pd.isna(median_diff) or median_diff <= 0:
        return 1.0

    return float(median_diff)


def get_analysis_period_days(df: pd.DataFrame) -> float:
    if df.empty:
        return 1.0

    start = df["timestamp"].min()
    end = df["timestamp"].max()

    hours = max((end - start).total_seconds() / 3600, 1.0)
    return max(hours / 24, 1.0 / 24)