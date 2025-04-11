import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QMessageBox
from Views.LogIn import Ui_MainWindow as LOGIN
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from Controllers.LogIn_Controller import LoginController


class LogIn(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LOGIN()
        self.ui.setupUi(self)

        print("Login window initialized!")  # Check if this is printed

        # Password hidden
        self.ui.PasswordInput.setEchoMode(QLineEdit.Password)  # Adjusted for PyQt5

        # Initialize login controller with reference to this window
        self.controller = LoginController(self)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        login_window = LogIn()
        login_window.show()
        print("Login window shown successfully!")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")