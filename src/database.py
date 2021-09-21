import sqlite3
import traceback
import sys
from typing import Union

class Database:

    def __init__(self, database_path: str):
        self.path = database_path
        self.connection = self._tryConnect()

    def _tryConnect(self) -> Union[sqlite3.Connection, None]:
        try:
            connection = sqlite3.connect(self.path, check_same_thread=False)
            print("[SQLite Database] => Successfull Connection")
            return connection
        except sqlite3.Error as err:
            print('SQLite error: %s' % (' '.join(err.args)))
            print('Exception class is: ', err.__class__)
            print('SQLITE traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return None