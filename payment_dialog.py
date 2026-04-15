from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class PaymentDialog(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chọn phương thức thanh toán")
        self.setFixedSize(300, 200)

        self.method = None

        layout = QVBoxLayout(self)

        label = QLabel(f"Tổng tiền: {total} VND")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size:16px;font-weight:bold;")
        layout.addWidget(label)

        # Buttons
        btn_cash = QPushButton(" Tiền mặt")
        btn_transfer = QPushButton(" Chuyển khoản")

        btn_cash.setStyleSheet(self.btn_style("#007042"))
        btn_transfer.setStyleSheet(self.btn_style("#1976D2"))

        btn_cash.clicked.connect(self.choose_cash)
        btn_transfer.clicked.connect(self.choose_transfer)

        layout.addWidget(btn_cash)
        layout.addWidget(btn_transfer)

    def btn_style(self, color):
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            opacity: 0.8;
        }}
        """

    def choose_cash(self):
        self.method = "Tiền mặt"
        self.accept()

    def choose_transfer(self):
        self.method = "Chuyển khoản"
        self.accept()