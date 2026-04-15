import json
import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class MenuEditorDialog(QDialog):
    def __init__(self, menu_data, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Quản lý món")
        self.resize(560, 460)

        self.images_dir = os.path.join(os.path.dirname(__file__), "images")
        self.menu_file = os.path.join(os.path.dirname(__file__), "menu_data.json")

        self.menu_data = {
            category: dict(items)
            for category, items in (menu_data or {}).items()
        }
        self.selected_image_path = ""

        os.makedirs(self.images_dir, exist_ok=True)

        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Thêm / bớt món và cập nhật ảnh")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:16px;font-weight:bold;color:#006241;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.fill_form_from_item)
        layout.addWidget(self.list_widget)

        form_widget = QVBoxLayout()

        form = QFormLayout()
        self.category_input = QComboBox()
        self.category_input.addItems(["coffee", "juice", "dessert"])

        self.name_input = QLineEdit()
        self.price_input = QSpinBox()
        self.price_input.setRange(1000, 1000000)
        self.price_input.setSingleStep(5000)

        self.image_label = QLabel("Chưa chọn ảnh")
        self.image_label.setWordWrap(True)

        form.addRow("Danh mục", self.category_input)
        form.addRow("Tên món", self.name_input)
        form.addRow("Giá", self.price_input)
        form.addRow("Ảnh", self.image_label)

        form_widget.addLayout(form)

        image_actions = QHBoxLayout()
        btn_choose_image = QPushButton("Chọn ảnh")
        btn_clear_image = QPushButton("Bỏ ảnh")
        btn_choose_image.clicked.connect(self.choose_image)
        btn_clear_image.clicked.connect(self.clear_image_selection)
        image_actions.addWidget(btn_choose_image)
        image_actions.addWidget(btn_clear_image)
        form_widget.addLayout(image_actions)

        actions = QHBoxLayout()
        btn_add_update = QPushButton("Lưu món")
        btn_remove = QPushButton("Xóa món")
        btn_close = QPushButton("Đóng")

        btn_add_update.clicked.connect(self.save_item)
        btn_remove.clicked.connect(self.remove_item)
        btn_close.clicked.connect(self.accept)

        actions.addWidget(btn_add_update)
        actions.addWidget(btn_remove)
        actions.addWidget(btn_close)
        form_widget.addLayout(actions)

        layout.addLayout(form_widget)

    def refresh_list(self):
        self.list_widget.clear()

        category_titles = {
            "coffee": "Coffee",
            "juice": "Juice",
            "dessert": "Dessert",
        }

        for category in ["coffee", "juice", "dessert"]:
            header = QListWidgetItem(f"[{category_titles.get(category, category)}]")
            header.setFlags(header.flags() & ~Qt.ItemIsSelectable)
            self.list_widget.addItem(header)

            items = self.menu_data.get(category, {})
            for name, price in sorted(items.items()):
                item = QListWidgetItem(f"  {name} - {self.format_money(price)}đ")
                item.setData(Qt.UserRole, {"category": category, "name": name, "price": price})
                self.list_widget.addItem(item)

    def format_money(self, value):
        return f"{int(value):,}".replace(",", ".")

    def slugify(self, text):
        slug = text.strip().lower()
        replacements = {
            " ": "_",
            "á": "a", "à": "a", "ả": "a", "ã": "a", "ạ": "a",
            "ă": "a", "ắ": "a", "ằ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
            "â": "a", "ấ": "a", "ầ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
            "đ": "d",
            "é": "e", "è": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
            "ê": "e", "ế": "e", "ề": "e", "ể": "e", "ễ": "e", "ệ": "e",
            "í": "i", "ì": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
            "ó": "o", "ò": "o", "ỏ": "o", "õ": "o", "ọ": "o",
            "ô": "o", "ố": "o", "ồ": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
            "ơ": "o", "ớ": "o", "ờ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
            "ú": "u", "ù": "u", "ủ": "u", "ũ": "u", "ụ": "u",
            "ư": "u", "ứ": "u", "ừ": "u", "ử": "u", "ữ": "u", "ự": "u",
            "ý": "y", "ỳ": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
        }
        for src, dst in replacements.items():
            slug = slug.replace(src, dst)

        cleaned = []
        for ch in slug:
            if ch.isalnum() or ch == "_":
                cleaned.append(ch)
            elif ch in "-.":
                cleaned.append("_")

        return "".join(cleaned).strip("_")

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn ảnh món",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp)"
        )
        if not file_path:
            return

        self.selected_image_path = file_path
        self.image_label.setText(os.path.basename(file_path))

    def clear_image_selection(self):
        self.selected_image_path = ""
        self.image_label.setText("Chưa chọn ảnh")

    def fill_form_from_item(self, item):
        data = item.data(Qt.UserRole)
        if not data:
            return

        self.category_input.setCurrentText(data["category"])
        self.name_input.setText(data["name"])
        self.price_input.setValue(int(data["price"]))
        self.clear_image_selection()

    def copy_image_for_item(self, item_name):
        if not self.selected_image_path:
            return

        ext = os.path.splitext(self.selected_image_path)[1].lower() or ".jpg"
        filename = f"{self.slugify(item_name)}{ext}"
        target_path = os.path.join(self.images_dir, filename)
        shutil.copyfile(self.selected_image_path, target_path)

    def remove_existing_images(self, item_name):
        base = self.slugify(item_name)
        for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            path = os.path.join(self.images_dir, f"{base}{ext}")
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def save_item(self):
        category = self.category_input.currentText().strip()
        name = self.name_input.text().strip()
        price = int(self.price_input.value())

        if not category:
            QMessageBox.warning(self, "Thông báo", "Chưa chọn danh mục!")
            return

        if not name:
            QMessageBox.warning(self, "Thông báo", "Tên món không được để trống!")
            return

        if category not in self.menu_data:
            self.menu_data[category] = {}

        old_name = None
        current_item = self.list_widget.currentItem()
        if current_item:
            item_data = current_item.data(Qt.UserRole)
            if item_data:
                old_name = item_data.get("name")

        if old_name and old_name != name:
            if old_name in self.menu_data.get(category, {}):
                del self.menu_data[category][old_name]
            self.remove_existing_images(old_name)

        self.menu_data[category][name] = price

        if self.selected_image_path:
            self.remove_existing_images(name)
            self.copy_image_for_item(name)

        self.refresh_list()
        self.persist_menu()
        QMessageBox.information(self, "Thành công", "Đã lưu món thành công!")

    def remove_item(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn món để xóa!")
            return

        data = current_item.data(Qt.UserRole)
        if not data:
            QMessageBox.warning(self, "Thông báo", "Hãy chọn một món hợp lệ!")
            return

        category = data["category"]
        name = data["name"]

        reply = QMessageBox.question(
            self,
            "Xác nhận",
            f"Xóa món '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        if name in self.menu_data.get(category, {}):
            del self.menu_data[category][name]

        self.remove_existing_images(name)
        self.refresh_list()
        self.persist_menu()
        self.name_input.clear()
        self.price_input.setValue(1000)
        self.clear_image_selection()

    def persist_menu(self):
        try:
            with open(self.menu_file, "w", encoding="utf-8") as f:
                json.dump(self.menu_data, f, ensure_ascii=False, indent=4)
        except OSError as e:
            QMessageBox.warning(self, "Thông báo", f"Không thể lưu menu: {e}")

    def get_menu_data(self):
        return {
            category: dict(items)
            for category, items in self.menu_data.items()
        }
