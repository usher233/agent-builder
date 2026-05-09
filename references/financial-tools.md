# Financial Analysis Tools

Pattern for integrating financial data into agents. Inspired by Anthropic's `claude-for-financial-services` repo — their skill-based approach maps well to LangChain tools.

## Tool Categories

### 1. Market Data (实时行情)
- Spot prices, OHLCV, option chains
- Real-time greeks, volume, open interest
- ETF holdings and composition

### 2. Financial Statements (财务报表)
- Income statements (利润表)
- Balance sheets (资产负债表)
- Cash flow statements (现金流量表)
- Provider: AKShare `stock_financial_abstract_ths`, `stock_balance_sheet_by_report_em`

### 3. Financial Ratios (财务指标)
- PE, PB, ROE, ROA
- Debt ratios, margins, growth rates
- Dividend yield and history
- Provider: AKShare `stock_financial_analysis_indicator`

### 4. Risk & P&L (风险分析)
- Option P&L calculator
- Strategy explainer with A-share specifics
- Position sizing guidance

## AKShare Function Reference

### Options Data
| Function | Description |
|----------|-------------|
| `option_sse_daily_sina(symbol)` | SSE option chain (daily) |
| `option_daily_sina(symbol)` | Option daily data |

### Stock Data
| Function | Description |
|----------|-------------|
| `stock_zh_a_spot_em()` | All A-share real-time spot |
| `stock_financial_abstract_ths(symbol)` | Financial abstract by report date |
| `stock_balance_sheet_by_report_em(symbol)` | Balance sheet |
| `stock_cash_flow_sheet_by_report_em(symbol)` | Cash flow statement |
| `stock_financial_analysis_indicator(symbol)` | Key financial ratios |
| `stock_history_dividend_detail(symbol)` | Dividend history |

### ETF Data
| Function | Description |
|----------|-------------|
| `fund_etf_hold_detail_sina(symbol)` | ETF top holdings |

## MCP Integration (Advanced)

For production use, wrap AKShare in a lightweight MCP server:

```python
# mcp_financial_server.py
from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent
import akshare as ak

app = Server("akshare-financial")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_option_chain", description="..."),
        Tool(name="get_financial_ratios", description="..."),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # route to AKShare functions
    ...
```

This follows the pattern from Anthropic's financial-services repo where MCP connectors centralize data access and are shared across agents.

## Connecting Fundamentals to Options

Key insights to surface when analyzing fundamentals for options decisions:

- **High dividend yield** → good for covered calls (extra income on top of divs)
- **Low debt, stable earnings** → good for cash-secured puts (lower assignment risk)
- **High growth, volatile** → protective puts or bull call spreads (limit downside)
- **Range-bound, low vol** → iron condor or covered strangle (collect premium)
- **Pre-earnings** → consider straddle/strangle if IV is low, or avoid if IV is already high

Always check the earnings calendar before selling premium — binary events can breach strikes quickly.
