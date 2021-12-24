import re
import sqlite3
import psycopg2
import psycopg2.extras
import sqlparse
from sqlite3 import Error
from typing import Any, Dict, Iterable, List

from converter.connector.base import BaseConnector
from converter.connector.errors import DBConnectionError, DBQueryError, DBInsertDataError
from converter.types.notset import NotSetType


class BaseDBConnector(BaseConnector):
    """
    Connects to a database for reading and writing data.

    **Options:**

    * `host` - Which host to use when connecting to the database
    * `port` - The port to use when connecting to the database
    * `database` - The database name or relative path to the file for sqlite3
    * `user` - The username to use when connecting to the database
    * `password` - The password to use when connecting to the database
    * `select_statement` - sql query to read the data from
    * `insert_statement` - sql query to insert the data from
    """
    name = "BaseDB Connector"
    options_schema = {
        "type": "object",
        "properties": {
            "host": {
                "type": "string",
                "description": (
                    "Which host to use when connecting to the database. Not used with SQLite."
                ),
                "default": "",
                "title": "Host",
            },
            "port": {
                "type": "string",
                "description": (
                    "The port to use when connecting to the database. Not used with SQLite."
                ),
                "default": "",
                "title": "Port",
            },
            "database": {
                "type": "string",
                "description": (
                    "The database name or relative path to the file for sqlite3"
                ),
                "title": "Database",
            },
            "user": {
                "type": "string",
                "description": (
                    "The username to use when connecting to the database. Not used with SQLite."
                ),
                "default": "",
                "title": "User",
            },
            "password": {
                "type": "string",
                "description": (
                    "The password to use when connecting to the database. Not used with SQLite."
                ),
                "default": "",
                "title": "Password",
            },
            "select_statement": {
                "type": "string",
                "description": "The path to the file which contains the select sql",
                "subtype": "path",
                "title": "Select Statement File",
            },
            "insert_statement": {
                "type": "string",
                "description": "The path to the file which contains the insert sql",
                "subtype": "path",
                "title": "Insert Statement File",
            },
        },
        "required": ["database", "select_statement", "insert_statement"],
    }

    def __init__(self, config, **options):
        super().__init__(config, **options)

        self.database = {
            "host": options.get("host", ""),
            "port": options.get("port", ""),
            "database": options["database"],
            "user": options.get("user", ""),
            "password": options.get("password", "")
        }
        self.select_statement_path = config.absolute_path(options["select_statement"])
        self.insert_statement_path = config.absolute_path(options["insert_statement"])

    def _create_connection(self, database: Dict[str, str]):
        raise NotImplementedError()

    def _get_cursor(self, conn):
        cur = conn.cursor()
        return cur

    def _get_select_statement(self) -> str:
        """
        SQL string to select the data from the DB

        :return: string
        """
        with open(self.select_statement_path) as f:
            select_statement = f.read()

        return select_statement

    def _get_insert_statements(self) -> List[str]:
        """
        SQL string(s) to insert the data into the DB

        :return: List of sql statements
        """
        with open(self.insert_statement_path) as f:
            sql = f.read()

        return sqlparse.split(sql)

    def load(self, data: Iterable[Dict[str, Any]]):

        conn = self._create_connection(self.database)
        insert_sql = self._get_insert_statements()
        data = list(data)  # convert iterable to list as we reuse it based on number of queries

        with conn:
            cur = self._get_cursor(conn)

            # insert query can contain more than 1 statement
            for sql in insert_sql:
                try:
                    cur.executemany(sql, data)
                except Error as e:
                    raise DBQueryError(sql, e, data=data)

    def extract(self) -> Iterable[Dict[str, Any]]:
        conn = self._create_connection(self.database)
        select_sql = self._get_select_statement()

        with conn:
            cur = self._get_cursor(conn)
            try:
                cur.execute(select_sql)
            except Error as e:
                raise DBQueryError(select_sql, e)

            rows = cur.fetchall()
            for row in rows:
                yield dict(row)


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


class PostgresConnector(BaseDBConnector):
    """
    Connects to a Postgres database for reading and writing data.
    """
    name = "Postgres Connector"

    def _create_connection(self, database: Dict[str, str]):
        """
        Create database connection to the Postgres database
        :param database: Dict with database connection settings

        :return: Connection object
        """
        try:
            conn = psycopg2.connect(**database)
        except Error as e:
            raise DBConnectionError()

        return conn

    def _get_cursor(self, conn):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return cur
