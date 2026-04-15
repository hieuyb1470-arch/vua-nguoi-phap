from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from history_dialog import HistoryDialog
import message_utils as msg

from order_manager import OrderManager
from ui_menu import create_menu_page
from payment_dialog import PaymentDialog


class POS(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("POS System")
        self.resize(1200, 700)

        self.manager = OrderManager()

        self.menu = {
            "coffee": {
                "Espresso": 30000,
                "Cappuccino": 40000,
                "Latte": 45000,
                "Salted Coffee": 50000,
                "Milk Coffee": 35000,
                "Coconut Coffee": 55000
            },
            "juice": {
                "Apple": 30000,
                "Orange": 30000,
                "Lime": 25000,
                "Pineapple": 35000,
                "Passion": 30000,
                "Watermelon": 30000
            },
            "dessert": {
                "Croissant": 25000,
                "Chocolate Roll": 30000,
                "Brownie": 35000,
                "Red Velvet": 40000,
                "Cheese Cake": 45000,
                "Bánh Cay": 20000
            }
        }

        self.total = 0
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout(self)

        # ===== HEADER =====
        header = QLabel("STARBUG POS SYSTEM")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(60)
        header.setStyleSheet("""
            background:#007042;
            color:white;
            font-size:24px;
            font-weight:bold;
            letter-spacing:1px;
        """)
        main.addWidget(header)

        # ===== BODY =====
        body = QHBoxLayout()

        # ===== LEFT (MENU) =====
        self.stacked = QStackedWidget()
        self.stacked.addWidget(create_menu_page(self, self.menu["coffee"], self.add_item))
        self.stacked.addWidget(create_menu_page(self, self.menu["juice"], self.add_item))
        self.stacked.addWidget(create_menu_page(self, self.menu["dessert"], self.add_item))

        menu_bar = QHBoxLayout()
        for i, name in enumerate(["COFFEE", "JUICE", "DESSERT"]):
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    border-radius: 8px;
                    background-color: white;
                    border: 1px solid #ccc;
                }
                QPushButton:hover {
                    background-color: #e6f4ee;
                    border: 1px solid #007042;
                }
            """)
            btn.clicked.connect(lambda _, x=i: self.stacked.setCurrentIndex(x))
            menu_bar.addWidget(btn)

        left = QVBoxLayout()
        left.addWidget(self.stacked)
        left.addLayout(menu_bar)

        # ===== RIGHT (ORDER PANEL) =====
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 12px;
            }
        """)

        right = QVBoxLayout(right_widget)
        right.setContentsMargins(10, 10, 10, 10)
        right.setSpacing(10)

        # List món
        self.listWidget = QListWidget()
        self.listWidget.setStyleSheet("""
            QListWidget {
                background: white;
                border: none;
                border-radius: 10px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #d4f5e9;
            }
        """)
        self.listWidget.itemDoubleClicked.connect(self.remove_item)

        # Total
        self.total_label = QLabel("0 VND")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #007042;
                background: white;
                padding: 10px;
                border-radius: 8px;
            }
        """)

        # Buttons
        btn_checkout = QPushButton("Thanh toán")
        btn_checkout.setStyleSheet("""
            QPushButton {
                background-color: #007042;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #009e5f;
            }
            QPushButton:pressed {
                background-color: #005c34;
            }
        """)

        btn_history = QPushButton("Lịch sử")
        btn_history.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #007042;
                color: #007042;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #e6f4ee;
            }
        """)

        btn_checkout.clicked.connect(self.checkout)
        btn_history.clicked.connect(self.show_history)

        right.addWidget(self.listWidget)
        right.addWidget(self.total_label)
        right.addWidget(btn_checkout)
        right.addWidget(btn_history)

        # ===== ADD TO BODY =====
        body.addLayout(left, 3)
        body.addWidget(right_widget, 1)
        right_widget.setMaximumWidth(320)

        main.addLayout(body)

    # ===== LOGIC =====
    def add_item(self, name, price):
        self.listWidget.addItem(f"{name} - {price}đ")
        self.total += price
        self.total_label.setText(f"{self.total} VND")

    def remove_item(self, item):
        price = int(item.text().split("-")[1].replace("đ", "").strip())
        self.total -= price
        self.total_label.setText(f"{self.total} VND")
        self.listWidget.takeItem(self.listWidget.row(item))

    def checkout(self):
        if self.total == 0:
            msg.show_warning(self, "Chưa có món!")
            return

        # chọn phương thức thanh toán
        dialog = PaymentDialog(self.total, self)
        if dialog.exec_() != QDialog.Accepted:
            return

        payment_method = dialog.method

        # xác nhận lại
        if not msg.confirm(self, f"{payment_method}\nTổng tiền: {self.total} VND\nXác nhận?"):
            return

        items = [self.listWidget.item(i).text() for i in range(self.listWidget.count())]

        order = {
            "time": datetime.now().strftime("%H:%M:%S %d-%m-%Y"),
            "items": items,
            "total": self.total,
            "payment": payment_method
        }

        self.manager.history.append(order)
        self.manager.save_history()
        self.manager.save_to_excel(order)

        msg.show_info(self, f"Thanh toán thành công ({payment_method})!")

        self.listWidget.clear()
        self.total = 0
        self.total_label.setText("0 VND")

    def show_history(self):
        dialog = HistoryDialog(self.manager.history, self)
        dialog.exec_()