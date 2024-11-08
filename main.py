from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from Components.DBManager import DBManager, DBRequestsHandler

app = Flask(__name__)
CORS(app)

class MainServer:
	def __init__(self):

		self.backup_delay = 24 * 60 * 60 # 24 hours

		#@@@@@@@@@@@[Dont edit past this line]@@@@@@@@@@@@@@@@@

		self.handler = DBManager()
		self.requester = DBRequestsHandler()

		#start backup thread
		threading.Thread(target=self.backup_thread, daemon=True).start()

		#routes
		app.add_url_rule('/insert_books', view_func=self.add_books, methods=['POST'])
		app.add_url_rule('/select_books', view_func=self.get_books, methods=['GET'])

	def backup_thread(self):
		while True:
			time.sleep(self.backup_delay)
			print("Backing up database...")
			self.handler.backup_database()
			print("Database backup completed")

	def add_books(self):
		data = request.get_json()
		books = data.get('books',[])
		return self.requester.insert_books(books)

	def get_books(self):
		page_number = request.args.get('page', default=0, type=int)
		print("page number: ", page_number)
		return jsonify(self.requester.select_books(page_number)), 200

if __name__ == "__main__":
	server = MainServer()
	server.handler.create_db_if_not_exists()
	server.handler.create_books_table()
	app.run(host="0.0.0.0", port=5000)
