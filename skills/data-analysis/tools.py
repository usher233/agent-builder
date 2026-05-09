import json
from pathlib import Path
from langchain_core.tools import tool

WORKSPACE = Path("./workspace")


@tool
def analyze_csv(path: str) -> str:
    """Load a CSV file and return a statistical summary: shape, columns, dtypes, describe()."""
    import pandas as pd

    try:
        df = pd.read_csv(WORKSPACE / path)
        lines = [
            f"File: {path}",
            f"Shape: {df.shape[0]} rows x {df.shape[1]} cols",
            "",
            "Columns:",
        ]
        for col in df.columns:
            lines.append(f"  {col}: {df[col].dtype} ({df[col].isna().sum()} missing)")

        lines.append("")
        lines.append("Summary Statistics:")
        lines.append(df.describe(include="all").to_string())

        return "\n".join(lines)
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error analyzing CSV: {e}"


@tool
def create_chart(path: str, spec: str) -> str:
    """Create a Plotly chart from a data file. 'spec' describes the chart in natural language.

    Examples: 'line chart of revenue over time', 'bar chart of sales by region',
              'scatter plot of price vs volume', 'box plot of returns by sector'
    """
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    try:
        # Load data
        if path.endswith(".csv"):
            df = pd.read_csv(WORKSPACE / path)
        elif path.endswith((".xlsx", ".xls")):
            df = pd.read_excel(WORKSPACE / path)
        else:
            return f"Unsupported format: {path}"

        # Heuristic chart selection based on spec keywords
        spec_lower = spec.lower()
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]

        if not numeric_cols:
            return "No numeric columns found for charting."

        x = date_cols[0] if date_cols else (categorical_cols[0] if categorical_cols else df.columns[0])
        y = numeric_cols[0]
        color = categorical_cols[1] if len(categorical_cols) > 1 else None

        if "bar" in spec_lower:
            fig = px.bar(df, x=x, y=y, color=color, title=spec.title())
        elif "scatter" in spec_lower:
            fig = px.scatter(df, x=x, y=y, color=color, title=spec.title())
        elif "box" in spec_lower:
            fig = px.box(df, x=x, y=y, color=color, title=spec.title())
        elif "pie" in spec_lower:
            fig = px.pie(df, names=categorical_cols[0] if categorical_cols else df.columns[0],
                         values=y, title=spec.title())
        elif "histogram" in spec_lower or "dist" in spec_lower:
            fig = px.histogram(df, x=y, color=color, title=spec.title())
        else:  # default to line
            fig = px.line(df, x=x, y=y, color=color, title=spec.title())

        chart_json = fig.to_json()
        chart_path = WORKSPACE / f"chart_{hash(spec) & 0xFFFF}.json"
        chart_path.parent.mkdir(parents=True, exist_ok=True)
        chart_path.write_text(chart_json)

        return f"Chart created: {chart_path}\nChart type: {fig.__class__.__name__}\nX: {x}, Y: {y}\nData: {len(df)} points"
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error creating chart: {e}"


def get_tools():
    return [analyze_csv, create_chart]
