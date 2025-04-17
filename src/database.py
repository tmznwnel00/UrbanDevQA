
import os
import sys
import sqlite3
import json
from loguru import logger
from pathlib import Path
from contextlib import closing
from typing import Any
import difflib
from rapidfuzz import fuzz, process


class SqliteDatabase:
    def __init__(self, db_path: str):
        self.db_path = str(Path(db_path).expanduser())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize connection to the SQLite database"""
        logger.debug("Initializing database connection")
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            conn.close()

    def _execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as a list of dictionaries"""
        logger.debug(f"Executing query: {query}")
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                with closing(conn.cursor()) as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                    if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                        conn.commit()
                        affected = cursor.rowcount
                        logger.debug(f"Write query affected {affected} rows")
                        return [{"affected_rows": affected}]

                    results = [dict(row) for row in cursor.fetchall()]
                    logger.debug(f"Read query returned {len(results)} rows")
                    return results
        except Exception as e:
            logger.error(f"Database error executing query: {e}")
            raise

    def search_region_code_by_name(self, name: str) -> str:
        """
        Search for region codes by name.
        
        :param region_name: The name to search for (e.g., London, North East)
        :return: List of matching region codes
        """
        # 1. Get all distinct names in the target column
        query = "SELECT DISTINCT RGN11NM FROM oa_mosa_lad_rgn"
        rows = self._execute_query(query)
        all_names: dict[str, str] = {row["RGN11NM"].lower(): row["RGN11NM"] for row in rows}

        # 2. Fuzzy match to get the closest name
        matched = process.extract(name, all_names.keys(), limit=1, score_cutoff=80)
        if not matched:
            # If no good match, suggest top 3 similar names
            suggestions = process.extract(name, all_names.keys(), limit=3, score_cutoff=60)
            suggestion_text = (
                f"No close match found for '{name}' in 'RGN11NM'."
            )
            if suggestions:
                suggestions = [f'`{s[0]}`' for s in suggestions]
                suggestion_text += f" Did you mean: {', '.join(suggestions)}?"
            else:
                suggestion_text += " No similar names found."
            return suggestion_text
        
        matched_key = matched[0][0]
        matched_name = all_names[matched_key]
        logger.debug(f"Fuzzy matched name: {matched_name}")

        # 3. Return the RGN11CD that match the fuzzy-matched name
        final_query = f"""
            SELECT DISTINCT RGN11CD FROM oa_mosa_lad_rgn
            WHERE RGN11NM = ?
        """
        results = self._execute_query(final_query, (matched_name,))
        return str([row["RGN11CD"] for row in results])
    
    def search_lad_code_by_name(self, name: str) -> str:
        """
        Search for local authority district (LAD) codes by name.
        
        :param lad_name: The name to search for local authority district name (e.g., City of London 001)
        :return: List of matching local authority district codes
        """
        # 1. Get all distinct names in the target column
        query = "SELECT DISTINCT LAD11NM FROM oa_mosa_lad_rgn"
        rows = self._execute_query(query)
        all_names: dict[str, str] = {row["LAD11NM"].lower(): row["LAD11NM"] for row in rows}

        # 2. Fuzzy match to get the closest name
        matched = process.extract(name, all_names.keys(), limit=1, score_cutoff=80)
        if not matched:
            # If no good match, suggest top 3 similar names
            suggestions = process.extract(name, all_names.keys(), limit=3, score_cutoff=60)
            suggestion_text = (
                f"No close match found for '{name}' in 'LAD11NM'."
            )
            if suggestions:
                suggestions = [f'`{s[0]}`' for s in suggestions]
                suggestion_text += f" Did you mean: {', '.join(suggestions)}?"
            else:
                suggestion_text += " No similar names found."
            return suggestion_text
        
        matched_key = matched[0][0]
        matched_name = all_names[matched_key]
        logger.debug(f"Fuzzy matched name: {matched_name}")

        # 3. Return the LAD11CD that match the fuzzy-matched name
        final_query = f"""
            SELECT DISTINCT LAD11CD FROM oa_mosa_lad_rgn
            WHERE LAD11NM = ?
        """
        results = self._execute_query(final_query, (matched_name,))
        return str([row["LAD11CD"] for row in results])

    def list_output_area_by_similarity(self, name: str, output_area_type: str) -> list[str]:
        """
        Perform a similarity-based search on a region or LAD name and return matching LSOA11CDs.
        
        :param name: The name to match (e.g., region or LAD name)
        :param output_area_type: 'RGN11NM' or 'LAD11NM'
        :return: List of matching LSOA11CDs
        """
        if output_area_type not in ["RGN11NM", "LAD11NM"]:
            raise ValueError(f"Invalid output_area_type: {output_area_type}")

        # 1. Get all distinct names in the target column
        query = f"SELECT DISTINCT {output_area_type} FROM oa_mosa_lad_rgn"
        rows = self._execute_query(query)
        all_names = [row[output_area_type] for row in rows]

        # 2. Fuzzy match to get the closest name
        matched = difflib.get_close_matches(name, all_names, n=1, cutoff=0.6)
        if not matched:
            # If no good match, suggest top 3 similar names
            suggestions = difflib.get_close_matches(name, all_names, n=3, cutoff=0.4)
            suggestion_text = (
                f"No close match found for '{name}' in '{output_area_type}'."
            )
            if suggestions:
                suggestion_text += f" Did you mean: {', '.join(suggestions)}?"
            else:
                suggestion_text += " No similar names found."
            raise ValueError(suggestion_text)

        matched_name = matched[0]

        # 3. Return the LSOA11CDs that match the fuzzy-matched name
        final_query = f"""
            SELECT LSOA11CD FROM oa_mosa_lad_rgn
            WHERE {output_area_type} = ?
        """
        results = self._execute_query(final_query, (matched_name,))
        return [row["LSOA11CD"] for row in results]