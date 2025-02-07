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
        
        @app.route("/users/insert", methods=["POST"])
        async def insert_multiple_users():
            users = await request.get_json()
            user_images = []

            for user in users:
                image_id = f"{user['email']}"
                if "profile_pic_buffer" in user:
                    image = {
                        "id" : image_id,
                        "profile_buffer" : user["profile_pic_buffer"]
                    }
                    user_images.append(image)
                    user["profile_pic"] = image_id
                else:
                    user["profile_pic"] = "default"
                user.pop("id", None)
                user.pop("created_at", None)
                
            result = await self.user_queries.insert_multiple_users(users)

            if result.get("success") is False:
                return result
            
            for image in user_images:
                await self.im.add_image(image.get("profile_buffer"), f"user_photos/{image.get("id")}")
            return result
        
        @app.route("/users/get_paged", methods=["POST"])
        async def get_paged_users():
            data = await request.get_json()
            result = await self.user_queries.get_paged_users(
                data.get("page", 0),
                data.get("per_page", 15),
                data.get("filters", None),
                data.get("order_by", "id"),
                data.get("order_direction", "asc")
            )
            return { "success": True, "data": result }
        
        @app.route("/users/get_by_id", methods=["POST"])
        async def get_users_by_id():
            data = await request.get_json()
            print(data)
            result = await self.user_queries.get_users_by_id(data)
            return { "success": True, "data": result }
        
        @app.route("/users/login", methods=["POST"])
        async def get_user_by_email_and_password():
            print("User logging in...")
            data = await request.get_json()
            email = data.get("email")
            password = data.get("password")
            result = await self.user_queries.get_user_by_email_and_password(email=email, password=password)
            if result is not None and len(result) > 0:
                print(f"User logged in: {email}")
            else:
                print(f"User not logged in: {email}")
            return { "success": True, "data": result }
        
        @app.route("/users/update", methods=["POST"])
        async def update_user():
            data = await request.get_json()
            user_images = []

            for user in data:
                image_id = f"{user['email']}"
                if "profile_pic_buffer" in user:
                    image = {
                        "id" : image_id,
                        "profile_buffer" : user["profile_pic_buffer"]
                    }
                    user_images.append(image)
                    user["profile_pic"] = image_id
                else:
                    if user.get("profile_pic") is None:
                        user["profile_pic"] = "default"

                user.pop("created_at", None)
                
            result = await self.user_queries.update_users(data)

            for image in user_images:
                await self.im.add_image(image.get("profile_buffer"), f"user_photos/{image.get("id")}")
            return result
        
        @app.route("/users/delete", methods=["POST"])
        async def delete_users_by_id():
            data = await request.get_json()
            accounts_to_delete = data.get("id")
            users = await self.user_queries.get_users_by_id(accounts_to_delete)
            result = await self.user_queries.delete_users_by_id(accounts_to_delete)
            for user in users:
                if user.get("profile_pic") != "default":
                    await self.im.delete_image(f"user_photos/{user.get('email')}")
            return result
