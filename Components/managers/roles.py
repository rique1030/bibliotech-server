from quart import Quart , request
from ..db import Database
from ..queries.roles import RoleQueries
class RoleManager:
    def __init__(self, app: Quart, db : Database):
        self.role_queries = RoleQueries(db.Session)
        self.register_routes(app)

    def register_routes(self, app: Quart):
        @app.route("/role/insert", methods=["POST"])
        async def insert_multiple_roles():
            roles = await request.get_json()
            result = await self.role_queries.insert_roles(roles)
            return result
        
        @app.route("/role/get", methods=["GET"])
        async def get_roles():
            result = await self.role_queries.get_roles()
            return result

        @app.route("/role/paged", methods=["POST"])
        async def paged_roles():
            data = await request.get_json()
            result = await self.role_queries.paged_roles(data)
            return result
        
        @app.route('/role/fetch:id', methods=["POST"])
        async def fetch_role_by_id():
            data = await request.get_json()
            result = await self.role_queries.fetch_via_id(data)
            return result
        
        @app.route("/role/update", methods=["POST"])
        async def update_role():
            data = await request.get_json()
            result = await self.role_queries.update_roles(data)
            return result
        
        @app.route("/role/delete", methods=["POST"])
        async def delete_roles():
            data = await request.get_json()
            result = await self.role_queries.delete_roles(data)
            return result
        


