from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
import requests

class QRDialog(QDialog):
    def __init__(self, qr_url):
        super().__init__()
        self.setWindowTitle("Thanh toán QR")

        layout = QVBoxLayout()

        title = QLabel("Quét mã để thanh toán")
        layout.addWidget(title)

        # tải QR
        response = requests.get(qr_url)
        with open("temp_qr.png", "wb") as f:
            f.write(response.content)

        qr_label = QLabel()
        qr_label.setPixmap(QPixmap("temp_qr.png"))
        layout.addWidget(qr_label)

        # nút đóng
        close_btn = QPushButton("Đã thanh toán")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)