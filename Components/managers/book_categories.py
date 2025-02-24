from quart import Quart , request
from ..db import Database
from ..queries.book_categories import BookCategoryQueries
class BookCategoryManager:
    def __init__(self, app: Quart, db : Database):
        self.book_category_queries = BookCategoryQueries(db.Session)
        self.register_routes(app)

    def register_routes(self, app: Quart):
        
        @app.route("/book_category/insert", methods=["POST"])
        async def insert_book_categories():
            book_categories = await request.get_json()
            result = await self.book_category_queries.insert_book_categories(book_categories)
            return result
        
        @app.route("/book_category/get", methods=["POST"])
        async def fetch_via_book_id():
            data = await request.get_json()
            result = await self.book_category_queries.fetch_via_book_id(data)
            return result
        
        @app.route("/book_category/paged", methods=["POST"])
        async def paged_book_categories():
            data = await request.get_json()
            result = await self.book_category_queries.paged_book_categories(data)
            return result
        
        @app.route("/book_category/delete", methods=["POST"])
        async def delete_book_categories():
            data = await request.get_json()
            result = await self.book_category_queries.delete_book_categories(data)
            return result
        

