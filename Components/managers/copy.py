from quart import Quart, request
from Components.db import Database
from Components.queries.copy import CopyQueries

class CopyManager:
    def __init__(self, app: Quart, db : Database):
        self.copy = CopyQueries(db.Session)
        self.register_routes(app)

    def register_routes(self, app: Quart):
        @app.route('/copy/insert', methods=['POST'])
        async def insert_copies():
            data = await request.get_json()
            result = await self.copy.insert_copies(data)
            return result

        @app.route('/copy/paged', methods=['POST'])
        async def paged_copies():
            data = await request.get_json()
            result = await self.copy.paged_copies(data)
            return result
        

        @app.route('/copy/paged:detailed', methods=['POST'])
        async def paged_copies_detailed():
            data = await request.get_json()
            result = await self.copy.paged_copies_detailed(data)
            return result
        
        @app.route('/copy/update', methods=['POST'])
        async def update_copies():
            data = await request.get_json()
            result = await self.copy.update_copies(data)  
            return result
        
        @app.route('/copy/delete', methods=['POST'])
        async def delete_copies():
            data = await request.get_json()
            result = await self.copy.delete_copies(data)
            return result

        @app.route('/copy/fetch:access_number', methods=['POST'])
        async def fetch_via_access_number():
            access_numbers = await request.get_json()
            result = await self.copy.fetch_via_access_number(access_numbers)
            return result