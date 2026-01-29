"""Tests for aurix.ai.forecasting — VarianceForecaster."""

import pandas as pd
import numpy as np
import pytest

from aurix.ai.forecasting import VarianceForecaster


@pytest.fixture
def forecaster():
    return VarianceForecaster()


# ---------------------------------------------------------------------------
# aggregate_monthly_variances
# ---------------------------------------------------------------------------

class TestAggregateMonthlyVariances:
    def test_returns_dataframe(self, forecaster, monthly_manual_df, monthly_daftra_df):
        result = forecaster.aggregate_monthly_variances(monthly_manual_df, monthly_daftra_df)
        assert isinstance(result, pd.DataFrame)

    def test_output_columns(self, forecaster, monthly_manual_df, monthly_daftra_df):
        result = forecaster.aggregate_monthly_variances(monthly_manual_df, monthly_daftra_df)
        expected = {"YearMonth", "total_abs_variance", "total_net_variance",
                    "variance_count", "matched_count", "total_coa", "match_rate"}
        assert expected.issubset(set(result.columns))

    def test_row_count_matches_months(self, forecaster, monthly_manual_df, monthly_daftra_df):
        result = forecaster.aggregate_monthly_variances(monthly_manual_df, monthly_daftra_df)
        # Fixture has 4 distinct months
        assert len(result) == 4

    def test_match_rate_range(self, forecaster, monthly_manual_df, monthly_daftra_df):
        result = forecaster.aggregate_monthly_variances(monthly_manual_df, monthly_daftra_df)
        assert (result["match_rate"] >= 0).all()
        assert (result["match_rate"] <= 100).all()


# ---------------------------------------------------------------------------
# forecast_linear
# ---------------------------------------------------------------------------

class TestForecastLinear:
    @pytest.fixture
    def monthly_df(self, forecaster, monthly_manual_df, monthly_daftra_df):
        return forecaster.aggregate_monthly_variances(monthly_manual_df, monthly_daftra_df)

    def test_returns_dict(self, forecaster, monthly_df):
        result = forecaster.forecast_linear(monthly_df)
        assert isinstance(result, dict)

    def test_expected_keys(self, forecaster, monthly_df):
        result = forecaster.forecast_linear(monthly_df)
        expected = {"historical", "forecast", "trend_direction", "slope", "r_squared"}
        assert expected == set(result.keys())

    def test_trend_direction_values(self, forecaster, monthly_df):
        result = forecaster.forecast_linear(monthly_df)
        assert result["trend_direction"] in {"stable", "increasing", "decreasing"}

    def test_forecast_count(self, forecaster, monthly_df):
        result = forecaster.forecast_linear(monthly_df, periods_ahead=3)
        assert len(result["forecast"]) == 3

    def test_forecasts_non_negative(self, forecaster, monthly_df):
        result = forecaster.forecast_linear(monthly_df)
        for f in result["forecast"]:
            assert f["value"] >= 0

    def test_historical_count(self, forecaster, monthly_df):
        result = forecaster.forecast_linear(monthly_df)
        assert len(result["historical"]) == len(monthly_df)

    def test_insufficient_data(self, forecaster):
        df = pd.DataFrame({
            "YearMonth": [pd.Period("2024-01", "M"), pd.Period("2024-02", "M")],
            "total_abs_variance": [100, 200],
        })
        result = forecaster.forecast_linear(df)
        assert "error" in result

    def test_r_squared_range(self, forecaster, monthly_df):
        result = forecaster.forecast_linear(monthly_df)
        assert 0 <= result["r_squared"] <= 1.0

    def test_increasing_data(self, forecaster):
        df = pd.DataFrame({
            "YearMonth": [pd.Period(f"2024-{m:02d}", "M") for m in range(1, 7)],
            "total_abs_variance": [100, 200, 300, 400, 500, 600],
        })
        result = forecaster.forecast_linear(df)
        assert result["trend_direction"] == "increasing"
