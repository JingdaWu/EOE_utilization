from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


PLOT_TEMPLATE = "plotly_dark"


def _transparent_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text=title, x=0.02, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.025)",
        font=dict(size=13),
        margin=dict(l=30, r=25, t=58, b=35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    return fig


def create_utilization_distribution(asset_df: pd.DataFrame, text: dict) -> go.Figure:
    fig = px.histogram(
        asset_df,
        x="avg_utilization",
        nbins=18,
        labels={
            "avg_utilization": text["x_util"],
            "count": text["y_count"],
        },
    )

    fig.update_traces(marker_line_width=0.4, opacity=0.85)
    fig.update_xaxes(title=text["x_util"])
    fig.update_yaxes(title=text["y_count"])

    return _transparent_layout(fig, text["chart_util_distribution"])


def create_energy_scatter(asset_df: pd.DataFrame, text: dict) -> go.Figure:
    color_col = "action_category" if "action_category" in asset_df.columns else "is_zombie"

    fig = px.scatter(
        asset_df,
        x="avg_utilization",
        y="energy_kwh",
        size="waste_cost",
        color=color_col,
        hover_data=[
            "asset_id",
            "asset_type",
            "group",
            "avg_utilization",
            "energy_kwh",
            "waste_cost",
        ],
        labels={
            "avg_utilization": text["x_util"],
            "energy_kwh": text["x_energy"],
            "waste_cost": text["waste_cost"],
            "asset_id": text["asset_id"],
            "asset_type": text["asset_type"],
            "group": text["group"],
        },
    )

    fig.update_traces(marker=dict(opacity=0.72, line=dict(width=0.3)))
    fig.update_xaxes(title=text["x_util"])
    fig.update_yaxes(title=text["x_energy"])

    return _transparent_layout(fig, text["chart_energy_scatter"])


def create_group_energy_chart(group_df: pd.DataFrame, text: dict) -> go.Figure:
    if group_df.empty:
        fig = go.Figure()
        return _transparent_layout(fig, text["chart_group_energy"])

    plot_df = group_df.sort_values("total_energy_kwh", ascending=False).head(12)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=plot_df["group"],
            y=plot_df["total_energy_kwh"],
            name=text["total_energy"],
        )
    )

    fig.add_trace(
        go.Bar(
            x=plot_df["group"],
            y=plot_df["waste_cost"],
            name=text["waste_cost"],
            yaxis="y2",
            opacity=0.65,
        )
    )

    fig.update_layout(
        yaxis=dict(title=text["y_energy"]),
        yaxis2=dict(
            title=text["y_cost"],
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        barmode="group",
    )

    fig.update_xaxes(title=text["x_group"])
    return _transparent_layout(fig, text["chart_group_energy"])


def create_zombie_top_chart(asset_df: pd.DataFrame, text: dict) -> go.Figure:
    if asset_df.empty:
        fig = go.Figure()
        return _transparent_layout(fig, text["chart_zombie_top"])

    if "selected_for_shutdown_assessment" in asset_df.columns:
        plot_df = asset_df[asset_df["selected_for_shutdown_assessment"]].copy()
        if plot_df.empty:
            plot_df = asset_df[asset_df["is_zombie"]].copy()
    else:
        plot_df = asset_df[asset_df["is_zombie"]].copy()

    if plot_df.empty:
        plot_df = asset_df.sort_values("waste_cost", ascending=False).head(10)
    else:
        plot_df = plot_df.sort_values("waste_cost", ascending=False).head(10)

    fig = px.bar(
        plot_df,
        x="asset_id",
        y="waste_cost",
        hover_data=[
            "asset_type",
            "group",
            "avg_utilization",
            "energy_kwh",
            "waste_cost",
        ],
        labels={
            "asset_id": text["x_asset"],
            "waste_cost": text["y_cost"],
        },
    )

    fig.update_xaxes(title=text["x_asset"])
    fig.update_yaxes(title=text["y_cost"])

    return _transparent_layout(fig, text["chart_zombie_top"])


def create_saving_waterfall(summary: dict, text: dict) -> go.Figure:
    labels = [
        text["saving_cost"],
        text["cooling_saving_cost"],
        text["migration_cost"],
        text["restart_risk_cost"],
        text["net_saving"],
    ]

    values = [
        summary.get("saving_cost", 0),
        summary.get("cooling_saving_cost", 0),
        -summary.get("migration_cost", 0),
        -summary.get("restart_risk_cost", 0),
        summary.get("net_saving_cost", 0),
    ]

    measures = ["relative", "relative", "relative", "relative", "total"]

    fig = go.Figure(
        go.Waterfall(
            x=labels,
            y=values,
            measure=measures,
            connector={"line": {"width": 1}},
        )
    )

    fig.update_yaxes(title=text["y_cost"])
    return _transparent_layout(fig, text["chart_saving_waterfall"])


def create_action_category_chart(action_df: pd.DataFrame, text: dict) -> go.Figure:
    if action_df.empty:
        fig = go.Figure()
        return _transparent_layout(fig, text["chart_action_category"])

    fig = px.bar(
        action_df,
        x="action_category",
        y="asset_count",
        hover_data=[
            "avg_risk_score",
            "total_waste_cost",
            "total_energy_kwh",
        ],
        labels={
            "action_category": text["action_category"],
            "asset_count": text["y_count"],
            "avg_risk_score": text["risk_score"],
            "total_waste_cost": text["waste_cost"],
            "total_energy_kwh": text["energy_kwh"],
        },
    )

    fig.update_xaxes(title="", tickangle=20)
    fig.update_yaxes(title=text["y_count"])

    return _transparent_layout(fig, text["chart_action_category"])


def create_hourly_power_chart(hourly_df: pd.DataFrame, text: dict) -> go.Figure:
    if hourly_df.empty:
        fig = go.Figure()
        return _transparent_layout(fig, text["chart_hourly_load"])

    fig = px.line(
        hourly_df,
        x="timestamp",
        y="total_power_kw",
        labels={
            "timestamp": text["x_time"],
            "total_power_kw": text["y_power"],
        },
    )

    fig.update_traces(line=dict(width=2.4))
    fig.update_xaxes(title=text["x_time"])
    fig.update_yaxes(title=text["y_power"])

    return _transparent_layout(fig, text["chart_hourly_load"])