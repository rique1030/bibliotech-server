from quart import Quart , request
from ..db import Database
from ..queries.user import UserQueries
from ..ImageManager import ImageManager
class UserManager:
    def __init__(self, app: Quart, db : Database):
        self.user_queries = UserQueries(db.Session)
        self.register_routes(app)
        self.im = ImageManager()

    def register_routes(self, app: Quart):
        
        @app.route("/user/insert", methods=["POST"])
        async def insert_multiple_users():
            users = await request.get_json()
            #TODO add images
            result = await self.user_queries.insert_users(users)
            return result
        
        @app.route("/user/paged", methods=["POST"])
        async def paged_users():
            data = await request.get_json()
            result = await self.user_queries.paged_users(data)
            return result

        @app.route("/user/fetch:id", methods=["POST"])
        async def fetch_user_via_id():
            data = await request.get_json()
            result = await self.user_queries.fetch_via_id(data)
            return result
        
        @app.route("/user/fetch:login", methods=["POST"])
        async def fetch_via_login():
            data = await request.get_json()
            email = data.get("email")
            passowrd = data.get("password")
            result = await self.user_queries.fetch_via_email_and_password(email, passowrd)
            return result
        
        @app.route("/user/update", methods=["POST"])
        async def update_users():
            data = await request.get_json()
            result = await self.user_queries.update_users(data)
            return result
        
        @app.route("/user/delete", methods=["POST"])
        async def delete_users_by_id():
            data = await request.get_json()
            result = await self.user_queries.delete_users(data)
            return result
        
        @app.route("/user/fetch:borrow", methods=["POST"])
        async def fetch_borrowed():
            data = await request.get_json()
            result = await self.user_queries.get_borrowed_books(data)
            return result

        @app.route("/user/count", methods=["GET"])
        async def count_users():
            result = await self.user_queries.count_all_users()
            return result

        @app.route("/user/count:role", methods=["GET"])
        async def count_users_by_role():
            result = await self.user_queries.count_user_roles()
            return result