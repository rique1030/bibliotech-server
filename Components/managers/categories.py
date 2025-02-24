from quart import Quart , request
from ..db import Database
from ..queries.categories import CategoryQueries
class CategoryManager:
    def __init__(self, app: Quart, db : Database):
        self.category_queries = CategoryQueries(db.Session)
        self.register_routes(app)

    def register_routes(self, app: Quart):
        
        @app.route("/category/insert", methods=["POST"])
        async def insert_multiple_categories():
            categories = await request.get_json()
            result = await self.category_queries.insert_categories(categories)
            return result
        @app.route("/category/get", methods=["GET"])
        async def get_all_categories():
            result = await self.category_queries.get_categories()
            return result
            
                
        @app.route("/category/paged", methods=["POST"])
        async def get_paged_categories():
            data = await request.get_json()
            result = await self.category_queries.paged_categories(data)
            return result
        
        @app.route("/category/fetch:id", methods=["POST"])
        async def get_categories_by_id():
            data = await request.get_json()
            result = await self.category_queries.fetch_via_id(data)
            return result
        
        @app.route("/category/update", methods=["POST"])
        async def update_categories():
            data = await request.get_json()
            result = await self.category_queries.update_categories(data)
            return result
        
        @app.route("/category/delete", methods=["POST"])
        async def delete_categories_by_id():
            data = await request.get_json()
            result = await self.category_queries.delete_categories(data)
            return result
