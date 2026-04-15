from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from collections import defaultdict


class HistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Lịch sử đơn hàng")
        self.resize(420, 520)

        self.history = history

        layout = QVBoxLayout(self)

        self.listWidget = QListWidget()

        # ===== GROUP THEO NGÀY =====
        grouped = defaultdict(list)

        for order in history:
            date = order["time"].split(" ")[1]
            grouped[date].append(order)

        # ===== HIỂN THỊ =====
        for date in sorted(grouped.keys(), reverse=True):

            orders = grouped[date]

            # 🔥 TÁCH THEO PAYMENT
            cash_orders = [o for o in orders if o.get("payment") == "Tiền mặt"]
            transfer_orders = [o for o in orders if o.get("payment") == "Chuyển khoản"]

            total_cash = sum(o["total"] for o in cash_orders)
            total_transfer = sum(o["total"] for o in transfer_orders)
            total_day = total_cash + total_transfer

            # ===== HEADER NGÀY =====
            header = QListWidgetItem(
                f"📅 {date} | Tổng: {total_day} VND"
            )
            header.setFlags(header.flags() & ~Qt.ItemIsSelectable)
            header.setBackground(Qt.lightGray)
            header.setTextAlignment(Qt.AlignCenter)

            self.listWidget.addItem(header)

            # ===== TIỀN MẶT =====
            if cash_orders:
                sub_header_cash = QListWidgetItem(
                    f"    Tiền mặt: {total_cash} VND"
                )
                sub_header_cash.setFlags(sub_header_cash.flags() & ~Qt.ItemIsSelectable)
                self.listWidget.addItem(sub_header_cash)

                for order in cash_orders:
                    time = order["time"].split(" ")[0]
                    text = f"      {time} - {order['total']} VND"

                    item = QListWidgetItem(text)
                    item.setData(Qt.UserRole, order)

                    self.listWidget.addItem(item)

            # ===== CHUYỂN KHOẢN =====
            if transfer_orders:
                sub_header_transfer = QListWidgetItem(
                    f"    Chuyển khoản: {total_transfer} VND"
                )
                sub_header_transfer.setFlags(sub_header_transfer.flags() & ~Qt.ItemIsSelectable)
                self.listWidget.addItem(sub_header_transfer)

                for order in transfer_orders:
                    time = order["time"].split(" ")[0]
                    text = f"      {time} - {order['total']} VND"

                    item = QListWidgetItem(text)
                    item.setData(Qt.UserRole, order)

                    self.listWidget.addItem(item)

        # ===== CLICK XEM CHI TIẾT =====
        self.listWidget.itemDoubleClicked.connect(self.show_detail)

        layout.addWidget(self.listWidget)

    # ===== CHI TIẾT =====
    def show_detail(self, item):
        order = item.data(Qt.UserRole)

        if not order:
            return

        detail = "\n".join(order["items"])
        payment = order.get("payment", "Không rõ")

        QMessageBox.information(
            self,
            "Chi tiết đơn",
            f"Thời gian: {order['time']}\n"
            f"Thanh toán: {payment}\n\n"
            f"{detail}\n\n"
            f"Tổng: {order['total']} VND"
        )