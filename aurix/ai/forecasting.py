"""Variance forecasting module for AURIX Reconciliation."""

import pandas as pd
import numpy as np
from typing import Dict, Any


class VarianceForecaster:
    """Predicts future variance trends from historical monthly aggregations."""

    def aggregate_monthly_variances(
        self,
        df_manual: pd.DataFrame,
        df_daftra: pd.DataFrame,
        date_col_manual: str = "Tanggal",
        date_col_daftra: str = "Date"
    ) -> pd.DataFrame:
        """Aggregate variance metrics by month."""
        df_m = df_manual.copy()
        df_d = df_daftra.copy()
        df_m['_YearMonth'] = pd.to_datetime(df_m[date_col_manual]).dt.to_period('M')
        df_d['_YearMonth'] = pd.to_datetime(df_d[date_col_daftra]).dt.to_period('M')

        all_months = sorted(set(df_m['_YearMonth'].dropna()) | set(df_d['_YearMonth'].dropna()))

        records = []
        for ym in all_months:
            m_slice = df_m[df_m['_YearMonth'] == ym]
            d_slice = df_d[df_d['_YearMonth'] == ym]

            m_agg = m_slice.groupby('COA Daftra').agg({
                'Debit-SAR': 'sum', 'Kredit-SAR': 'sum', 'Nilai Mutasi': 'sum'
            }).reset_index()
            m_agg.columns = ['COA', 'M_Debit', 'M_Credit', 'M_Net']

            d_agg = d_slice.groupby('Account Code').agg({
                'Debit': 'sum', 'Credit': 'sum', 'Nilai Mutasi': 'sum'
            }).reset_index()
            d_agg.columns = ['COA', 'D_Debit', 'D_Credit', 'D_Net']

            merged = pd.merge(m_agg, d_agg, on='COA', how='outer').fillna(0)
            merged['Net_Variance'] = merged['M_Net'] - merged['D_Net']
            merged['Abs_Variance'] = merged['Net_Variance'].abs()

            total_coa = len(merged)
            matched = len(merged[merged['Abs_Variance'] <= 1.0])

            records.append({
                'YearMonth': ym,
                'total_abs_variance': merged['Abs_Variance'].sum(),
                'total_net_variance': merged['Net_Variance'].sum(),
                'variance_count': len(merged[merged['Abs_Variance'] > 1.0]),
                'matched_count': matched,
                'total_coa': total_coa,
                'match_rate': (matched / total_coa * 100) if total_coa > 0 else 0
            })

        return pd.DataFrame(records)

    def forecast_linear(
        self,
        monthly_df: pd.DataFrame,
        target_col: str = "total_abs_variance",
        periods_ahead: int = 3
    ) -> Dict[str, Any]:
        """Linear regression forecast on monthly variance data."""
        if len(monthly_df) < 3:
            return {"error": "Insufficient data (need at least 3 months)"}

        from sklearn.linear_model import LinearRegression

        y = monthly_df[target_col].values.astype(float)
        X = np.arange(len(y)).reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)
        slope = float(model.coef_[0])
        r_squared = float(model.score(X, y))

        future_X = np.arange(len(y), len(y) + periods_ahead).reshape(-1, 1)
        forecast_values = model.predict(future_X)

        if abs(slope) < (y.mean() * 0.01):
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        historical = []
        for _, row in monthly_df.iterrows():
            historical.append({
                "month": str(row['YearMonth']),
                "value": float(row[target_col])
            })

        last_period = monthly_df['YearMonth'].iloc[-1]
        forecast = []
        for j, val in enumerate(forecast_values):
            forecast_period = last_period + (j + 1)
            forecast.append({
                "month": str(forecast_period),
                "value": max(0, float(val)),
                "type": "forecast"
            })

        return {
            "historical": historical,
            "forecast": forecast,
            "trend_direction": trend,
            "slope": slope,
            "r_squared": r_squared
        }
