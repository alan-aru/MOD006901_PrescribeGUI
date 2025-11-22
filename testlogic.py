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


def test_categorical_summary():
    df = sample_df()
    numeric = detect_numeric_columns(df)
    result = categorical_summary(df, numeric, exclude_cols=[])
    assert "REGION" in result
    assert result["REGION"]["X"] == 2
