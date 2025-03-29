from itertools import zip_longest
from quart import Quart, send_from_directory
# import quart
from hypercorn.asyncio import serve
from hypercorn.config import Config
from socketio import AsyncServer, ASGIApp
import asyncio
from quart_cors import cors
from tabulate import tabulate
# from Components.config import *
# from Components.config import
from Components.db import Database
# ? Books
from Components.managers.book_borrow import BookBorrowManager
from Components.managers.catalog import CatalogManager
from Components.managers.copy import CopyManager
# ? User
from Components.managers.roles import RoleManager
from Components.managers.user import UserManager
# ? Category
from Components.managers.categories import CategoryManager
from Components.managers.book_categories import BookCategoryManager
# ? Records
from Components.managers.records import RecordManager

import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ? App
app = Quart(__name__, static_folder="./storage")
cors(app)

# ? Use ASGI-compatible server
sio = AsyncServer(async_mode='asgi', cors_allowed_origins="*")
app.asgi_app = ASGIApp(sio, app.asgi_app)


class MainServer:

	def __init__(self):
		os.system('cls' if os.name == 'nt' else 'clear')
		logging.info("Initializing server...")
		self.app = app
		self.socketio = sio
		self.db = Database(app, self)

		# ? category
		self.category_manager = CategoryManager(self.app, self.db)
		self.book_category_manager = BookCategoryManager(self.app, self.db)
		# ? books
		self.catalog = CatalogManager(self.app, self.db,
		                              self.book_category_manager,
		                              self.category_manager)
		self.copy = CopyManager(self.app, self.db)
		# ? user
		self.role_manager = RoleManager(self.app, self.db)
		self.user_manager = UserManager(self.app,self.db)
		# ? > roles first for the role id
		# ? records
		self.book_borrow_manager = BookBorrowManager(self.socketio, self.db, self.app)
		self.book_borrow_manager.set_queries(self.copy, self.user_manager)
		self.record_manager = RecordManager(self.app)
		self.record_manager.set_queries(self.copy, self.book_borrow_manager,
		                                self.book_category_manager,
		                                self.user_manager)
		# ? register routes
		self.socketio.on('connect', self.handle_connect)
		self.socketio.on('disconnect', self.handle_disconnect)
		self.socketio.on('mount_connection', self.mount_connection)
		self.app.add_url_rule('/clients', view_func=self.get_available_clients, methods=["GET"])

	async def populate_tables(self):
		await self.role_manager.role_queries.populate_roles()
		await self.user_manager.user_queries.populate_users()

	@app.before_serving
	async def before_serving():
		logging.info("Starting the server...")


	@app.route("/test_connection", methods=["GET"])
	async def test():
		return "Server is running as expected"

	@app.route('/<path:filename>')
	async def get_file(filename):

		if not os.path.exists(app.static_folder or "./storage"):
			logging.error("Static folder not found")
			return "Static folder not found"
		logging.info(f"Requested file: {filename}")
		return await send_from_directory(app.static_folder or "./sotorage", filename)

	async def get_available_clients(self):
		return {
		    "success": True,
		    "message": "Clients Fetched",
		    "data": self.book_borrow_manager.available_clients
		}

	""" CONNECTION HANDLERS """

	async def handle_connect(self, sid, environ):
		self.book_borrow_manager.unauthenticated_connections.add(sid)
		await self.show_connections()

	async def mount_connection(self, sid, data):
		data = await self.book_borrow_manager.parse_request(data)
		self.book_borrow_manager.unauthenticated_connections.discard(sid)
		data["busy"] = False
		self.book_borrow_manager.available_clients[sid] = data
		await self.show_connections()

	async def show_connections(self):
		os.system('cls' if os.name == 'nt' else 'clear')
		clients = [
		    client_id
		    for client_id in self.book_borrow_manager.available_clients.keys()
		]
		other_connections = self.book_borrow_manager.unauthenticated_connections
		table_data = list(zip_longest(clients, other_connections, fillvalue=""))
		print(
		    tabulate(table_data,
		             headers=["Available Clients", "Other Connections"],
		             tablefmt="psql"))

	async def unmount_connection(self, sid):
		self.book_borrow_manager.available_clients.pop(sid, None)
		self.book_borrow_manager.unauthenticated_connections.discard(sid)
		await self.show_connections()

	async def handle_disconnect(self, sid):
		self.book_borrow_manager.available_clients.pop(sid, None)
		self.book_borrow_manager.unauthenticated_connections.discard(sid)
		await self.show_connections()

async def main():
	server = MainServer()
	await server.db.init_db()
	await server.populate_tables()

	config = Config()
	config.bind = ["0.0.0.0:5000"]

	await serve(server.app, config=config)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nServer shutdown requested.")
	# asyncio.run(main())
