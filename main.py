import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QMessageBox
from Views.LogIn import Ui_Login as LOGIN
# Add root path for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from Controllers.LogIn_Controller import LoginController
from socket_server import SocketServer

class LogIn(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LOGIN()
        self.ui.setupUi(self)

        print("Login window initialized!")

        self.ui.PasswordInput.setEchoMode(QLineEdit.Password)
        self.controller = LoginController(self)

if __name__ == "__main__":
    try:
        # Start the socket server in the background
        socket_server = SocketServer()
        socket_server.start()
        print("Socket server started in background.")

        # Start the PyQt5 application
        app = QApplication(sys.argv)
        login_window = LogIn()
        login_window.show()
        print("Login window shown successfully!")

        # Run the event loop
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")