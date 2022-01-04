import pyodbc
from typing import Dict

from .base import BaseDBConnector
from .errors import DBConnectionError


class SQLServerConnector(BaseDBConnector):
    """
    Connects to an Microsoft SQL Server for reading and writing data.
    """
    name = "SQL Server Connector"
    driver = "{ODBC Driver 17 for SQL Server}"

    def _create_connection(self, database: Dict[str, str]):
        """
        Create database connection to the SQLite database specified in database
        :param database: Dict object with connection info

        :return: Connection object
        """

        try:
            conn = pyodbc.connect(
                'DRIVER={};SERVER={};PORT={};DATABASE={};UID={};PWD={}'.format(
                    self.driver,
                    database["host"],
                    database["port"],
                    database["database"],
                    database["user"],
                    database["password"]
                ))
        except Exception as e:
            raise DBConnectionError()

        return conn

    def row_to_dict(self, row):
        return dict(zip([t[0] for t in row.cursor_description], row))
