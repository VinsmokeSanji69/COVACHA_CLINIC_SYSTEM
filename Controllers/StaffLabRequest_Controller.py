from PyQt5 import QtWidgets, QtCore
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Models.Doctor import Doctor
from Models.DB_Connection import DBConnection
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
        print("Staff Lab Request UI initialized!")


        # Connect buttons (if the button exists)
        if hasattr(self.labreq_ui, 'Modify'):
            print("Modify exists")
            self.labreq_ui.Modify.clicked.connect(self.open_form)
            print("Modify connected to open_add_user_form!")
        else:
            print("Modify is missing!")

    def refresh_table(self):
        """Reload data into the tables"""
        try:
            self.load_staff_labrequest_table()
            print("Tables refreshed successfully!")
        except Exception as e:
            print(f"Error refreshing tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh tables: {e}")

    def load_staff_labrequest_table(self):
        """Load the details of the table containing check-up IDs with lab codes."""
        conn = DBConnection.get_db_connection()
        if not conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return

        try:
            # Query to fetch all checkup IDs with associated lab codes
            query = """
                SELECT DISTINCT clt.chck_id
                FROM checkup_lab_tests clt
                JOIN checkup c ON clt.chck_id = c.chck_id;
            """
            with conn.cursor() as cursor:
                cursor.execute(query)
                checkup_ids = [row[0] for row in cursor.fetchall()]

            # Clear the table before populating it
            self.labreq_ui.LabRequestTable.setRowCount(0)

            # Populate the table with filtered data
            for checkup_id in checkup_ids:
                # Fetch check-up details
                checkup_details = CheckUp.get_checkup_details(checkup_id)
                if not checkup_details:
                    continue

                pat_id = checkup_details['pat_id']
                doc_id = checkup_details['doc_id']

                # Fetch patient details
                patient_details = Patient.get_patient_details(pat_id)
                if not patient_details:
                    continue

                # Format patient name (lname, fname)
                patient_name = f"{patient_details['pat_lname'].capitalize()}, {patient_details['pat_fname'].capitalize()}"

                # Fetch doctor details
                doctor_details = Doctor.get_doctor_by_id(doc_id)
                if not doctor_details:
                    continue

                # Format doctor name (lname, fname)
                doctor_name = f"{doctor_details['doc_lname'].capitalize()}, {doctor_details['doc_fname'].capitalize()}"

                # Fetch all lab attachments for this chck_id
                query = """
                    SELECT lab_attachment
                    FROM checkup_lab_tests
                    WHERE chck_id = %s;
                """
                with conn.cursor() as cursor:
                    cursor.execute(query, (checkup_id,))
                    lab_attachments = cursor.fetchall()

                # Determine the status based on lab_attachment values
                if not lab_attachments:
                    status = "No Results Yet"
                else:
                    # Separate NULL and non-NULL lab_attachment values
                    null_count = sum(1 for lab_attachment in lab_attachments if lab_attachment[0] is None)
                    total_count = len(lab_attachments)

                    if null_count == total_count:
                        # All lab_attachment values are NULL
                        status = "No Results Yet"
                    elif null_count > 0:
                        # Some lab_attachment values are NULL
                        status = "Incomplete"
                    else:
                        # All lab_attachment values are non-NULL
                        status = "Completed"

                # Add a new row to the table
                row_position = self.ui.LabRequestTable.rowCount()
                self.labreq_ui.LabRequestTable.insertRow(row_position)

                # Insert data into the table
                self.labreq_ui.LabRequestTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(checkup_id)))
                self.labreq_ui.LabRequestTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(patient_name))
                self.labreq_ui.LabRequestTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(doctor_name))
                self.labreq_ui.LabRequestTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(status))

            print("Lab Request Table loaded successfully!")

        except Exception as e:
            print(f"Error loading lab request table: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load lab request table: {e}")

        finally:
            if conn:
                conn.close()

    def open_form(self):
        """Open the Staff Add Attachment form with parameters from the selected row."""
        print("Opening Add User Form...")
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
            print("Staff Attach Form shown successfully!")

        except Exception as e:
            print(f"Error opening Staff Attach Form: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Staff Attach Form: {e}")