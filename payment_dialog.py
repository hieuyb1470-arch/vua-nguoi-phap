from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class PaymentDialog(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Thanh toán")
        self.setFixedSize(300, 200)

        self.method = None

        layout = QVBoxLayout(self)

        label = QLabel(f"Tổng tiền: {self.format_money(total)} VND")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size:16px;font-weight:bold;")
        layout.addWidget(label)

        btn_cash = QPushButton("Tiền mặt")
        btn_transfer = QPushButton("Chuyển khoản")

        btn_cash.clicked.connect(self.choose_cash)
        btn_transfer.clicked.connect(self.choose_transfer)

        layout.addWidget(btn_cash)
        layout.addWidget(btn_transfer)

    def format_money(self, value):
        return f"{value:,}".replace(",", ".")

    def choose_cash(self):
        self.method = "Tiền mặt"
        self.accept()

    def choose_transfer(self):
        self.method = "Chuyển khoản"
        self.accept()