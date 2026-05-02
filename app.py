from __future__ import annotations

import pandas as pd
import streamlit as st

from i18n import get_text
from report import build_utilization_report

from core.data_loader import (
    read_uploaded_file,
    read_sample_csv_bytes,
    clean_utilization_data,
    estimate_time_step_hours,
    get_analysis_period_days,
)
from core.metrics import (
    calculate_asset_metrics,
    calculate_group_metrics,
    calculate_type_metrics,
)
from core.power_model import (
    apply_power_model,
    attach_energy_cost_to_asset_metrics,
    calculate_energy_by_time,
)
from core.consolidation import calculate_consolidation
from core.risk_scoring import calculate_risk_score
from core.summary import (
    calculate_summary,
    build_priority_asset_list,
    build_management_action_counts,
)

from visualization.plots import (
    create_asset_status_pie,
    create_cost_saving_pie,
    create_annual_economics_bar,
    create_hourly_power_chart,
)


# ============================================================
# Language state
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = "en"


def toggle_language() -> None:
    st.session_state.language = "zh" if st.session_state.language == "en" else "en"


language = st.session_state.language
T = get_text(language)
is_zh = language == "zh"

st.set_page_config(
    page_title=T["page_title"],
    page_icon="📊",
    layout="wide",
)


# ============================================================
# UI style
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2.4rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255,255,255,0.10);
        overflow-y: auto;
    }

    [data-testid="stSidebarContent"] {
        overflow-y: auto;
        max-height: 100vh;
        padding-bottom: 2rem;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(0,174,239,0.18), rgba(14,17,23,0.96));
        border: 1px solid rgba(0,194,255,0.28);
        border-radius: 20px;
        padding: 24px 24px 18px 24px;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 6px;
        letter-spacing: 0.2px;
        color: #F7FBFF;
    }

    .hero-subtitle {
        font-size: 15px;
        opacity: 0.86;
        line-height: 1.5;
        margin-bottom: 14px;
        color: #EAF8FF;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 6px;
    }

    .chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        color: #EAF8FF;
        background: rgba(0,174,239,0.16);
        border: 1px solid rgba(0,174,239,0.30);
    }

    .section-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 14px 14px 10px 14px;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }

    .section-title {
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 2px;
        color: #F5FBFF;
    }

    .section-desc {
        font-size: 12px;
        opacity: 0.76;
        margin-bottom: 0px;
        color: #EAF8FF;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 2px;
        color: #F7FBFF;
    }

    .sidebar-subtitle {
        font-size: 12px;
        opacity: 0.74;
        margin-bottom: 10px;
        color: #EAF8FF;
    }

    .panel-title {
        font-size: 22px;
        font-weight: 800;
        margin: 4px 0 12px 0;
        color: #F7FBFF;
    }

    .panel-subtitle {
        font-size: 13px;
        opacity: 0.74;
        margin-top: -6px;
        margin-bottom: 12px;
        color: #EAF8FF;
    }

    .scenario-bar {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 14px;
    }

    .scenario-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
    }

    .scenario-item {
        background: rgba(255,255,255,0.025);
        border-radius: 12px;
        padding: 10px 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }

    .scenario-label {
        font-size: 11px;
        opacity: 0.65;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 4px;
        color: #EAF8FF;
    }

    .scenario-value {
        font-size: 14px;
        font-weight: 700;
        color: #F7FBFF;
    }

    .summary-card {
        background: linear-gradient(135deg, rgba(0,174,239,0.12), rgba(255,255,255,0.02));
        border: 1px solid rgba(0,174,239,0.20);
        border-radius: 18px;
        padding: 16px 16px 4px 16px;
        margin-bottom: 14px;
    }

    .summary-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 10px;
        color: #F7FBFF;
    }

    .comparison-title {
        font-size: 18px;
        line-height: 1.25;
        font-weight: 800;
        margin: 4px 0 12px 0;
        color: #F7FBFF;
    }

    .small-note {
        font-size: 12px;
        opacity: 0.72;
        margin-top: 4px;
        margin-bottom: 0px;
        color: #EAF8FF;
    }

    .empty-state {
        background: rgba(255,255,255,0.02);
        border: 1px dashed rgba(0,194,255,0.25);
        border-radius: 18px;
        padding: 24px 20px;
        margin-top: 10px;
    }

    .empty-title {
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 8px;
        color: #F7FBFF;
    }

    .empty-body {
        font-size: 14px;
        opacity: 0.80;
        line-height: 1.7;
        color: #EAF8FF;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(0,194,255,0.30) !important;
        background: rgba(0,174,239,0.16) !important;
        color: #F7FBFF !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: rgba(0,194,255,0.65) !important;
        background: rgba(0,174,239,0.26) !important;
        color: #FFFFFF !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, rgba(0,174,239,0.85), rgba(0,115,180,0.85)) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(0,194,255,0.65) !important;
        box-shadow: 0 8px 18px rgba(0,174,239,0.18) !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(0,194,255,0.95), rgba(0,130,205,0.95)) !important;
        color: #FFFFFF !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.035) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        border-radius: 16px !important;
        padding: 14px 14px 10px 14px !important;
        min-height: 104px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.08) !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] div,
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span {
        color: rgba(234,248,255,0.78) !important;
        font-size: 14px !important;
        line-height: 1.25 !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] span {
        color: #F7FBFF !important;
        font-weight: 800 !important;
    }

    [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent !important;
        border-bottom: none !important;
    }

    [data-baseweb="tab-border"],
    [data-baseweb="tab-highlight"] {
        display: none !important;
        height: 0px !important;
        background: transparent !important;
        border: none !important;
    }

    [data-baseweb="tab"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 12px !important;
        color: #EAF8FF !important;
        padding: 10px 14px !important;
        min-height: 46px !important;
        box-shadow: none !important;
    }

    [data-baseweb="tab"] p,
    [data-baseweb="tab"] span,
    [data-baseweb="tab"] div {
        color: #EAF8FF !important;
        font-weight: 750 !important;
        font-size: 16px !important;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(0,174,239,0.20) !important;
        border-color: rgba(0,194,255,0.35) !important;
        box-shadow: none !important;
    }

    [data-baseweb="tab"][aria-selected="true"] p,
    [data-baseweb="tab"][aria-selected="true"] span,
    [data-baseweb="tab"][aria-selected="true"] div {
        color: #FFFFFF !important;
    }

    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.035) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 16px !important;
        color: #F7FBFF !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] summary:hover {
        background: rgba(0,174,239,0.08) !important;
    }

    [data-testid="stPlotlyChart"] {
        background: rgba(255,255,255,0.025) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        padding: 6px !important;
    }

    @media (max-width: 1100px) {
        .scenario-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Helpers
# ============================================================

def render_sidebar_section(title: str, desc: str) -> None:
    st.sidebar.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <div class="section-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fmt(value: float, digits: int = 0) -> str:
    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return str(value)


def money(value: float, digits: int = 0) -> str:
    return f"{T['currency']}{fmt(value, digits)}"


def pct(value: float, digits: int = 2) -> str:
    return f"{fmt(value, digits)} {T['percent']}"


def localize_bool_columns(df: pd.DataFrame, text: dict) -> pd.DataFrame:
    result = df.copy()
    bool_cols = [
        "is_low_util",
        "is_zombie",
        "is_business_protected",
        "is_migratable",
        "selected_for_shutdown_assessment",
    ]
    for col in bool_cols:
        if col in result.columns:
            result[col] = result[col].map({True: text["yes"], False: text["no"]}).fillna(result[col])
    return result


def rename_columns_for_display(df: pd.DataFrame, text: dict, columns: list[str]) -> pd.DataFrame:
    rename_map = {
        "asset_id": text["asset_id"],
        "asset_type": text["asset_type"],
        "group": text["group"],
        "avg_utilization": text["avg_utilization"],
        "max_utilization": text["max_utilization"],
        "p95_utilization": text["p95_utilization"],
        "high_load_duty": text["high_load_duty"],
        "avg_memory_utilization": text["avg_memory_utilization"],
        "avg_disk_io": text["avg_disk_io"],
        "avg_network_io": text["avg_network_io"],
        "avg_power_kw": text["avg_power_kw"],
        "energy_kwh": text["energy_kwh"],
        "cost": text["cost"],
        "waste_energy_kwh": text["waste_energy_kwh"],
        "waste_cost": text["waste_cost"],
        "is_low_util": text["is_low_util"],
        "is_zombie": text["is_zombie"],
        "is_business_protected": text["is_business_protected"],
        "is_migratable": text["is_migratable"],
        "risk_score": text["risk_score"],
        "priority_level": text["priority_level"],
        "action_category": text["action_category"],
        "selected_for_shutdown_assessment": text["selected_for_shutdown_assessment"],
        "asset_count": text["total_assets"],
        "candidate_assets": text["candidate_assets"],
        "estimated_shutdown": text["estimated_shutdown"],
        "post_avg_utilization": text["post_avg_utilization"],
        "saving_energy_kwh": text["saving_energy_kwh"],
        "saving_cost": text["saving_cost"],
        "cooling_saving_kwh": text["cooling_saving_kwh"],
        "cooling_saving_cost": text["cooling_saving_cost"],
        "migration_cost": text["migration_cost"],
        "restart_risk_cost": text["restart_risk_cost"],
        "baseline_cost": text["baseline_cost"],
        "post_consolidation_cost": text["post_consolidation_cost"],
        "cost_saving_ratio": text["cost_saving_ratio"],
        "annual_operating_saving": text["annual_operating_saving"],
        "one_time_consolidation_cost": text["one_time_consolidation_cost"],
        "first_year_net_benefit": text["first_year_net_benefit"],
        "low_util_ratio": text["low_util_assets"],
        "zombie_ratio": text["zombie_assets"],
        "total_energy_kwh": text["total_energy"],
        "total_cost": text["cost"],
    }

    valid_cols = [col for col in columns if col in df.columns]
    return df[valid_cols].rename(columns={col: rename_map.get(col, col) for col in valid_cols})


def mode_key_from_label(mode_label: str) -> str:
    if mode_label == T["mode_basic"]:
        return "basic"
    if mode_label == T["mode_standard"]:
        return "standard"
    return "enhanced"


def mode_notice(mode: str) -> str:
    if mode == "basic":
        return T["basic_notice"]
    if mode == "standard":
        return T["standard_notice"]
    return T["enhanced_notice"]


# ============================================================
# Sidebar header
# ============================================================

top_left, top_right = st.sidebar.columns([4, 1])
with top_left:
    st.markdown(
        f"""
        <div class="sidebar-title">{T['sidebar_title']}</div>
        <div class="sidebar-subtitle">{T['sidebar_desc']}</div>
        """,
        unsafe_allow_html=True,
    )
with top_right:
    st.button(T["language_toggle"], on_click=toggle_language, use_container_width=True)


# ============================================================
# Sidebar - Data input
# ============================================================

render_sidebar_section(T["section_data"], T["section_data_desc"])

load_col1, load_col2 = st.sidebar.columns([3, 2])
with load_col1:
    uploaded_file = st.file_uploader(
        T["uploaded_file_label"],
        type=["csv"],
        help=T["uploaded_file_help"],
        key="uploaded_file",
    )
with load_col2:
    st.download_button(
        label=T["download_template"],
        data=read_sample_csv_bytes(),
        file_name=T["template_filename"],
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Sidebar - Mode
# ============================================================

render_sidebar_section(T["section_model"], T["section_model_desc"])

mode_label = st.sidebar.selectbox(
    T["analysis_mode"],
    [
        T["mode_basic"],
        T["mode_standard"],
        T["mode_enhanced"],
    ],
    key="analysis_mode_select",
)

mode = mode_key_from_label(mode_label)

if mode == "basic":
    st.sidebar.info(T["mode_basic_help"])
elif mode == "standard":
    st.sidebar.info(T["mode_standard_help"])
else:
    st.sidebar.info(T["mode_enhanced_help"])


# ============================================================
# Sidebar - Thresholds
# ============================================================

render_sidebar_section(T["section_threshold"], T["section_threshold_desc"])

low_util_threshold = st.sidebar.slider(
    T["low_util_threshold"],
    min_value=1,
    max_value=50,
    value=10,
    step=1,
    key="low_util_threshold",
)

high_util_threshold = st.sidebar.slider(
    T["high_util_threshold"],
    min_value=10,
    max_value=90,
    value=40,
    step=5,
    key="high_util_threshold",
)

high_duty_threshold = st.sidebar.slider(
    T["high_duty_threshold"],
    min_value=1,
    max_value=50,
    value=5,
    step=1,
    key="high_duty_threshold",
)


# ============================================================
# Sidebar - Power and tariff
# ============================================================

render_sidebar_section(T["section_power"], T["section_power_desc"])

default_idle_power = st.sidebar.number_input(
    T["idle_power"],
    min_value=1.0,
    value=220.0,
    step=10.0,
    key="default_idle_power",
)

default_peak_power = st.sidebar.number_input(
    T["peak_power"],
    min_value=1.0,
    value=520.0,
    step=10.0,
    key="default_peak_power",
)

electricity_price = st.sidebar.number_input(
    T["electricity_price"],
    min_value=0.0,
    value=0.85,
    step=0.05,
    key="electricity_price",
)


# ============================================================
# Sidebar - Consolidation
# ============================================================

# Basic Mode keeps advanced assumptions hidden and uses conservative defaults.
consolidation_ratio = 70
safe_util_limit = 70
cooling_factor = 0.30
migration_cost_multiplier = 1.0
risk_cost_multiplier = 1.0

if mode in ["standard", "enhanced"]:
    render_sidebar_section(T["section_consolidation"], T["section_consolidation_desc"])

    consolidation_ratio = st.sidebar.slider(
        T["consolidation_ratio"],
        min_value=0,
        max_value=100,
        value=70,
        step=5,
        key="consolidation_ratio",
    )

    safe_util_limit = st.sidebar.slider(
        T["safe_util_limit"],
        min_value=30,
        max_value=95,
        value=70,
        step=5,
        key="safe_util_limit",
    )

    cooling_factor = st.sidebar.slider(
        T["cooling_factor"],
        min_value=0.0,
        max_value=1.0,
        value=0.30,
        step=0.05,
        key="cooling_factor",
    )


# ============================================================
# Sidebar - Advanced
# ============================================================

if mode == "enhanced":
    render_sidebar_section(T["section_advanced"], T["section_advanced_desc"])

    with st.sidebar.expander(T["section_advanced"], expanded=False):
        migration_cost_multiplier = st.number_input(
            T["migration_cost_multiplier"],
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
            key="migration_cost_multiplier",
        )

        risk_cost_multiplier = st.number_input(
            T["risk_cost_multiplier"],
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
            key="risk_cost_multiplier",
        )


# ============================================================
# Sidebar - Run button
# ============================================================

st.sidebar.markdown("")
st.sidebar.markdown(
    f"""
    <div class="small-note">{T['run_hint']}</div>
    """,
    unsafe_allow_html=True,
)

run_button = st.sidebar.button(
    T["run_button_new"],
    type="primary",
    use_container_width=True,
    key="run_button",
)


# ============================================================
# Hero area
# ============================================================

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">{T['app_name']}</div>
        <div class="hero-subtitle">{T['page_subtitle']}</div>
        <div class="chip-row">
            {''.join([
                f"<span class='chip'>{chip}</span>"
                for chip in [
                    T["chip_utilization"],
                    T["chip_zombie"],
                    T["chip_consolidation"],
                    T["chip_energy_saving"],
                ]
            ])}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Scenario summary before execution
# ============================================================

scenario_data = T["value_uploaded"] if uploaded_file is not None else T["value_not_uploaded"]

st.markdown(
    f"""
    <div class="scenario-bar">
        <div class="section-title" style="margin-bottom:10px;">{T['scenario_summary']}</div>
        <div class="scenario-grid">
            <div class="scenario-item">
                <div class="scenario-label">{T['label_mode']}</div>
                <div class="scenario-value">{mode_label}</div>
            </div>
            <div class="scenario-item">
                <div class="scenario-label">{T['label_data_status']}</div>
                <div class="scenario-value">{scenario_data}</div>
            </div>
            <div class="scenario-item">
                <div class="scenario-label">{T['label_price']}</div>
                <div class="scenario-value">{electricity_price:,.2f}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Empty state
# ============================================================

if not run_button:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-title">{T['empty_title']}</div>
            <div class="empty-body">{T['empty_body']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# Main execution
# ============================================================

try:
    if uploaded_file is None:
        st.warning(T["no_data"])
        st.stop()

    raw_df = read_uploaded_file(uploaded_file)

    clean_df = clean_utilization_data(
        raw_df,
        default_idle_power=default_idle_power,
        default_peak_power=default_peak_power,
    )

    clean_df["migration_cost"] = clean_df["migration_cost"] * migration_cost_multiplier
    clean_df["restart_risk_cost"] = clean_df["restart_risk_cost"] * risk_cost_multiplier

    time_step_hours = estimate_time_step_hours(clean_df)
    period_days = get_analysis_period_days(clean_df)
    annualization_factor = 365 / max(period_days, 1 / 24)

    power_ts = apply_power_model(
        clean_df,
        time_step_hours=time_step_hours,
    )

    hourly_power = calculate_energy_by_time(
        power_ts,
        electricity_price=electricity_price,
    )

    asset_metrics = calculate_asset_metrics(
        clean_df,
        high_util_threshold=high_util_threshold,
        low_util_threshold=low_util_threshold,
        high_duty_threshold=high_duty_threshold,
    )

    asset_metrics = attach_energy_cost_to_asset_metrics(
        asset_metrics=asset_metrics,
        power_timeseries=power_ts,
        electricity_price=electricity_price,
    )

    if mode == "enhanced":
        asset_metrics = calculate_risk_score(
            asset_metrics=asset_metrics,
            low_util_threshold=low_util_threshold,
            high_duty_threshold=high_duty_threshold,
        )
    else:
        asset_metrics["risk_score"] = 0.0
        asset_metrics["priority_level"] = "-"
        asset_metrics["action_category"] = asset_metrics["is_zombie"].map(
            {
                True: "Migration / Consolidation Candidate",
                False: "Normal Operation",
            }
        )

    asset_metrics, group_consolidation, consolidation_summary = calculate_consolidation(
        asset_metrics=asset_metrics,
        consolidation_ratio=consolidation_ratio,
        safe_util_limit=safe_util_limit,
        electricity_price=electricity_price,
        cooling_factor=cooling_factor,
        annualization_factor=annualization_factor,
    )

    group_metrics = calculate_group_metrics(asset_metrics)
    type_metrics = calculate_type_metrics(asset_metrics)

    summary = calculate_summary(
        asset_metrics=asset_metrics,
        group_metrics=group_metrics,
        consolidation_summary=consolidation_summary,
        period_days=period_days,
    )

    priority_assets = build_priority_asset_list(asset_metrics, limit=20)
    action_counts = build_management_action_counts(asset_metrics)

    thresholds = {
        "low_util_threshold": low_util_threshold,
        "high_util_threshold": high_util_threshold,
        "high_duty_threshold": high_duty_threshold,
        "safe_util_limit": safe_util_limit,
    }

    report = build_utilization_report(
        summary=summary,
        thresholds=thresholds,
        mode=mode,
        lang=language,
        currency=T["currency"],
        action_counts=action_counts,
    )

    st.success(T["analysis_done"])

except Exception as e:
    st.error(f"{T['simulation_failed']}: {e}")
    st.stop()


# ============================================================
# Results overview
# ============================================================

st.markdown(
    f"""
    <div class="summary-card">
        <div class="summary-title">{T['results_title']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Key metrics
# ============================================================

st.markdown(f"<div class='panel-title'>{T['key_metrics']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='panel-subtitle'>{T['kpi_desc']}</div>", unsafe_allow_html=True)

if mode == "basic":
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(T["total_assets"], f"{summary['total_assets']} {T['assets_unit']}")
    kpi2.metric(T["low_util_assets"], f"{summary['low_util_assets']} {T['assets_unit']}")
    kpi3.metric(T["zombie_assets"], f"{summary['zombie_assets']} {T['assets_unit']}")

    kpi4, kpi5, kpi6 = st.columns(3)
    kpi4.metric(T["total_energy"], f"{fmt(summary['total_energy_kwh'], 0)} {T['kwh']}")
    kpi5.metric(T["waste_energy"], f"{fmt(summary['waste_energy_kwh'], 0)} {T['kwh']}")
    kpi6.metric(T["candidate_assets"], f"{summary['candidate_assets']} {T['assets_unit']}")
else:
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(T["total_assets"], f"{summary['total_assets']} {T['assets_unit']}")
    kpi2.metric(T["low_util_assets"], f"{summary['low_util_assets']} {T['assets_unit']}")
    kpi3.metric(T["zombie_assets"], f"{summary['zombie_assets']} {T['assets_unit']}")

    kpi4, kpi5, kpi6 = st.columns(3)
    kpi4.metric(T["candidate_assets"], f"{summary['candidate_assets']} {T['assets_unit']}")
    kpi5.metric(T["shutdown_assets"], f"{summary['estimated_shutdown_assets']} {T['assets_unit']}")
    kpi6.metric(T["one_time_consolidation_cost"], money(summary["one_time_consolidation_cost"]))

    kpi7, kpi8, kpi9 = st.columns(3)
    kpi7.metric(T["cost_saving_ratio"], pct(summary["cost_saving_ratio"]))
    kpi8.metric(T["annual_operating_saving"], money(summary["annual_operating_saving"]))
    kpi9.metric(T["first_year_net_benefit"], money(summary["first_year_net_benefit"]))


# ============================================================
# Charts
# ============================================================

st.markdown(f"<div class='panel-title'>{T['charts_title']}</div>", unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.plotly_chart(
        create_asset_status_pie(asset_metrics, T),
        use_container_width=True,
    )

with chart_col2:
    st.plotly_chart(
        create_hourly_power_chart(hourly_power, T),
        use_container_width=True,
    )

if mode in ["standard", "enhanced"]:
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.plotly_chart(
            create_cost_saving_pie(summary, T),
            use_container_width=True,
        )

    with chart_col4:
        st.plotly_chart(
            create_annual_economics_bar(summary, T),
            use_container_width=True,
        )


# ============================================================
# Model notice
# ============================================================

with st.expander(T["model_notice_title"], expanded=False):
    st.write(mode_notice(mode))


# ============================================================
# Report
# ============================================================

st.markdown(f"<div class='panel-title'>{T['report_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='panel-subtitle'>{T['report_desc']}</div>", unsafe_allow_html=True)

report_sections = report.get("sections", [])

if report_sections:
    report_tabs = st.tabs([section.get("tab", T["summary_tab"]) for section in report_sections])

    for report_tab, section in zip(report_tabs, report_sections):
        with report_tab:
            if section.get("title"):
                st.subheader(section["title"])

            if section.get("body"):
                st.write(section["body"])

            if section.get("warning"):
                st.warning(section["warning"])

            for item in section.get("items", []):
                st.write(f"- {item}")
else:
    st.info(T["report_empty"])


# ============================================================
# Detailed tables
# ============================================================

with st.expander(T["detailed_tables"], expanded=False):
    st.caption(T["detailed_tables_hint"])

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            T["priority_table_title"],
            T["table_title"],
            T["group_table_title"],
            T["type_table_title"],
        ]
    )

    with tab1:
        priority_cols = [
            "asset_id",
            "asset_type",
            "group",
            "avg_utilization",
            "high_load_duty",
            "avg_memory_utilization",
            "avg_disk_io",
            "avg_network_io",
            "waste_cost",
            "risk_score",
            "priority_level",
            "action_category",
            "selected_for_shutdown_assessment",
        ]

        priority_table = localize_bool_columns(priority_assets, T)
        priority_table = rename_columns_for_display(priority_table, T, priority_cols)

        st.dataframe(priority_table, use_container_width=True, height=360)

    with tab2:
        asset_display_cols = [
            "asset_id",
            "asset_type",
            "group",
            "avg_utilization",
            "max_utilization",
            "p95_utilization",
            "high_load_duty",
            "avg_memory_utilization",
            "avg_disk_io",
            "avg_network_io",
            "avg_power_kw",
            "energy_kwh",
            "waste_cost",
            "is_low_util",
            "is_zombie",
            "is_business_protected",
            "is_migratable",
            "risk_score",
            "priority_level",
            "action_category",
            "selected_for_shutdown_assessment",
        ]

        asset_table = localize_bool_columns(asset_metrics, T)
        asset_table = rename_columns_for_display(asset_table, T, asset_display_cols)

        st.dataframe(asset_table, use_container_width=True, height=420)

    with tab3:
        group_cols = [
            "group",
            "asset_count",
            "zombie_assets",
            "protected_assets",
            "candidate_assets",
            "estimated_shutdown",
            "avg_utilization",
            "post_avg_utilization",
            "saving_energy_kwh",
            "baseline_cost",
            "cost_saving_ratio",
            "annual_operating_saving",
            "one_time_consolidation_cost",
            "first_year_net_benefit",
        ]

        group_table = rename_columns_for_display(group_consolidation, T, group_cols)
        st.dataframe(group_table, use_container_width=True, height=360)

    with tab4:
        type_cols = [
            "asset_type",
            "asset_count",
            "avg_utilization",
            "p95_utilization",
            "low_util_assets",
            "zombie_assets",
            "total_energy_kwh",
            "total_cost",
            "waste_energy_kwh",
            "waste_cost",
        ]

        type_table = rename_columns_for_display(type_metrics, T, type_cols)
        st.dataframe(type_table, use_container_width=True, height=360)