from quart import Quart , request
from ..db import Database
from ..queries.book_categories import BookCategoryQueries
class BookCategoryManager:
    def __init__(self, app: Quart, db : Database):
        self.book_category_queries = BookCategoryQueries(db.Session)
        self.register_routes(app)

    def register_routes(self, app: Quart):
        
        @app.route("/book_categories/insert", methods=["POST"])
        def insert_multiple_book_categories():
            book_categories = request.get_json()
            result = self.book_category_queries.insert_multiple_book_categories(book_categories)
            return { "success": True, "data": result }
        
        @app.route("/book_categories/get_by_id", methods=["POST"])
        def get_book_categories_by_id():
            data = request.get_json()
            result = self.book_category_queries.get_book_categories_by_id(data)
            return { "success": True, "data": result }
        
        @app.route("/book_categories/update", methods=["POST"])
        def update_book_categories():
            data = request.get_json()
            result = self.book_category_queries.update_book_categories(data)
            return { "success": True, "data": result }
        
        @app.route("/book_categories/delete", methods=["POST"])
        def delete_book_categories_by_id():
            data = request.get_json()
            result = self.book_category_queries.delete_book_categories_by_id(data)
            return { "success": True, "data": result }
        

