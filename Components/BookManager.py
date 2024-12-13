from flask import  request, jsonify
from .DatabaseHandlers.CrudHandler import CrudHandler
from .DatabaseHandlers.BookDataParser import BookDataParser
from .DatabaseQueries import BOOK_HANDLER_QUERIES, RECORD_QUERIES
from .QRManager import QRManager

class BookManager:
    def __init__(self):
        self.book = BookDataParser()
        self.crud = CrudHandler()
        self.qr = QRManager()
        self.page_size = 15

    def get_books(self):
        data = request.get_json()
        starting_index = data["page"] * self.page_size
        search_filter, search_params = BookDataParser.build_search_filter(self, data["filter"], data["search"])
        query = BOOK_HANDLER_QUERIES.SELECT_BOOKS.format(search_filter=search_filter)
        params = search_params + [self.page_size, starting_index]
        count = self.crud.execute_query(BOOK_HANDLER_QUERIES.COUNT_BOOKS.format(search_filter=search_filter), search_params, fetch=True)
        page_count = 0
        if count["success"]:
            page_count = count["data"][0][0] // self.page_size
        return {"books": self.crud.execute_query(query, params, fetch=True)["data"], "page_count": page_count}

    def insert_books(self):
        data = request.get_json()
        for book in data["books"]:

            qr_code_path = self.qr.generate_qr_code((f"{book['access_number']}_{book['call_number']}"))
            book['qr_code_path'] =  qr_code_path

        books = self.book.parse_book_insertion_data(data["books"])
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.INSERT_BOOK, books)
        return result
    
    def update_books(self):
        data = request.get_json()
        books = self.book.parse_book_update_data(data["books"])
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.UPDATE_BOOK_STATUS, books)
        return result
    
    def delete_books(self):
        data = request.get_json()
        book_ids = data["book_ids"]
        if not book_ids:
            return {"success": False, "message": "No book ids provided."}
        placeholders = ",".join(["?"] * len(book_ids))
        qr_query = BOOK_HANDLER_QUERIES.SELECT_QR_CODE_NAME.format(placeholders=placeholders)
        qr_names = self.crud.execute_query(qr_query, tuple(book_ids), fetch=True)

        if qr_names["success"] and qr_names["data"]:
            for qr_name in qr_names["data"]:
                if qr_name[0]:
                    self.qr.delete_qr_code(qr_name[0])
        delete_query = BOOK_HANDLER_QUERIES.DELETE_BOOK.format(placeholders=placeholders)
        print(delete_query)
        print(tuple(book_ids))
        result = self.crud.execute_query(delete_query, tuple(book_ids))
        return result
    
    def add_cateories(self):
        data = request.get_json()
        categories = [(data,) for data in data["categories"]]
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.INSERT_CATEGORY, categories)
        return result
    
    def get_categories(self):
        return self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_CATEGORIES, fetch=True)
    
    def update_categories(self):
        data = request.get_json()
        categories = [(data["category"], data["category_id"]) for data in data["categories"]]
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.UPDATE_CATEGORIES, categories)
        return result
    
    def delete_categories(self):
        data = request.get_json()
        category_ids = [(data,) for data in data["category_ids"]]
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.DELETE_CATEGORY, category_ids)
        return result
    
    def add_joint_categories(self):
        data = request.get_json()
        joint_categories = [(data[0],data[1]) for data in data["joint_categories"]]
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.INSERT_JOINT_CATEGORY, joint_categories)
        return result
    
    def remove_joint_categories(self):
        data = request.get_json()
        joint_category_ids = [(data[0],data[1]) for data in data["joint_category_ids"]]
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.DELETE_JOINT_CATEGORY, joint_category_ids)
        return result
    
    def get_joint_categories(self):
        data = request.get_json()
        book_id = (data["book_id"],)
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_JOINT_CATEGORY, book_id, fetch=True)
        return result
    
    def request_books(self):
        data = request.get_json()
        book_ids = data["book_info"]
        if not book_ids:
            return {"success": False, "message": "No book ids provided."}
        book_ids = book_ids.split("_")
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.REQUEST_BOOK, tuple(book_ids), fetch=True)
        return result
    
    def get_book_by_id(self, book_id):
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_BOOK_BY_ID, (book_id,), fetch=True)
        return result
    
    def accept_request(self):
        data = request.get_json()
        book_id = data["book_id"]
        username = data["username"]

        days = data["days"]

        book = self.get_book_by_id(book_id)["data"][0]
        book = (
            book[1],
            book[2],
            book[3],
            book[4],
            book[5],
            'borrowed',
            book[0]
        )
        update = self.crud.execute_query(BOOK_HANDLER_QUERIES.UPDATE_BOOK_STATUS, book)
        insert = self.crud.execute_query(BOOK_HANDLER_QUERIES.INSERT_BORROWED_BOOK, (book_id, username, days))
        return {"success": update["success"] and insert["success"], "message": update["message"] + " " + insert["message"]}
    
    def get_records_book_copies(self):
        return self.crud.execute_query(RECORD_QUERIES.SELECT_COPIES_AVAILABLE, fetch=True)
    
    def get_records_borrowed_books(self):
        return self.crud.execute_query(RECORD_QUERIES.SELECT_BORROWED_RECORDS, fetch=True)
    
    def get_records_user(self):
        return self.crud.execute_query(RECORD_QUERIES.SELECT_USER_RECORDS, fetch=True)
    
    def get_records_category(self):
        return self.crud.execute_query(RECORD_QUERIES.SELECT_CATEGORY_RECORDS, fetch=True)
    