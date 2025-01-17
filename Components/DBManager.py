import os
import datetime
from .config import *
SQL_CONNECTION = None

if DEPLOYMENT_MODE == DeploymentMode.DEVELOPMENT:
	import mariadb as sql
	SQL_CONNECTION = DEVELOPMENT_CONFIG
else:
	import pymysql as sql
	SQL_CONNECTION = PRODUCTION_CONFIG
print("sql version: ",sql.__version__)

class DBCreationConnectionManager:
	def __init__(self):		
		self.host = SQL_CONNECTION['DB_HOST']
		self.user = SQL_CONNECTION['DB_USER'] # Adjust username if needed
		#self.password = os.getenv('db_password')
		# Assert that the password is not None (i.e., it is set)
		assert self.password is not None, "Environment variable 'db_password' is not set!"

	def __enter__(self):
		# Establish connection to the MySQL/sql server
		self.conn = sql.connect(
			host= self.host,
			user= self.user,
			password=self.password
		)
		return self.conn.cursor()

	def __exit__(self, exc_type, exc_value, traceback):
		self.conn.commit()  # Commit any changes if needed
		self.conn.close()



class DBConnectionManager:
	def __init__(self):
		self.host = "localhost"
		self.user = "root"  # Adjust username if needed
		self.password = os.getenv('db_password')
		self.database = "bibliotech_planestill"
		# Assert that the password is not None (i.e., it is set)
		assert self.password is not None, "Environment variable 'db_password' is not set!"

	def __enter__(self):
		# Establish connection to the MySQL/sql server
		self.conn = sql.connect(
			host= self.host,
			user= self.user,
			database=self.database,
			password=self.password
		)
		return self.conn.cursor()

	def __exit__(self, exc_type, exc_value, traceback):
		self.conn.commit()  # Commit any changes if needed
		self.conn.close()

class DBManager:
	def __init__(self):
		self.database = "bibliotech_planestill"
		self.sql_file_path = "../Database/bibliotech_planestill_setup.sql"
		self.password = os.getenv('db_password')
		os.makedirs(os.path.dirname(self.sql_file_path), exist_ok=True)

	def backup_database(self):
		backup_file = f"{self.database}_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
		command = f"mysqldump -u root -p{self.password} {self.database} > ./Backups/{backup_file}"
		os.system(command)
		print(f"Backup created: {backup_file}")

	def create_db_if_not_exists(self):
		try:
			with DBCreationConnectionManager() as cursor:
			# Create the database if it doesn't exist
				cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
		except sql.Error as err:
			print(f"Error: {err}")

	def create_books_table(self):
		try:
			with DBConnectionManager() as cursor:
				sql = """
				CREATE TABLE IF NOT EXISTS books (
					id INT AUTO_INCREMENT PRIMARY KEY,
					access_number VARCHAR(50) NOT NULL,
					call_number VARCHAR(50) NOT NULL,
					title VARCHAR(255) NOT NULL,
					author VARCHAR(255) NOT NULL,
					status ENUM('available', 'borrowed') DEFAULT 'available'  -- Status as an ENUM type
				);
				"""
				cursor.execute(sql)
				print("Books table created.")
		except sql.Error as err:
			print(f"Error: {err}")


class DBRequestsHandler:
	def __init__(self):

		pass

	def get_book_count(self):
		try:
			with DBConnectionManager() as cursor:
				cursor.execute("SELECT COUNT(*) FROM books")
				count = cursor.fetchone()[0]
				return count
		except sql.Error as err:
			print(f"Error: {err}")
			return None


	def insert_books(self, books):
		try:
			with DBConnectionManager() as cursor:
				book_array = []
				# Create a sample book
				for book in books:
					book_array.append((book['access_number'], book['call_number'], book['title'], book['author'], book['status']))
				sql = """
					INSERT INTO books (access_number, call_number, title, author, status)
					VALUES (%s, %s, %s, %s, %s)
				"""
				cursor.executemany(sql, book_array)
				return (f"{cursor.rowcount} books inserted successfully.")

		except sql.Error as err:
			return (f"Error while inserting data: {err}")

	def select_books(self, page_index = 0, filter_term = None, search_term= None):
		print("Selecting books...")
		try:
			with DBConnectionManager() as cursor:
				starting_index = page_index * 15
				limit = 15

				#base query
				search_filter = ""
				params = [limit, starting_index]
				if search_term and filter_term:
					f_term = "access_number"
					match filter_term:
						case "acc_num":
							f_term = "access_number"
						case "call_num":
							f_term = "call_number"
						case _:
							f_term = filter_term

					# search_filter = (" WHERE %s LIKE %s", (f_term, search_term))
					search_filter = f"WHERE {f_term} LIKE %s"
					params.insert(0, f"%{search_term}%")

				query = f"SELECT * FROM books {search_filter} LIMIT %s OFFSET %s"
				cursor.execute(query, tuple(params))
				# cursor.execute("SELECT * FROM books %s LIMIT  %s OFFSET %s", ( search_filter, limit, starting_index))
				rows = cursor.fetchall()

				# Initialize books with a key and an empty list
				books = {"books": []}  # Key "books" initialized as an empty list

					#4 = author
				# Convert each row to a dictionary
				for row in rows:
					book = {
						"unique_key": row[0],
						"access_number": row[1],  # Assuming first column is access number
						"call_number": row[2],    # Assuming second column is call number
						"title": row[3],          # Assuming third column is title
						"author": row[4],         # Assuming fourth column is author
						"status": row[5],         # Assuming fifth column is status
						# Add more fields as necessary
					}
					# Append book dictionary to the list under "books"
					books["books"].append(book)

				print(type(books))  # Debug print
				return books  # Return the dictionary containing the list of books
		except sql.Error as err:
			return f"Error: {err}"
