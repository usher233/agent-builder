---
name: financial-data
description: Financial market data via AKShare. Use when the agent needs stock prices, financial statements, options chains, or ETF holdings. Focused on China A-shares.
metadata:
  author: agent-builder
  version: "1.0.0"
  requires:
    - akshare>=1.14.0
---

# Financial Data Skill

Gives agents access to China A-share market data through AKShare. Covers real-time quotes, financial statements, options chains, and ETF data.

## Tools

- **get_spot(symbol)** — Real-time spot price and key metrics for an A-share stock
- **get_financials(symbol)** — Financial abstract: revenue, profit, margins, growth rates
- **get_option_chain(symbol)** — SSE option chain with strikes, expiries, bid/ask
- **get_etf_holdings(symbol)** — Top holdings of an ETF

## Configuration

```toml
[skills.financial-data]
default_market = "sh"    # sh (Shanghai) | sz (Shenzhen)
```

See `references/financial-tools.md` for the full AKShare function reference.
