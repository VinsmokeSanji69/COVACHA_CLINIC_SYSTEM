import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QMessageBox
from Views.LogIn import Ui_Login as LOGIN

# Add root path for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from Controllers.LogIn_Controller import LoginController
from socket_server import SocketServer
import psutil


def get_mac_address():
    """Get the MAC address of the primary network interface"""
    try:
        interfaces = psutil.net_if_addrs()
        for interface in ['Wi-Fi', 'Ethernet', 'eth0', 'wlan0']:
            if interface in interfaces:
                for addr in interfaces[interface]:
                    if addr.family == psutil.AF_LINK:
                        return addr.address.replace('-', ':').upper()
        return None
    except Exception:
        return None

class LogIn(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LOGIN()
        self.ui.setupUi(self)
        self.ui.PasswordInput.setEchoMode(QLineEdit.Password)
        self.controller = LoginController(self)


if __name__ == "__main__":
    try:
        # Check if this machine has the admin MAC address
        ADMIN_MAC_ADDRESS = "40:1A:58:BF:52:B8"
        current_mac = get_mac_address()

        if current_mac and current_mac.upper() == ADMIN_MAC_ADDRESS.upper():
            # Only start server if this is the admin machine
            socket_server = SocketServer()
            socket_server.start()
            print("✅ Socket server started (admin machine)")
        else:
            print("⚠️ Socket server not started - not admin machine")
            print(f"Current MAC: {current_mac}, Admin MAC: {ADMIN_MAC_ADDRESS}")

        # Start the PyQt5 application
        app = QApplication(sys.argv)
        login_window = LogIn()
        login_window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"An error occurred: {e}")
        QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")