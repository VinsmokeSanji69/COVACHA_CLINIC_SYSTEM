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
        self.transactions_ui.SearchIcon.clicked.connect(self.apply_search_filter)
        self.transactions_ui.ViewTransaction.clicked.connect(self.view_transaction)
        self.refresh_tables()

    def view_transaction(self):
        try:
            selected_row = self.transactions_ui.TransactionTable.currentRow()
            if selected_row == -1:
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

    def refresh_tables(self):
        self.load_transaction_table()


    def apply_search_filter(self):
        search_text = self.transactions_ui.Search.text().strip().lower()
        self.load_transaction_table(search_text)

    def load_transaction_table(self, search_term=None):
        try:
            transactions = Transaction.get_all_transaction()
            filtered_transactions = []

            for transaction in transactions:
                if "chck_id" not in transaction:
                    continue

                chck_id = transaction["chck_id"]
                checkup = CheckUp.get_checkup_details(chck_id)
                if not checkup:
                    continue

                pat_id = checkup.get("pat_id")
                if not pat_id:
                    continue

                patient = Patient.get_patient_details(int(pat_id))
                if not patient:
                    continue

                name = f"{patient['pat_lname']}, {patient['pat_fname']} {patient['pat_mname']}"
                date_str = safe_date_format(checkup["chck_date"])

                if search_term:
                    combined_text = f"{name} {date_str}".lower()
                    if search_term not in combined_text:
                        continue

                filtered_transactions.append((chck_id, name, date_str))  # Removed diagnosis

            # Update the table
            table = self.transactions_ui.TransactionTable
            table.clearContents()
            table.setRowCount(0)
            table.setColumnCount(3)  # Now only 3 columns: chck_id, name, date
            table.verticalHeader().setVisible(False)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

            if not filtered_transactions:
                table.setRowCount(1)
                table.setColumnCount(3)
                table.setItem(0, 0, QTableWidgetItem("No Records Found"))
                table.setSpan(0, 0, 1, 3)  # Span across all columns
                for col in range(1, 3):
                    table.setItem(0, col, QTableWidgetItem(""))
                return

            table.setRowCount(len(filtered_transactions))
            for row, (chck_id, name, date_str) in enumerate(filtered_transactions):
                table.setItem(row, 0, QTableWidgetItem(str(chck_id)))
                table.setItem(row, 1, QTableWidgetItem(name))
                table.setItem(row, 2, QTableWidgetItem(date_str))

        except Exception as e:
            pass

    def view_transaction_details_ui(self, transaction_id):
        from Controllers.AdminTransactionDetails_Controller import AdminTransactionDetailsController
        self.admin_transaction_controller = AdminTransactionDetailsController(transaction_id)
        self.admin_transaction_controller.show()
        self.hide()


    def view_patient_ui(self):
        from Controllers.AdminPatients_Controller import AdminPatientsController
        self.admin_patients_controller = AdminPatientsController()
        self.admin_patients_controller.show()
        self.hide()


    def view_dashboard_ui(self):
        from Controllers.AdminDashboard_Controller import AdminDashboardController
        self.admin_dashboard_controller = AdminDashboardController()
        self.admin_dashboard_controller.show()
        self.hide()


    def view_staff_ui(self):
        from Controllers.AdminStaffs_Controller import AdminStaffsController
        self.admin_staff_controller = AdminStaffsController()
        self.admin_staff_controller.show()
        self.hide()


    def view_charges_ui(self):
        from Controllers.AdminCharges_Controller import AdminChargesController
        self.admin_charges_controller = AdminChargesController()
        self.admin_charges_controller.show()
        self.hide()


