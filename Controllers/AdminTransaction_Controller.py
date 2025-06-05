from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QWidget

from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Models.Transaction import Transaction
from Views.Admin_Transactions import Ui_Admin_Transactions as AdminTransactionUI

def safe_date_format(date_value, date_format="%B %d, %Y"):
    if not date_value:
        return "N/A"
    if isinstance(date_value, str):
        try:
            # Try parsing if it's a date string
            from datetime import datetime
            return datetime.strptime(date_value, "%Y-%m-%d").strftime(date_format)
        except ValueError:
            return date_value  # Return as-is if parsing fails
    elif hasattr(date_value, 'strftime'):  # If it's a date/datetime object
        return date_value.strftime(date_format)
    return "N/A"

class AdminTransactionsController(QWidget):
    def __init__(self, transactions_ui):
        super().__init__()
        self.ui = AdminTransactionUI()
        self.transactions_ui = transactions_ui
        self.ui.setupUi(self)

        print("Admin Transactions UI initialized!")

        # self.transactions_ui.DashboardButton.clicked.connect(self.view_dashboard_ui)
        # self.transactions_ui.ChargesButton.clicked.connect(self.view_charges_ui)
        # self.transactions_ui.StaffsButton.clicked.connect(self.view_staff_ui)
        # self.transactions_ui.PatientsButton.clicked.connect(self.view_patient_ui)
        self.transactions_ui.ViewTransaction.clicked.connect(self.view_transaction)
        self.refresh_tables()

    def view_transaction(self):
        try:
            selected_row = self.transactions_ui.TransactionTable.currentRow()
            if selected_row == -1:
                print("no row selected")
                return

            transaction_id = self.transactions_ui.TransactionTable.item(selected_row, 0)
            if not transaction_id:
                raise ValueError(f"No patient ID found in selected row")

            transaction_id = transaction_id.text().strip()
            if not transaction_id:
                raise ValueError(f" ID is empty")

            self.view_transaction_details_ui(transaction_id)

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Failed to select patient: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(error_msg)

    def refresh_tables(self):
        try:
            self.load_transaction_table()
            print("Tables refreshed successfully!")
        except Exception as e:
            print(f"Error refreshing tables: {e}")

    def load_transaction_table(self):
        transactions = Transaction.get_all_transaction()  # Assume this returns a list of transactions
        self.transactions_ui.TransactionTable.setRowCount(len(transactions))
        self.transactions_ui.TransactionTable.verticalHeader().setVisible(False)
        self.transactions_ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        for row, transaction in enumerate(transactions):
            checkup = CheckUp.get_checkup_details(transaction["chck_id"])
            patient = Patient.get_patient_details(int(checkup["pat_id"]))
            name = f"{patient['pat_lname']}, {patient['pat_fname']} {patient['pat_mname']}"

            # Populate table columns
            self.transactions_ui.TransactionTable.setItem(row, 0, QTableWidgetItem(str(transaction["chck_id"])))
            self.transactions_ui.TransactionTable.setItem(row, 1, QTableWidgetItem(name))
            self.transactions_ui.TransactionTable.setItem(row, 2, QTableWidgetItem(checkup["chck_diagnoses"]))
            self.transactions_ui.TransactionTable.setItem(row, 3, QTableWidgetItem(safe_date_format(checkup["chck_date"])))

    def view_transaction_details_ui(self, transaction_id):
        try:
            from Controllers.AdminTransactionDetails_Controller import AdminTransactionDetailsController
            self.admin_transaction_controller = AdminTransactionDetailsController(transaction_id)
            self.admin_transaction_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction List Error: {e}")

    def view_patient_ui(self):
        try:
            from Controllers.AdminPatients_Controller import AdminPatientsController
            self.admin_patients_controller = AdminPatientsController()
            self.admin_patients_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction List Error: {e}")

    def view_dashboard_ui(self):
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction List Error: {e}")

    def view_staff_ui(self):
        try:
            from Controllers.AdminStaffs_Controller import AdminStaffsController
            self.admin_staff_controller = AdminStaffsController()
            self.admin_staff_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction List Error: {e}")

    def view_charges_ui(self):
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction List Error: {e}")

