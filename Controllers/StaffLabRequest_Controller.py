from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtWidgets import QTableWidgetItem,QWidget
from PyQt5.QtCore import Qt
from Controllers.ClientSocketController import DataRequest
from Views.Staff_LabRequest import Ui_Staff_LabRequest as StaffLabRequestUI
from PyQt5.QtWidgets import QMessageBox, QWidget
from Controllers.StaffAddLabAttachment_Controller import StaffAddAttachment

class StaffLabRequest(QWidget):
    def __init__(self, labreq_ui):
        super().__init__()
        self.ui = StaffLabRequestUI()
        self.labreq_ui = labreq_ui
        self.ui.setupUi(self)
        self.load_staff_labrequest_table()
        self.labreq_ui.SearchIcon.clicked.connect(self.filter_lab_request_table)

        # Connect buttons (if the button exists)
        if hasattr(self.labreq_ui, 'Modify'):
            self.labreq_ui.Modify.clicked.connect(self.open_form)


    def filter_lab_request_table(self):
        search_text = self.labreq_ui.Search.text().strip().lower()
        if not search_text:
            self.load_staff_labrequest_table()
            return

        found = False
        table = self.labreq_ui.LabRequestTable
        row_count = table.rowCount()

        # Clear previous highlights/selections
        for row in range(row_count):
            table.setRowHidden(row, True)

        for row in range(row_count):
            # Search in Patient Name and Doctor Name columns
            patient_item = table.item(row, 1)
            doctor_item = table.item(row, 2)

            if patient_item and doctor_item:
                patient_name = patient_item.text().lower()
                doctor_name = doctor_item.text().lower()

                if search_text in patient_name or search_text in doctor_name:
                    table.setRowHidden(row, False)
                    found = True

        if not found:
            table.setRowCount(0)
            table.setRowCount(1)
            table.setSpan(0, 0, 1, 4)  # Merge all columns for the message
            not_found_item = QtWidgets.QTableWidgetItem("No Found Records")
            not_found_item.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(0, 0, not_found_item)

    def refresh_table(self):
        """Reload data into the tables"""
        try:
            self.load_staff_labrequest_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh tables: {e}")

    def load_staff_labrequest_table(self):
        """Load the details of the table containing check-up IDs with lab codes."""
        try:
            self.labreq_ui.LabRequestTable.setRowCount(0)

            # Fetch checkup rows
            rows = DataRequest.send_command("GET_CHECKUPS_WITH_LAB_REQUESTS")

            if not rows:
                # Show "No Lab Request Exist" centered
                self.labreq_ui.LabRequestTable.setRowCount(1)
                self.labreq_ui.LabRequestTable.setColumnCount(4)  # Ensure column count matches actual
                item = QtWidgets.QTableWidgetItem("No Lab Request Exist")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsEnabled)  # Read-only
                self.labreq_ui.LabRequestTable.setItem(0, 0, item)
                self.labreq_ui.LabRequestTable.setSpan(0, 0, 1, 4)  # Span across all columns
                return

            # Otherwise, populate the table
            checkup_ids = [row[0] for row in rows]

            for checkup_id in checkup_ids:
                checkup_details = DataRequest.send_command("GET_CHECKUP_DETAILS", checkup_id)
                if not checkup_details:
                    continue

                pat_id = checkup_details['pat_id']
                doc_id = checkup_details['doc_id']

                patient_details = DataRequest.send_command("GET_PATIENT_DETAILS", pat_id)
                doctor_details = DataRequest.send_command("GET_DOCTOR_BY_ID", doc_id)

                if not patient_details or not doctor_details:
                    continue

                patient_name = f"{patient_details['pat_lname'].capitalize()}, {patient_details['pat_fname'].capitalize()}"
                doctor_name = f"{doctor_details['last_name'].capitalize()}, {doctor_details['first_name'].capitalize()}"

                lab_attachments = DataRequest.send_command("GET_LAB_ATTACHMENTS_BY_CHECKUP", checkup_id)

                if not lab_attachments:
                    status = "No Results Yet"
                else:
                    null_count = sum(1 for lab_attachment in lab_attachments if lab_attachment[0] is None)
                    total_count = len(lab_attachments)
                    if null_count == total_count:
                        status = "No Results Yet"
                    elif null_count > 0:
                        status = "Incomplete"
                    else:
                        status = "Completed"

                row_position = self.labreq_ui.LabRequestTable.rowCount()
                self.labreq_ui.LabRequestTable.insertRow(row_position)
                self.labreq_ui.LabRequestTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(checkup_id)))
                self.labreq_ui.LabRequestTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(patient_name))
                self.labreq_ui.LabRequestTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(doctor_name))
                self.labreq_ui.LabRequestTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(status))

        except ConnectionError as ce:
            QMessageBox.critical(self, "Database Error", str(ce))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load lab request table: {e}")

    def open_form(self):
        """Open the Staff Add Attachment form with parameters from the selected row."""
        try:
            # Get the currently selected row in the LabRequestTable
            selected_row = self.labreq_ui.LabRequestTable.currentRow()
            if selected_row == -1:  # No row selected
                QMessageBox.warning(self, "Selection Error", "Please select a row from the table.")
                return

            # Retrieve data from the selected row with proper validation
            chk_id_item = self.labreq_ui.LabRequestTable.item(selected_row, 0)  # Check-Up ID (Column 0)
            patient_name_item = self.labreq_ui.LabRequestTable.item(selected_row, 1)  # Patient Name (Column 1)
            doctor_name_item = self.labreq_ui.LabRequestTable.item(selected_row, 2)  # Doctor Name (Column 2)

            # Validate that all required cells are populated
            if not chk_id_item or not patient_name_item or not doctor_name_item:
                QMessageBox.critical(self, "Data Error", "Selected row contains missing data.")
                return

            # Extract text from QTableWidgetItem objects
            chk_id = chk_id_item.text().strip()  # Strip whitespace
            patient_name = patient_name_item.text().strip()
            doctor_name = doctor_name_item.text().strip()

            # Open the StaffAddAttachment form with the retrieved parameters
            self.staff_attach_window = StaffAddAttachment(
                parent=self,
                chck_id=chk_id,
                doctorname=doctor_name,
                patientname=patient_name,
                refresh_table = self.refresh_table
            )
            self.staff_attach_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Staff Attach Form: {e}")