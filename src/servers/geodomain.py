import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from loguru import logger

import mcp.types as types
from typing import Any
import json 

from ..database import SqliteDatabase
from ..config import ServersConfig
CONFIG = ServersConfig.geodomain()

mcp: FastMCP = FastMCP(
    server_name=CONFIG.server_name,
    instructions="A Sqlite Server to retrieve GeoDomain Data",
    host=CONFIG.host,
    port=CONFIG.port,
)

# Register Tools
db_path = str(Path(CONFIG.data_path) / CONFIG.db_filename)
db = SqliteDatabase(db_path=str(db_path))

async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="list_tables",
            description="List all tables in the SQLite database",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="describe_table",
            description="Describe the schema and data dictionary of a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    }
                },
                "required": ["table_name"]
            }
        ),
        types.Tool(
            name="read_query",
            description="Execute a SELECT query on the SQLite database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL SELECT query to execute"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="list_output_area",
            description="Find LSOA11CD codes using a fuzzy match on a region or local authority name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to match (e.g., region or LAD name)"
                    },
                    "output_area_type": {
                        "type": "string",
                        "description": "'RGN11NM' or 'LAD11NM'"
                    }
                },
                "required": ["name", "output_area_type"]
            }
        )
    ]

@mcp.tool()
async def list_tables() -> list[str]:
    """List all tables in the SQLite database
    
    :return: A list of table names
    """
    res = db._execute_query("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in res]

    table_descriptions = """1. Broadband Coverage(`table_name=broadband_coverage`): Contains detailed broadband service availability statistics (e.g., SFBB, UFBB, full fibre) and coverage quality metrics for residential premises across Lower Layer Super Output Areas (LSOAs) in the UK.
2. Broadband Speed(`table_name=broadband_speed`): Records broadband speed performance and usage metrics, including median and average upload/download speeds, categorized by connection type and speed tier for each LSOA.
3. Classification of Workplace Zones (COWZ) Description(`table_name=cowz_description`): Provides metadata and qualitative descriptions (e.g., level, name, and pen portrait) for Supergroup and Group classifications within the Classification of Workplace Zones (COWZ) system.
4. Classification of Workplace Zones (COWZ) (`table_name=cowz`): Maps each Workplace Zone to its corresponding MSOA and LAD and provides its classification into COWZ Supergroup and Group categories.
5. House Age(`table_name=house_age`): Offers statistical and modal summaries of property construction periods within each LSOA, including dominant age bands and post-2016 build percentages.
6. House Median Price and Transaction(`table_name=house_med_trans`): Captures the quarterly median house prices and the number of housing transactions in each LSOA over time.
7. Residential Mobility Index(`table_name=rmi_base2023`): Reports the annual residential churn rate, defined as the proportion of properties that changed occupants relative to the start of 2023, for each LSOA.
8. Population(`table_name=population_{{year}}`): Provides annual demographic breakdowns for each LSOA, including total population and gender-specific age bands from 0-9 up to 90+
9. Spatial Signatures(`table_name=spatial_signatures`): Categorizes LSOAs into detailed urban and rural spatial types (e.g. Wild Countryside, Dense Urban Neighbourhoods, Hyper Concentrated Urbanity) based on land use, built environment, connectivity, and population/job density.
10. Point of Interest(`table_name=poi`): Lists categorized points of interest in each LSOA, including their names, locations, source providers, and geographical attributes such as address and coordinates.
11. Index of Multiple Deprivation (IMD) (`table_name=imd`): Provides deprivation metrics and rankings for LSOAs and Local Authorities, including decile and percentile classifications of socio-economic status
12. Output Area with different layers(`table_name=oa_mosa_lad_rgn`): Maps hierarchical geographic codes and names—LSOA, MSOA, Local Authority District (LAD), and Region—for administrative data linkage.
"""
    results = f"## Tables in the SQLite database:\n"
    for table in tables:
        results += f"- {table}\n"
    results += "\n## Table Descriptions:\n" + table_descriptions
    return results

@mcp.tool()
async def describe_table(table_name: str) -> str:
    """Describe the schema and the data dictionary of a specific table
    
    :param table_name: The name of the table to describe
    :return: A string containing the table schema and data dictionary
    """
    results = f'## Table `{table_name}` Info:'
    res = db._execute_query(f"PRAGMA table_info({table_name})")
    for row in res:
        results += f"\n- {row['name']} ({row['type']})"

    if 'population' in table_name:
        table_name = 'population'
    
    with open(Path(CONFIG.data_path) / f"{table_name}-data_dictionary.json", 'r') as file:
        data_dictionary = json.load(file)
    results += "\n## Data Dictionary:"
    results += "\n" + json.dumps(data_dictionary, indent=2)
    return results

@mcp.tool()
async def read_query(query: str) -> list[dict[str, Any]]:
    """Execute a SELECT query on the SQLite database
    
    :param query: The SQL SELECT query to execute
    :return: A list of results from the query
    """
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")
    results = db._execute_query(query)
    return results

@mcp.tool()
async def search_region_code_by_name(region_name: str) -> str:
    """
    Search for region codes (RGN11CD) by name (RGN11NM).
    
    :param region_name: The name to search for (e.g., London, North East)
    :return: List of matching region codes
    """
    results = db.search_region_code_by_name(name=region_name)
    if not results:
        raise ValueError(f"No close match found for '{region_name}'.")
    return results

@mcp.tool()
async def search_lad_code_by_name(lad_name: str) -> str:
    """
    Search for local authority district codes (LAD11CD) by name (LAD11NM).
    
    :param lad_name: The name to search for local authority district name (e.g., City of London 001)
    :return: List of matching local authority district codes
    """
    results = db.search_lad_code_by_name(name=lad_name)
    if not results:
        raise ValueError(f"No close match found for '{lad_name}'.")
    return results

# @mcp.tool()
# async def list_output_area(name: str, output_area_type: str) -> list[Any]:
#     """
#     Find LSOA11CD codes using a fuzzy match on a region or local authority name.
    
#     :param name: The name to match (e.g., region or LAD name)
#     :param output_area_type: 'RGN11NM' or 'LAD11NM'
#     :return: List of matching LSOA11CDs
#     """
#     results = db.list_output_area_by_similarity(
#         name=name,
#         output_area_type=output_area_type
#     )
#     if not results:
#         raise ValueError(f"No close match found for '{name}' in '{output_area_type}'.")
#     return results

if __name__ == "__main__":
    logger.info(f"Starting server on {CONFIG.host}:{CONFIG.port}")
    mcp.run(transport="sse")