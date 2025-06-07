from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox
from Controllers.StaffViewTransaction_Controller import StaffViewTransaction
from Views.Staff_Transactions import Ui_Staff_Transactions as StaffTransactionUI
from Models.Transaction import Transaction
from Models.Doctor import Doctor
from Models.CheckUp import CheckUp
from Models.Patient import Patient


class StaffTransactions(QWidget):
    def __init__(self, transactions_ui):
        super().__init__()
        self.ui = StaffTransactionUI()
        self.transactions_ui = transactions_ui
        self.ui.setupUi(self)

        # Debug print
        print("Initializing StaffTransactions...")

        # Load initial transaction data
        self.load_transaction_details()

        # Connect search functionality
        self.is_filtering = False
        self.transactions_ui.SearchIcon.clicked.connect(self.search_transactions)

        # View Button
        if hasattr(self.transactions_ui, 'ViewButton'):
            self.transactions_ui.ViewButton.clicked.connect(self.view_transaction)

    def search_transactions(self):
        """Filter transactions based on search input."""
        search_term = self.transactions_ui.Search.text().strip().lower()
        print(f"Searching for: '{search_term}'")  # DEBUG

        if not search_term:
            self.is_filtering = False
            self.load_transaction_details()
            return
        else:
            self.is_filtering = True

        # Clear table
        self.transactions_ui.TransactionTable.setRowCount(0)

        try:
            checkups = CheckUp.get_all_checkups()
            if not checkups:
                self.show_no_results()
                return

            checkups.sort(key=lambda x: x['chck_id'].strip(), reverse=True)
            transactions = Transaction.get_all_transaction()
            transaction_dict = {tran['chck_id'].strip().lower(): tran['tran_status'] for tran in transactions}

            match_found = False
            for checkup in checkups:
                chck_id = checkup['chck_id'].strip().lower()
                pat_id = checkup['pat_id']
                doc_id = checkup['doc_id']

                patient = Patient.get_patient_details(pat_id)
                doctor = Doctor.get_doctor(doc_id)

                if not patient or not doctor:
                    continue

                pat_full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                doc_full_name = f"{doctor['last_name'].capitalize()}, {doctor['first_name'].capitalize()}"
                tran_status = transaction_dict.get(chck_id, "Pending")

                if (search_term in chck_id or
                    search_term in pat_full_name.lower() or
                    search_term in doc_full_name.lower() or
                    search_term in tran_status.lower()):

                    match_found = True
                    row = self.transactions_ui.TransactionTable.rowCount()
                    self.transactions_ui.TransactionTable.insertRow(row)
                    self.transactions_ui.TransactionTable.setItem(row, 0, QtWidgets.QTableWidgetItem(chck_id))
                    self.transactions_ui.TransactionTable.setItem(row, 1, QtWidgets.QTableWidgetItem(pat_full_name))
                    self.transactions_ui.TransactionTable.setItem(row, 2, QtWidgets.QTableWidgetItem(doc_full_name))
                    self.transactions_ui.TransactionTable.setItem(row, 3, QtWidgets.QTableWidgetItem(tran_status))

            if not match_found:
                self.show_no_results()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search error: {e}")

    def show_no_results(self):
        """Display 'No records found' message"""
        self.transactions_ui.TransactionTable.setRowCount(1)
        item = QtWidgets.QTableWidgetItem("No records found.")
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.transactions_ui.TransactionTable.setItem(0, 0, item)
        for col in range(1, 4):
            self.transactions_ui.TransactionTable.setItem(0, col, QtWidgets.QTableWidgetItem(""))

    def load_transaction_details(self):
        """Load all transaction details into the table."""
        try:
            checkups = CheckUp.get_all_checkups()
            if not checkups:
                return

            checkups.sort(key=lambda x: x['chck_id'].strip(), reverse=True)
            transactions = Transaction.get_all_transaction()
            transaction_dict = {tran['chck_id'].strip().lower(): tran['tran_status'] for tran in transactions}

            self.transactions_ui.TransactionTable.setRowCount(0)

            for row, checkup in enumerate(checkups):
                chck_id = checkup['chck_id'].strip().lower()
                pat_id = checkup['pat_id']
                doc_id = checkup['doc_id']

                patient = Patient.get_patient_details(pat_id)
                doctor = Doctor.get_doctor(doc_id)

                if not patient or not doctor:
                    continue

                pat_full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                doc_full_name = f"{doctor['last_name'].capitalize()}, {doctor['first_name'].capitalize()}"
                tran_status = transaction_dict.get(chck_id, "Pending")

                self.transactions_ui.TransactionTable.insertRow(row)
                self.transactions_ui.TransactionTable.setItem(row, 0, QtWidgets.QTableWidgetItem(chck_id))
                self.transactions_ui.TransactionTable.setItem(row, 1, QtWidgets.QTableWidgetItem(pat_full_name))
                self.transactions_ui.TransactionTable.setItem(row, 2, QtWidgets.QTableWidgetItem(doc_full_name))
                self.transactions_ui.TransactionTable.setItem(row, 3, QtWidgets.QTableWidgetItem(tran_status))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

        self.transactions_ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.transactions_ui.TransactionTable.horizontalHeader().setVisible(True)
        self.transactions_ui.TransactionTable.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.transactions_ui.TransactionTable.verticalHeader().setVisible(False)

    def view_transaction(self):
        try:
            selected_row = self.transactions_ui.TransactionTable.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "No Selection", "Please select a transaction to view.")
                return

            chck_id_item = self.transactions_ui.TransactionTable.item(selected_row, 0)
            if not chck_id_item or not chck_id_item.text():
                QMessageBox.critical(self, "Error", "Failed to retrieve check-up ID from the selected row.")
                return

            chck_id = chck_id_item.text().strip()
            self.staff_transaction_view = StaffViewTransaction(chck_id=chck_id, parent=self)
            self.staff_transaction_view.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")