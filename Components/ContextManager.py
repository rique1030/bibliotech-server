import os
from .config import *
SQL_CONNECTION = None

if DEPLOYMENT_MODE == DeploymentMode.DEVELOPMENT:
    import mariadb as sql
    SQL_CONNECTION = DEVELOPMENT_CONFIG
else:
	import pymysql as sql
	SQL_CONNECTION = PRODUCTION_CONFIG

class CreationContextManager:
    def __init__(self):
        self.host = SQL_CONNECTION['DB_HOST']
        self.user = SQL_CONNECTION['DB_USER']
        self.port = SQL_CONNECTION['DB_PORT']
        # TODO: put password into env
        # HACK : for testing
        self.password = SQL_CONNECTION['DB_PASSWORD']
        # Assert that the password is not None (i.e., it is set)
        assert self.password is not None, "Environment variable 'db_password' is not set!"

    def __enter__(self):
        # Establish connection to the MySQL/sql server
        self.conn = sql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password
        )
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()  # Commit any changes if needed
        self.conn.close()

class RequestContextManager:
    def __init__(self):
        self.host = SQL_CONNECTION['DB_HOST']
        self.user = SQL_CONNECTION['DB_USER']
        self.port = SQL_CONNECTION['DB_PORT']
        # TODO: put password into env
        #self.password = os.getenv('db_password')
        # HACK : for testing
        self.password = SQL_CONNECTION['DB_PASSWORD']
        self.database = SQL_CONNECTION['DB_NAME']
        # Assert that the password is not None (i.e., it is set)
        assert self.password is not None, "Environment variable 'db_password' is not set!"

    def __enter__(self):
        # Establish connection to the MySQL/sql server
        self.conn = sql.connect(
            host=self.host,
            user=self.user,
            port=self.port,
            password=self.password,
            database=self.database
        )
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()  # Commit any changes if needed
        self.conn.close()