from flask import Flask , request
from ..db import Database
from ..queries.user import UserQueries
from ..ImageManager import ImageManager
class UserManager:
    def __init__(self, app: Flask, db : Database):
        self.user_queries = UserQueries(db.Session)
        self.register_routes(app)
        self.im = ImageManager()
    def register_routes(self, app: Flask):
        
        @app.route("/users/insert", methods=["POST"])
        def insert_multiple_users():
            users = request.get_json()
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
                
            result = self.user_queries.insert_multiple_users(users)

            if result.get("success") is False:
                return result
            
            for image in user_images:
                self.im.add_image(image.get("profile_buffer"), f"user_photos/{image.get("id")}")
            return result
        
        @app.route("/users/get_paged", methods=["POST"])
        def get_paged_users():
            data = request.get_json()
            result = self.user_queries.get_paged_users(
                data.get("page", 0),
                data.get("per_page", 15),
                data.get("filters", None),
                data.get("order_by", "id"),
                data.get("order_direction", "asc")
            )
            return { "success": True, "data": result }
        
        @app.route("/users/get_by_id", methods=["POST"])
        def get_users_by_id():
            data = request.get_json()
            result = self.user_queries.get_users_by_id(data)
            return { "success": True, "data": result }
        
        @app.route("/users/login", methods=["POST"])
        def get_user_by_email_and_password():
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            print(email, password)
            result = self.user_queries.get_user_by_email_and_password(email=email, password=password)
            return { "success": True, "data": result }
        
        @app.route("/users/update", methods=["POST"])
        def update_user():
            data = request.get_json()
            result = self.user_queries.update_users(data)
            return { "success": True, "data": result }
        
        @app.route("/users/delete", methods=["POST"])
        def delete_users_by_id():
            data = request.get_json()
            accounts_to_delete = data.get("id")
            result = self.user_queries.delete_users_by_id(accounts_to_delete)
            return result
        
        