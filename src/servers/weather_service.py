
import asyncio
from loguru import logger
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl
from typing import Any
from datetime import datetime
from datetime import timedelta
import json 
import random


WEATHER_DATA = {
    "seoul": {
        "temperature": 16,
        "conditions": "Sunny",
        "humidity": 20,
        "wind_speed": 3.8
    },
    "tokyo": {
        "temperature": 12,
        "conditions": "Rainy",
        "humidity": 70,
        "wind_speed": 9.4
    },
    "new_york": {
        "temperature": 10,
        "conditions": "Cloudy",
        "humidity": 40,
        "wind_speed": 5.1
    },
}
# DEFAULT_CITY = "Seoul"


async def fetch_weather(city: str) -> dict[str, Any]:
    """Fetch weather data for a specific city."""
    data = WEATHER_DATA.get(city)
    if data is None:
        logger.error(f"Weather data for {city} not found.")
        return {}
    logger.info(f"Fetching weather data for {city}")

    return {
        "temperature": data["temperature"],
        "conditions": data["conditions"],
        "humidity": data["humidity"],
        "wind_speed": data["wind_speed"],
        "timestamp": datetime.now().isoformat()
    }

server = Server("weather-server")
logger.info("Starting weather server")

# Register handlers
logger.debug("Registering handlers")
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List current weather data for all cities"""
    uris = [AnyUrl(f"weather://{city}/current") for city in WEATHER_DATA.keys()]
    return [
        types.Resource(
            uri=uri,
            name=f"Avaliable Cites",
            mimeType="application/json",
            description="Avalibale cities",
        )
        for uri in uris
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read current weather data for a specific city"""
    if str(uri).startswith("weather://") and str(uri).endswith("/current"):
        city = str(uri).split("/")[-2]
    else:
        raise ValueError(f"Unknown: {uri}")

    try:
        weather_data = await fetch_weather(city)
        return json.dumps(weather_data, indent=2)
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")

# Register Tools
logger.debug("Registering tools")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_forecast",
            description="Get weather forecast for a specific city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name to get the forecast data",
                    },
                    "days": {
                        "type": "number",
                        "description": "Days (1-5)",
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                "required": ["city"]
            }
        )
    ]

def weather_forcast(city: str, days: int) -> list[dict[str, Any]]:
    """Get weather forecast for a specific city"""
    if city not in WEATHER_DATA:
        raise ValueError(f"City {city} not found in weather data")
    forecasts = []
    for i in range(days):
        forecasts.append({
            "date": (datetime.now() + timedelta(days=i)).isoformat(),
            "temperature": random.randint(10, 30),
            "conditions": random.choice(["Sunny", "Rainy", "Cloudy"]),
            "humidity": random.randint(20, 80),
            "wind_speed": random.uniform(1.0, 10.0)
        })
    return forecasts

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Handle tool execution requests"""
    if name != "get_forecast":
        raise ValueError(f"Unknown tool: {name}")

    if not isinstance(arguments, dict) or "city" not in arguments:
        raise ValueError("Missing required argument: city")
    if not isinstance(arguments, dict) or "days" not in arguments:
        raise ValueError("Missing required argument: days")

    city = arguments["city"]
    days = arguments["days"]

    try:
        forecasts = weather_forcast(city, days)
        if not forecasts:
            raise ValueError(f"No forecast data available for {city}")
        logger.info(f"Fetching weather forecast for {city} for {days} days")

        return [
            types.TextContent(
                type="text",
                text=json.dumps(forecasts, indent=2)
            )
        ]
    except Exception as e:
        logger.error(f"Error fetching weather forecast: {e}")
        raise RuntimeError(f"Error fetching weather forecast: {e}")


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())