from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog, QVBoxLayout, QPushButton, \
    QStackedWidget, QHeaderView, QSizePolicy, QWidget
from PyQt5.QtCore import QTimer, pyqtSlot, Qt
from Views.Staff_Dashboard import Ui_Staff_Dashboard
from Controllers.StaffAddLabAttachment_Controller import StaffAddAttachment
from Controllers.ClientSocketController import DataRequest
from Controllers.StaffAddCheckUp_Controller import StaffAddCheckUp
from Controllers.StaffLabRequest_Controller import StaffLabRequest
from Controllers.StaffTransactionModal_Controller import StaffTransactionModal
from Controllers.StaffTransactions_Controller import StaffTransactions

from datetime import datetime

from Views.Staff_LabRequest import Ui_Staff_LabRequest
from Views.Staff_Transactions import Ui_Staff_Transactions


class StaffDashboardController(QMainWindow):
    def __init__(self, staff_id=None, login_window=None):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Staff Dashboard")

        # Store staff ID
        self.staff_id = staff_id

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout for central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create a shared single navbar
        self.navbar_ui = Ui_Staff_Dashboard()

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

        # Start with dashboard view
        self.go_to_dashboard()

        # Responsive for Staff Dashboard Page
        header = self.dashboard_ui.PendingTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.dashboard_ui.PendingTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dashboard_ui.PendingTable.setWordWrap(True)
        self.dashboard_ui.PendingTable.resizeRowsToContents()

        # Responsive for Staff Transaction Page
        header = self.transactions_ui.TransactionTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.transactions_ui.TransactionTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.transactions_ui.TransactionTable.setWordWrap(True)
        self.transactions_ui.TransactionTable.resizeRowsToContents()

        # Responsive table for LabReq Page
        header = self.labreq_ui.LabRequestTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.labreq_ui.LabRequestTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.labreq_ui.LabRequestTable.setWordWrap(True)
        self.labreq_ui.LabRequestTable.resizeRowsToContents()

        self.staff_transactions = StaffTransactions(self.transactions_ui)
        self.staff_labrequests = StaffLabRequest(self.labreq_ui)

        # Calling Methods
        self.load_pending_checkups()
        self.get_transaction_details()
        self.get_labrequest_details()

        # Table styles
        self.apply_table_styles(self.dashboard_ui.PendingTable)
        self.apply_table_styles(self.transactions_ui.TransactionTable)
        self.apply_table_styles(self.labreq_ui.LabRequestTable)

    def setup_pages(self):
        """Set up complete pages with navbar and content"""
        # Dashboard page
        self.dashboard_page = QWidget()
        self.dashboard_ui = Ui_Staff_Dashboard()
        self.dashboard_ui.setupUi(self.dashboard_page)
        self.page_stack.addWidget(self.dashboard_page)

        # Transactions page
        self.transactions_page = QWidget()
        self.transactions_ui = Ui_Staff_Transactions()
        self.transactions_ui.setupUi(self.transactions_page)
        self.page_stack.addWidget(self.transactions_page)

        # LabReq page
        self.labreq_page = QWidget()
        self.labreq_ui = Ui_Staff_LabRequest()
        self.labreq_ui.setupUi(self.labreq_page)
        self.page_stack.addWidget(self.labreq_page)

    def connect_all_buttons(self):
        """Connect navigation buttons for all pages"""
        # Connect dashboard page buttons
        self.dashboard_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.dashboard_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.dashboard_ui.LabButton.clicked.connect(self.go_to_labreq)
        self.dashboard_ui.LogOutButton.clicked.connect(self.logout)

        # Connect transactions page buttons
        self.transactions_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.transactions_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.transactions_ui.LabButton.clicked.connect(self.go_to_labreq)
        self.transactions_ui.LogOutButton.clicked.connect(self.logout)  # Add this line

        # Connect labreq page buttons
        self.labreq_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.labreq_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.labreq_ui.LabButton.clicked.connect(self.go_to_labreq)
        self.labreq_ui.LogOutButton.clicked.connect(self.logout)  # Add this line

        # # Connect buttons
        if hasattr(self.dashboard_ui, 'AddCheckUpButton'):
            self.dashboard_ui.AddCheckUpButton.clicked.connect(self.open_checkup_user_form)
        else:
            pass
        if hasattr(self.dashboard_ui, 'AddTransactionButton'):
            self.dashboard_ui.AddTransactionButton.clicked.connect(self.open_transaction_modal)

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
                self.hide()
            if hasattr(self, "deleteLater"):
                QTimer.singleShot(0, self.deleteLater)

            # 3. Show login window
            if hasattr(self, "login_window") and self.login_window:
                self.login_window.ui.UserIDInput.clear()
                self.login_window.ui.PasswordInput.clear()
                self.login_window.show()
            else:
                from Views.LogIn import LogInWindow
                from Controllers.LogIn_Controller import LoginController
                from Controllers.LogIn_Controller import LoginController

                login_window = LogInWindow()
                LoginController(login_window)
                login_window.show()

        except Exception as e:
            pass

    @pyqtSlot()
    def go_to_dashboard(self):
        self.page_stack.setCurrentWidget(self.dashboard_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_transactions(self):
        self.page_stack.setCurrentWidget(self.transactions_page)
        self.staff_transactions.load_transaction_details()
        self.update_time_labels()

    @pyqtSlot()
    def go_to_labreq(self):
        self.page_stack.setCurrentWidget(self.labreq_page)
        self.update_time_labels()


    def apply_table_styles(self, table_widget):
        # Ensure horizontal headers are visible
        table_widget.horizontalHeader().setVisible(True)

        # Align headers to the left
        table_widget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Hide the vertical header (row index)
        table_widget.verticalHeader().setVisible(False)

        # Set selection behavior
        table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def load_pending_checkups(self):
        """Fetch and display today's pending check-ups in the PendingTable."""
        try:
            # Fetch all pending check-ups
            pending_checkups  = DataRequest.send_command("GET_PENDING_CHECKUP")

            # Get today's date in YYYYMMDD format
            today_date = datetime.now().strftime("%Y%m%d")

            # Filter check-ups for today only
            todays_checkups = [
                checkup for checkup in pending_checkups
                if checkup["chck_id"].startswith(today_date)
            ]

            # Clear the table
            self.dashboard_ui.PendingTable.setRowCount(0)

            # Handle case: No check-ups for today
            if not todays_checkups:
                self.dashboard_ui.PendingTable.insertRow(0)
                no_data_item = QTableWidgetItem("No Check Ups For Today")
                self.dashboard_ui.PendingTable.setItem(0, 0, no_data_item)

                column_count = self.dashboard_ui.PendingTable.columnCount()
                self.dashboard_ui.PendingTable.setSpan(0, 0, 1, column_count)
                return

            # Populate the table with today's check-ups
            for row, checkup in enumerate(todays_checkups):
                pat_id = checkup["pat_id"]
                chck_id = checkup["chck_id"]
                chck_type = checkup["chckup_type"]

                # Fetch patient details
                patient = DataRequest.send_command("GET_PATIENT_BY_ID",pat_id)
                if not patient:
                    continue

                full_name = f"{patient['last_name'].capitalize()}, {patient['first_name'].capitalize()}"

                self.dashboard_ui.PendingTable.insertRow(row)
                self.dashboard_ui.PendingTable.setItem(row, 0, QTableWidgetItem(chck_id))
                self.dashboard_ui.PendingTable.setItem(row, 1, QTableWidgetItem(full_name))
                self.dashboard_ui.PendingTable.setItem(row, 2, QTableWidgetItem(chck_type))

            self.dashboard_ui.PendingTable.resizeColumnsToContents()
            self.dashboard_ui.PendingTable.setColumnWidth(0, 150)
            self.dashboard_ui.PendingTable.setColumnWidth(1, 150)
            self.dashboard_ui.PendingTable.setColumnWidth(2, 200)

        except Exception as e:
            pass

    def open_checkup_user_form(self):
        try:
            # Pass the staff_id and a refresh callback to the AddCheckUp form
            self.add_checkup_window = StaffAddCheckUp(parent=self, staff_id=self.staff_id)
            self.add_checkup_window.refresh_callback = self.load_pending_checkups
            self.add_checkup_window.show()
        except Exception as e:
            pass

    def open_transaction_modal(self):
        """Open the StaffTransaction modal."""
        try:
            # Open the modal window with a reference to the parent (dashboard)
            self.add_transaction_window = StaffTransactionModal(parent=self, staff_dashboard=self)
            self.add_transaction_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Add Transaction Modal: {e}")

    def ViewStaffLabRequest(self):
        try:
            # Instantiate and show the AdminStaffsController window
            self.staff_request_controller = StaffLabRequest(self.staff_id)
            self.staff_request_controller.show()
            self.hide()  # Hide the current dashboard window
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")

    def setup_ui(self):
        self.update_time_labels()

    def update_time_labels(self):
        """Update time labels on the current page"""
        now = datetime.now()
        current_page_index = self.page_stack.currentIndex()

        if current_page_index == 0:  # Dashboard
            ui = self.dashboard_ui
        elif current_page_index == 1:  # Transactions
            ui = self.transactions_ui
        else:
            return

        if hasattr(ui, 'Time'):
            ui.Time.setText(now.strftime("%I:%M %p"))
        if hasattr(ui, 'Day'):
            ui.Day.setText(now.strftime("%A"))
        if hasattr(ui, 'Month'):
            ui.Month.setText(f"{now.strftime('%B')} {now.day}, {now.year}")



    def open_modify_form(self):
        """Open the Modify Lab Req Form as a modal dialog"""
        try:
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Modify Lab Req")

            # Remove all margins and spacing
            dialog_layout = QVBoxLayout(dialog)
            dialog_layout.setContentsMargins(0, 0, 0, 0)
            dialog_layout.setSpacing(0)

            # Add your custom form widget
            modify_form = StaffAddAttachment(chck_id=None, doctorname=None, patientname=None)
            dialog_layout.addWidget(modify_form)

            # Cancel button functionality
            cancel_button = dialog.findChild(QPushButton, 'Cancel')
            if cancel_button:
                cancel_button.clicked.connect(dialog.reject)

            # Optional: remove title bar buttons (X, Min, Max)
            dialog.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)

            # Size settings
            dialog.setMinimumWidth(600)
            dialog.setMinimumHeight(400)

            # Show the modal dialog
            dialog.exec_()

        except Exception as e:
            pass

    def get_transaction_details(self):
        try:
            self.staff_transactions.load_transaction_details()  # Call method from StaffTransactions instance
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

    def get_labrequest_details(self):
        try:
            self.staff_labrequests.load_staff_labrequest_table()  # Call your existing method
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load lab request details: {e}")





