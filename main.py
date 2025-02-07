from quart import Quart, json, send_from_directory, request
# import quart
import hypercorn.asyncio
from hypercorn.config import Config
import socketio
import asyncio
from quart_cors import cors
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
import weakref


# ? App
app = Quart(__name__, static_folder="./storage")
cors(app)

# ? Use ASGI-compatible server
sio = socketio.AsyncServer( async_mode='asgi', cors_allowed_origins="*")
app.asgi_app = socketio.ASGIApp(sio, app.asgi_app) 

class MainServer:
	def __init__(self):
		os.system('cls' if os.name == 'nt' else 'clear')
		print("Initializing server...")
		self.app = app
		self.socketio = sio
		self.db = Database()
	
		# Database Managers
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
		# ? websocket events
		# ? ==============
		self.socketio.on('connect', self.handle_connect)
		self.socketio.on('disconnect', self.handle_disconnect)
		self.socketio.on('client_connect', self.handle_client_connect)
		self.socketio.on('request', self.handle_request)
		self.socketio.on('review_request', self.handle_review_request)
		self.socketio.on('accept_request', self.handle_accept_request)
		self.socketio.on('deny_request', self.handle_deny_request)

	# ? ===============
	# ? private methods 
	# ? ===============
	@app.before_serving
	async def before_serving():
		print("Starting the server...")

	@app.route("/test_connection", methods=["GET"])
	async def test():
		return "Server is running as expected"

	@app.route('/<path:filename>')
	async def get_file(filename):
		print(f"Requested file: {filename}")
		return await send_from_directory(app.static_folder, filename)

	def parse_request(self, data):
		if isinstance(data, str):
			return json.loads(data)
		return data

	def handle_connect(self):
		print(f"Incoming connection from: {request.sid}")

	def handle_client_connect(self, data):
		newData = self.parse_request(data)
		print("Client data received")
		newData["busy"] = False
		self.available_clients[request.sid] = newData
	
	def handle_disconnect(self):
		client_id = self.available_clients.pop(request.sid, None)
		print(f"Client disconnected: {request.sid} (Name: {client_id.get('first_name')} {client_id.get('last_name')})")

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
			try:
				if type == "borrow":
					days = newData.get("num_days")
					result = self.book_borrow_query.insert_book_borrow(user.get("book"), user.get("user"), days)
				elif type == "return":
					result = self.book_borrow_query.delete_book_borrow_by_id(user.get("book"), user.get("user"))
				if result.get("success") is False:
					raise Exception(result.get("message"))
				self.socketio.emit('request_accepted', "Request accepted", room=request_id, namespace='/')
				self.available_clients[user.get("receiver_id")]["busy"] = False
				self.requests.pop(request_id)
				print("Request accepted")
			except Exception as e:
				self.socketio.emit('request_denied', str(e), room=request_id, namespace='/')
				user = self.requests[request_id]
				self.available_clients[user.get("receiver_id")]["busy"] = False
				self.requests.pop(request_id)
				print("Something went wrong")

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
		asyncio.create_task(self.timeout_thread(requester_id))
		print(f"Request sent to client: {client_id} (Request ID: {requester_id})")

	def timeout_thread(self, request_id):
		try:
			timeout = 10
			current_time = 0
			is_accepted = False
			while current_time < timeout:
				if self.requests.get(request_id) is None:
					raise Exception("Request not found")
				if self.requests.get(request_id).get("accepted") is True:
					if is_accepted is False:
						is_accepted = True
						timeout = 30
						current_time = 0
				time.sleep(1)
				current_time += 1
				print(f"Current time for request {request_id}: {current_time}")
			if self.requests.get(request_id).get("accepted") is False:
				raise Exception("Request timed out")
		except Exception as e:
			try:
				self.available_clients[client_id]["busy"] = False
			except Exception as e:
				print(e)
			client_id = self.requests.get(request_id)
			if client_id is None: return
			self.socketio.emit('request_timeout', {"error": str(e)}, room=request_id, namespace='/')
			client_id = client_id.get("receiver_id")
			self.requests.pop(request_id)

	def get_available_clients(self):
		return self.available_clients

# if __name__ == "__main__":
async def main():
	server = MainServer()
	await server.user_manager.user_queries.populate_user()
	await server.role_manager.role_queries.populate_roles()
	cofig = Config()
	Config.bind = ["0.0.0.0:5000"]
	# asyncio.run(hypercorn.asyncio.serve(server.app, config=cofig))
	await hypercorn.asyncio.serve(server.app, config=cofig)

asyncio.run(main())
