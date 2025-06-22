# import mcp
# from mcp.client.streamable_http import streamablehttp_client
# import json
# import base64

# config = {}
# # Encode config in base64
# config_b64 = base64.b64encode(json.dumps(config).encode())
# smithery_api_key = "9ac49307-b992-41b8-af2d-cae7b441da75"

# # Create server URL
# url = f"https://server.smithery.ai/@smithery-ai/server-sequential-thinking/mcp?config={config_b64}&api_key={smithery_api_key}"

# async def main():
#     # Connect to the server using HTTP client
#     async with streamablehttp_client(url) as (read_stream, write_stream, _):
#         async with mcp.ClientSession(read_stream, write_stream) as session:
#             # Initialize the connection
#             await session.initialize()
#             # List available tools
#             tools_result = await session.list_tools()
#             print(f"Available tools: {', '.join([t.name for t in tools_result.tools])}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())

from mcp.server.fastmcp import FastMCP
import base64
import json
from loguru import logger

SERVER_NAME = "sequential_thinking"
HOST = "0.0.0.0"
PORT = 8114

mcp = FastMCP(
    name=SERVER_NAME,
    instructions="A server that provides sequential thinking (MCP) for query decomposition.",
    host=HOST,
    port=PORT,
)

@mcp.tool()
async def sequential_thinking(query: str) -> dict:
    """
    쿼리를 단계적으로 분해하여 반환합니다.
    (여기에 실제 sequential thinking MCP 로직을 구현하거나, 외부 API 호출/프롬프트 호출 등)
    """

    steps = [
        {"step": 1, "thought": "문제의 주요 목표 파악"},
        {"step": 2, "thought": "핵심 요소 분해"},
        {"step": 3, "thought": "각 요소별 세부 쿼리 생성"},
        {"step": 4, "thought": "논리적 순서로 정렬"},
    ]
    return {"steps": steps, "original_query": query}

if __name__ == "__main__":
    mcp.run(transport="sse")
    logger.info(f"Starting Sequential Thinking MCP server on {HOST}:{PORT}")