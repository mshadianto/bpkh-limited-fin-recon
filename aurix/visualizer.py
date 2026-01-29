"""Visualization module for AURIX Reconciliation dashboards."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any


class ReconciliationVisualizer:
    """Creates interactive Plotly charts with Apple-inspired styling."""

    COLORS = {
        "primary": "#1D1D1F",
        "secondary": "#0071E3",
        "success": "#34C759",
        "success_light": "#30D158",
        "warning": "#FF9500",
        "danger": "#FF3B30",
        "info": "#5AC8FA",
        "teal": "#64D2FF",
        "purple": "#BF5AF2",
        "light": "#F5F5F7",
        "muted": "#86868B",
        "dark": "#1D1D1F",
    }

    LAYOUT_DEFAULTS = dict(
        font=dict(family="Inter, SF Pro Display, -apple-system, sans-serif"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=60, b=80, l=60, r=40),
    )

    @classmethod
    def _base_layout(cls, **kwargs):
        """Merge default layout with overrides."""
        layout = dict(cls.LAYOUT_DEFAULTS)
        layout.update(kwargs)
        return layout

    @classmethod
    def create_status_donut(cls, summary: Dict[str, Any]) -> go.Figure:
        """Create donut chart for reconciliation status distribution."""
        labels = ['Matched', 'Tolerance', 'Variance', 'Only Manual', 'Only Daftra']
        values = [
            summary['matched_count'],
            summary['tolerance_count'],
            summary['variance_count'],
            summary['unmatched_manual'],
            summary['unmatched_daftra']
        ]
        colors = [cls.COLORS['success'], cls.COLORS['success_light'],
                  cls.COLORS['warning'], cls.COLORS['danger'], cls.COLORS['info']]

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.65,
            marker_colors=colors, textinfo='percent+value',
            textposition='outside',
            textfont=dict(size=11, color=cls.COLORS['dark']),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
            pull=[0.02] * 5,
        )])

        fig.update_layout(**cls._base_layout(
            title=dict(text="Status Distribution",
                       font=dict(size=15, color=cls.COLORS['dark'], family="Inter"), x=0.5),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5,
                        font=dict(size=11)),
            height=400,
            annotations=[dict(
                text=f"<b>{summary['total_coa_accounts']}</b><br><span style='font-size:11px;color:#86868B'>Total</span>",
                x=0.5, y=0.5, font_size=18, showarrow=False,
                font=dict(color=cls.COLORS['dark'])
            )]
        ))
        return fig

    @classmethod
    def create_variance_waterfall(cls, coa_recon: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """Create waterfall chart for top variances."""
        top_variances = coa_recon[coa_recon['Net_Variance'] != 0].head(top_n)

        if len(top_variances) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No variances found", x=0.5, y=0.5,
                               font_size=14, showarrow=False,
                               font=dict(color=cls.COLORS['muted']))
            fig.update_layout(**cls._base_layout(height=400))
            return fig

        fig = go.Figure(go.Waterfall(
            name="Variance", orientation="v",
            measure=["relative"] * len(top_variances),
            x=[f"COA {int(x)}" for x in top_variances['COA']],
            y=top_variances['Net_Variance'].tolist(),
            textposition="outside",
            text=[f"{x:,.0f}" for x in top_variances['Net_Variance']],
            textfont=dict(size=10),
            connector={"line": {"color": "#E8E8ED", "width": 1}},
            increasing={"marker": {"color": cls.COLORS['success']}},
            decreasing={"marker": {"color": cls.COLORS['danger']}}
        ))

        fig.update_layout(**cls._base_layout(
            title=dict(text=f"Top {top_n} Net Variances (SAR)",
                       font=dict(size=15, color=cls.COLORS['dark']), x=0.5),
            showlegend=False, height=400,
            xaxis_title="COA Code", yaxis_title="Variance (SAR)",
            xaxis=dict(tickfont=dict(size=10)),
            margin=dict(t=60, b=80, l=80, r=40)
        ))
        return fig

    @classmethod
    def create_comparison_bar(cls, summary: Dict[str, Any]) -> go.Figure:
        """Create grouped bar chart comparing Manual vs Daftra totals."""
        categories = ['Total Debit', 'Total Credit']
        manual_values = [summary['total_manual_debit'], summary['total_manual_credit']]
        daftra_values = [summary['total_daftra_debit'], summary['total_daftra_credit']]

        fig = go.Figure(data=[
            go.Bar(name='Manual Journal', x=categories, y=manual_values,
                   marker_color=cls.COLORS['primary'],
                   marker_line=dict(width=0),
                   text=[f"SAR {x:,.0f}" for x in manual_values], textposition='outside',
                   textfont=dict(size=10)),
            go.Bar(name='Daftra Export', x=categories, y=daftra_values,
                   marker_color=cls.COLORS['secondary'],
                   marker_line=dict(width=0),
                   text=[f"SAR {x:,.0f}" for x in daftra_values], textposition='outside',
                   textfont=dict(size=10))
        ])

        fig.update_layout(**cls._base_layout(
            title=dict(text="Manual vs Daftra Comparison",
                       font=dict(size=15, color=cls.COLORS['dark']), x=0.5),
            barmode='group', height=400,
            xaxis_title="", yaxis_title="Amount (SAR)",
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5,
                        font=dict(size=11)),
            bargap=0.3, bargroupgap=0.1,
            margin=dict(t=60, b=80, l=80, r=40)
        ))
        return fig

    @classmethod
    def create_variance_heatmap(cls, coa_recon: pd.DataFrame) -> go.Figure:
        """Create bar chart showing variance distribution by amount range."""
        bins = [-np.inf, -100000, -10000, -1000, -100, 0, 100, 1000, 10000, 100000, np.inf]
        labels = ['<-100K', '-100K~-10K', '-10K~-1K', '-1K~-100',
                  '-100~0', '0~100', '100~1K', '1K~10K', '10K~100K', '>100K']

        coa_recon = coa_recon.copy()
        coa_recon['Variance_Bin'] = pd.cut(coa_recon['Net_Variance'], bins=bins, labels=labels)
        bin_counts = coa_recon['Variance_Bin'].value_counts().reindex(labels).fillna(0)

        bar_colors = [cls.COLORS['danger']] * 5 + [cls.COLORS['success']] * 5

        fig = go.Figure(data=go.Bar(
            x=labels, y=bin_counts.values,
            marker_color=bar_colors,
            marker_line=dict(width=0),
            text=bin_counts.values.astype(int), textposition='outside',
            textfont=dict(size=10)
        ))

        fig.update_layout(**cls._base_layout(
            title=dict(text="Variance Distribution (SAR)",
                       font=dict(size=15, color=cls.COLORS['dark']), x=0.5),
            xaxis_title="", yaxis_title="COA Accounts",
            height=400, xaxis_tickangle=-45,
            xaxis=dict(tickfont=dict(size=9)),
            margin=dict(t=60, b=100, l=60, r=40)
        ))
        return fig
