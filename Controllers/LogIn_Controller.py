from PyQt5.QtWidgets import QMessageBox, QMainWindow
from Models.DB_Connection import DBConnection
from Controllers.AdminDashboard_Controller import AdminDashboardController
from Controllers.StaffDashboard_Controller import StaffDashboardController
from Controllers.DoctorDashboard_Controller import DoctorDashboardController
import hashlib
import bcrypt
import traceback

class LoginController:
    ADMIN_ID = "100000"

    def __init__(self, login_window):
        self.login_window = login_window
        self.login_window.ui.SignInButton.clicked.connect(self.handle_login)
        self.login_window.ui.UserIDInput.setPlaceholderText("User ID")
        self.login_window.ui.PasswordInput.setPlaceholderText("Password")

        # Debugging print to confirm the connection
        print("SignInButton connected to handle_login method!")

        # Test connection at initialization
        if not DBConnection.test_connection():
            QMessageBox.critical(
                login_window,
                "Database Error",
                "Cannot connect to database. Application may not function properly."
            )

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

        conn = None
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                return  # Error message already shown by DBConnection

            # Check if the user is an admin
            if user_id == self.ADMIN_ID:
                self._handle_admin_login(conn, password)
                return

            # Check if the user is a doctor (5-digit ID)
            if len(user_id) == 5 and user_id.isdigit():
                doctor = self._get_user(conn, "doctor", user_id)
                if doctor and self._verify_hashed_password(password, doctor[4]):
                    self._show_dashboard(DoctorDashboardController, doctor)
                    return
                else:
                    QMessageBox.warning(
                        self.login_window,
                        "Login Failed",
                        "Incorrect doctor password"
                    )
                    return

            # Check if the user is a staff member
            staff = self._get_user(conn, "staff", user_id)
            if staff:
                # DEBUG: Print verification details before checking
                print("\n--- DEBUG INFO ---")
                print(f"Input password: {password}")
                print(f"Stored hash: {staff[3]}")
                print(f"Generated SHA-256: {hashlib.sha256(password.encode()).hexdigest()}")
                print(f"Verification result: {self._verify_hashed_password(password, staff[3])}")
                print("------------------\n")

                if self._verify_hashed_password(password, staff[3]):
                    # Route to StaffDashboardController for non-admin staff
                    if user_id != self.ADMIN_ID:
                        self._show_dashboard(StaffDashboardController, staff)
                    return
                else:
                    QMessageBox.warning(
                        self.login_window,
                        "Login Failed",
                        "Incorrect staff password"
                    )
                    return

            # If no match found in any table
            QMessageBox.warning(
                self.login_window,
                "Login Failed",
                "Invalid credentials"
            )

        except Exception as e:
            QMessageBox.critical(
                self.login_window,
                "Error",
                f"Login error: {str(e)}"
            )
            traceback.print_exc()
        finally:
            if conn:
                conn.close()

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

        conn = None
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                return  # Error message already shown by DBConnection

            # Check if the user is an admin
            if user_id == self.ADMIN_ID:
                self._handle_admin_login(conn, password)
                return

            # Check if the user is a doctor (5-digit ID)
            if len(user_id) == 5 and user_id.isdigit():
                doctor = self._get_user(conn, "doctor", user_id)
                if doctor and self._verify_hashed_password(password, doctor[4]):
                    self._show_dashboard(DoctorDashboardController, doctor)
                    return
                else:
                    QMessageBox.warning(
                        self.login_window,
                        "Login Failed",
                        "Incorrect doctor password"
                    )
                    return

            # Check if the user is a staff member
            staff = self._get_user(conn, "staff", user_id)
            if staff:
                if self._verify_hashed_password(password, staff[3]):
                    # Route to StaffDashboardController for non-admin staff
                    if user_id != self.ADMIN_ID:
                        self._show_dashboard(StaffDashboardController, staff)
                    return
                else:
                    QMessageBox.warning(
                        self.login_window,
                        "Login Failed",
                        "Incorrect staff password"
                    )
                    return

            # If no match found in any table
            QMessageBox.warning(
                self.login_window,
                "Login Failed",
                "Invalid credentials"
            )

        except Exception as e:
            QMessageBox.critical(
                self.login_window,
                "Error",
                f"Login error: {str(e)}"
            )
            traceback.print_exc()
        finally:
            if conn:
                conn.close()

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
            self.admin_dashboard = AdminDashboardController()
            self.admin_dashboard.show()
            self.login_window.close()

        else:
            QMessageBox.warning(
                self.login_window,
                "Login Failed",
                "Incorrect admin password"
            )

    def _get_user(self, conn, table, user_id):
        """Generic user retrieval from database"""
        cursor = conn.cursor()
        if table == "staff":
            cursor.execute(
                "SELECT staff_id, staff_fname, staff_lname, staff_password FROM staff WHERE staff_id = %s",
                (user_id,)
            )
        elif table == "doctor":
            cursor.execute(
                "SELECT doc_id, doc_fname, doc_lname, doc_specialty, doc_password FROM doctor WHERE doc_id = %s",
                (user_id,)
            )
        return cursor.fetchone()

    def _verify_hashed_password(self, input_password, stored_hash):
        """Verify password against stored hash"""
        try:
            # First check if it's a bcrypt hash
            if stored_hash.startswith("$2a$") or stored_hash.startswith("$2b$"):
                return bcrypt.checkpw(input_password.encode(), stored_hash.encode())

            # Otherwise assume it's SHA-256
            input_hash = hashlib.sha256(input_password.encode()).hexdigest()

            # DEBUG: Print comparison details
            print(f"Comparing hashes:\nInput: {input_hash}\nStored: {stored_hash}")

            # Compare with stored hash (case-insensitive)
            return input_hash.lower() == stored_hash.lower()
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    def _show_dashboard(self, dashboard_controller, user):
        if dashboard_controller == DoctorDashboardController:
            # Pass doc_id, fname, lname, and specialty to DoctorDashboardController
            self.dashboard = dashboard_controller(
                doc_id=user[0],
                fname=user[1],
                lname=user[2],
                specialty=user[3]
            )
        elif dashboard_controller == StaffDashboardController:
            # Pass only the staff_id to the StaffDashboardController
            self.dashboard = dashboard_controller(staff_id=user[0])
        else:
            self.dashboard = dashboard_controller()

        # Close the login window
        self.login_window.close()

        # Show the dashboard
        self.dashboard.show()