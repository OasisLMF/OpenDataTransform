from typing import Any, Dict, Iterable, List

import sqlparams
import sqlparse

from converter.connector.base import BaseConnector

from .errors import DBQueryError


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
                    "Which host to use when connecting to the database. "
                    "Not used with SQLite."
                ),
                "default": "",
                "title": "Host",
            },
            "port": {
                "type": "string",
                "description": (
                    "The port to use when connecting to the database. "
                    "Not used with SQLite."
                ),
                "default": "",
                "title": "Port",
            },
            "database": {
                "type": "string",
                "description": (
                    "The database name or relative path to the file for "
                    "sqlite3"
                ),
                "title": "Database",
            },
            "user": {
                "type": "string",
                "description": (
                    "The username to use when connecting to the database. "
                    "Not used with SQLite."
                ),
                "default": "",
                "title": "User",
            },
            "password": {
                "type": "password",
                "description": (
                    "The password to use when connecting to the database. "
                    "Not used with SQLite."
                ),
                "default": "",
                "title": "Password",
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
    sql_params_output = "qmark"

    def __init__(self, config, **options):
        super().__init__(config, **options)

        self.database = {
            "host": options.get("host", ""),
            "port": options.get("port", ""),
            "database": options["database"],
            "user": options.get("user", ""),
            "password": options.get("password", ""),
        }
        self.sql_statement_path = config.absolute_path(
            options["sql_statement"]
        )

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
        with open(self.sql_statement_path) as f:
            select_statement = f.read()

        return select_statement

    def _get_insert_statements(self) -> List[str]:
        """
        SQL string(s) to insert the data into the DB

        :return: List of sql statements
        """
        with open(self.sql_statement_path) as f:
            sql = f.read()

        return sqlparse.split(sql)

    def load(self, data: Iterable[Dict[str, Any]]):
        insert_sql = self._get_insert_statements()
        data = list(
            data
        )  # convert iterable to list as we reuse it based on number of queries
        conn = self._create_connection(self.database)

        with conn:
            cur = self._get_cursor(conn)
            query = sqlparams.SQLParams("named", self.sql_params_output)

            # insert query can contain more than 1 statement
            for line in insert_sql:
                sql, params = query.formatmany(line, data)
                try:
                    cur.executemany(sql, params)
                except Exception as e:
                    raise DBQueryError(sql, e, data=data)

    def row_to_dict(self, row):
        """
        Convert the row returned from the cursor into a dictionary

        :return: Dict
        """
        return dict(row)

    def extract(self) -> Iterable[Dict[str, Any]]:
        select_sql = self._get_select_statement()
        conn = self._create_connection(self.database)

        with conn:
            cur = self._get_cursor(conn)
            try:
                cur.execute(select_sql)
            except Exception as e:
                raise DBQueryError(select_sql, e)

            rows = cur.fetchall()
            for row in rows:
                yield self.row_to_dict(row)
