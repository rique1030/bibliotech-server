from flask import  request
from .DatabaseHandlers.CrudHandler import CrudHandler
from .DatabaseHandlers.BookDataParser import BookDataParser
from .DatabaseQueries import BOOK_HANDLER_QUERIES, RECORD_QUERIES
from .QRManager import QRManager
from json import dumps

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
        result = self.crud.execute_query(query, params, fetch=True)
        return result

    def insert_books(self):
        data = request.get_json()
        self.debug_print(data, "insert_books")
        books = data["book"]["books"]
        new_books = []
        categories = data["book"]["categories"]
        new_categories = []
        for  index, book in enumerate(books):
            if book[0] == None or book[0] == "":
                continue
            qr_code = f"{book[0]}_{book[1]}.png"
            new_books.append((book[0], book[1], book[2], book[3], qr_code))
            new_categories.append(categories[index])
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.INSERT_BOOK, new_books)
        if result["success"] == False:
            return result
        if result["rows_affected"] > 0:
            for book in new_books:
                print("qrcode book", book)
                self.qr.generate_qr_code(book[4])
            if result["lastrowid"]:
                ids = [result["lastrowid"] + i for i in range(result["rows_affected"])]
                if len(ids) == len(new_categories):
                    category_join = []
                    for index, category in enumerate(new_categories):
                        for cat in category:
                            category_join.append((ids[index], cat))
                        
                    print("category_join", category_join)
                    cat_result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.INSERT_JOINT_CATEGORY, category_join)
                    print("cat_result", cat_result)
                else:
                    result = { "success": False, "message": "Insert success but something went wrong when adding categories." }
        return result
    
    def update_books(self):
        data = request.get_json()
        self.debug_print(data, "update_books")
        old_qr = []
        for book in data["book"]["books"]:
            old_qr.append(book[5])
        books = self.book.parse_book_update_data(data["book"]["books"])
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.UPDATE_BOOK_STATUS, books)
        self.debug_print(result, "update_books")
        if result["success"]:
            if result["rows_affected"] > 0:
                for qr in old_qr:
                    self.qr.delete_qr_code(qr)
                for book in books:
                    self.qr.generate_qr_code(book[4])

        book_categories = []
        book_ids = [book[6] for book in books]
        placeholders = ",".join(["%s"] * len(data))    
        delete = self.crud.execute_query(BOOK_HANDLER_QUERIES.DELETE_JOINT_CATEGORY_BY_BOOK_ID.format(placeholders=placeholders), book_ids)
        self.debug_print(delete, "update_books")
        for book, category in zip(books, data["book"]["categories"]):
            book_id = book[6]
            for cat in category:
                book_categories.append((book_id, cat))
        result2 = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.INSERT_JOINT_CATEGORY, book_categories)

        self.debug_print(result2, "update_books")
        if result["success"] == False and result2["success"] == True:
            result = result2
        return result
    
    def delete_books(self):
        data = request.get_json()
        if len (data) < 1:
            return { "success": True, "data": [] }
        
        placeholders = ",".join(["%s"] * len(data))        
        books = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_BOOK_BY_ID.format(placeholders=placeholders), data, fetch=True)
        self.debug_print(books, "delete_books")
        QR = [ book[5] for book in books["data"] ]
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.DELETE_BOOK.format(placeholders=placeholders), data)
        self.debug_print(result, "delete_books")
        if result["rows_affected"] > 0:
            for qr in QR:
                self.qr.delete_qr_code(qr)
        return result
    
    def insert_categories(self):
        data = request.get_json()
        self.debug_print(data, "insert_categories")
        categories = data["category"]
        if len(data) < 1:
            return { "success": True, "data": [] }
        categories = [(data[0],) for data in categories if data[0] != None and data[0] != ""]
        print("categories", categories)
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.INSERT_CATEGORY, categories)
        return result
    
    def get_categories(self):
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_CATEGORIES, fetch=True)
        return result
    
    def get_category_by_id(self):
        data = request.get_json()
        self.debug_print(data, "get_category_by_id")
        if len(data) < 1:
            return { "success": True, "data": [] }
        placeholders = ",".join(["%s"] * len(data))
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_CATEGORY_BY_ID.format(placeholders=placeholders), data, fetch=True)
        return result
    
    def fetch_categories(self):
        data = request.get_json()
        starting_index = data["page"] * self.page_size
        search_filter, search_params = BookDataParser.build_search_filter(self, data["filter"], data["search"])
        query = BOOK_HANDLER_QUERIES.FETCH_CATEGORIES.format(search_filter=search_filter)
        params = search_params + [self.page_size, starting_index]    
        result = self.crud.execute_query(query, params, fetch=True)
        return result


    def update_categories(self):
        data = request.get_json()
        self.debug_print(data, "update_categories")
        categories = [(data[1],data[0]) for data in data["category"]]
        result = self.crud.execyte_multiple_query(BOOK_HANDLER_QUERIES.UPDATE_CATEGORIES, categories)
        return result
    
    def delete_categories(self):
        data = request.get_json()
        self.debug_print(data, "delete_categories")
        if len(data) < 1:
            return { "success": True, "data": [] }
        placeholders = ",".join(["%s"] * len(data))
        query= BOOK_HANDLER_QUERIES.DELETE_CATEGORY.format(placeholders=placeholders)
        result = self.crud.execute_query(query, data)
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
        self.debug_print(data, "get_joint_categories")
        if len(data) < 1:
            return { "success": True, "data": [] }
        placeholders = ",".join(["%s"] * len(data))
        query = BOOK_HANDLER_QUERIES.SELECT_JOINT_CATEGORY_BY_ID.format(placeholders=placeholders)
        result = self.crud.execute_query(query, data, fetch=True)
        if result["success"] and len(result["data"]) > 0:
            print("result", result)
            result_dict = {id_: [] for id_ in data}            
            for category_id, book_id in result["data"]:
                result_dict[category_id].append(book_id)
                result = { "success": True, "data": list(result_dict.values()) }
        return result
    
    def request_books(self):
        data = request.get_json()
        book_ids = data["book_info"]
        if not book_ids:
            return {"success": False, "message": "No book ids provided."}
        book_ids = book_ids[:-4]
        book_ids = book_ids.split("_")
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.REQUEST_BOOK, tuple(book_ids), fetch=True)
        return result
        
    def get_book_by_id(self):
        data = request.get_json()
        self.debug_print(data, "get_book_by_id")
        if len(data) < 1:
            return { "success": True, "data": [] }
        placeholders = ",".join(["%s"] * len(data))
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_BOOK_BY_ID.format(placeholders=placeholders), data, fetch=True)
        return result
    
    def get_book_by_id_for_borrow(self, book_id):
        placeholders = ",".join(["%s"] * len([book_id]))
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_BOOK_BY_ID.format(placeholders=placeholders), [book_id], fetch=True)
        print("result", result)
        return result
    
    def accept_request(self):
        data = request.get_json()
        book_id = data["book_id"]
        print("book_id", book_id)
        username = data["username"]
        print("username", username)
        days = data["days"]
        print("days", days)

        book = self.get_book_by_id_for_borrow(book_id)["data"][0]
        print("book", book)
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
        data = request.get_json()
        starting_index = data["page"] * self.page_size
        search_filter, search_params = BookDataParser.build_search_filter(self, data["filter"], data["search"])
        query = RECORD_QUERIES.SELECT_COPIES_AVAILABLE.format(search_filter=search_filter)
        params = search_params + [self.page_size, starting_index]
        result = self.crud.execute_query(query, params, fetch=True)
        return result
    
    def get_records_borrowed_books(self):
        data = request.get_json()
        starting_index = data["page"] * self.page_size
        search_filter, search_params = BookDataParser.build_search_filter(self, data["filter"], data["search"])
        query = RECORD_QUERIES.SELECT_BORROWED_RECORDS.format(search_filter=search_filter)
        params = search_params + [self.page_size, starting_index]
        result = self.crud.execute_query(query, params, fetch=True)
        return result
    
    def get_records_user(self):
        data = request.get_json()
        starting_index = data["page"] * self.page_size
        search_filter, search_params = BookDataParser.build_search_filter(self, data["filter"], data["search"])
        query = RECORD_QUERIES.SELECT_USER_RECORDS.format(search_filter=search_filter)
        params = search_params + [self.page_size, starting_index]
        result = self.crud.execute_query(query, params, fetch=True)
        return result
    
    def get_records_category(self):
        data = request.get_json()
        starting_index = data["page"] * self.page_size
        search_filter, search_params = BookDataParser.build_search_filter(self, data["filter"], data["search"])
        query = RECORD_QUERIES.SELECT_CATEGORY_RECORDS.format(search_filter=search_filter)
        params = (self.page_size, starting_index)
        print("params", params)
        result = self.crud.execute_query(query, params, fetch=True)
        return result

    def fetch_borrow(self):
        data = request.get_json()
        self.debug_print(data, "fetch_borrow")
        username = data["username"]
        result = self.crud.execute_query(BOOK_HANDLER_QUERIES.SELECT_BORROWED_BOOKS_BY_USERNAME, (username,), fetch=True)   
        return result     

    def debug_print(self, data , function_name):
        print("+=================================")
        print(f"| Function: {function_name}")
        print(f"| Data: {dumps(data)}")
        print("+=================================")

