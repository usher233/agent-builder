import httpx
from langchain_core.tools import tool

_config = {
    "tavily_api_key": "",
    "max_results": 5,
}


def get_default_config():
    return dict(_config)


def configure(user_config: dict):
    _config.update({k: v for k, v in user_config.items() if k in _config})


@tool
async def search_web(query: str, max_results: int | None = None) -> str:
    """Search the web for current information. Returns titles, URLs, and text snippets."""
    api_key = _config["tavily_api_key"]
    if not api_key:
        return "Error: tavily_api_key not configured in [skills.config.web-search]."

    if max_results is None:
        max_results = _config["max_results"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": True,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

    results = [data.get("answer", "")]
    for r in data.get("results", []):
        results.append(f"- [{r['title']}]({r['url']}): {r['content']}")

    return "\n".join(results) if results else "No results found."


@tool
async def fetch_page(url: str) -> str:
    """Fetch and extract readable text content from a web page URL."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url,
            headers={"User-Agent": "AgentBuilder/1.0"},
            timeout=15,
            follow_redirects=True,
        )
        resp.raise_for_status()

    # Simple text extraction: strip HTML tags
    import re
    text = resp.text
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    MAX_CHARS = 8000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + f"\n\n... (truncated {len(text) - MAX_CHARS} chars)"

    return text


def get_tools():
    return [search_web, fetch_page]
