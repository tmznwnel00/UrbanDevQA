from mcp.server.fastmcp import FastMCP
from loguru import logger
from duckduckgo_search import DDGS

SERVER_NAME = "web_search"
HOST = "0.0.0.0"
PORT = 8115  

mcp = FastMCP(
    name=SERVER_NAME,
    instructions="A server that provides web search functionality using DuckDuckGo.",
    host=HOST,
    port=PORT,
)

@mcp.tool()
async def web_search(query: str, max_results: int = 3) -> dict:
    """
    Performs a web search using DuckDuckGo and returns the results.

    Args:
        query: The search query.
        max_results: The maximum number of results to return (default: 3, max: 5).
    
    Returns:
        A dictionary containing the search results.
    """
    max_results = min(max_results, 5)
    
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=max_results)]
    
    limited_results = []
    for result in results:
        limited_result = {
            "title": result.get("title", "")[:200], 
            "body": result.get("body", "")[:500],   
            "link": result.get("link", "")[:100],   
        }
        limited_results.append(limited_result)
    
    return {"results": limited_results, "original_query": query}

if __name__ == "__main__":
    mcp.run(transport="sse")
    logger.info(f"Starting Web Search MCP server on {HOST}:{PORT}")