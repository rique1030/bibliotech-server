from flask import Flask , request
from ..db import Database
from ..queries.categories import CategoryQueries
class CategoryManager:
    def __init__(self, app: Flask, db : Database):
        self.category_queries = CategoryQueries(db.Session)
        self.register_routes(app)

    def register_routes(self, app: Flask):
        
        @app.route("/categories/insert", methods=["POST"])
        def insert_multiple_categories():
            categories = request.get_json()
            result = self.category_queries.insert_multiple_categories(categories)
            return result

        @app.route("/categories/get_all", methods=["GET"])
        def get_all_categories():
            result = self.category_queries.get_all_categories()
            return { "success": True, "data": result }
                
        @app.route("/categories/get_paged", methods=["POST"])
        def get_paged_categories():
            data = request.get_json()
            result = self.category_queries.get_paged_categories(
                data.get("page", 0),
                data.get("per_page", 15),
                data.get("filters", None),
                data.get("order_by", "id"),
                data.get("order_direction", "asc")
            )
            return { "success": True, "data": result }
        
        @app.route("/categories/get_by_id", methods=["POST"])
        def get_categories_by_id():
            data = request.get_json()
            result = self.category_queries.get_categories_by_id(data)
            return { "success": True, "data": result }
        
        @app.route("/categories/update", methods=["POST"])
        def update_categories():
            data = request.get_json()
            result = self.category_queries.update_categories(data)
            return result
        
        @app.route("/categories/delete", methods=["POST"])
        def delete_categories_by_id():
            data = request.get_json()
            categories_to_delete = data.get("id")
            result = self.category_queries.delete_categories_by_id(categories_to_delete)
            return result
        
        
