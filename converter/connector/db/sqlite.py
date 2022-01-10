import sqlite3
import sqlparse
from sqlite3 import Error
from typing import Any, Dict, Iterable, List

from converter.types.notset import NotSetType
from .base import BaseDBConnector
from .errors import DBConnectionError


class SQLiteConnector(BaseDBConnector):
    """
    Connects to an sqlite file on the local machine for reading and writing data.
    """
    name = "SQLite Connector"

    def _create_connection(self, database: Dict[str, str]):
        """
        Create database connection to the SQLite database specified in database
        :param database: Dict object with connection info

        :return: Connection object
        """

        try:
            conn = sqlite3.connect(self.config.absolute_path(database["database"]))
        except Error as e:
            raise DBConnectionError()

        conn.row_factory = sqlite3.Row
        return conn
