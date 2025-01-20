from flask import Flask, request

from Components.queries.book_borrow import BorrowedBookQueries
from Components.queries.book_categories import BookCategoryQueries
from Components.queries.books import BookQueries
from Components.queries.categories import CategoryQueries
from Components.queries.roles import RoleQueries
from Components.queries.user import UserQueries


class RecordManager: 
    def __init__(self, app: Flask): 
        self.register_routes(app)
        self.role : RoleQueries = None
        self.user : UserQueries = None
        self.category : CategoryQueries = None
        self.book : BookQueries = None
        self.book_category : BookCategoryQueries = None
        self.book_borrow : BorrowedBookQueries = None
    

    def register_routes(self, app: Flask): 
        @app.route("/records/get_book_count", methods=["POST"])
        def get_book_count():
            data = request.get_json()
            if data is None:
                return { "success": False, "data": None }
            result = self.book.get_books_count(
                data.get("page", 0),
                data.get("per_page", 15),
                data.get("filters", None),
                data.get("order_by", "id"),
                data.get("order_direction", "asc")
            )
            return { "success": True, "data": result }
            
        @app.route("/records/borrowings", methods=["POST"])
        def get_borrowings():
            data = request.get_json()
            if data is None:
                return { "success": False, "data": None }
            result = self.book_borrow.get_borrowed_books(
                data.get("page", 0),
                data.get("per_page", 15),
                data.get("filters", None),
                data.get("order_by", "id"),
                data.get("order_direction", "asc")
            )
            return { "success": True, "data": result }

    