from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QHeaderView, QSizePolicy

from Controllers.AdminPatients_Controller import AdminPatientsController
from Controllers.AdminStaffs_Controller import AdminStaffsController
from Controllers.AdminTransaction_Controller import AdminTransactionsController
from Controllers.AdminCharges_Controller import AdminChargesController  # Add this import
from Controllers.AdminPatientDetails_Controller import AdminPatientDetailsController
from Views.Admin_Charges import Ui_Admin_Charges
from Views.Admin_Dashboard import Ui_Admin_Dashboard as AdminDashboardUI, Ui_Admin_Dashboard
from Models.Admin import Admin
import datetime
from Views.Admin_Patients import Ui_Admin_Patients
from Views.Admin_Staffs import Ui_Admin_Staff
from Views.Admin_Transactions import Ui_Admin_Transactions

class AdminDashboardController(QMainWindow):
    def __init__(self, login_window=None):
        super().__init__()
        self.ui = AdminDashboardUI()
        self.login_window = login_window
        self.ui.setupUi(self)

        print("Admin Dashboard UI initialized!")

        self.load_counts()

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout for central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create a shared single navbar
        self.navbar_ui = Ui_Admin_Dashboard()

        # Create stacked widget for page content (navbar + content area for each page)
        self.page_stack = QStackedWidget()
        self.main_layout.addWidget(self.page_stack)

        # Initialize pages
        self.setup_pages()

        # Setup timer for time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_labels)
        self.timer.start(1000)

        # Connect navigation buttons - will be connected for each page
        self.connect_all_buttons()

        # Initialize controller instances AFTER setting up pages
        self.admin_staff = AdminStaffsController(self.staff_ui)
        self.admin_records = AdminPatientsController(self.records_ui)
        self.admin_transactions = AdminTransactionsController(self.transactions_ui)
        self.admin_charges = AdminChargesController(self.charges_ui)  # Add this line

        # Start with dashboard view
        self.go_to_dashboard()

        # Responsive for Admin Staffs View Page
        header = self.staff_ui.DoctorTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.staff_ui.DoctorTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.staff_ui.DoctorTable.setWordWrap(True)
        self.staff_ui.DoctorTable.resizeRowsToContents()

        header = self.staff_ui.StaffTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.staff_ui.StaffTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.staff_ui.StaffTable.setWordWrap(True)
        self.staff_ui.StaffTable.resizeRowsToContents()

        # Responsive for Admin Records
        header = self.records_ui.PatientTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.records_ui.PatientTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.records_ui.PatientTable.setWordWrap(True)
        self.records_ui.PatientTable.resizeRowsToContents()

        # Responsive for Admin Transactions
        header = self.transactions_ui.TransactionTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.transactions_ui.TransactionTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.transactions_ui.TransactionTable.setWordWrap(True)
        self.transactions_ui.TransactionTable.resizeRowsToContents()

        # Responsive for Admin Charges
        header = self.charges_ui.DoctorTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.charges_ui.DoctorTable.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.charges_ui.DoctorTable.setWordWrap(True)
        self.charges_ui.DoctorTable.resizeRowsToContents()

        header = self.charges_ui.LaboratoryTestTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.charges_ui.LaboratoryTestTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.charges_ui.LaboratoryTestTable.setWordWrap(True)
        self.charges_ui.LaboratoryTestTable.resizeRowsToContents()

    def setup_pages(self):
        """Set up complete pages with navbar and content"""
        # Dashboard page
        self.dashboard_page = QWidget()
        self.dashboard_ui = Ui_Admin_Dashboard()
        self.dashboard_ui.setupUi(self.dashboard_page)
        self.page_stack.addWidget(self.dashboard_page)

        # Staff page
        self.staff_page = QWidget()
        self.staff_ui = Ui_Admin_Staff()
        self.staff_ui.setupUi(self.staff_page)
        self.page_stack.addWidget(self.staff_page)

        # Records page - Patients
        self.records_page = QWidget()
        self.records_ui = Ui_Admin_Patients()
        self.records_ui.setupUi(self.records_page)
        self.page_stack.addWidget(self.records_page)

        # Transactions page
        self.transactions_page = QWidget()
        self.transactions_ui = Ui_Admin_Transactions()
        self.transactions_ui.setupUi(self.transactions_page)
        self.page_stack.addWidget(self.transactions_page)

        # Charges page
        self.charges_page = QWidget()
        self.charges_ui = Ui_Admin_Charges()
        self.charges_ui.setupUi(self.charges_page)
        self.page_stack.addWidget(self.charges_page)

    def connect_all_buttons(self):
        """Connect navigation buttons for all pages"""
        # Connect dashboard page buttons
        self.dashboard_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.dashboard_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.dashboard_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.dashboard_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.dashboard_ui.ChargesButton.clicked.connect(self.go_to_charges)
        self.dashboard_ui.LogOutButton.clicked.connect(self.logout)

        # Connect staff page buttons
        self.staff_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.staff_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.staff_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.staff_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.staff_ui.ChargesButton.clicked.connect(self.go_to_charges)

        # Connect records page buttons
        self.records_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.records_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.records_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.records_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.records_ui.ChargesButton.clicked.connect(self.go_to_charges)

        # Connect transactions page buttons
        self.transactions_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.transactions_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.transactions_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.transactions_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.transactions_ui.ChargesButton.clicked.connect(self.go_to_charges)

        # Connect charges page buttons
        self.charges_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.charges_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.charges_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.charges_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.charges_ui.ChargesButton.clicked.connect(self.go_to_charges)

    @pyqtSlot()
    def logout(self):
        """Return to the login screen and clear the credentials."""
        try:
            # 1. Cleanup and delete all tracked windows
            for window in getattr(self, "open_windows", []):
                if window and hasattr(window, "deleteLater"):
                    window.deleteLater()

            # 2. Close and delete dashboard safely
            if hasattr(self, "cleanup"):
                self.cleanup()
            if hasattr(self, "hide"):
                self.hide()  # Prefer hide over deleteLater to avoid premature deletion
            if hasattr(self, "deleteLater"):
                QTimer.singleShot(0, self.deleteLater)  # Delay deletion

            # 3. Show login window
            if hasattr(self, "login_window") and self.login_window:
                self.login_window.ui.UserIDInput.clear()
                self.login_window.ui.PasswordInput.clear()
                self.login_window.show()
            else:
                from Views.LogIn import LogInWindow
                from Controllers.Login_Controller import LoginController

                login_window = LogInWindow()
                LoginController(login_window)
                login_window.show()
        except Exception as e:
            print("Logout error:", e)

    @pyqtSlot()
    def go_to_dashboard(self):
        self.page_stack.setCurrentWidget(self.dashboard_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_staffs(self):
        self.page_stack.setCurrentWidget(self.staff_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_records(self):
        self.page_stack.setCurrentWidget(self.records_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_transactions(self):
        self.page_stack.setCurrentWidget(self.transactions_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_charges(self):
        self.page_stack.setCurrentWidget(self.charges_page)
        self.update_time_labels()
        # Refresh the charges tables when navigating to charges page
        if hasattr(self, 'admin_charges'):
            self.admin_charges.refresh_tables()

    def update_time_labels(self):
        now = datetime.datetime.now()
        current_page_index = self.page_stack.currentIndex()

        if current_page_index == 0:  # Dashboard
            ui = self.dashboard_ui
        elif current_page_index == 1:  # Staff
            ui = self.staff_ui
        elif current_page_index == 2:   # Records - Patients
            ui = self.records_ui
        elif current_page_index == 3:   # Transactions
            ui = self.transactions_ui
        elif current_page_index == 4:   # Charges
            ui = self.charges_ui
        else:
            return

        if hasattr(ui, 'Time'):
            ui.Time.setText(now.strftime("%I:%M %p"))
        if hasattr(ui, 'Day'):
            ui.Day.setText(now.strftime("%A"))
        if hasattr(ui, 'Month'):
            ui.Month.setText(f"{now.strftime('%B')} {now.day}, {now.year}")

    def load_counts(self):
        try:
            # Count doctors
            doctor_count = Admin.count_doctor()
            self.ui.TotalDoctor.setText(str(doctor_count))

            # Count staff
            staff_count = Admin.count_staff()
            self.ui.TotalStaff.setText(str(staff_count))

            print(f"Loaded counts - Doctors: {doctor_count}, Staff: {staff_count}")

        except Exception as e:
            print(f"Dashboard: {e}")