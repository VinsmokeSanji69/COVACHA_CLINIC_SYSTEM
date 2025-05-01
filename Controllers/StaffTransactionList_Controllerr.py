from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow
from Views.Staff_TransactionList import Ui_MainWindow as StaffTransactionListUI
from Models.Transaction import Transaction
from Models.Doctor import Doctor
from Models.CheckUp import CheckUp
from Models.Patient import Patient

class StaffTransactionList(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = StaffTransactionListUI()
        self.ui.setupUi(self)
        self.apply_table_styles()
        self.load_transaction_details()


    def apply_table_styles(self):

        self.ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.TransactionTable.horizontalHeader().setVisible(True)
        self.ui.TransactionTable.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.ui.TransactionTable.verticalHeader().setVisible(False)

    def load_transaction_details(self):
        try:
            # Fetch all completed check-ups
            checkups = CheckUp.get_all_checkups()
            if not checkups:
                print("No completed check-ups found.")
                return

            # Fetch all transactions to determine their status
            transactions = Transaction.get_all_transaction()
            transaction_dict = {tran['chck_id'].strip().lower(): tran['tran_status'] for tran in transactions}

            # Debug: Log all chck_id from transactions
            print(f"All transaction chck_id: {list(transaction_dict.keys())}")

            # Clear the table before populating it
            self.ui.TransactionTable.clearContents()
            self.ui.TransactionTable.setRowCount(0)

            # Populate the table
            for row, checkup in enumerate(checkups):
                chck_id = checkup['chck_id'].strip().lower()

                # Debug: Log the current chck_id
                print(f"Processing chck_id: {chck_id}")

                # Fetch patient details
                pat_id = checkup['pat_id']
                patient = Patient.get_patient_details(pat_id)
                if not patient:
                    print(f"No patient found for pat_id={pat_id}")
                    continue

                # Fetch doctor details
                doc_id = checkup['doc_id']
                doctor = Doctor.get_doctor_by_id(doc_id)
                if not doctor:
                    print(f"No doctor found for doc_id={doc_id}")
                    continue

                # Format patient and doctor names
                pat_full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                doc_full_name = f"{doctor['doc_lname'].capitalize()}, {doctor['doc_fname'].capitalize()}"

                # Determine the transaction status
                tran_status = transaction_dict.get(chck_id, "Pending")

                # Debug: Log the transaction status
                print(f"Transaction status for chck_id {chck_id}: {tran_status}")

                # Insert data into the table
                self.ui.TransactionTable.insertRow(row)
                self.ui.TransactionTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(chck_id)))  # Check-up ID
                self.ui.TransactionTable.setItem(row, 1, QtWidgets.QTableWidgetItem(pat_full_name))  # Patient Name
                self.ui.TransactionTable.setItem(row, 2, QtWidgets.QTableWidgetItem(doc_full_name))  # Doctor Name
                self.ui.TransactionTable.setItem(row, 3, QtWidgets.QTableWidgetItem(tran_status))  # Transaction Status

            # Resize columns to fit content
            self.ui.TransactionTable.resizeColumnsToContents()

            print("Transaction details loaded successfully!")

        except Exception as e:
            print(f"Error loading transaction details: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

