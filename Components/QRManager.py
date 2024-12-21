import os
import qrcode

class QRManager:
    def __init__(self):
        self.QR_CODE_PATH = os.path.join(os.path.dirname(__file__), "../storage/qr-codes/")
        os.makedirs(self.QR_CODE_PATH, exist_ok=True)
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
    
    def generate_qr_code(self, data):
        self.qr.clear()
        self.qr.add_data(data)
        self.qr.make(fit=True)
        img = self.qr.make_image(fill_color="black", back_color="white")
        if data.endswith(".png"):
            data = data[:-4]
            print(data)
        img.save(os.path.join(self.QR_CODE_PATH, f"{data}.png"))
        return f"{data}.png"
    
    def delete_qr_code(self, image_name):
        qr_code_path = os.path.join(self.QR_CODE_PATH, f"{image_name}")
        if os.path.exists(qr_code_path):
            os.remove(qr_code_path)
            print(f"QR code deleted: {qr_code_path}")
        else:
            print(f"QR code not found: {qr_code_path}")

if __name__ == "__main__":
    qr_manager = QRManager()
    qr_manager.qr.add_data("https://github.com/riquelicious/WicksEnd4.3/releases/tag/Latest")
    qr_manager.qr.make(fit=True)
    img = qr_manager.qr.make_image(fill_color="black", back_color="white")
    img.save(os.path.join(qr_manager.QR_CODE_PATH, f"asd.png"))
