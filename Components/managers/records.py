from quart import Quart, request

from Components.queries.book_borrow import BorrowedBookQueries
from Components.queries.book_categories import BookCategoryQueries
from Components.queries.categories import CategoryQueries
from Components.queries.copy import CopyQueries
from Components.queries.roles import RoleQueries
from Components.queries.user import UserQueries


class RecordManager: 
    def __init__(self, app: Quart): 
        self.copy : CopyQueries = None
        self.book_borrow : BorrowedBookQueries = None
        self.book_category : BookCategoryQueries = None
        self.user : UserQueries = None
        self.register_routes(app)
        pass
    
    def set_queries(self, copy_manager, book_borrow_manager, book_category_manager, user_manager): 
        self.copy = copy_manager.copy
        self.book_borrow = book_borrow_manager.book_borrow
        self.book_category = book_category_manager.book_category_queries
        self.user = user_manager.user_queries   

    def register_routes(self, app: Quart): 
        @app.route("/record/paged_books:count", methods=["POST"])
        async def get_book_count():
            data = await request.get_json()
            print(data)
            result = await self.copy.paged_count(data)
            return result
            
        @app.route("/record/paged_borrowings", methods=["POST"])
        async def get_borrowings():
            data = await request.get_json()
            result = await self.book_borrow.paged_borrowings(data)
            return result

        @app.route("/record/paged_book_categories:count", methods=["POST"])    
        async def get_book_categories():
            data = await request.get_json()
            result = await self.book_category.paged_book_categories(data)
            return result