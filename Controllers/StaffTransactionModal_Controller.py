from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMainWindow, QMessageBox, QHeaderView, QSizePolicy

from Controllers.ClientSocketController import DataRequest
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Models.Doctor import Doctor
from Models.Transaction import Transaction
from Views.Staff_TransactionsList import Ui_Staff_TransactionList
from Controllers.StaffTransactionProcess_Controller import StaffTransactionProcess


class StaffTransactionModal(QMainWindow):
    def __init__(self, parent=None , staff_dashboard=None):
        super().__init__(parent)
        self.ui = Ui_Staff_TransactionList()
        self.ui.setupUi(self)
        self.staff_dashboard = staff_dashboard

        # Set window properties
        self.setWindowTitle("Add Transaction")

        self.apply_table_styles()
        self.load_pending_transaction()
        self.ui.AddBUtton.clicked.connect(self.open_transaction_process) # Connect the Add button to open_transaction_process

    def apply_table_styles(self):
        # Ensure horizontal headers are visible
        self.ui.TransactionTable.horizontalHeader().setVisible(True)

        # Align headers to the left
        self.ui.TransactionTable.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Hide the vertical header (row index)
        self.ui.TransactionTable.verticalHeader().setVisible(False)

        # Set selection behavior
        self.ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        header = self.ui.TransactionTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.ui.TransactionTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def load_pending_transaction(self):
        """Fetch and display pending check-ups in the TransactionTable."""
        try:
            # Fetch all transactions to determine which check-ups are already completed
            transactions = Transaction.get_all_transaction()
            # transactions = DataRequest.send_command("GET_ALL_TRANSACTION")

            # Create a mapping of chck_id to tran_status
            transaction_status_map = {tran['chck_id']: tran['tran_status'] for tran in transactions}

            # Fetch all check-ups from the database
            pending_checkups = CheckUp.get_all_checkups()
            # pending_checkups = DataRequest.send_command("GET_ALL_CHECKUP")

            # Clear the table before populating it
            self.ui.TransactionTable.setRowCount(0)

            # Filter out check-ups whose chck_id exists in the transactions
            filtered_checkups = [
                checkup for checkup in pending_checkups
                if checkup["chck_id"] not in transaction_status_map
                   or transaction_status_map[checkup["chck_id"]] in ("Pending", "Partial")
            ]

            # Check if there are no pending check-ups after filtering
            if not filtered_checkups:
                self.ui.TransactionTable.insertRow(0)
                no_data_item = QTableWidgetItem("No Transaction Yet")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.TransactionTable.setItem(0, 0, no_data_item)

                # Span the message across all columns
                column_count = self.ui.TransactionTable.columnCount()
                self.ui.TransactionTable.setSpan(0, 0, 1, column_count)
                return

            # Ensure the table has at least 5 columns to show tran_status
            expected_columns = 5  # chck_id, patient name, check-up type, doctor, tran_status
            if self.ui.TransactionTable.columnCount() < expected_columns:
                self.ui.TransactionTable.setColumnCount(expected_columns)

            # Optional: Set headers (only if needed)
            self.ui.TransactionTable.setHorizontalHeaderLabels([
                "Check-Up ID", "Patient Name", "Check-Up Type", "Doctor", "Transaction Status"
            ])

            # Populate the table with filtered pending check-ups
            for row, checkup in enumerate(filtered_checkups):
                try:
                    doc_id = checkup.get('doc_id')
                    if not doc_id:
                        # Skip rows with null or empty doctor ID
                        continue

                    pat_id = checkup["pat_id"]
                    chck_id = checkup["chck_id"]
                    chck_type = checkup['chckup_type']

                    # Patient details
                    patient = Patient.get_patient_by_id(pat_id)
                    # patient = DataRequest.send_command("GET_PATIENT_BY_ID", pat_id)

                    if not patient:
                        continue

                    full_name = f"{patient['last_name'].capitalize()}, {patient['first_name'].capitalize()}"

                    # Doctor details
                    doctor = Doctor.get_doctor(doc_id)
                    # doctor = DataRequest.send_command("GET_DOCTOR_BY_ID", doc_id)

                    if not doctor:
                        docFullname = "Unknown Doctor"
                    else:
                        docFullname = f"{doctor['last_name'].capitalize()}, {doctor['first_name'].capitalize()}"

                    # Status
                    tran_status = transaction_status_map.get(chck_id, "Pending")

                    # Insert row
                    self.ui.TransactionTable.insertRow(self.ui.TransactionTable.rowCount())
                    self.ui.TransactionTable.setItem(self.ui.TransactionTable.rowCount() - 1, 0,
                                                     QTableWidgetItem(chck_id))
                    self.ui.TransactionTable.setItem(self.ui.TransactionTable.rowCount() - 1, 1,
                                                     QTableWidgetItem(full_name))
                    self.ui.TransactionTable.setItem(self.ui.TransactionTable.rowCount() - 1, 2,
                                                     QTableWidgetItem(chck_type))
                    self.ui.TransactionTable.setItem(self.ui.TransactionTable.rowCount() - 1, 3,
                                                     QTableWidgetItem(docFullname))
                    self.ui.TransactionTable.setItem(self.ui.TransactionTable.rowCount() - 1, 4,
                                                     QTableWidgetItem(tran_status))

                except Exception as inner_e:
                    print(f"[ERROR] Failed to load row for checkup ID {checkup.get('chck_id')}: {inner_e}")

            # Resize columns to fit the content
            if self.ui.TransactionTable.rowCount() > 0:
                self.ui.TransactionTable.resizeColumnsToContents()

        except Exception as e:
            pass

    def open_transaction_process(self):
        try:
            # Determine which row is selected
            selected_row = self.ui.TransactionTable.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a row to add a transaction.")
                return

            # Retrieve the chck_id from the selected row
            chck_id_item = self.ui.TransactionTable.item(selected_row, 0)
            if not chck_id_item:
                QMessageBox.critical(self, "Error", "Failed to retrieve check-up ID.")
                return

            chck_id = chck_id_item.text()

            # Open the StaffTransactionProcess modal with the selected chck_id
            self.transaction_process_window = StaffTransactionProcess(chck_id=chck_id)

            # Close the parent dashboard window
            # self.staff_dashboard.close()

            # Close the current modal (StaffTransactionModal)
            self.close()

            # Show the StaffTransactionProcess modal
            self.transaction_process_window.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open StaffTransactionProcess: {e}")
