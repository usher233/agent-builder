from langchain_core.tools import tool

_config = {
    "default_market": "sh",
}


def get_default_config():
    return dict(_config)


def configure(user_config: dict):
    _config.update({k: v for k, v in user_config.items() if k in _config})


@tool
def get_spot(symbol: str) -> str:
    """Get real-time spot data for an A-share stock. Symbol can be code (600000) or full (sh600000).

    Returns: name, price, change%, volume, PE, PB, market cap, turnover.
    """
    try:
        import akshare as ak

        df = ak.stock_zh_a_spot_em()
        # Match by code
        code = symbol.replace("sh", "").replace("sz", "")
        match = df[df["代码"] == code]
        if match.empty:
            match = df[df["名称"].str.contains(symbol)]

        if match.empty:
            return f"Symbol not found: {symbol}"

        row = match.iloc[0]
        lines = [
            f"名称: {row['名称']} ({row['代码']})",
            f"最新价: {row['最新价']}",
            f"涨跌幅: {row['涨跌幅']}%",
            f"成交量: {row['成交量']}",
            f"成交额: {row['成交额']}",
            f"市盈率: {row.get('市盈率-动态', 'N/A')}",
            f"市净率: {row.get('市净率', 'N/A')}",
            f"总市值: {row.get('总市值', 'N/A')}",
        ]
        return "\n".join(lines)
    except ImportError:
        return "Error: akshare not installed. Run: pip install akshare"
    except Exception as e:
        return f"Error fetching spot data: {e}"


@tool
def get_financials(symbol: str) -> str:
    """Get financial abstract for an A-share stock: revenue, net profit, margins, ROE, growth rates."""
    try:
        import akshare as ak

        df = ak.stock_financial_abstract_ths(symbol=symbol, indicator="按报告期")
        if df.empty:
            return f"No financial data found for: {symbol}"

        latest = df.iloc[0]
        lines = [f"财务摘要 - {symbol} (报告期: {latest.get('报告期', 'N/A')})"]
        for col in df.columns[:15]:
            lines.append(f"  {col}: {latest.get(col, 'N/A')}")

        return "\n".join(lines)
    except ImportError:
        return "Error: akshare not installed. Run: pip install akshare"
    except Exception as e:
        return f"Error fetching financials: {e}"


@tool
def get_option_chain(symbol: str) -> str:
    """Get the SSE option chain for an underlying symbol (e.g., 510050 for 50ETF options).

    Returns calls and puts with strike, expiry, bid, ask, volume, open interest.
    """
    try:
        import akshare as ak

        df = ak.option_sse_daily_sina(symbol=symbol)
        if df.empty:
            return f"No option data found for: {symbol}"

        lines = [f"期权链 - {symbol}"]
        cols = ["代码", "名称", "行权价", "到期日", "认购认沽", "最新价", "成交量", "持仓量"]
        available = [c for c in cols if c in df.columns]
        lines.append(df[available].head(30).to_string(index=False))
        lines.append(f"\n{len(df)} total contracts")

        return "\n".join(lines)
    except ImportError:
        return "Error: akshare not installed. Run: pip install akshare"
    except Exception as e:
        return f"Error fetching option chain: {e}"


@tool
def get_etf_holdings(symbol: str) -> str:
    """Get the top holdings of an ETF by symbol code."""
    try:
        import akshare as ak

        df = ak.fund_etf_hold_detail_sina(symbol=symbol)
        if df.empty:
            return f"No holding data found for: {symbol}"

        lines = [f"ETF持仓 - {symbol}"]
        lines.append(df.head(20).to_string(index=False))
        return "\n".join(lines)
    except ImportError:
        return "Error: akshare not installed. Run: pip install akshare"
    except Exception as e:
        return f"Error fetching ETF holdings: {e}"


def get_tools():
    return [get_spot, get_financials, get_option_chain, get_etf_holdings]
