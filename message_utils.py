from PyQt5.QtWidgets import QMessageBox


def show_warning(parent, text):
    QMessageBox.warning(parent, "Thông báo", text)


def show_info(parent, text):
    QMessageBox.information(parent, "Thành công", text)


def confirm(parent, text):
    reply = QMessageBox.question(
        parent,
        "Xác nhận",
        text,
        QMessageBox.Yes | QMessageBox.No
    )
    return reply == QMessageBox.Yes