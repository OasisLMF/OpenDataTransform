import re
import sqlite3
from sqlite3 import Error
from typing import Any, Dict, Iterable, List

from converter.connector.base import BaseConnector
from converter.connector.errors import SQLiteConnectionError, SQLiteQueryError, SQLiteInsertDataError
from converter.types.notset import NotSetType


class SQLiteConnector(BaseConnector):
    """
    Connects to an sqlite file on the local machine for reading and writing data.

    **Options:**

    * `path` - The path to the sqlite file to read/write
    * `select_statement` - sql query to read the data from
    * `insert_statement` - sql query to insert the data from
    """
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
        "required": ["path", "select_statement", "insert_statement"],
    }

    def __init__(self, config, **options):
        super().__init__(config, **options)

        self.file_path = config.absolute_path(options["path"])
        self.select_statement_path = config.absolute_path(options["select_statement"])
        self.insert_statement_path = config.absolute_path(options["insert_statement"])

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
        with open(self.select_statement_path) as f:
            select_statement = f.read()

        return select_statement

    def _get_insert_statements(self) -> List[str]:
        """
        SQL string to insert the data into the specified table
        :param fields: List of field names

        :return: List of sql statements
        """
        with open(self.insert_statement_path) as f:
            insert_statements = f.readlines()

        return list(insert_statements)

    def load(self, data: Iterable[Dict[str, Any]]):

        conn = self._create_connection(self.file_path)
        insert_sql = self._get_insert_statements()
        data = list(data)  # convert iterable to list as we reuse it based on number of queries

        with conn:
            cur = conn.cursor()

            # insert query can contain more than 1 insert statement
            for sql in insert_sql:
                sql = sql.strip()  # remove any white spacing from beginning and end
                if sql:
                    # assume the insert string contains VALUES (:<param>, :<param>) so we
                    # can extract named parameters and get from data dict
                    keys = re.findall(":\w+", sql)
                    if len(keys) == 0:
                        raise SQLiteInsertDataError(f"Cannot find keys in sql string {sql}")

                    # extract out only the keys we want to insert from data
                    extracted_data = [tuple([row.get(key[1:]) for key in keys]) for row in data]
                    # check number of parameters extracted is correct
                    if len(keys) != len(extracted_data[0]):
                        raise SQLiteInsertDataError(
                            f"Number of keys ({len(keys)}) does not match extracted fields ({len(extracted_data[0])})")

                    try:
                        cur.executemany(sql, extracted_data)
                    except Error:
                        raise SQLiteQueryError(sql, data=extracted_data)

    def extract(self) -> Iterable[Dict[str, Any]]:
        conn = self._create_connection(self.file_path)
        select_sql = self._get_select_statement()

        with conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute(select_sql)
            except Error:
                raise SQLiteQueryError(select_sql)

            rows = cur.fetchall()
            for row in rows:
                yield dict(row)
