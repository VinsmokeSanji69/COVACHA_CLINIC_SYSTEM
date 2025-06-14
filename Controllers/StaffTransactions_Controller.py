from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget

from Controllers.ClientSocketController import DataRequest
from Controllers.StaffViewTransaction_Controller import StaffViewTransaction
from Views.Staff_Transactions import Ui_Staff_Transactions as StaffTransactionUI

class StaffTransactions(QWidget):
    def __init__(self, transactions_ui):
        super().__init__()
        self.ui = StaffTransactionUI()
        self.transactions_ui = transactions_ui
        self.ui.setupUi(self)

        self.all_checkups = []
        self.load_transaction_details()

        if hasattr(self.transactions_ui, 'ViewButton'):
            self.transactions_ui.ViewButton.clicked.connect(self.view_transaction)

        if hasattr(self.transactions_ui, 'SearchIcon'):
            self.transactions_ui.SearchIcon.clicked.connect(self.search_transactions)

    def load_transaction_details(self):
        try:
            #checkups = CheckUp.get_all_checkups()
            checkups = DataRequest.send_command("GET_ALL_CHECKUP")

            checkups.sort(key=lambda c: c['chck_id'], reverse=True)
            #transactions = Transaction.get_all_transaction()
            transactions = DataRequest.send_command("GET_ALL_TRANSACTION")

            transaction_dict = {tran['chck_id'].strip().lower(): tran['tran_status'] for tran in transactions}

            self.all_checkups = []  # Store for search use
            self.transactions_ui.TransactionTable.clearContents()
            self.transactions_ui.TransactionTable.setRowCount(0)

            for checkup in checkups:
                chck_id = checkup['chck_id'].strip().lower()
                pat_id = checkup['pat_id']
                #patient = Patient.get_patient_details(pat_id)
                patient = DataRequest.send_command("GET_PATIENT_DETAILS", pat_id)

                if not patient:
                    continue

                doc_id = checkup['doc_id']
                #doctor = Doctor.get_doctor(doc_id)
                doctor = DataRequest.send_command("GET_DOCTOR_BY_ID", doc_id)

                if not doctor:
                    continue

                pat_full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                doc_full_name = f"{doctor['last_name'].capitalize()}, {doctor['first_name'].capitalize()}"
                tran_status = transaction_dict.get(chck_id, "Pending")

                self.all_checkups.append({
                    'chck_id': checkup['chck_id'],
                    'patient_name': pat_full_name,
                    'doctor_name': doc_full_name,
                    'tran_status': tran_status
                })

            self.populate_transaction_table(self.all_checkups)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

        self.transactions_ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.transactions_ui.TransactionTable.horizontalHeader().setVisible(True)
        self.transactions_ui.TransactionTable.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.transactions_ui.TransactionTable.verticalHeader().setVisible(False)

    def load_transaction_details(self):
        try:
            #checkups = CheckUp.get_all_checkups()
            checkups = DataRequest.send_command("GET_ALL_CHECKUP")

            checkups.sort(key=lambda c: c['chck_id'], reverse=True)
            #transactions = Transaction.get_all_transaction()
            transactions = DataRequest.send_command("GET_ALL_TRANSACTION")

            transaction_dict = {tran['chck_id'].strip().lower(): tran['tran_status'] for tran in transactions}

            self.all_checkups = []  # Store for search use
            self.transactions_ui.TransactionTable.clearContents()
            self.transactions_ui.TransactionTable.setRowCount(0)

            for checkup in checkups:
                chck_id = checkup['chck_id'].strip().lower()
                pat_id = checkup['pat_id']
                #patient = Patient.get_patient_details(pat_id)
                patient = DataRequest.send_command("GET_PATIENT_DETAILS", pat_id)

                if not patient:
                    continue

                doc_id = checkup['doc_id']
                #doctor = Doctor.get_doctor(doc_id)
                doctor = DataRequest.send_command("GET_DOCTOR_BY_ID", doc_id)

                if not doctor:
                    continue

                pat_full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                doc_full_name = f"{doctor['last_name'].capitalize()}, {doctor['first_name'].capitalize()}"
                tran_status = transaction_dict.get(chck_id, "Pending")

                self.all_checkups.append({
                    'chck_id': checkup['chck_id'],
                    'patient_name': pat_full_name,
                    'doctor_name': doc_full_name,
                    'tran_status': tran_status
                })

            self.populate_transaction_table(self.all_checkups)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

        self.transactions_ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.transactions_ui.TransactionTable.horizontalHeader().setVisible(True)
        self.transactions_ui.TransactionTable.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.transactions_ui.TransactionTable.verticalHeader().setVisible(False)

    def populate_transaction_table(self, checkup_data):
        self.transactions_ui.TransactionTable.setRowCount(0)

        if not checkup_data:
            self.transactions_ui.TransactionTable.setRowCount(1)
            self.transactions_ui.TransactionTable.setColumnCount(
                4)  # Assuming 4 columns (chck_id, patient, doctor, status)

            item = QtWidgets.QTableWidgetItem("No Records Found")
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFlags(QtCore.Qt.ItemIsEnabled)  # Make it non-editable

            self.transactions_ui.TransactionTable.setItem(0, 0, item)
            for col in range(1, 4):  # Empty other columns
                self.transactions_ui.TransactionTable.setItem(0, col, QtWidgets.QTableWidgetItem(""))

            return

        for row, item in enumerate(checkup_data):
            self.transactions_ui.TransactionTable.insertRow(row)
            self.transactions_ui.TransactionTable.setItem(row, 0, QtWidgets.QTableWidgetItem(item['chck_id']))
            self.transactions_ui.TransactionTable.setItem(row, 1, QtWidgets.QTableWidgetItem(item['patient_name']))
            self.transactions_ui.TransactionTable.setItem(row, 2, QtWidgets.QTableWidgetItem(item['doctor_name']))
            self.transactions_ui.TransactionTable.setItem(row, 3, QtWidgets.QTableWidgetItem(item['tran_status']))

    def search_transactions(self):
        keyword = self.transactions_ui.Search.text().strip().lower()
        if not keyword:
            self.populate_transaction_table(self.all_checkups)
            return

        filtered = [
            checkup for checkup in self.all_checkups
            if keyword in checkup['chck_id'].lower()
               or keyword in checkup['patient_name'].lower()
               or keyword in checkup['doctor_name'].lower()
               or keyword in checkup['tran_status'].lower()
        ]
        self.populate_transaction_table(filtered)

    def view_transaction(self):
        try:
            # Get the currently selected row
            selected_row = self.transactions_ui.TransactionTable.currentRow()
            if selected_row == -1:
                QtWidgets.QMessageBox.warning(
                    self,
                    "No Selection",
                    "Please select a transaction to view."
                )
                return

            # Retrieve the chck_id from the first column of the selected row
            chck_id_item = self.transactions_ui.TransactionTable.item(selected_row, 0)
            if not chck_id_item or not chck_id_item.text():
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to retrieve check-up ID from the selected row."
                )
                return

            chck_id = chck_id_item.text().strip()

            # Ensure chck_id is a valid string
            if not isinstance(chck_id, str) or not chck_id:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Invalid check-up ID retrieved from the selected row."
                )
                return

            # Open the StaffViewTransaction modal with the selected chck_id
            self.staff_transaction_view = StaffViewTransaction(chck_id=chck_id, parent=self)
            self.staff_transaction_view.show()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")



