import os 
import base64

class ImageManager():
    """NEW"""
    async def convert_to_image(self, image):
        if not image:
            return
        return base64.b64decode(image)

    async def save_image(self, image, name, path):
        print(type(image))
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
