import mariadb
import os

class CreationContextManager:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"  # Adjust username if needed
        self.password = os.getenv('db_password')

        # Assert that the password is not None (i.e., it is set)
        assert self.password is not None, "Environment variable 'db_password' is not set!"

    def __enter__(self):
        # Establish connection to the MySQL/MariaDB server
        self.conn = mariadb.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()  # Commit any changes if needed
        self.conn.close()

class RequestContextManager:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"  # Adjust username if needed
        self.password = os.getenv('db_password')
        self.database = "bibliotech_db"
        # Assert that the password is not None (i.e., it is set)
        assert self.password is not None, "Environment variable 'db_password' is not set!"

    def __enter__(self):
        # Establish connection to the MySQL/MariaDB server
        self.conn = mariadb.connect(
            host=self.host,
            user=self.user,
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