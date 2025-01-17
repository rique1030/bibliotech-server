from flask import Flask, json , request
from ..db import Database
from ..queries.books import BookQueries
from ..QRManager import QRManager
from ..ImageManager import ImageManager

class BookManager:
    def __init__(self, app: Flask, db : Database):
        self.book_queries = BookQueries(db.Session)
        self.register_routes(app)
        self.qr = QRManager()
        self.im = ImageManager()

    def register_routes(self, app: Flask):
        
        @app.route("/books/insert", methods=["POST"])
        def insert_multiple_books():
            data = request.get_json()
            book_images = []
            
            for book in data:
                image_id = f"{book['access_number']}_{book['call_number']}"
                if "cover_image_buffer" in book:
                    image = {
                        "id" : image_id,
                        "cover_buffer" : book["cover_image_buffer"]
                    }
                    book_images.append(image)
                    book["cover_image"] = image_id

                book.pop("id", None)
                book.pop("date_added", None)
                book.pop("date_updated", None)

            success, books = self.qr.add_code(data)

            if not success:
                return { "success": False, "data": None, "error": "Failed to add QR codes" }
            
            result = self.book_queries.insert_multiple_books(books)
            
            if result.get("success") is False:
                return result
            
            for image in book_images:
                self.im.add_image(image.get("cover_buffer"), f"book_covers/{image.get('id')}")
            
            return result

        @app.route("/books/get_paged", methods=["POST"])
        def get_paged_books():
            data = request.get_json()
            result = self.book_queries.get_paged_books(
                data.get("page", 0),
                data.get("per_page", 15),
                data.get("filters", None),
                data.get("order_by", "id"),
                data.get("order_direction", "asc")
            )
            return { "success": True, "data": result }
        
        @app.route("/books/get_by_id", methods=["POST"])
        def get_books_by_id():
            data = request.get_json()
            result = self.book_queries.get_books_by_id(data)
            return { "success": True, "data": result }
        
        @app.route("/books/get_by_access_number", methods=["POST"])
        def get_books_by_access_number():
            data = request.get_json()
            result = self.book_queries.get_books_by_access_number(data)
            return { "success": True, "data": result }

        @app.route("/books/update", methods=["POST"])
        def update_books():
            data = request.get_json()
            book_images = []
            
            for book in data:
                image_id = f"{book['access_number']}_{book['call_number']}"
                if "cover_image_buffer" in book:
                    image = {
                        "id" : image_id,
                        "cover_buffer" : book["cover_image_buffer"],
                        "old_id" : book["cover_image"]
                    }
                    book_images.append(image)
                    book["cover_image"] = image_id

                book.pop("date_added", None)
                book.pop("date_updated", None)

            success, books = self.qr.update_code(data)

            if not success:
                return { "success": False, "data": None, "error": "Failed to add QR codes" }

            result = self.book_queries.update_books(books)
            
            if result.get("success") is False:
                return result
            
            for image in book_images:
                self.im.update_image(image.get("cover_buffer"), f"book_covers/{image.get('id')}", f"book_covers/{image.get('old_id')}")

            return result
        
        @app.route("/books/delete", methods=["POST"])
        def delete_books_by_id():
            data = request.get_json()
            books_to_delete = data.get("id")
            result = self.book_queries.delete_books_by_id(books_to_delete)
            return result
        
