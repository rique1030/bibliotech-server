from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from Components.config import *
from Components.db import Database
from Components.managers.roles import RoleManager
from Components.managers.books import BookManager
from Components.managers.categories import CategoryManager
from Components.managers.book_categories import BookCategoryManager
from Components.managers.user import UserManager
import os
import time
import random

app = Flask(__name__, static_folder="./storage")

CORS(app)

class MainServer:
	def __init__(self):
		os.system('cls' if os.name == 'nt' else 'clear')
		self.app = app
		self.socketio = SocketIO(self.app)
		
		self.db = Database()

		self.role_manager = RoleManager(self.app, self.db)
		self.user_manager = UserManager(self.app, self.db)
		self.book_manager = BookManager(self.app, self.db)
		self.category_manager = CategoryManager(self.app, self.db)
		self.book_category_manager = BookCategoryManager(self.app, self.db)

		# ? clients
		self.available_clients = {}
		self.ping_interval = 30 # seconds

		#routes
		# app.before_request(self.before_request)
		
		# ? static files
		app.add_url_rule('/<path:filename>', view_func=self.get_file, methods=['GET'])
		#app.add_url_rule('/<path:filename>', view_func=self.get_file, methods=['GET'])
		# # ? client routes
		# self.socketio.on_event('connect', self.handle_connect)
		# self.socketio.on_event('disconnect', self.handle_disconnect)

		# # ? user routes
		# app.add_url_rule('/get_available_clients', view_func=self.get_available_clients, methods=['GET'])
		# app.add_url_rule('/request_books', view_func=self.book_handler.request_books, methods=['POST'])
		# app.add_url_rule('/request_borrow_on_client', view_func=self.request_borrow_on_client, methods=['POST'])
	
	
	def before_request(self):
		delay = random.uniform(0.5, 2)  # 500ms to 2000ms
		time.sleep(delay)  # Adding delay to simulate throttl


	def get_file(self, filename):
		return send_from_directory('./storage/', filename)
	
	def handle_connect(self):
		client_id = request.args.get('client_id')  # Or use socketio's event data instead
		self.available_clients[client_id] = request.sid
		print(f"Client connected: {request.sid} (Client ID: {client_id})")

	def handle_disconnect(self):
		client_id = self.available_clients.pop(request.sid, None)
		print(f"Client disconnected: {request.sid} (Client ID: {client_id})")

	def request_borrow_on_client(self):
		data  = request.get_json()
		book_id = data['book_id']
		user_id = data['user_id']
		client_id = data['client_id']
		print("request_borrow_on_client", book_id, user_id)
		data = self.book_handler.get_book_by_id_for_borrow(book_id)
		user = self.account_handler.get_account_by_id(user_id)
		if client_id in self.available_clients:
			socket_id = self.available_clients[client_id]
			self.socketio.emit('request_borrow', {'book': data, 'user': user}, room=socket_id, namespace='/')
			return {"success": True}
		else:
			return {"error": "User not connected"}, 400
		

	def get_available_clients(self):
		return self.available_clients



if __name__ == "__main__":
	server = MainServer()
	server.socketio.run(app, host='0.0.0.0', port=5000 , debug=True)
