import sqlite3
from sqlite3 import Error
from typing import Dict

from .base import BaseDBConnector
from .errors import DBConnectionError


class SQLiteConnector(BaseDBConnector):
    """
    Connects to an sqlite file on the local machine for reading and writing
    data.
    """

    name = "SQLite Connector"
    options_schema = {
        "type": "object",
        "properties": {
            "database": {
                "type": "string",
                "description": (
                    "The database name or relative path to the file for "
                    "sqlite3"
                ),
                "title": "Database",
                "subtype": "path",
            },
            "sql_statement": {
                "type": "string",
                "description": "The path to the file which contains the "
                "sql statement to run",
                "subtype": "path",
                "title": "Select Statement File",
            },
        },
        "required": ["database", "select_statement", "insert_statement"],
    }

    def _create_connection(self, database: Dict[str, str]):
        """
        Create database connection to the SQLite database specified in database
        :param database: Dict object with connection info

        :return: Connection object
        """

        try:
            conn = sqlite3.connect(
                self.config.absolute_path(database["database"])
            )
        except Error:
            raise DBConnectionError()

        conn.row_factory = sqlite3.Row
        return conn
