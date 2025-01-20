from flask import Flask, json, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from Components.config import *
from Components.db import Database
from Components.managers.records import RecordManager
from Components.managers.roles import RoleManager
from Components.managers.books import BookManager
from Components.managers.categories import CategoryManager
from Components.managers.book_categories import BookCategoryManager
from Components.managers.user import UserManager
from Components.queries.book_borrow import BorrowedBookQueries
import os
import time
import random
import weakref
import gevent.monkey

gevent.monkey.patch_all()


app = Flask(__name__, static_folder="./storage")

CORS(app)

class MainServer:
	def __init__(self):
		os.system('cls' if os.name == 'nt' else 'clear')
		self.app = app
		self.socketio = SocketIO(self.app)
		self.db = Database()
		# ? ==============
		# ? Database Managers
		# ? ==============
		self.role_manager = RoleManager(self.app, self.db)
		self.user_manager = UserManager(self.app, self.db)
		self.category_manager = CategoryManager(self.app, self.db)
		self.book_manager = BookManager(self.app, self.db)
		self.book_category_manager = BookCategoryManager(self.app, self.db)
		self.book_manager._book_category_manager = weakref.ref(self.book_category_manager)
		self.book_borrow_query = BorrowedBookQueries(self.db.Session)
		self.record_manager = RecordManager(self.app)
		self.record_manager.role = self.role_manager.role_queries
		self.record_manager.user = self.user_manager.user_queries
		self.record_manager.category = self.category_manager.category_queries
		self.record_manager.book = self.book_manager.book_queries
		self.record_manager.book_category = self.book_category_manager.book_category_queries
		self.record_manager.book_borrow = self.book_borrow_query
		
		# ? ==============
		# ? clients
		# ? ==============
		self.available_clients = {}
		self.requests = {}
		self.ping_interval = 30 # seconds
		
		# ? ==============
		# ? static files
		# ? ==============
		app.add_url_rule('/<path:filename>', view_func=self.get_file, methods=['GET'])

		# ? ==============
		# ? websocket events
		# ? ==============
		self.socketio.on_event('connect', self.handle_connect)
		self.socketio.on_event('disconnect', self.handle_disconnect)
		self.socketio.on_event('client_connect', self.handle_client_connect)
		self.socketio.on_event('request', self.handle_request)
		self.socketio.on_event('review_request', self.handle_review_request)
		self.socketio.on_event('accept_request', self.handle_accept_request)
		self.socketio.on_event('deny_request', self.handle_deny_request)

	# ? ==============
	# ? private methods
	# ? ==============
	def before_request(self): # ? for debug purposes
		delay = random.uniform(0.5, 2)  # 500ms to 2000ms
		time.sleep(delay)  # Adding delay to simulate throttle

	def parse_request(self, data):
		if isinstance(data, str):
			return json.loads(data)
		return data

	def get_file(self, filename):
		return send_from_directory('./storage/', filename)
	
	def handle_connect(self):
		print(f"Incoming connection from: {request.sid}")

	def handle_client_connect(self, data):
		newData = self.parse_request(data)
		newData["busy"] = False
		self.available_clients[request.sid] = newData
		
	def handle_disconnect(self):
		client_id = self.available_clients.pop(request.sid, None)
		print(f"Client disconnected: {request.sid} (Client ID: {client_id})")

	def verify_request_id(self, data):
		if data is None:
			print("No data provided")
			return False, None
		if data.get("request_id") is None:
			print("No request id provided")
			return False, None
		if self.requests.get(data.get("request_id")) is not None:
			return True, data.get("request_id")
		return False, None

	def handle_deny_request(self, data):
		print("Request denied")
		newData = self.parse_request(data)
		available, request_id = self.verify_request_id(newData)
		if available:
			self.socketio.emit('request_denied', "Request denied", room=request_id, namespace='/')
			user = self.requests[request_id]
			self.available_clients[user.get("receiver_id")]["busy"] = False
			self.requests.pop(request_id)



	def handle_accept_request(self, data):
		newData = self.parse_request(data)
		available, request_id = self.verify_request_id(newData)
		if available:
			user = self.requests[request_id]
			type = user.get("type")
			result = None
			if type == "borrow":
				days = newData.get("num_days")
				result = self.book_borrow_query.insert_book_borrow(user.get("book"), user.get("user"), days)
			elif type == "return":
				result = self.book_borrow_query.delete_book_borrow_by_id(user.get("book"), user.get("user"))
			if result.get("success") is False:
				self.socketio.emit('request_denied', "Something went wrong", room=request_id, namespace='/')
				user = self.requests[request_id]
				self.available_clients[user.get("receiver_id")]["busy"] = False
				self.requests.pop(request_id)
				print("Something went wrong")
				return
			self.socketio.emit('request_accepted', "Request accepted", room=request_id, namespace='/')
			user = self.requests[request_id]
			self.available_clients[user.get("receiver_id")]["busy"] = False
			self.requests.pop(request_id)
			print("Request accepted")

	def handle_review_request(self, data):
		newData = self.parse_request(data)
		available, request_id = self.verify_request_id(newData)
		if available:
			print("Request is being reviewed")
			self.requests[request_id]["accepted"] = True
			
	def handle_request(self, data):
		newData = self.parse_request(data)
		if newData is None:
			return
		# * check if request is ongoing
		if self.is_request_ongoing(request.sid): return

		book_id = [newData.get('book_id'),]
		user_id = [newData.get('user_id'),]
		request_book = self.book_manager.book_queries.get_books_by_id(book_id)
		if len(request_book) == 0: 
			self.socketio.emit('request_denied', "Book not found", room=request.sid, namespace='/')
			return
		request_book = request_book[0]
		request_user = self.user_manager.user_queries.get_users_by_id(user_id)
		if len(request_user) == 0: 
			self.socketio.emit('request_denied', "User not found", room=request.sid, namespace='/')
			return
		request_user = request_user[0]
		book = {
			"id": request_book.get('id'),
			"title": request_book.get('title'),
			"author": request_book.get('author'),
			"publisher": request_book.get('publisher'),
			"access_number": request_book.get('access_number'),
			"call_number": request_book.get('call_number'),
			"cover_image": request_book.get('cover_image'),
		}
		user = {
			"id": request_user.get('id'),
			"profile_pic": request_user.get('profile_pic'),
			"first_name": request_user.get('first_name'),
			"last_name": request_user.get('last_name'),
			"email": request_user.get('email'),
			"school_id": request_user.get('school_id'),
			"role_id": request_user.get('role_id'),
		}
		current_request = {
			"request_id": request.sid,
			"receiver_id": newData.get('receiver_id'),
			"type": newData.get('type'),
			"accepted": False,
			"book": book,
			"user": user
		}
		self.requests[request.sid] = current_request
		if not self.is_borrower_verified(current_request): return
		socket_id = current_request.get('receiver_id')
		if self.is_client_available(socket_id):
			self.send_client_request(socket_id, request.sid, current_request)
		else:
			print(f"Client not found: {current_request['receiver_id']}")
	
	def is_request_ongoing(self, request_id) -> bool:
		if self.requests.get(request_id) is not None:
			self.socketio.emit(
				'request_denied', 
				{"error": "Request already sent"}, 
				room=request_id, 
				namespace='/'
			)
			return True
		return False

	def is_borrower_verified(self, request) -> bool:
		if request['user'].get("is_verified") is False:
			self.socketio.emit('request_denied', {"error": "User not verified"}, room=request.sid, namespace='/')
			self.requests.pop(request.sid)
			return False
		return True
		
	def is_client_available(self, client_id) -> bool:
		if self.available_clients.get(client_id) is None:
			self.socketio.emit(
				'request_denied',{"error": "Client not found"}, 
				room=request.sid, 
				namespace='/'
			)
			self.requests.pop(request.sid)
			return False
		if  self.available_clients.get(client_id).get("busy") is True:
			self.socketio.emit(
				'request_denied',{"error": "Client is busy"}, 
				room=request.sid, 
				namespace='/'
			)
			self.requests.pop(request.sid)
			return False
		return True

	def send_client_request(self, client_id, requester_id, data):
		self.available_clients[client_id]["busy"] = True
		self.socketio.emit('request_borrow', data, room=client_id, namespace='/')
		gevent.spawn(self.timeout_thread, requester_id)
		print(f"Request sent to client: {client_id} (Request ID: {requester_id})")

	def timeout_thread(self, request_id):
		current_time = 0
		while current_time < 5:
			if self.requests.get(request_id) is None:
				break
			if self.requests.get(request_id).get("accepted") is True:
				break
			time.sleep(1)
			current_time += 1
			print(f"Current time for request {request_id}: {current_time}")
			print(f"Request status: {self.requests.get(request_id).get('accepted')}")
		if self.requests.get(request_id).get("accepted") is False:
			self.socketio.emit('request_timeout', {"error": "Request timed out"}, room=request_id, namespace='/')
			client_id = self.requests.get(request_id).get("receiver_id")
			self.available_clients[client_id]["busy"] = False
			self.requests.pop(request_id)
			return
		print(f"Request is being reviewed by client: {self.requests.get(request_id).get('receiver_id')} (Request ID: {request_id})")

	def get_available_clients(self):
		return self.available_clients



if __name__ == "__main__":
	server = MainServer()
	server.socketio.run(app, host='0.0.0.0', port=5000 , debug=True)
