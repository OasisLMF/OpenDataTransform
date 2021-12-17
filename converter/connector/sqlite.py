import sqlite3
from sqlite3 import Error
from typing import Any, Dict, Iterable, List

from converter.connector.base import BaseConnector
from converter.connector.errors import SQLiteConnectionError
from converter.types.notset import NotSetType


class SQLiteConnector(BaseConnector):
    """
    Connects to an sqlite file on the local machine for reading and writing data.

    **Options:**

    * `path` - The path to the sqlite file to read/write
    * `table` - table to read the data from
    """
    CREATE_STATEMENT = "CREATE TABLE IF NOT EXISTS {} ({});"
    SELECT_STATEMENT = "SELECT * FROM {};"
    INSERT_STATEMENT = "INSERT INTO {} ({}) VALUES ({});"
    DELETE_STATEMENT = "DELETE FROM {};"

    name = "SQLite Connector"
    options_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "The path to the file to load relative to the config file"
                ),
                "subtype": "path",
                "title": "Path",
            },
            "table": {
                "type": "string",
                "description": "The table to read the data from",
                "title": "Table",
            },
            "truncate_table": {
                "type": "boolean",
                "description": "Should the loader table be truncated first?",
                "default": True,
                "title": "Include Header",
            },
        },
        "required": ["path", "table"],
    }

    def __init__(self, config, **options):
        super().__init__(config, **options)

        self.file_path = config.absolute_path(options["path"])
        self.truncate = options.get("truncate_table", True)
        self.table = options["table"]

    def _create_connection(self, database: str):
        """
        Create database connection to the SQLite database specified in file_path
        :param database: Path to SQLite db file

        :return: Connection object
        """
        try:
            conn = sqlite3.connect(database)
        except Error as e:
            raise SQLiteConnectionError()

        return conn

    def _get_select_statement(self) -> str:
        """
        SQL string to select the data from the specified table

        :return: string
        """
        return self.SELECT_STATEMENT.format(self.table)

    def _get_delete_statement(self) -> str:
        """
        SQL string to truncate the data from the specified table

        :return: string
        """
        return self.DELETE_STATEMENT.format(self.table)

    def _get_insert_statement(self, fields: List[str]) -> str:
        """
        SQL string to insert the data into the specified table
        :param fields: List of field names

        :return: string
        """
        columns = ', '.join(fields)
        values = ', '.join(['?'] * len(fields))
        return self.INSERT_STATEMENT.format(self.table, columns, values)

    def _get_create_table_statement(self, fields: List[str]) -> str:
        """
        SQL string to create the table if it doesn't already exist
        :param fields: List of field names

        :return: string
        """
        field_string = ', '.join(['%s integer' % f for f in fields])
        return self.CREATE_STATEMENT.format(self.table, field_string)

    def load(self, data: Iterable[Dict[str, Any]]):
        try:
            data = iter(data)
            first_row = next(data)
        except StopIteration:
            return

        conn = self._create_connection(self.file_path)
        create_table_sql = self._get_create_table_statement(list(first_row.keys()))
        insert_sql = self._get_insert_statement(list(first_row.keys()))

        with conn:
            cur = conn.cursor()
            cur.execute(create_table_sql)
            if self.truncate:
                delete_sql = self._get_delete_statement()
                cur.execute(delete_sql)

            cur.execute(insert_sql, tuple(first_row.values()))
            cur.executemany(insert_sql, [tuple(row.values()) for row in data])

    def extract(self) -> Iterable[Dict[str, Any]]:
        conn = self._create_connection(self.file_path)
        select_sql = self._get_select_statement()

        with conn:
            conn.row_factory = sqlite3.Row
            try:
                cur = conn.cursor()
                cur.execute(select_sql)
            except Error:
                raise SQLiteConnectionError()

            rows = cur.fetchall()
            for row in rows:
                yield dict(row)
