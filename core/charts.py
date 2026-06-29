"""
charts.py
Plotly figures themed to the RegWatch palette. Returns figures; pages render them.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

INK = "#0A0E1A"
BONE = "#ECE7DA"
MUTED = "#8A93A8"
COPPER = "#4FB6A6"
AMBER = "#E0A93D"
LINE = "#232C46"

_FONT = dict(family="IBM Plex Mono, monospace", color=MUTED, size=11)


def _base_layout(height: int = 280) -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=_FONT,
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        showlegend=False,
    )


def horizontal_bar(df: pd.DataFrame, label_col: str, value_col: str, color: str = COPPER) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=df[value_col],
            y=df[label_col],
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=df[value_col],
            textposition="outside",
            textfont=dict(color=BONE, size=11),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    layout = _base_layout(height=max(220, 34 * len(df)))
    layout["xaxis"] = dict(showgrid=False, zeroline=False, showticklabels=False)
    layout["yaxis"] = dict(showgrid=False, zeroline=False, color=BONE)
    fig.update_layout(**layout)
    return fig


def donut(df: pd.DataFrame, label_col: str, value_col: str) -> go.Figure:
    palette = [COPPER, AMBER, "#6F8FD8", "#C77DCB", "#5FB87A", "#D85A5A", "#8A93A8"]
    fig = go.Figure(
        go.Pie(
            labels=df[label_col],
            values=df[value_col],
            hole=0.62,
            marker=dict(colors=palette, line=dict(color=INK, width=2)),
            textinfo="none",
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    layout = _base_layout(height=280)
    layout["showlegend"] = True
    layout["legend"] = dict(font=dict(color=BONE, size=10), orientation="v", x=1.0, y=0.5)
    fig.update_layout(**layout)
    return fig
