import platform
import re
import socket
import subprocess
from functools import lru_cache

from PyQt5.QtWidgets import QMessageBox

import hashlib
import bcrypt

ADMIN_MAC_ADDRESS = "74:04:F1:4E:E6:02"

def _verify_hashed_password(input_password, stored_hash):
    """Verify password against stored hash"""
    try:
        # First check if it's a bcrypt hash
        if stored_hash.startswith("$2a$") or stored_hash.startswith("$2b$"):
            return bcrypt.checkpw(input_password.encode(), stored_hash.encode())

        # Otherwise assume it's SHA-256
        input_hash = hashlib.sha256(input_password.encode()).hexdigest()

        # Compare with stored hash (case-insensitive)
        return input_hash.lower() == stored_hash.lower()
    except Exception as e:
        return False

def normalize_mac(mac):
    """Normalize MAC to uppercase colon-separated format"""
    mac = mac.replace('-', ':').replace('.', ':').upper()
    return mac

class LoginController:
    ADMIN_ID = "100000"

    def __init__(self, login_window):
        self.login_window = login_window
        self.login_window.ui.SignInButton.clicked.connect(self.handle_login)
        self.login_window.ui.UserIDInput.setPlaceholderText("User ID")
        self.login_window.ui.PasswordInput.setPlaceholderText("Password")

    def handle_login(self):
        user_id = self.login_window.ui.UserIDInput.text().strip()
        password = self.login_window.ui.PasswordInput.text().strip()

        if not user_id or not password:
            QMessageBox.warning(
                self.login_window,
                "Input Error",
                "Please enter both ID and password"
            )
            return

        try:
            # Check if the user is an admin
            if user_id == self.ADMIN_ID:
                admin_mac_found = False
                try:
                    # Cross-platform MAC address detection
                    if platform.system() == "Windows":
                        # Windows implementation
                        result = subprocess.check_output("getmac", shell=True).decode()
                        macs = re.findall(r"([0-9A-F-]{17})", result.upper())
                    else:
                        # Linux/Mac implementation
                        result = subprocess.check_output(
                            ["ifconfig"] + (["-a"] if platform.system() != "Darwin" else []),
                            stderr=subprocess.DEVNULL).decode()
                        macs = re.findall(r"ether ([0-9a-f:]{17})", result.lower())
                        macs = [m.upper() for m in macs]

                    # Check if admin MAC is present
                    admin_mac_found = any(
                        normalize_mac(mac) == normalize_mac(ADMIN_MAC_ADDRESS)
                        for mac in macs
                    )
                except Exception as e:
                    print(f"MAC detection error: {e}")
                    admin_mac_found = False

                if not admin_mac_found:
                    QMessageBox.critical(
                        self.login_window,
                        "Access Denied",
                        "Admin login only allowed from authorized devices.\n"
                    )
                    return

                conn = None
                try:
                    from Models.DB_Connection import DBConnection
                    conn = DBConnection.get_db_connection()
                    if not conn:
                        QMessageBox.critical(
                            self.login_window,
                            "Database Error",
                            "Failed to connect to the admin database.\n\n"
                            "Please ensure:\n"
                            "1. The database server is running\n"
                            "2. Your network connection is stable\n"
                            "3. You have proper permissions"
                        )
                        return

                    self._handle_admin_login(conn, password)
                    return
                finally:
                    if conn:
                        conn.close()

                # Check if the user is a doctor (5-digit ID)
            if len(user_id) == 5 and user_id.isdigit():
                from Controllers.ClientSocketController import DataRequest
                doctor = DataRequest.send_command("GET_USER", ["doctor", user_id])
                print(doctor)
                if not doctor:
                    QMessageBox.warning(
                         self.login_window,
                        "Login Failed",
                        "Doctor ID not found."
                    )
                    return

                if _verify_hashed_password(password, doctor[4]):
                    from Controllers.DoctorDashboard_Controller import DoctorDashboardController
                    self._show_dashboard(DoctorDashboardController, doctor)
                    return
                else:
                    QMessageBox.warning(
                        self.login_window,
                        "Login Failed",
                        "Incorrect doctor password."
                    )
                    return

                # Check if the user is a staff member
            from Controllers.ClientSocketController import DataRequest
            staff = DataRequest.send_command("GET_USER", ["staff", user_id])
            print(staff)
            if not staff:
                QMessageBox.warning(
                    self.login_window,
                    "Login Failed",
                    "Staff ID not found."
                )
                return

            if _verify_hashed_password(password, staff[3]):
                if user_id != self.ADMIN_ID:
                    from Controllers.StaffDashboard_Controller import StaffDashboardController
                    self._show_dashboard(StaffDashboardController, staff)
                return
            else:
                QMessageBox.warning(
                    self.login_window,
                    "Login Failed",
                    "Incorrect staff password."
                )
                return

                # Fallback for invalid credentials
            QMessageBox.warning(
                self.login_window,
                "Login Failed",
                "Invalid credentials."
            )

        except Exception as e:
            QMessageBox.critical(
                self.login_window,
                "Login Error",
                f"An error occurred during login: \n"
                f"Please ensure the database server is running\n"
            )


    def _handle_admin_login(self, conn, password):
        """Special handling for admin login with plaintext password"""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT staff_id, staff_fname, staff_lname, staff_password FROM staff WHERE staff_id = %s",
            (self.ADMIN_ID,)
        )
        admin = cursor.fetchone()

        if not admin:
            QMessageBox.warning(
                self.login_window,
                "Login Failed",
                "Admin account not found"
            )
            return

        if password == admin[3]:  # Plaintext comparison
            # Show the admin dashboard modally
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard = AdminDashboardController(login_window=self.login_window)
            self.admin_dashboard.show()
            self.login_window.close()

        else:
            QMessageBox.warning(
                self.login_window,
                "Login Failed",
                "Incorrect admin password"
            )

    def _show_dashboard(self, dashboard_controller, user):
        from Controllers.DoctorDashboard_Controller import DoctorDashboardController
        from Controllers.StaffDashboard_Controller import StaffDashboardController

        if dashboard_controller == DoctorDashboardController:
            self.dashboard = dashboard_controller(
                doc_id=user[0],
                fname=user[1],
                lname=user[2],
                specialty=user[3],
                login_window=self.login_window  # ← NEW
            )

        elif dashboard_controller == StaffDashboardController:
            self.dashboard = dashboard_controller(
                staff_id=user[0],
                login_window=self.login_window
            )
        else:
            self.dashboard = dashboard_controller(login_window=self.login_window)

        # 2. “hide”, don’t close, so we can bring it back later
        self.login_window.hide()

        # 3. show dashboard
        self.dashboard.show()
