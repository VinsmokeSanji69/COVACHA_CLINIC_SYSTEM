from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog, QVBoxLayout, QPushButton, \
    QStackedWidget, QHeaderView, QSizePolicy, QWidget
from PyQt5.QtCore import QTimer, pyqtSlot, Qt

from Controllers.StaffAddLabAttachment_Controller import StaffAddAttachment
from Models.Doctor import Doctor
from Models.Transaction import Transaction
from Views.Staff_Dashboard import Ui_Staff_Dashboard
from Controllers.StaffAddCheckUp_Controller import StaffAddCheckUp
from Controllers.StaffLabRequest_Controller import StaffLabRequest
from Controllers.StaffTransactionModal_Controller import StaffTransactionModal
from Controllers.StaffTransactions_Controller import StaffTransactions
from Models.CheckUp import CheckUp
from  Models.Patient import Patient
import datetime

from Views.Staff_LabRequest import Ui_Staff_LabRequest
from Views.Staff_Transactions import Ui_Staff_Transactions


class StaffDashboardController(QMainWindow):
    def __init__(self, staff_id=None):
        super().__init__()
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

        # # Responsive table for Dashboard Page
        # # tableWidget
        # header = self.dashboard_ui.PendingTable.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.Stretch)
        #
        # self.dashboard_ui.PendingTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.dashboard_ui.PendingTable.setWordWrap(True)
        # self.dashboard_ui.PendingTable.resizeRowsToContents()
        #
        # # # Responsive table for Record Page
        # # # DoneTable
        # # header = self.records_ui.DoneTable.horizontalHeader()
        # # header.setSectionResizeMode(QHeaderView.Stretch)
        # #
        # # self.records_ui.DoneTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # # self.records_ui.DoneTable.setWordWrap(True)
        # # self.records_ui.DoneTable.resizeRowsToContents()
        #
        # # Responsive table for Transaction Page
        # # DoneTable
        # header = self.transactions_ui.TransactionTable.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.Stretch)
        #
        # self.transactions_ui.TransactionTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.transactions_ui.TransactionTable.setWordWrap(True)
        # self.transactions_ui.TransactionTable.resizeRowsToContents()

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

        # # Records page
        # self.records_page = QWidget()
        # self.records_ui = Ui_Staff_Records()
        # self.records_ui.setupUi(self.records_page)
        # self.page_stack.addWidget(self.records_page)

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

        # Connect transactions page buttons
        self.transactions_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.transactions_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.transactions_ui.LabButton.clicked.connect(self.go_to_labreq)

        # Connect labreq page buttons
        self.labreq_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.labreq_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.labreq_ui.LabButton.clicked.connect(self.go_to_labreq)

        # # Connect buttons
        if hasattr(self.dashboard_ui, 'AddCheckUpButton'):
            self.dashboard_ui.AddCheckUpButton.clicked.connect(self.open_checkup_user_form)
        else:
            # print("Missing!")
            pass
        if hasattr(self.dashboard_ui, 'AddTransactionButton'):
            self.dashboard_ui.AddTransactionButton.clicked.connect(self.open_transaction_modal)

    @pyqtSlot()
    def go_to_dashboard(self):
        self.page_stack.setCurrentWidget(self.dashboard_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_transactions(self):
        self.page_stack.setCurrentWidget(self.transactions_page)
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

    def load_pending_checkupss(self):
        """Fetch and display pending check-ups in the PatientDetails table."""
        try:
            pending_checkups = CheckUp.get_pending_checkups()
            # print("Fetched pending checkups:", pending_checkups)

            self.dashboard_ui.PendingTable.setRowCount(0)

            if not pending_checkups:
                # print("No pending check-ups found.")
                self.dashboard_ui.PendingTable.insertRow(0)
                no_data_item = QTableWidgetItem("No Pending Check Ups")
                self.dashboard_ui.PendingTable.setItem(0, 0, no_data_item)

                column_count = self.dashboard_ui.PendingTable.columnCount()
                self.dashboard_ui.PendingTable.setSpan(0, 0, 1, column_count)
                return

            for row, checkup in enumerate(pending_checkups):
                pat_id = checkup["pat_id"]
                chck_id = checkup["chck_id"]
                chck_type = checkup["chckup_type"]

                patient = Patient.get_patient_by_id(pat_id)
                if not patient:
                    # print(f"No patient found for pat_id={pat_id}")
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
            # print(f"Error loading pending check-ups: {e}")
            pass

    def open_checkup_user_form(self):
        # print("Opening Add Check-Up Form...")
        try:
            # Pass the staff_id and a refresh callback to the AddCheckUp form
            self.add_checkup_window = StaffAddCheckUp(parent=self, staff_id=self.staff_id)
            self.add_checkup_window.refresh_callback = self.load_pending_checkups
            self.add_checkup_window.show()
            # print("Add Check-Up Form shown successfully!")
        except Exception as e:
            # print(f"Error opening Add Check-Up Form: {e}")
            pass

    def open_transaction_modal(self):
        """Open the StaffTransaction modal."""
        # print("Opening Add Transaction Modal...")
        try:
            # Open the modal window with a reference to the parent (dashboard)
            self.add_transaction_window = StaffTransactionModal(parent=self, staff_dashboard=self)
            self.add_transaction_window.show()
            # print("Add Transaction Modal shown successfully!")
        except Exception as e:
            # print(f"Error opening Add Transaction Modal: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Add Transaction Modal: {e}")

    def ViewStaffLabRequest(self):
        # print("Opening staff lab request feature")
        try:
            # Instantiate and show the AdminStaffsController window
            self.staff_request_controller = StaffLabRequest(self.staff_id)
            self.staff_request_controller.show()
            self.hide()  # Hide the current dashboard window
        except Exception as e:
            # print(f"Error loading tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")

    def setup_ui(self):
        self.update_time_labels()

    def update_time_labels(self):
        """Update time labels on the current page"""
        now = datetime.datetime.now()
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

    # def open_transaction_form(self):
    #     """Open the Add Transaction Form"""
    #     print("Opening Add Transaction Form...")
    #     # Implement transaction form functionality here

    def open_modify_form(self):
        """Open the Modify Lab Req Form as a modal dialog"""
        # print("Opening Modify Lab Req Dialog...")
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

            print("Modify Form closed")
        except Exception as e:
            # print(f"Error opening Modify Form Dialog: {e}")
            pass

    def get_transaction_details(self):
        try:
            self.staff_transactions.load_transaction_details()  # Call method from StaffTransactions instance
        except Exception as e:
            # print(f"Error loading transaction details: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

    def get_labrequest_details(self):
        try:
            self.staff_labrequests.load_staff_labrequest_table()  # Call your existing method
        except Exception as e:
            # print(f"Error loading lab request details: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load lab request details: {e}")