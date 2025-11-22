# logic.py
import pandas as pd


def load_csv_file(path: str) -> pd.DataFrame:
    """
    Load a CSV file and return a DataFrame.
    A thin wrapper so it can be tested independently.
    """
    return pd.read_csv(path)


def detect_numeric_columns(df: pd.DataFrame):
    """
    Identify numeric columns, excluding SNOMED_CODE.
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if "SNOMED_CODE" in numeric_cols:
        numeric_cols.remove("SNOMED_CODE")
    return numeric_cols


def detect_categorical_columns(df: pd.DataFrame, numeric_cols):
    """
    Everything not numeric is considered categorical.
    """
    return [c for c in df.columns if c not in numeric_cols]


def apply_filters(df: pd.DataFrame, filter_values: dict) -> pd.DataFrame:
    """
    Generic filter routine.
    filter_values = { column_name: selected_value_or_"All" }
    """
    filtered = df.copy()
    for col, selected in filter_values.items():
        if selected and selected != "All":
            filtered = filtered[filtered[col] == selected]
    return filtered


def aggregate_for_plot(df: pd.DataFrame, x_col: str, y_col: str, method: str):
    """
    Group and aggregate data for plotting:
    method ∈ {"Sum", "Average", "Count"}
    """
    grouped = df.groupby(x_col)[y_col]

    if method == "Sum":
        result = grouped.sum()
    elif method == "Average":
        result = grouped.mean()
    elif method == "Count":
        result = grouped.count()
    else:
        result = grouped.sum()

    # GUI keeps top 15 sorted descending
    return result.sort_values(ascending=False).head(15)


def numeric_summary(df, numeric_cols, agg_method=None, group_col=None):
    """
    Returns a numeric summary of the dataframe.
    
    If agg_method and group_col are provided, it aggregates numeric columns by the group.
    
    Parameters:
        df (DataFrame): Filtered dataframe
        numeric_cols (list): List of numeric column names
        agg_method (str, optional): "Sum", "Average", or "Count"
        group_col (str, optional): Column to group by if aggregation is needed
        
    Returns:
        DataFrame: Summary table
    """
    if agg_method and group_col:
        grouped = df.groupby(group_col)[numeric_cols]
        if agg_method == "Sum":
            summary = grouped.sum()
        elif agg_method == "Average":
            summary = grouped.mean()
        elif agg_method == "Count":
            summary = grouped.count()
        else:
            summary = grouped.sum()  # default to sum
        return summary.round(2)
    else:
        # Normal descriptive stats
        return df[numeric_cols].describe().round(2)



def categorical_summary(df: pd.DataFrame, numeric_cols, exclude_cols):
    """
    Returns a dict: { column_name: value_counts_series }
    excluding fields in exclude_cols.
    """
    categorical_cols = [
        c for c in df.columns
        if c not in numeric_cols and c not in exclude_cols
    ]

    summaries = {}
    for col in categorical_cols:
        summaries[col] = df[col].value_counts().head(20)

    return summaries
