from itertools import zip_longest
import signal
import sys
from quart import Quart, send_from_directory, request
# import quart
from hypercorn.asyncio import serve
from hypercorn.config import Config
import socketio
import asyncio
from quart_cors import cors
from tabulate import tabulate
from Components.config import *
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ? App
app = Quart(__name__, static_folder="./storage")
cors(app)

# ? Use ASGI-compatible server
sio = socketio.AsyncServer( async_mode='asgi', cors_allowed_origins="*")
app.asgi_app = socketio.ASGIApp(sio, app.asgi_app) 

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
		self.catalog = CatalogManager(self.app, self.db, self.book_category_manager, self.category_manager)
		self.copy = CopyManager(self.app, self.db)
		# ? user
		self.role_manager = RoleManager(self.app, self.db)
		self.user_manager = UserManager(self.app, self.db) # ? > roles first for the role id
		# ? records
		self.book_borrow_manager = BookBorrowManager(self.socketio, self.db)
		self.book_borrow_manager.set_queries(self.copy, self.user_manager)
		self.record_manager = RecordManager(self.app)
		self.record_manager.set_queries(self.copy, self.book_borrow_manager, self.book_category_manager,self.user_manager)
		# ? register routes
		self.socketio.on('connect', self.handle_connect)
		self.socketio.on('disconnect', self.handle_disconnect)
		self.socketio.on('mount_connection', self.mount_connection)
		# self.socketio.on("*", self.catch_all)
		self.app.add_url_rule('/clients', view_func=self.get_available_clients, methods=["GET"])
	
	# @sio.on("*")
	# async def catch_all(event, sid, data=None):
	# 	logging.info(f"Event: {event}")
	# 	logging.info(f"Data: {data}")
	# 	logging.info(f"SID: {sid}")


	async def populate_tables(self):
		await self.role_manager.role_queries.populate_roles()
		await self.user_manager.user_queries.populate_users()
		
	@app.before_serving
	async def before_serving():
		logging.info("Starting the server...")

	@app.after_request
	async def add_ngrok_header(response):
		response.headers['ngrok-skip-browser-warning'] = 'skip-browser-warning'
		return response


	# @app.before_request
	# async def before_request():
	# 	logging.info(f"\nIncoming request...")
	# 	logging.info(request.url)

	@app.route("/test_connection", methods=["GET"])
	async def test():
		return "Server is running as expected"

	@app.route('/<path:filename>')
	async def get_file(filename):
		logging.info(f"Requested file: {filename}")
		return await send_from_directory(app.static_folder, filename)

	async def get_available_clients(self):
		return self.book_borrow_manager.available_clients

	""" CONNECTION HANDLERS """

	async def handle_connect(self, sid, environ):
		self.book_borrow_manager.unauthenticated_connections.add(sid)
		await self.show_connections()
		return
		logging.info(f"Incoming Unauthenticated Connection with ID: {sid}")

	async def mount_connection(self, sid, data):
		data = await self.book_borrow_manager.parse_request(data)
		self.book_borrow_manager.unauthenticated_connections.discard(sid)
		# logging.info(f"Client Authenticated: {sid} (Name: {data.get('first_name')} {data.get('last_name')})")
		data["busy"] = False
		self.book_borrow_manager.available_clients[sid] = data
		await self.show_connections()
		# logging.info(f"\nAvailable clients:")
		# self.book_borrow_manager.print_json({
		# 	client_id: "online" for client_id in self.book_borrow_manager.available_clients
		# })

	async def show_connections(self):
		os.system('cls' if os.name == 'nt' else 'clear')
		clients = [client_id for client_id in self.book_borrow_manager.available_clients.keys()]
		other_connections = self.book_borrow_manager.unauthenticated_connections
		table_data = list(zip_longest(clients, other_connections, fillvalue=""))
		print(tabulate(table_data, headers=["Available Clients", "Other Connections"], tablefmt="psql"))
	
	async def unmount_connection(self, sid):
		client_id = self.book_borrow_manager.available_clients.pop(sid, None)
		self.book_borrow_manager.unauthenticated_connections.discard(sid)
		await self.show_connections()
		return
		if client_id is None:
			logging.info(f"Unauthenticated Client disconnected: {sid}")
			return
		logging.info(f"Client disconnected: {sid} (Name: {client_id.get('first_name')} {client_id.get('last_name')})")

	async def handle_disconnect(self, sid):
		client_id = self.book_borrow_manager.available_clients.pop(sid, None)
		self.book_borrow_manager.unauthenticated_connections.discard(sid)
		await self.show_connections()
		return
		if client_id is None:
			logging.info(f"Unauthenticated Client disconnected: {sid}")
			return
		logging.info(f"Client disconnected: {sid} (Name: {client_id.get('first_name')} {client_id.get('last_name')})")

async def main():
    server = MainServer()
    await server.db.init_db()
    await server.populate_tables()

    config = Config()
    config.bind = ["0.0.0.0:5000"]

    # Run Hypercorn in the background
    server_task = asyncio.create_task(serve(server.app, config=config))

    stop_event = asyncio.Event()

    async def shutdown():
        logging.info("Stopping server...")
        stop_event.set()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        # Ensure database connections are properly closed
        # await server.db.close()

    if sys.platform != "win32":  # Signal handling only for non-Windows
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))
    else:
        # Windows: Use a separate task to listen for keyboard interrupt
        async def windows_shutdown_handler():
            try:
                await asyncio.get_running_loop().run_in_executor(None, input, "\nPress Enter to stop...")
            except Exception:
                pass
            await shutdown()

        asyncio.create_task(windows_shutdown_handler())

    await stop_event.wait()




if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nServer shutdown requested.")
	# asyncio.run(main())

