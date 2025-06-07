from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QWidget
from Views.Doctor_Records import Ui_Doctor_Records as DoctorRecordsUI
from Controllers.DoctorLabResult_Controller import DoctorLabResult
from Controllers.DoctorModifyCheckUp_Controller import DoctorDiagnosisModify
from Controllers.DoctorCheckUpList_Controller import DoctorCheckUpList
from Models.CheckUp import CheckUp
from Models.Patient import Patient


class DoctorRecords(QWidget):
    def __init__(self, doc_id, checkup_ui):
        super().__init__()
        self.ui = DoctorRecordsUI()
        self.checkup_ui = checkup_ui
        self.ui.setupUi(self)
        self.checkuplist_window = None

        # Store the doc_id
        self.doc_id = str(doc_id)
        print(f"Doctor Records UI initialized with doc_id: {self.doc_id}")

        # Initialize a QTimer for automatic refresh
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_tables)  # Connect to refresh_tables method
        self.refresh_timer.start(5000)


        # Fetch all check-ups for the doctor
        checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
        if not checkups:
            print("No check-ups found for this doctor.")
            return

        # Separate check-ups based on status
        self.accepted_checkups = [checkup for checkup in checkups if checkup['chck_status'] != "Completed"]
        self.completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]

        # Populate the AcceptedCheckUp table
        self.populate_accepted_checkups(self.accepted_checkups)

        # Populate the DoneTable
        self.populate_done_table(self.completed_checkups)

        # Connect buttons
        self.checkup_ui.DiagnoseButton.clicked.connect(self.open_doctor_lab_result_modal)
        self.checkup_ui.ModifyCheckUp.clicked.connect(self.ModifyCheckUp)
        self.ui.SeeAllButton.clicked.connect(lambda: self.see_all_checkup_list(self.doc_id))

    def refresh_tables(self):
        """Refresh both AcceptedCheckUp and DoneTable with the latest data without applying any filters or sorting."""
        try:
            # Fetch all check-ups for the doctor
            checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
            if not checkups:
                print("No check-ups found for this doctor.")
                return

            # Separate check-ups based on status
            accepted_checkups = [checkup for checkup in checkups if checkup['chck_status'] != "Completed"]
            completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]

            # Repopulate both tables with unfiltered data
            self.populate_accepted_checkups(accepted_checkups)
            self.populate_done_table(completed_checkups)

        except Exception as e:
            print(f"Error refreshing tables: {e}")

    def populate_accepted_checkups(self, checkups):
        # Clear existing rows
        self.checkup_ui.AcceptedCheckUp.clearContents()
        self.checkup_ui.AcceptedCheckUp.setRowCount(0)

        if not checkups:
            # If no checkups, show a single row with the message
            self.checkup_ui.AcceptedCheckUp.setRowCount(1)
            self.checkup_ui.AcceptedCheckUp.setColumnCount(1)  # Only one column for the message
            item = QtWidgets.QTableWidgetItem("No Accepted Check Ups")
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.checkup_ui.AcceptedCheckUp.setItem(0, 0, item)
            self.checkup_ui.AcceptedCheckUp.setSpan(0, 0, 1, 4)  # Span across all 4 columns
            return

        # Restore the correct number of columns in case they were changed
        self.checkup_ui.AcceptedCheckUp.setColumnCount(4)

        # Populate the table
        for row, checkup in enumerate(checkups):
            pat_id = checkup['pat_id']
            chck_id = checkup['chck_id']
            chck_status = checkup['chck_status']
            chckup_type = checkup['chckup_type']

            # Fetch patient details
            patient = Patient.get_patient_details(pat_id)
            if not patient:
                print(f"No patient found for pat_id={pat_id}")
                continue

            # Extract and format patient name
            full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"

            # Add row to the table
            self.checkup_ui.AcceptedCheckUp.insertRow(row)
            self.checkup_ui.AcceptedCheckUp.setItem(row, 0, QtWidgets.QTableWidgetItem(str(chck_id)))
            self.checkup_ui.AcceptedCheckUp.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name))
            self.checkup_ui.AcceptedCheckUp.setItem(row, 2, QtWidgets.QTableWidgetItem(chck_status))
            self.checkup_ui.AcceptedCheckUp.setItem(row, 3, QtWidgets.QTableWidgetItem(chckup_type))

    def populate_done_table(self, checkups):
        # Clear existing rows
        self.checkup_ui.DoneTable.clearContents()
        self.checkup_ui.DoneTable.setRowCount(0)

        # Sort checkups by chck_id in descending order
        sorted_checkups = sorted(checkups, key=lambda x: x['chck_id'], reverse=True)

        # Populate the table
        for row, checkup in enumerate(sorted_checkups):
            chck_id = checkup['chck_id']
            pat_id = checkup['pat_id']
            chck_diagnoses = checkup['chck_diagnoses']
            chck_date = checkup['chck_date']

            # Fetch patient details
            patient = Patient.get_patient_details(pat_id)
            if not patient:
                print(f"No patient found for pat_id={pat_id}")
                continue

            # Extract and format patient name
            full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"

            # Add row to the table
            self.checkup_ui.DoneTable.insertRow(row)
            self.checkup_ui.DoneTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(chck_id)))
            self.checkup_ui.DoneTable.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name))
            self.checkup_ui.DoneTable.setItem(row, 2, QtWidgets.QTableWidgetItem(chck_diagnoses))
            self.checkup_ui.DoneTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(chck_date)))

    def open_doctor_lab_result_modal(self):
        """Open the DoctorLabResult modal."""
        try:
            # Get the selected row
            selected_row = self.checkup_ui.AcceptedCheckUp.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a row to diagnose.")
                return

            # Retrieve the chck_id from the selected row
            chck_id_item = self.checkup_ui.AcceptedCheckUp.item(selected_row, 0)
            if not chck_id_item:
                QMessageBox.critical(self, "Error", "Failed to retrieve check-up ID.")
                return

            chck_id = chck_id_item.text()

            # Open the modal with the selected chck_id
            print(f"Attempting to open DoctorLabResult modal with chck_id: {chck_id}")
            self.doctor_lab_result = DoctorLabResult(
                checkup_id=chck_id,
                parent=self,
                refresh_callback=self.refresh_tables
            )
            self.doctor_lab_result.show()
            print("DoctorLabResult modal opened successfully!")

        except Exception as e:
            print(f"Error opening DoctorLabResult modal: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open DoctorLabResult modal: {e}")

    def see_all_checkup_list(self, doc_id):
        print(f"Opening DoctorCheckUp list form with CheckUp ID: {doc_id}")
        try:
            if self.checkuplist_window is None or not self.checkuplist_window.isVisible():
                self.checkuplist_window = DoctorCheckUpList(doc_id=doc_id)  # Create the window
            self.checkuplist_window.show()  # Show the window
            self.close()
            print("DoctorCheckUp window opened successfully.")
        except Exception as e:
            print(f"Error opening DoctorCheckUp list window: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open diagnosis form: {e}")

    def ModifyCheckUp(self):
        # Get the currently selected row in the AcceptedCheckUp table
        selected_row = self.checkup_ui.AcceptedCheckUp.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a row in the Accepted Check-Up table.")
            return

        # Retrieve the check-up ID (chck_id) from the selected row
        chck_id_item = self.checkup_ui.AcceptedCheckUp.item(selected_row, 0)  # Assuming chck_id is in the first column
        if not chck_id_item:
            QMessageBox.critical(self, "Error", "Failed to retrieve check-up ID from the selected row.")
            return

        # Extract the check-up ID as an integer
        try:
            chck_id = chck_id_item.text().strip()
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid check-up ID format.")
            return

        # Open the DoctorDiagnosisModify modal with the selected check-up ID
        try:
            self.doctor_diagnosis_modify = DoctorDiagnosisModify(checkup_id=chck_id, doc_id=self.doc_id, parent=self)
            self.doctor_diagnosis_modify.show()
        except Exception as e:
            print(f"Error opening DoctorDiagnosisModify modal: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open the modify check-up modal: {e}")