import json
import os
from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from history_dialog import HistoryDialog
import message_utils as msg

from order_manager import OrderManager
from ui_menu import create_menu_page
from payment_dialog import PaymentDialog
from menu_editor import MenuEditorDialog

from qr_dialog import QRDialog

def get_qr_url(amount, order_id):
    bank_code = "BIDV"          # ngân hàng (VD: VCB, TCB, BIDV...)
    account_no = "3711503588"   # số tài khoản của bạn
    description = f"DH{order_id}"

    return f"https://img.vietqr.io/image/{bank_code}-{account_no}-compact.png?amount={amount}&addInfo={description}"

class POS(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("POS System")
        self.resize(1200, 700)

        self.manager = OrderManager()
        self.cart = {}
        self.category_keys = ["coffee", "juice", "dessert"]
        self.current_category_index = 0

        self.menu_file = os.path.join(os.path.dirname(__file__), "menu_data.json")
        self.default_menu = {
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
                "Bánh Cáy": 20000
            }
        }
        self.menu = self.load_menu_data()

        self.total = 0
        self.init_ui()


    # FORMAT TIỀN

    def format_money(self, value):
        return f"{value:,}".replace(",", ".")


    # UI

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

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm món trong danh mục hiện tại...")
        self.search_input.textChanged.connect(self.refresh_current_menu_page)

        menu_bar = QHBoxLayout()
        for i, name in enumerate(["COFFEE", "JUICE", "DESSERT"]):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, x=i: self.change_category(x))
            menu_bar.addWidget(btn)

        left = QVBoxLayout()
        left.addWidget(self.search_input)
        left.addWidget(self.stacked)
        left.addLayout(menu_bar)

        self.build_menu_pages()

        right_widget = QWidget()
        right = QVBoxLayout(right_widget)

        self.listWidget = QListWidget()
        self.listWidget.itemDoubleClicked.connect(self.remove_item)

        self.total_label = QLabel("0 VND")
        self.total_label.setAlignment(Qt.AlignCenter)

        btn_checkout = QPushButton("Thanh toán")
        btn_history = QPushButton("Lịch sử")
        btn_clear_cart = QPushButton("Xóa giỏ hàng")
        btn_manage_menu = QPushButton("Quản lý món")

        btn_checkout.clicked.connect(self.checkout)
        btn_history.clicked.connect(self.show_history)
        btn_clear_cart.clicked.connect(self.clear_cart)
        btn_manage_menu.clicked.connect(self.open_menu_editor)

        cart_actions = QHBoxLayout()
        self.btn_decrease = QPushButton("-")
        self.btn_increase = QPushButton("+")
        self.btn_remove_selected = QPushButton("Xóa món")

        self.btn_decrease.clicked.connect(self.decrease_selected_item)
        self.btn_increase.clicked.connect(self.increase_selected_item)
        self.btn_remove_selected.clicked.connect(self.remove_selected_item)

        cart_actions.addWidget(self.btn_decrease)
        cart_actions.addWidget(self.btn_increase)
        cart_actions.addWidget(self.btn_remove_selected)

        right.addWidget(self.listWidget)
        right.addLayout(cart_actions)
        right.addWidget(self.total_label)
        right.addWidget(btn_clear_cart)
        right.addWidget(btn_manage_menu)
        right.addWidget(btn_checkout)
        right.addWidget(btn_history)

        body.addLayout(left, 3)
        body.addWidget(right_widget, 1)
        right_widget.setMaximumWidth(320)

        main.addLayout(body)

    def load_menu_data(self):
        menu = {
            category: dict(items)
            for category, items in self.default_menu.items()
        }

        if not os.path.exists(self.menu_file):
            return menu

        try:
            with open(self.menu_file, "r", encoding="utf-8") as f:
                saved_menu = json.load(f)

            if not isinstance(saved_menu, dict):
                return menu

            for category in self.category_keys:
                saved_items = saved_menu.get(category, {})
                if isinstance(saved_items, dict):
                    menu[category] = {
                        str(name): int(price)
                        for name, price in saved_items.items()
                    }
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return menu

        return menu

    def open_menu_editor(self):
        dialog = MenuEditorDialog(self.menu, self)
        if dialog.exec_() == QDialog.Accepted:
            self.menu = dialog.get_menu_data()
            self.refresh_current_menu_page()


  
    def build_menu_pages(self):
        while self.stacked.count():
            widget = self.stacked.widget(0)
            self.stacked.removeWidget(widget)
            widget.deleteLater()

        keyword = self.search_input.text().strip().lower()

        for category_key in self.category_keys:
            items = self.menu.get(category_key, {})

            if keyword:
                filtered_items = {
                    name: price
                    for name, price in items.items()
                    if keyword in name.lower()
                }
            else:
                filtered_items = items

            self.stacked.addWidget(
                create_menu_page(self, filtered_items, self.add_item)
            )

        self.stacked.setCurrentIndex(self.current_category_index)

    def change_category(self, index):
        self.current_category_index = index
        self.stacked.setCurrentIndex(index)

    def refresh_current_menu_page(self):
        current_index = self.current_category_index
        self.build_menu_pages()
        self.current_category_index = current_index
        self.stacked.setCurrentIndex(current_index)


    # ADD ITEM

    def add_item(self, name, price):
        if name in self.cart:
            self.cart[name]["qty"] += 1
        else:
            self.cart[name] = {"qty": 1, "price": price}

        self.refresh_cart()

  
    # REFRESH CART
  
    def refresh_cart(self):
        selected_name = self.get_selected_cart_name()

        self.listWidget.clear()
        self.total = 0

        for name, data in self.cart.items():
            qty = data["qty"]
            price = data["price"]

            total_item = qty * price
            self.total += total_item

            item = QListWidgetItem(
                f"{name} x{qty} - {self.format_money(total_item)}đ"
            )
            item.setData(Qt.UserRole, name)
            self.listWidget.addItem(item)

        self.total_label.setText(f"{self.format_money(self.total)} VND")

        if selected_name:
            for index in range(self.listWidget.count()):
                item = self.listWidget.item(index)
                if item.data(Qt.UserRole) == selected_name:
                    self.listWidget.setCurrentItem(item)
                    break

    def get_selected_cart_name(self):
        item = self.listWidget.currentItem()
        if item:
            return item.data(Qt.UserRole)
        return None

    # =========================
    # CART ACTIONS
    # =========================
    def decrease_item(self, name):
        if name in self.cart:
            self.cart[name]["qty"] -= 1
            if self.cart[name]["qty"] <= 0:
                del self.cart[name]
            self.refresh_cart()

    def increase_item(self, name):
        if name in self.cart:
            self.cart[name]["qty"] += 1
            self.refresh_cart()

    def remove_item_completely(self, name):
        if name in self.cart:
            del self.cart[name]
            self.refresh_cart()

    def decrease_selected_item(self):
        name = self.get_selected_cart_name()
        if not name:
            msg.show_warning(self, "Vui lòng chọn món trong giỏ hàng!")
            return
        self.decrease_item(name)

    def increase_selected_item(self):
        name = self.get_selected_cart_name()
        if not name:
            msg.show_warning(self, "Vui lòng chọn món trong giỏ hàng!")
            return
        self.increase_item(name)

    def remove_selected_item(self):
        name = self.get_selected_cart_name()
        if not name:
            msg.show_warning(self, "Vui lòng chọn món trong giỏ hàng!")
            return
        self.remove_item_completely(name)

    def clear_cart(self):
        if not self.cart:
            msg.show_warning(self, "Giỏ hàng đang trống!")
            return

        if not msg.confirm(self, "Xóa toàn bộ giỏ hàng?"):
            return

        self.cart.clear()
        self.refresh_cart()

   
    # REMOVE ITEM
  
    def remove_item(self, item):
        name = item.data(Qt.UserRole)
        if not name:
            name = item.text().split(" x")[0]

        self.decrease_item(name)

   
    # CHECKOUT 
   
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

            if payment_method == "Chuyển khoản":
                order_id = len(self.manager.history) - 1
                self.open_qr_dialog(self.total, order_id)

            msg.show_info(self, "Thanh toán thành công!")

            self.cart.clear()
            self.refresh_cart()

        except Exception as e:
            msg.show_warning(self, f"Lỗi hệ thống: {str(e)}")
    def open_qr_dialog(self, amount, order_id):
        total_amount = self.format_money(amount)
        order_id = f"DH{order_id}"

        qr_url = get_qr_url(amount, order_id) 
        dialog = QRDialog(qr_url)   
        dialog.exec_()
    # HISTORY
  
    def show_history(self):
        dialog = HistoryDialog(self.manager.history, self)
        dialog.exec_()
