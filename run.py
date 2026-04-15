import sys
from PyQt5.QtWidgets import QApplication, QWidget

from ui_main import POS
from login import Ui_Form
import message_utils as msg


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.setWindowTitle("STARBUG - Đăng nhập")
        self.ui.loginBtn.clicked.connect(self.handle_login)
        self.ui.username.setFocus()

    def handle_login(self):
        user = self.ui.username.text().strip()
        pwd = self.ui.password.text()

        self.ui.username.setText(user)

        if user == "admin" and pwd == "123":
            self.pos = POS(user)
            self.pos.show()
            self.close()
        else:
            msg.show_warning(self, "Sai tài khoản hoặc mật khẩu!")
            self.ui.password.clear()
            self.ui.password.setFocus()

# mấy thg chó c7-102
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("STARBUG POS")

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())