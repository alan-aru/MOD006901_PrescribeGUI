import pandas as pd
from logic import (
    detect_numeric_columns,
    detect_categorical_columns,
    apply_filters,
    aggregate_for_plot,
    numeric_summary,
    categorical_summary
)

def sample_df():
    return pd.DataFrame({
        "A": [1, 2, 3, 4],
        "B": [10, 20, 30, 40],
        "REGION": ["X", "X", "Y", "Y"],
        "SNOMED_CODE": [111, 222, 333, 444]  # should be excluded
    })


def test_detect_numeric_columns():
    df = sample_df()
    numeric = detect_numeric_columns(df)
    assert "A" in numeric
    assert "B" in numeric
    assert "SNOMED_CODE" not in numeric


def test_detect_categorical_columns():
    df = sample_df()
    numeric = detect_numeric_columns(df)
    cat = detect_categorical_columns(df, numeric)
    assert "REGION" in cat
    assert "A" not in cat


def test_apply_filters():
    df = sample_df()
    filtered = apply_filters(df, {"REGION": "X"})
    assert len(filtered) == 2
    assert all(filtered["REGION"] == "X")


def test_aggregate_for_plot_sum():
    df = sample_df()
    result = aggregate_for_plot(df, "REGION", "A", "Sum")
    assert result["X"] == 1 + 2
    assert result["Y"] == 3 + 4


def test_numeric_summary():
    df = sample_df()
    numeric = detect_numeric_columns(df)
    summary = numeric_summary(df, numeric)
    assert summary.loc["mean", "A"] == 2.5


def test_numeric_summary_with_aggregation():
    df = sample_df()
    numeric_cols = detect_numeric_columns(df)

    # Test Sum aggregation by REGION
    summary_sum = numeric_summary(df, numeric_cols, agg_method="Sum", group_col="REGION")
    assert summary_sum.loc["X", "A"] == 1 + 2  # X region total for column A
    assert summary_sum.loc["Y", "B"] == 30 + 40  # Y region total for column B

    # Test Average aggregation by REGION
    summary_avg = numeric_summary(df, numeric_cols, agg_method="Average", group_col="REGION")
    assert summary_avg.loc["X", "A"] == (1 + 2) / 2
    assert summary_avg.loc["Y", "B"] == (30 + 40) / 2

    # Test Count aggregation by REGION
    summary_count = numeric_summary(df, numeric_cols, agg_method="Count", group_col="REGION")
    assert summary_count.loc["X", "A"] == 2  # 2 rows in region X
    assert summary_count.loc["Y", "B"] == 2  # 2 rows in region Y


def test_categorical_summary():
    df = sample_df()
    numeric = detect_numeric_columns(df)
    result = categorical_summary(df, numeric, exclude_cols=[])
    assert "REGION" in result
    assert result["REGION"]["X"] == 2
