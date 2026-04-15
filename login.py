from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


class Ui_Form(object):
    def setupUi(self, Form):
        Form.resize(500, 360)
sdsasadasd
        # ===== MAIN LAYOUT =====
        self.mainLayout = QVBoxLayout(Form)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        # ===== HEADER =====
        self.header = QLabel("STARBUG")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFixedHeight(65)
        self.header.setStyleSheet("""
            background-color: #006241;
            color: white;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        self.mainLayout.addWidget(self.header)

        # ===== CENTER =====
        self.centerWidget = QWidget()
        self.centerLayout = QVBoxLayout(self.centerWidget)
        self.centerLayout.setAlignment(Qt.AlignCenter)

        # ===== LOGIN BOX =====
        self.loginBox = QWidget()
        self.loginBox.setFixedSize(330, 270)
        self.loginBox.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
        """)

        # ===== SHADOW =====
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.loginBox.setGraphicsEffect(shadow)

        # ===== FORM LAYOUT =====
        self.formLayout = QVBoxLayout(self.loginBox)
        self.formLayout.setContentsMargins(25, 25, 25, 25)
        self.formLayout.setSpacing(12)

        # ===== TITLE =====
        self.title = QLabel("Sign in")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            color:#006241;
            font-size:20px;
            font-weight:bold;
        """)
        self.formLayout.addWidget(self.title)

        # ===== USERNAME =====
        self.formLayout.addWidget(QLabel("Username"))
        self.username = QLineEdit()
        self.username.setFixedHeight(32)
        self.username.setStyleSheet("""
            border: 1px solid #ccc;
            border-radius: 8px;
            padding-left: 8px;
        """)
        self.formLayout.addWidget(self.username)

        # ===== PASSWORD =====
        self.formLayout.addWidget(QLabel("Password"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(32)
        self.password.setStyleSheet("""
            border: 1px solid #ccc;
            border-radius: 8px;
            padding-left: 8px;
        """)
        self.formLayout.addWidget(self.password)

        # ===== LOGIN BUTTON (FIX MÀU XANH) =====
        self.loginBtn = QPushButton("Log in")
        self.loginBtn.setFixedHeight(40)
        self.loginBtn.setCursor(Qt.PointingHandCursor)

        self.loginBtn.setStyleSheet("""
            QPushButton {
                background-color: #006241;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #007a52;
            }
            QPushButton:pressed {
                background-color: #004d33;
            }
        """)

        self.formLayout.addWidget(self.loginBtn)

        # ===== ADD TO CENTER =====
        self.centerLayout.addWidget(self.loginBox)
        self.mainLayout.addWidget(self.centerWidget)