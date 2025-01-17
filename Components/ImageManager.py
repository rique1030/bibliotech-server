import os 
import base64

class ImageManager():
    def __init__(self):

        self.storage = os.path.join(os.path.dirname(__file__), "../storage/images")
        self.book_cover = os.path.join(self.storage, "book_covers")
        self.user_photos = os.path.join(self.storage, "user_photos")
        os.makedirs(self.book_cover, exist_ok=True)
        os.makedirs(self.user_photos, exist_ok=True)

    def add_image(self, image_data, image_name):
        image_data = base64.b64decode(image_data)
        file_path = os.path.join(self.storage, f"{image_name}.png")
        print(f"Image saved to {file_path}")
        with open(f"{file_path}", "wb") as f:
            f.write(image_data)
        return print(f"Image saved to {file_path}")
    
    def update_image(self, image_data, image_name, old_image_name):
        self.delete_image(old_image_name)
        image_data = base64.b64decode(image_data)
        file_path = os.path.join(self.storage, f"{image_name}.png")
        print(f"Image saved to {file_path}")
        with open(f"{file_path}", "wb") as f:
            f.write(image_data)
        return print(f"Image saved to {file_path}")


    def delete_image(self, image_name):
        image_path = os.path.join(self.storage, f"{image_name}.png")
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"Image deleted: {image_path}")
        else:
            print(f"Image not found: {image_path}")
