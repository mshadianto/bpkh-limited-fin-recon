"""Visualization module for AURIX Reconciliation dashboards."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any


class ReconciliationVisualizer:
    """Creates interactive Plotly charts with BPKH branding."""

    COLORS = {
        "primary": "#1B5E20",
        "secondary": "#FFD700",
        "accent": "#0D47A1",
        "success": "#2E7D32",
        "warning": "#F57C00",
        "danger": "#C62828",
        "info": "#0288D1",
        "light": "#F5F5F5",
        "dark": "#212121"
    }

    @classmethod
    def create_status_donut(cls, summary: Dict[str, Any]) -> go.Figure:
        """Create donut chart for reconciliation status distribution."""
        labels = ['Matched', 'Within Tolerance', 'Variance', 'Only Manual', 'Only Daftra']
        values = [
            summary['matched_count'],
            summary['tolerance_count'],
            summary['variance_count'],
            summary['unmatched_manual'],
            summary['unmatched_daftra']
        ]
        colors = [cls.COLORS['success'], '#81C784', cls.COLORS['warning'],
                  cls.COLORS['danger'], cls.COLORS['info']]

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.6,
            marker_colors=colors, textinfo='percent+value',
            textposition='outside', textfont=dict(size=12),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )])

        fig.update_layout(
            title=dict(text="Reconciliation Status Distribution",
                       font=dict(size=16, color=cls.COLORS['dark']), x=0.5),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
            height=400, margin=dict(t=60, b=80, l=40, r=40),
            annotations=[dict(
                text=f"<b>{summary['total_coa_accounts']}</b><br>Total COA",
                x=0.5, y=0.5, font_size=14, showarrow=False
            )]
        )
        return fig

    @classmethod
    def create_variance_waterfall(cls, coa_recon: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """Create waterfall chart for top variances."""
        top_variances = coa_recon[coa_recon['Net_Variance'] != 0].head(top_n)

        if len(top_variances) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No variances found", x=0.5, y=0.5,
                               font_size=16, showarrow=False)
            return fig

        fig = go.Figure(go.Waterfall(
            name="Variance", orientation="v",
            measure=["relative"] * len(top_variances),
            x=[f"COA {int(x)}" for x in top_variances['COA']],
            y=top_variances['Net_Variance'].tolist(),
            textposition="outside",
            text=[f"{x:,.0f}" for x in top_variances['Net_Variance']],
            connector={"line": {"color": cls.COLORS['light']}},
            increasing={"marker": {"color": cls.COLORS['success']}},
            decreasing={"marker": {"color": cls.COLORS['danger']}}
        ))

        fig.update_layout(
            title=dict(text=f"Top {top_n} Net Variances by COA (SAR)",
                       font=dict(size=16, color=cls.COLORS['dark']), x=0.5),
            showlegend=False, height=400,
            xaxis_title="COA Code", yaxis_title="Variance Amount (SAR)",
            margin=dict(t=60, b=80, l=80, r=40)
        )
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
                   text=[f"SAR {x:,.0f}" for x in manual_values], textposition='outside'),
            go.Bar(name='Daftra Export', x=categories, y=daftra_values,
                   marker_color=cls.COLORS['accent'],
                   text=[f"SAR {x:,.0f}" for x in daftra_values], textposition='outside')
        ])

        fig.update_layout(
            title=dict(text="Manual Journal vs Daftra: Debit/Credit Comparison",
                       font=dict(size=16, color=cls.COLORS['dark']), x=0.5),
            barmode='group', height=400,
            xaxis_title="Category", yaxis_title="Amount (SAR)",
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
            margin=dict(t=60, b=80, l=80, r=40)
        )
        return fig

    @classmethod
    def create_variance_heatmap(cls, coa_recon: pd.DataFrame) -> go.Figure:
        """Create bar chart showing variance distribution by amount range."""
        bins = [-np.inf, -100000, -10000, -1000, -100, 0, 100, 1000, 10000, 100000, np.inf]
        labels = ['<-100K', '-100K to -10K', '-10K to -1K', '-1K to -100',
                  '-100 to 0', '0 to 100', '100 to 1K', '1K to 10K', '10K to 100K', '>100K']

        coa_recon = coa_recon.copy()
        coa_recon['Variance_Bin'] = pd.cut(coa_recon['Net_Variance'], bins=bins, labels=labels)
        bin_counts = coa_recon['Variance_Bin'].value_counts().reindex(labels).fillna(0)

        fig = go.Figure(data=go.Bar(
            x=labels, y=bin_counts.values,
            marker_color=[cls.COLORS['danger'] if i < 5 else cls.COLORS['success']
                          for i in range(10)],
            text=bin_counts.values.astype(int), textposition='outside'
        ))

        fig.update_layout(
            title=dict(text="Variance Distribution by Amount Range (SAR)",
                       font=dict(size=16, color=cls.COLORS['dark']), x=0.5),
            xaxis_title="Variance Range", yaxis_title="Number of COA Accounts",
            height=400, margin=dict(t=60, b=100, l=60, r=40), xaxis_tickangle=-45
        )
        return fig
