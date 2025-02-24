# from quart import Quart, json , request

# from Components.managers.book_categories import BookCategoryManager
# from ..db import Database
# from ..queries.books import BookQueries
# from ..QRManager import QRManager
# from ..ImageManager import ImageManager
# import weakref

# class BookManager:
#     def __init__(self, app: Quart, db : Database, book_category_manager_instance = None):
#         self._book_category_manager: BookCategoryManager = weakref.ref(book_category_manager_instance) if book_category_manager_instance else None
#         self.book_queries = BookQueries(db.Session)
#         self.register_routes(app)
#         self.qr = QRManager()
#         self.im = ImageManager()

#     def get_book_category_manager(self):
#         return self._book_category_manager() if self._book_category_manager else None

#     def process_book_image(self, book):
#             if "cover_image_buffer" in book:
#                 image_id = f"{book['access_number']}_{book['call_number']}"
#                 book["cover_image"] = image_id
#                 image = {
#                     "id" : image_id,
#                     "cover_buffer" : book["cover_image_buffer"]
#                 }
#                 if "cover_image" in book:
#                     image["old_id"] = book["cover_image"]
#                 return image
#             book["cover_image"] = "default"
#             return None
        
#     def process_book_category(self, book):
#         if "book_categories" in book:
#             return [{
#                 "book_access_number" : book["access_number"],
#                 "category_id" : category.get("id")
#             } for category in book["book_categories"]]
#         return []

#     def register_routes(self, app: Quart):
        
#         @app.route("/books/insert", methods=["POST"])
#         def insert_multiple_books():
#             data = request.get_json()
#             book_images = []
#             book_categories = []
#             # * for book in data:
#             for book in data:
#                 image = self.process_book_image(book)
#                 if image:
#                     book_images.append(image)
#                 categories = self.process_book_category(book)
#                 if categories:
#                     book_categories.extend(categories)
#                 # * remove unnecessary fields
#                 book.pop("id", None)
#                 book.pop("date_added", None)
#                 book.pop("date_updated", None)
#                 book.pop("cover_image_buffer", None)
#                 book.pop("book_categories", None)
#             success, books = self.qr.add_code(data)
#             if not success:
#                 return { "success": False, "data": None, "error": "Failed to add QR codes" }
#             result = self.book_queries.insert_multiple_books(books)
#             if result.get("success") is False:
#                 return result
#             for image in book_images:
#                 self.im.add_image(image.get("cover_buffer"), f"book_covers/{image.get('id')}")
#             bcm = self.get_book_category_manager()
#             if bcm:
#                 category_result = bcm.book_category_queries.insert_multiple_book_categories(book_categories)
#             if category_result.get("success") is False:
#                 return {"success": False, "data": None, "error": "Books successfully added, but failed to add categories"}
#             return result

#         @app.route("/books/get_paged", methods=["POST"])
#         def get_paged_books():
#             data = request.get_json()
#             print(data)
#             result = self.book_queries.get_paged_books(
#                 data.get("page", 0),
#                 data.get("per_page", 15),
#                 data.get("filters", None),
#                 data.get("order_by", "id"),
#                 data.get("order_direction", "asc")
#             )
            
#             books = result.get("data")
#             for book in books:
#                 bcm = self.get_book_category_manager()
#                 if bcm:
#                     categories = bcm.book_category_queries.get_book_categories_by_access_number([book.get("access_number"),])
#                     for category in categories:
#                         if "book_category_ids" not in book:
#                             book["book_category_ids"] = []
#                         book["book_category_ids"].append(category.get("category_id"))
#             return { "success": True, "data": result }
        
#         @app.route("/books/get_by_id", methods=["POST"])
#         def get_books_by_id():
#             data = request.get_json()
#             result = self.book_queries.get_books_by_id(data)
#             book_access_number = [book["access_number"] for book in result] # for fetching categories
#             book_categories = {}
#             bcm = self.get_book_category_manager()
#             if bcm:
#                 categories = bcm.book_category_queries.get_book_categories_by_access_number(book_access_number)
#                 for category in categories:
#                     if category.get("book_access_number") not in book_categories:
#                         book_categories[category.get("book_access_number")] = []
#                     book_categories[category.get("book_access_number")].append(category.get("category_id"))

#             for book in result:
#                 if "book_category_ids" not in book:
#                     book["book_category_ids"] = []
#                 book["book_category_ids"].extend(book_categories.get(book.get("access_number"), []))
#             return { "success": True, "data": result }
        
#         @app.route("/books/get_by_access_number", methods=["POST"])
#         def get_books_by_access_number():
#             data = request.get_json()
#             result = self.book_queries.get_books_by_access_number(data)
#             return { "success": True, "data": result }

#         @app.route("/books/update", methods=["POST"])
#         def update_books():
#             data = request.get_json()
#             book_images = []
#             categories_to_add = []
#             categories_to_remove = []
    
#             for book in data:
#                 image = self.process_book_image(book)
#                 if image:
#                     book_images.append(image)
                
#                 new_cat_id : set = set()
#                 old_cat_id : set = set()

#                 if "book_categories" in book:
#                     new_cat_id = set(category.get("id") for category in book.get("book_categories") )

#                 if "book_category_ids" in book:
#                     old_cat_id = set(book.get("book_category_ids"))

#                 # existing_cat_id = old_cat_id | new_cat_id
#                 id_to_add = new_cat_id - old_cat_id
#                 id_to_remove = old_cat_id - new_cat_id
                
#                 for cat_id in id_to_add:
#                     categories_to_add.append({ "book_access_number" : book["access_number"], "category_id" : cat_id })
#                 for cat_id in id_to_remove:
#                     categories_to_remove.append({ "book_access_number" : book["access_number"], "category_id" : cat_id })

#                 book.pop("date_added", None)
#                 book.pop("date_updated", None)

#             # return { "success": False, "data": None, "error": "Not implemented" }

#             success, books = self.qr.update_code(data)

#             if not success:
#                 return { "success": False, "data": None, "error": "Failed to add QR codes" }

#             result = self.book_queries.update_books(books)
            
#             if result.get("success") is False:
#                 return result
            
#             for image in book_images:
#                 self.im.update_image(image.get("cover_buffer"), f"book_covers/{image.get('id')}", f"book_covers/{image.get('old_id')}")

#             bcm = self.get_book_category_manager()
#             if bcm:
#                 category_result = bcm.book_category_queries.insert_multiple_book_categories(categories_to_add)
#                 if category_result.get("success") is False:
#                     return {"success": False, "data": None, "error": "Books successfully added, but failed to add some categories"}
#                 category_result = bcm.book_category_queries.delete_book_categories_by_access_number_and_category_id(categories_to_remove)
#                 if category_result.get("success") is False:
#                     return {"success": False, "data": None, "error": "Books successfully added, but failed to remove some categories"}
            
#             return result
        
#         @app.route("/books/delete", methods=["POST"])
#         def delete_books_by_id():
#             data = request.get_json()
#             books_to_delete = data.get("id")
#             books = self.book_queries.get_books_by_id(books_to_delete)
#             result = self.book_queries.delete_books_by_id(books_to_delete)
#             if result.get("success") is False:
#                 return result
#             for book in books:
#                 self.qr.delete_qr_code(book.get("qrcode"))
#                 if book.get("cover_image") != "default":
#                     self.im.delete_image(f"book_covers/{book.get('id')}")
#             return result
        
