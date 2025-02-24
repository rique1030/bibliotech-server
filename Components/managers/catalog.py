from quart import Quart, request
from Components.db import Database
from Components.managers.book_categories import BookCategoryManager
from Components.managers.categories import CategoryManager
from Components.queries.catalog import CatalogQueries


class CatalogManager:
    def __init__(self, app: Quart, db : Database, book_category_manager : BookCategoryManager, category_manager : CategoryManager):
        self.catalog = CatalogQueries(db.Session, book_category_manager, category_manager)
        self.register_routes(app)

    def register_routes(self, app: Quart):
        @app.route("/catalog/insert", methods=["POST"])
        async def insert_catalogs():
            books = await request.get_json()
            #TODO add images
            result = await self.catalog.insert_catalogs(books)
            if result.get("success") is False:
                return result
            #TODO add categories
            return result
        
        @app.route("/catalog/fetch:id", methods=["POST"])
        async def fetch_via_ids():
            data = await request.get_json()
            print(data)
            result = await self.catalog.fetch_via_ids(data)
            return result
    
        @app.route("/catalog/paged", methods=["POST"])
        async def paged_catalogs():
            data = await request.get_json()
            result = await self.catalog.paged_catalogs(data)
            return result
        
        @app.route("/catalog/update", methods=["POST"])
        async def update_catalogs():
            books = await request.get_json()
            #TODO change images
            result = await self.catalog.update_catalogs(books)
            if result.get("success") is False:
                return result
            #TODO change categories
            return result
        
        @app.route("/catalog/delete", methods=["POST"])
        async def delete_catalogs():
            data = await request.get_json()
            result = await self.catalog.delete_catalogs(data)
            return result