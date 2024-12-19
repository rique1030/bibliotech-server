import mariadb
from colorama import Fore, Style
import os
import datetime
import inspect
from .ContextManager import CreationContextManager, RequestContextManager
from .DatabaseQueries import DATABASE_QUERIES, ACCOUNT_HANDLER_QUERIES

print( Fore.GREEN + "mariadb version: ",mariadb.__version__ + Style.RESET_ALL)


class DatabaseManager:
	def __init__(self):
		self.database = "bibliotech_db"
		self.password = os.getenv('db_password')
		self.default_user_types = [("Admin",1 , 1 , 1, 1), ("User", 0, 0 ,0 ,0)]

	def backup_database(self):
		backup_file = f"{self.database}_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
		command = Fore.GREEN +  f"mysqldump -u root -p{self.password} {self.database} > ./Backups/{backup_file} " + Style.RESET_ALL
		os.system(command)
		print( Fore.GREEN + f"Backup created: {backup_file}" + Style.RESET_ALL)

	def create_database(self):
		# Create the database
		self.create_db_if_not_exists()
		# Create the tables
		# Create the account table
		self.create_user_type_table()
		self.create_accounts_table()
		# Create the books table
		self.create_books_table()
		self.create_categories_table()
		self.create_book_categories_table()
		self.create_borrowed_books_table()


	def create_db_if_not_exists(self):
		try:
			with CreationContextManager() as cursor:
				cursor.execute(DATABASE_QUERIES.CREATE_DATABASE.format(db_name=self.database))
				print( Fore.GREEN + f"Database {self.database} created" + Style.RESET_ALL)
		except mariadb.Error as err:
			print( Fore.RED + "Database creation failed" + Style.RESET_ALL)
			print( Fore.RED + f"Error: {err}" + Style.RESET_ALL)

	def execute_query(self, query, query_name):
		try:
			with RequestContextManager() as cursor:
				cursor.execute(query)
				print( Fore.GREEN + f"Function: {inspect.currentframe().f_code.co_name} - {query_name} Table Created" + Style.RESET_ALL)
		except mariadb.Error as err:
			if hasattr(err, 'errno') and hasattr(err, 'msg'):
				print( Fore.RED + f"Error Code: {err.errno}, Message: {err.msg}" + Style.RESET_ALL)
			else:
				print( Fore.RED + f"Error: {err}" + Style.RESET_ALL)

	def populate_if_empty(self, table_name, insert_query, data):
		try:
			with RequestContextManager() as cursor:
				check_empty = f"SELECT COUNT(*) FROM {table_name}"
				cursor.execute(check_empty)
				(count,) = cursor.fetchone()
				if count == 0:
					cursor.executemany(insert_query, data)
		except mariadb.Error as err:
			print( Fore.RED + f"Table population failed  || Error: {err}" + Style.RESET_ALL)
			print(Fore.BLUE + f"Executing query: {insert_query}" + Style.RESET_ALL)

	def create_user_type_table(self):
		self.execute_query(DATABASE_QUERIES.CREATE_USER_TYPE_TABLE, "user_type")
		self.populate_if_empty("user_type", ACCOUNT_HANDLER_QUERIES.INSERT_ACCOUNT_TYPE , self.default_user_types)

	def create_accounts_table(self):
		self.execute_query(DATABASE_QUERIES.CREATE_ACCOUNTS_TABLE, "accounts")

	def create_books_table(self):
		self.execute_query(DATABASE_QUERIES.CREATE_BOOKS_TABLE, "books")

	def create_categories_table(self):
		self.execute_query(DATABASE_QUERIES.CREATE_CATEGORIES_TABLE, "categories")

	def create_book_categories_table(self):
		self.execute_query(DATABASE_QUERIES.CREATE_BOOK_CATEGORIES_TABLE, "book_categories")

	def create_borrowed_books_table(self):
		self.execute_query(DATABASE_QUERIES.CREATE_BORROWED_BOOKS_TABLE, "borrowed_books")

		