---
name: data-analysis
description: Data analysis with Pandas and Plotly. Use when the agent needs to read CSV/Excel files, compute statistics, or generate charts.
metadata:
  author: agent-builder
  version: "1.0.0"
  requires:
    - pandas>=2.2.0
    - plotly>=5.24.0
---

# Data Analysis Skill

Gives agents the ability to load data files, compute statistics, and generate interactive Plotly charts.

## Tools

- **analyze_csv(path)** — Load a CSV, return shape, columns, dtypes, and summary statistics
- **create_chart(path, spec)** — Generate a Plotly chart from data based on a natural language spec

## Configuration

```toml
[skills.data-analysis]
workspace = "./workspace"
```
