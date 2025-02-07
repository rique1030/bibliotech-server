from quart import Quart , request
from ..db import Database
from ..queries.roles import RoleQueries
class RoleManager:
    def __init__(self, app: Quart, db : Database):
        self.role_queries = RoleQueries(db.Session)
        self.register_routes(app)

    def register_routes(self, app: Quart):
        @app.route("/roles/insert", methods=["POST"])
        async def insert_multiple_roles():
            roles = await request.get_json()
            result = await self.role_queries.insert_multiple_roles(roles)
            return result
        
        @app.route("/roles/get_all", methods=["GET"])
        async def get_all_roles():
            result = await self.role_queries.get_all_roles()
            return { "success": True, "data": result }

        @app.route("/roles/get_paged", methods=["POST"])
        async def get_paged_roles():
            data = await request.get_json()
            result = await self.role_queries.get_paged_roles(
                data.get("page", 0),
                data.get("per_page", 15),
                data.get("filters", None),
                data.get("order_by", "id"),
                data.get("order_direction", "asc")
            )
            return { "success": True, "data": result }
        
        @app.route("/roles/get_by_id", methods=["POST"])
        async def get_roles_by_id():
            data = await request.get_json()
            result = await self.role_queries.get_roles_by_id(data)
            return { "success": True, "data": result }
        
        @app.route("/roles/update", methods=["POST"])
        async def update_role():
            data = await request.get_json()
            result = await self.role_queries.update_roles(data)
            return result
        
        @app.route("/roles/delete", methods=["POST"])
        async def delete_roles_by_id():
            data = await request.get_json()
            roles_to_delete = data.get("id", [])
            result = await self.role_queries.delete_roles_by_id(roles_to_delete)
            return result
        
