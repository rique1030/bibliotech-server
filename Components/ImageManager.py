import os 
import base64

class ImageManager():
    """NEW"""
    async def convert_to_image(self, image):
        if not image:
            return
        return base64.b64decode(image)

    # ?  image[key] = await save_image(dict, key, name, path)
    async def save_image(self, image, name, path):
        if not image:
            return None
        file_path = os.path.join(path, f"{name}.png")
        try:
            with open(file_path, "wb") as f:
                f.write(image)
            print(f"Image saved to {file_path}")
            return name
        except Exception as e:
            print(f"Failed to save image: {e}")
            return None

    async def delete_image(self, name, path):
        image_path = os.path.join(path, f"{name}.png")
        if os.path.exists(image_path):
            os.remove(image_path)
            return print(f"Image deleted: {image_path}")
        else:
            return print(f"Image not found: {image_path}")

    # def add_image(self, image_data, image_name):
    #     image_data = base64.b64decode(image_data)
    #     file_path = os.path.join(self.storage, f"{image_name}.png")
    #     print(f"Image saved to {file_path}")
    #     with open(f"{file_path}", "wb") as f:
    #         f.write(image_data)
    #     return print(f"Image saved to {file_path}")
    
    # def update_image(self, image_data, image_name, old_image_name):
    #     self.delete_image(old_image_name)
    #     image_data = base64.b64decode(image_data)
    #     file_path = os.path.join(self.storage, f"{image_name}.png")
    #     print(f"Image saved to {file_path}")
    #     with open(f"{file_path}", "wb") as f:
    #         f.write(image_data)
    #     return print(f"Image saved to {file_path}")


    # def delete_image(self, image_name):
    #     image_path = os.path.join(self.storage, f"{image_name}.png")
    #     if os.path.exists(image_path):
    #         os.remove(image_path)
    #         print(f"Image deleted: {image_path}")
    #     else:
    #         print(f"Image not found: {image_path}")
