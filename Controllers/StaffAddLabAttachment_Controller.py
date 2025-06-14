import os
import subprocess
import sys
from PyQt5 import QtCore, QtWidgets
from pkg_resources import non_empty_lines

from Controllers.ClientSocketController import DataRequest
from Views.Staff_AddLabAttachment import Ui_Staff_AddLabAttachment as StaffAddAttachmentUI
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QFileDialog, \
    QHeaderView, QSizePolicy

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Add Attachment")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want to update this?")
        layout.addWidget(self.message_label)

        # Add button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Apply stylesheet to the button box
        self.button_box.setStyleSheet("""
            QPushButton {
                background-color: #2E6E65;
                color: white;
                border-radius: 10px;
                padding: 5px 10px;
                margin-top: 5px
            }
            QPushButton:hover {
                background-color: #235C5A;
            }
        """)
        layout.addWidget(self.button_box)

        # Set layout
        self.setLayout(layout)


class StaffAddAttachment(QtWidgets.QMainWindow):  # Inherit from QMainWindow or QWidget
    def __init__(self, parent=None, chck_id=None, doctorname=None, patientname=None , refresh_table = None):
        super().__init__(parent)  # Properly initialize the parent class
        self.parent = parent
        self.chck_id = chck_id
        self.doctorname = doctorname
        self.patientname = patientname
        self.refresh_table1 = refresh_table

        # Initialize the UI
        self.ui = StaffAddAttachmentUI()
        self.ui.setupUi(self)

        # Window settings
        self.setWindowTitle("Staff Registration")
        self.setFixedSize(700, 550)

        # Apply table styles and refresh the table
        self.apply_table_styles()
        self.refresh_table()

        # Set initial values for Patient and Doctor fields
        self.ui.Patient.setText(self.patientname or "N/A")
        self.ui.Doctor.setText(self.doctorname or "N/A")
        # Connect the "Attach" button to the attach_file method
        self.ui.Attach.clicked.connect(self.attach_file)
        self.ui.View.clicked.connect(self.view_file)
        self.ui.Cancel.clicked.connect(self.close_modal)  # Close modal on Cancel
        self.ui.UpdateButton.clicked.connect(self.handle_update_button)  # Handle UpdateButton action

    def close_modal(self):
        """Close the modal when Cancel is clicked."""
        self.close()

    def handle_update_button(self):
        """Handle the UpdateButton click event."""

        # Show the ConfirmationDialog
        confirmation_dialog = ConfirmationDialog(self)
        result = confirmation_dialog.exec_()  # Show the dialog and wait for user response

        if result == QDialog.Accepted:  # User clicked "Yes"
            if callable(self.refresh_table1):  # Ensure refresh_table1 is a valid function
                try:
                    self.refresh_table1()  # Call the parent's refresh_table function
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to refresh parent table: {e}")
            self.close()  # Close the modal after refreshing the table
        else:  # User clicked "No"
            pass
    def refresh_table(self):
        """Reload data into the tables"""
        try:
            self. load_staff_labattach_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh tables: {e}")

    def apply_table_styles(self):
        self.ui.LabTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # Ensure horizontal headers are visible
        self.ui.LabTable.horizontalHeader().setVisible(True)

        # Align headers to the left
        self.ui.LabTable.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Hide the vertical header (row index)
        self.ui.LabTable.verticalHeader().setVisible(False)

        # Responsive table
        header = self.ui.LabTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.ui.LabTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.LabTable.setWordWrap(True)
        self.ui.LabTable.resizeRowsToContents()

    def load_staff_labattach_table(self):
        try:
            # Clear the table before populating it
            self.ui.LabTable.setRowCount(0)

            # Fetch lab codes and attachments for the given check-up ID
            #lab_tests = CheckUp.get_test_names_by_chckid(self.chck_id)
            lab_tests = DataRequest.send_command("GET_TEST_BY_CHECK_ID", self.chck_id)

            if not lab_tests:
                return

            # Populate the table with lab test details
            for lab_test in lab_tests:

                # Handle dictionaries only
                if isinstance(lab_test, dict):
                    lab_code = lab_test.get('lab_code')
                    lab_attachment = lab_test.get('lab_attachment')
                else:
                    continue

                # Validate lab_code
                if not lab_code:
                    continue

                # Fetch the lab test name using the lab code
                #lab_test_details = Laboratory.get_test_by_labcode(lab_code)
                lab_test_details = DataRequest.send_command("GET_TEST_BY_LAB_CODE", lab_code)
                # Handle the case where get_test_by_labcode returns a tuple
                if isinstance(lab_test_details, list):
                    if len(lab_test_details) > 0 and isinstance(lab_test_details[0], dict):
                        lab_test_details = lab_test_details[0]
                    else:
                        continue

                # Validate lab_test_details
                if not isinstance(lab_test_details, dict):
                    continue

                if not lab_test_details:
                    continue

                lab_test_name = lab_test_details.get('lab_test_name', 'Unknown').capitalize()

                # Determine attachment status
                if lab_attachment:
                    # Convert memoryview to string and extract the file name
                    if isinstance(lab_attachment, memoryview):
                        lab_attachment = lab_attachment.tobytes().decode('utf-8')
                    file_name = os.path.basename(lab_attachment)
                    attachment_status = file_name
                else:
                    attachment_status = "No Attach File"

                # Add a new row to the table
                row_position = self.ui.LabTable.rowCount()
                self.ui.LabTable.insertRow(row_position)

                # Insert data into the table
                self.ui.LabTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(lab_test_name))
                self.ui.LabTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(attachment_status))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load lab attach table: {e}")

    def attach_file(self):
        # Get the currently selected row in the LabTableattach
        selected_row = self.ui.LabTable.currentRow()
        if selected_row == -1:  # No row selected
            QMessageBox.warning(self, "Selection Error", "Please select a lab test from the table.")
            return

        # Retrieve the lab_test_name from the selected row
        lab_test_name = self.ui.LabTable.item(selected_row, 0).text()

        # Normalize the lab_test_name: strip whitespace and convert to lowercase
        lab_test_name = lab_test_name.strip().lower()

        # Retrieve the lab_code using the normalized lab_test_name
        #lab_code = Laboratory.get_lab_code_by_name(lab_test_name)
        lab_code = DataRequest.send_command("GET_LAB_CODE_BY_NAME", lab_test_name)
        if not lab_code:
            QMessageBox.critical(self, "Error", "Failed to retrieve lab code.")
            return

        # Open file explorer to select a file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if not file_path:  # User canceled the file selection
            return

        # Extract the file name from the file path
        file_name = os.path.basename(file_path)  # Extracts the file name from the path

        # Update the database with the file path
        #success = CheckUp.update_lab_attachment(self.chck_id, lab_code, file_path)
        success = DataRequest.send_command("UPDATE_LAB_ATTACHMENT",[self.chck_id, lab_code, file_path])
        if success:

            # Update the table directly without refreshing (optional optimization)
            self.ui.LabTable.setItem(selected_row, 1, QtWidgets.QTableWidgetItem(file_name))

            # Optionally refresh the table to ensure consistency
            self.refresh_table()

            QMessageBox.information(self, "Success", f"File '{file_name}' attached successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to attach file.")

    def view_file(self):
        """Handle viewing the attached file for the selected lab test."""
        # Get the currently selected row in the LabTable
        selected_row = self.ui.LabTable.currentRow()
        if selected_row == -1:  # No row selected
            QMessageBox.warning(self, "Selection Error", "Please select a lab test from the table.")
            return

        # Retrieve the lab_test_name from the selected row
        lab_test_name = self.ui.LabTable.item(selected_row, 0).text()

        # Normalize the lab_test_name: strip whitespace and convert to lowercase
        lab_test_name = lab_test_name.strip().lower()

        # Retrieve the lab_code using the normalized lab_test_name
        #lab_code = Laboratory.get_lab_code_by_name(lab_test_name)
        lab_code = DataRequest.send_command("GET_LAB_CODE_BY_NAME", lab_test_name)
        if not lab_code:
            QMessageBox.critical(self, "Error", "Failed to retrieve lab code.")
            return

        # Fetch the file path from the CheckUp model
        #file_path = CheckUp.get_lab_attachment(self.chck_id, lab_code)
        file_path = DataRequest.send_command("GET_LAB_ATTACHMENT", [self.chck_id, lab_code])

        if not file_path:
            QMessageBox.warning(self, "No Attachment", "No file is attached to this lab test.")
            return

        # Check if the file exists
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file '{file_path}' does not exist.")
            return

        # Open the file using the default application
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # Unix-like systems
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, file_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {e}")