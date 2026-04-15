from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class HistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Lịch sử đơn hàng")
        self.resize(420, 520)

        self.history = history or []

        layout = QVBoxLayout(self)

        self.listWidget = QListWidget()

        grouped = defaultdict(list)

        for order in self.history:
            date = self.extract_date(order.get("time", ""))
            grouped[date].append(order)

        for date in sorted(grouped.keys(), reverse=True):
            orders = grouped[date]

            cash_orders = [o for o in orders if o.get("payment") == "Tiền mặt"]
            transfer_orders = [o for o in orders if o.get("payment") == "Chuyển khoản"]
            other_orders = [o for o in orders if o.get("payment") not in ["Tiền mặt", "Chuyển khoản"]]

            total_cash = sum(self.parse_money(o.get("total", 0)) for o in cash_orders)
            total_transfer = sum(self.parse_money(o.get("total", 0)) for o in transfer_orders)
            total_other = sum(self.parse_money(o.get("total", 0)) for o in other_orders)
            total_day = total_cash + total_transfer + total_other

            header = QListWidgetItem(
                f"📅 {date} | Tổng: {self.format_money(total_day)} VND"
            )
            header.setFlags(header.flags() & ~Qt.ItemIsSelectable)
            header.setBackground(Qt.lightGray)
            header.setTextAlignment(Qt.AlignCenter)
            self.listWidget.addItem(header)

            self.add_payment_group("Tiền mặt", cash_orders, total_cash)
            self.add_payment_group("Chuyển khoản", transfer_orders, total_transfer)

            if other_orders:
                self.add_payment_group("Khác", other_orders, total_other)

        self.listWidget.itemDoubleClicked.connect(self.show_detail)

        layout.addWidget(self.listWidget)

    def format_money(self, value):
        return f"{self.parse_money(value):,}".replace(",", ".")

    def parse_money(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def extract_date(self, time_text):
        text = str(time_text).strip()

        if not text:
            return "Không rõ ngày"

        parts = text.split(" ")
        if len(parts) >= 2:
            return parts[-1]

        return text

    def extract_time(self, time_text):
        text = str(time_text).strip()

        if not text:
            return "Không rõ giờ"

        parts = text.split(" ")
        if len(parts) >= 2:
            return parts[0]

        return text

    def normalize_items(self, items):
        normalized = []

        if not isinstance(items, list):
            return normalized

        for item in items:
            if isinstance(item, dict):
                name = str(item.get("name", "")).strip()
                qty = self.parse_money(item.get("qty", 1))
                if qty <= 0:
                    qty = 1
                price = self.parse_money(item.get("price", 0))

                if name:
                    normalized.append({
                        "name": name,
                        "qty": qty,
                        "price": price
                    })

            elif isinstance(item, str):
                text = item.strip()
                if text:
                    normalized.append({
                        "name": text,
                        "qty": 1,
                        "price": 0
                    })

        return normalized

    def add_payment_group(self, label, orders, total_amount):
        if not orders:
            return

        sub_header = QListWidgetItem(
            f"    {label}: {self.format_money(total_amount)} VND"
        )
        sub_header.setFlags(sub_header.flags() & ~Qt.ItemIsSelectable)
        self.listWidget.addItem(sub_header)

        for order in orders:
            time_text = self.extract_time(order.get("time", ""))
            total_text = self.format_money(order.get("total", 0))
            text = f"      {time_text} - {total_text} VND"

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, order)
            self.listWidget.addItem(item)

    def build_detail_text(self, order):
        lines = []
        total_from_items = 0

        for item in self.normalize_items(order.get("items", [])):
            line_total = item["qty"] * item["price"]
            total_from_items += line_total

            if item["price"] > 0:
                lines.append(
                    f"- {item['name']} x{item['qty']} | {self.format_money(item['price'])}đ | {self.format_money(line_total)}đ"
                )
            else:
                lines.append(f"- {item['name']} x{item['qty']}")

        if not lines:
            lines.append("Không có chi tiết món")

        order_total = self.parse_money(order.get("total", total_from_items))
        payment = order.get("payment", "Không rõ") or "Không rõ"
        time_text = order.get("time", "Không rõ thời gian") or "Không rõ thời gian"

        return (
            f"Thời gian: {time_text}\n"
            f"Thanh toán: {payment}\n\n"
            f"{chr(10).join(lines)}\n\n"
            f"Tổng: {self.format_money(order_total)} VND"
        )

    def show_detail(self, item):
        order = item.data(Qt.UserRole)

        if not order:
            return

        QMessageBox.information(
            self,
            "Chi tiết đơn",
            self.build_detail_text(order)
        )