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
        self.cart = {}

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

    # =========================
    # FORMAT TIỀN
    # =========================
    def format_money(self, value):
        return f"{value:,}".replace(",", ".")

    # =========================
    # UI
    # =========================
    def init_ui(self):
        main = QVBoxLayout(self)

        header = QLabel("STARBUG POS SYSTEM")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(60)
        header.setStyleSheet("""
            background:#007042;
            color:white;
            font-size:24px;
            font-weight:bold;
        """)
        main.addWidget(header)

        body = QHBoxLayout()

        self.stacked = QStackedWidget()

        self.stacked.addWidget(create_menu_page(self, self.menu["coffee"], self.add_item))
        self.stacked.addWidget(create_menu_page(self, self.menu["juice"], self.add_item))
        self.stacked.addWidget(create_menu_page(self, self.menu["dessert"], self.add_item))

        menu_bar = QHBoxLayout()
        for i, name in enumerate(["COFFEE", "JUICE", "DESSERT"]):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, x=i: self.stacked.setCurrentIndex(x))
            menu_bar.addWidget(btn)

        left = QVBoxLayout()
        left.addWidget(self.stacked)
        left.addLayout(menu_bar)

        right_widget = QWidget()
        right = QVBoxLayout(right_widget)

        self.listWidget = QListWidget()
        self.listWidget.itemDoubleClicked.connect(self.remove_item)

        self.total_label = QLabel("0 VND")
        self.total_label.setAlignment(Qt.AlignCenter)

        btn_checkout = QPushButton("Thanh toán")
        btn_history = QPushButton("Lịch sử")

        btn_checkout.clicked.connect(self.checkout)
        btn_history.clicked.connect(self.show_history)

        right.addWidget(self.listWidget)
        right.addWidget(self.total_label)
        right.addWidget(btn_checkout)
        right.addWidget(btn_history)

        body.addLayout(left, 3)
        body.addWidget(right_widget, 1)
        right_widget.setMaximumWidth(320)

        main.addLayout(body)

    # =========================
    # ADD ITEM
    # =========================
    def add_item(self, name, price):
        if name in self.cart:
            self.cart[name]["qty"] += 1
        else:
            self.cart[name] = {"qty": 1, "price": price}

        self.refresh_cart()

    # =========================
    # REFRESH CART
    # =========================
    def refresh_cart(self):
        self.listWidget.clear()
        self.total = 0

        for name, data in self.cart.items():
            qty = data["qty"]
            price = data["price"]

            total_item = qty * price
            self.total += total_item

            self.listWidget.addItem(
                f"{name} x{qty} - {self.format_money(total_item)}đ"
            )

        self.total_label.setText(f"{self.format_money(self.total)} VND")

    # =========================
    # REMOVE ITEM
    # =========================
    def remove_item(self, item):
        name = item.text().split(" x")[0]

        if name in self.cart:
            self.cart[name]["qty"] -= 1
            if self.cart[name]["qty"] <= 0:
                del self.cart[name]

        self.refresh_cart()

    # =========================
    # CHECKOUT (ỔN ĐỊNH 100%)
    # =========================
    def checkout(self):
        try:
            if self.total == 0:
                msg.show_warning(self, "Chưa có món!")
                return

            dialog = PaymentDialog(self.total, self)

            if dialog.exec_() != QDialog.Accepted:
                return

            payment_method = dialog.method

            if not payment_method:
                msg.show_warning(self, "Chưa chọn phương thức!")
                return

            if not msg.confirm(
                self,
                f"{payment_method}\nTổng tiền: {self.format_money(self.total)} VND\nXác nhận?"
            ):
                return

            # =========================
            # FIX DATA CHUẨN JSON
            # =========================
            items = [
                {
                    "name": name,
                    "qty": data["qty"],
                    "price": data["price"]
                }
                for name, data in self.cart.items()
            ]

            order = {
                "time": datetime.now().strftime("%H:%M:%S %d-%m-%Y"),
                "items": items,
                "total": self.total,
                "payment": payment_method
            }

            self.manager.history.append(order)
            self.manager.save_history()
            self.manager.save_to_excel(order)

            msg.show_info(self, "Thanh toán thành công!")

            self.cart.clear()
            self.refresh_cart()

        except Exception as e:
            msg.show_warning(self, f"Lỗi hệ thống: {str(e)}")

    # =========================
    # HISTORY
    # =========================
    def show_history(self):
        dialog = HistoryDialog(self.manager.history, self)
        dialog.exec_()