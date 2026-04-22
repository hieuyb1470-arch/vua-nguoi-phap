import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from message_utils import slugify


def format_money(value):
    return f"{value:,}".replace(",", ".")


def create_menu_page(parent, items, add_callback):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("border:none;")

    container = QWidget()
    grid = QGridLayout(container)
    grid.setSpacing(15)
    grid.setContentsMargins(10, 10, 10, 10)

    row, col = 0, 0

    for name, price in items.items():

        # OUTER FRAME (KHUNG NGOÀI)
        outer = QFrame()
        outer.setFixedSize(160, 190)
        outer.setStyleSheet("""
            QFrame {
                background: #f5f5f5;
                border-radius: 14px;
            }
        """)

        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(6, 6, 6, 6)

        # BUTTON CARD (KHUNG TRONG - CLICKABLE)

        card = QPushButton()
        card.setCursor(Qt.PointingHandCursor)
        card.setFixedSize(148, 178)

        card.setStyleSheet("""
            QPushButton {
                background: white;
                border-radius: 12px;
                border: 1px solid #ddd;
            }
            QPushButton:hover {
                background: #e6f4ee;
                border: 1px solid #007042;
            }
            QPushButton:pressed {
                background: #d4f5e9;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(5, 5, 5, 5)
        card_layout.setSpacing(4)


        # IMAGE
  
        img = QLabel()
        img.setFixedHeight(80)
        img.setAlignment(Qt.AlignCenter)

        image_base = os.path.join(
            os.path.dirname(__file__),
            "images",
            slugify(name)
        )

        image_path = None
        for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            candidate = image_base + ext
            if os.path.exists(candidate):
                image_path = candidate
                break

        if image_path:
            pixmap = QPixmap(image_path).scaled(
                120, 80,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            img.setPixmap(pixmap)
        else:
            img.setText("🍽️")
            img.setStyleSheet("font-size:22px;")

  
        # NAME
  
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight:bold;font-size:12px;")

        # PRICE
   
        price_label = QLabel(f"{format_money(price)}đ")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("""
            color:#007042;
            font-weight:bold;
            font-size:12px;
        """)

        card_layout.addWidget(img)
        card_layout.addWidget(name_label)
        card_layout.addWidget(price_label)

        # CLICK EVENT 
        card.clicked.connect(lambda _, n=name, p=price: add_callback(n, p))

        outer_layout.addWidget(card)

        grid.addWidget(outer, row, col)

        col += 1
        if col == 5:
            col = 0
            row += 1

    scroll.setWidget(container)
    return scroll
