import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


def create_menu_page(parent, items, add_callback):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("border:none;")

    widget = QWidget()
    grid = QGridLayout(widget)
    grid.setSpacing(10)

    row, col = 0, 0

    for name, price in items.items():
        card = QFrame()
        card.setFixedSize(150, 140)

        card.setStyleSheet("""
            QFrame {
                background:white;
                border-radius:10px;
            }
            QFrame:hover {
                background:#f1f2f6;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(6, 6, 6, 6)

        img = QLabel()
        img.setFixedHeight(80)
        img.setAlignment(Qt.AlignCenter)

        path = os.path.join(
            os.path.dirname(__file__),
            "images",
            name.lower().replace(" ", "_").replace("á", "a") + ".jpg"
        )

        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(
                120, 80,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            img.setPixmap(pixmap)
        else:
            img.setText("No Image")

        text = QLabel(f"{name}\n{price}đ")
        text.setAlignment(Qt.AlignCenter)

        layout.addWidget(img)
        layout.addWidget(text)

        card.mousePressEvent = lambda e, n=name, p=price: add_callback(n, p)

        grid.addWidget(card, row, col)

        col += 1
        if col == 5:
            col = 0
            row += 1

    scroll.setWidget(widget)
    return scroll