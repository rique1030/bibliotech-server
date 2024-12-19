from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from Components.config import *
from Components.BookManager import BookManager
from Components.AccountManager import AccountManager
from Components.DatabaseManager import DatabaseManager
import threading
import time

app = Flask(__name__, static_folder="./storage")

CORS(app)



class MainServer:
	def __init__(self):
		self.app = app
		self.socketio = SocketIO(self.app)
		
		self.backup_delay = HOURS_PER_BACKUP * 60 * 60 # 24 hours
		self.book_handler = BookManager()
		self.account_handler = AccountManager()
		self.handler = DatabaseManager()

		# ? clients
		self.available_clients = {}
		self.ping_interval = 30 # seconds
		#start backup thread
		threading.Thread(target=self.backup_thread, daemon=True).start()

		#routes

		### ? book routes
		app.add_url_rule('/books/fetch', view_func=self.book_handler.get_books, methods=['POST'])
		app.add_url_rule('/books/get', view_func=self.book_handler.get_book_by_id, methods=['POST'])
		app.add_url_rule('/books/insert', view_func=self.book_handler.insert_books, methods=['POST'])
		app.add_url_rule('/books/update', view_func=self.book_handler.update_books, methods=['POST'])
		app.add_url_rule('/books/delete', view_func=self.book_handler.delete_books, methods=['POST'])
		app.add_url_rule('/request/accept', view_func=self.book_handler.accept_request, methods=['POST'])
		# ? category routes
		app.add_url_rule('/categories/insert', view_func=self.book_handler.insert_categories, methods=['POST'])
		app.add_url_rule('/categories/get-get', view_func=self.book_handler.get_categories, methods=['GET'])
		app.add_url_rule('/categories/get', view_func=self.book_handler.get_category_by_id, methods=['POST'])
		app.add_url_rule('/categories/fetch', view_func=self.book_handler.fetch_categories, methods=['POST'])
		app.add_url_rule('/categories/update', view_func=self.book_handler.update_categories, methods=['POST'])
		app.add_url_rule('/categories/delete', view_func=self.book_handler.delete_categories, methods=['POST'])
		app.add_url_rule('/categories/join', view_func=self.book_handler.add_joint_categories, methods=['POST'])
		app.add_url_rule('/categories/dissolve', view_func=self.book_handler.remove_joint_categories, methods=['POST'])
		app.add_url_rule('/categories/join/get', view_func=self.book_handler.get_joint_categories, methods=['POST'])
		### ? account routes
		app.add_url_rule('/accounts/login', view_func=self.account_handler.login, methods=['POST'])
		app.add_url_rule('/accounts/fetch', view_func=self.account_handler.fetch_accounts, methods=['POST'])
		app.add_url_rule('/accounts/get', view_func=self.account_handler.get_accounts, methods=['POST'])
		app.add_url_rule('/accounts/insert', view_func=self.account_handler.signup, methods=['POST'])
		app.add_url_rule('/accounts/update', view_func=self.account_handler.update_accounts, methods=['POST'])
		app.add_url_rule('/accounts/delete', view_func=self.account_handler.delete_accounts, methods=['POST'])
		# ? user type routes
		app.add_url_rule('/usertype/fetch', view_func=self.account_handler.fetch_user_types, methods=['POST'])
		app.add_url_rule('/usertype/insert', view_func=self.account_handler.insert_user_types, methods=['POST'])
		app.add_url_rule('/usertype/update', view_func=self.account_handler.update_user_types, methods=['POST'])
		app.add_url_rule('/usertype/get-get', view_func=self.account_handler.get_user_types, methods=['GET'])
		app.add_url_rule('/usertype/delete', view_func=self.account_handler.delete_user_types, methods=['POST'])
		app.add_url_rule('/usertype/get', view_func=self.account_handler.get_user_type_by_id, methods=['POST'])
		# ? records routes
		app.add_url_rule('/records/copies', view_func=self.book_handler.get_records_book_copies, methods=['POST'])
		app.add_url_rule('/records/borrow', view_func=self.book_handler.get_records_borrowed_books, methods=['POST'])
		app.add_url_rule('/records/user', view_func=self.book_handler.get_records_user, methods=['POST'])
		app.add_url_rule('/records/assigned', view_func=self.book_handler.get_records_category, methods=['POST'])

		# ? static files
		app.add_url_rule('/qr/<path:filename>', view_func=self.get_file, methods=['GET'])
		# ? client routes
		self.socketio.on_event('connect', self.handle_connect)

		# ? user routes
		app.add_url_rule('/get_available_clients', view_func=self.get_available_clients, methods=['GET'])
		app.add_url_rule('/request_books', view_func=self.book_handler.request_books, methods=['POST'])
		app.add_url_rule('/request_borrow_on_client', view_func=self.request_borrow_on_client, methods=['POST'])
		
	def backup_thread(self):
		while True:
			time.sleep(self.backup_delay)
			print("Backing up database...")
			self.handler.backup_database()
			print("Database backup completed")

	def get_file(self, filename):
		return send_from_directory('./storage/qr-codes/', filename)
	
	def handle_connect(self):
		client_id = request.args.get('client_id')  # Or use socketio's event data instead
		self.available_clients[request.sid] = client_id
		print(f"Client connected: {request.sid} (Client ID: {client_id})")


	def request_borrow_on_client(self):
		data  = request.get_json()
		book_id = data['book_id']
		user_id = data['user_id']
		data = self.book_handler.get_book_by_id(book_id)
		user = self.account_handler.get_account_by_id(user_id)
		self.socketio.emit('request_borrow', {'book': data, 'user_id': user}, namespace='/')
		return {"success": True}
		

	def get_available_clients(self):
		return self.available_clients



if __name__ == "__main__":
	server = MainServer()
	server.handler.create_database()
	server.socketio.run(app, host='0.0.0.0', port=5000)
	# app.run(host="0.0.0.0", port=5000)
