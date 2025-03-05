import os
import qrcode
from PIL import Image
from io import BytesIO
class QRManager:
    def __init__(self):
        self.QR_CODE_PATH = os.path.join(os.path.dirname(__file__), "../storage/qr-codes/")
        os.makedirs(self.QR_CODE_PATH, exist_ok=True)
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4

        )

    def generate_image(self, id):
        """Generate QR code image for a book"""
        try:
            self.qr.clear()
            self.qr.add_data(id)
            self.qr.make(fit=True)
            img = self.qr.make_image(fill_color="black", back_color="white").convert('RGB')
            img = self.add_logo(img)
            image_bytes = BytesIO()
            img.save(image_bytes, format="PNG")
            return image_bytes.getvalue()
        except Exception as e:
            print(e)
            return None
    
    def add_logo(self, img):
        logo = Image.open(os.path.join(self.QR_CODE_PATH, "logo.png"))
        qr_width, qr_height = img.size
        logo_size = min(qr_width, qr_height) // 4
        logo = logo.resize((logo_size, logo_size))
        logo_position = ((qr_width - logo.width) // 2, (qr_height - logo.height) // 2)
        img.paste(logo, logo_position, mask=logo.convert("RGBA").split()[3])
        return img
