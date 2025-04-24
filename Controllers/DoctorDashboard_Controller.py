from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from Controllers.DoctorDiagnosis_Controller import DoctorDiagnosis
from Controllers.DoctorRecords_Controller import DoctorRecords
from Views.Doctor_Dashboard import Ui_MainWindow as DoctorDashboardUi
from Models.CheckUp import CheckUp
from Models.Patient import Patient

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Check Up")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want to accept this check up?")
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

class DoctorDashboardController(QMainWindow):
    def __init__(self, doc_id, fname, lname, specialty):
        super().__init__()
        self.ui = DoctorDashboardUi()
        self.ui.setupUi(self)

        # Store the doctor's details
        self.doc_id = doc_id
        self.fname = fname
        self.lname = lname
        self.specialty = specialty

        # Example: Set up UI elements (customize as needed)
        self.ui.User.setText(f"{fname} {lname}")
        self.ui.UserSpecialty.setText(specialty)

        # Populate the PatientDetails table with pending check-ups
        self.load_pending_checkups()

        # Connect the Accept Check-Up button
        self.ui.AcceptCheckUp.clicked.connect(self.accept_checkup)

        print("Doctor Dashboard UI initialized!")

        self.apply_table_styles()

        if hasattr(self.ui, 'RecordButton'):
            print("RecordButton exists")
            self.ui.RecordButton.clicked.connect(self.ViewRecord)
            print("RecordButton connected to button_clicked method!")
        else:
            print("RecordButton is missing!")

    def ViewRecord(self):
        print("StaffButton clicked!")
        try:
            # Instantiate and show the AdminStaffsController window
            self.record_controller = DoctorRecords(self.doc_id)
            self.record_controller.show()
            self.hide()  # Hide the current dashboard window
        except Exception as e:
            print(f"Error loading tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")

    def apply_table_styles(self):
        """Apply custom styles to the tables"""
        # Style for PatientDetails table
        self.ui.PatientDetails.setStyleSheet("""
               QTableWidget {
                background-color: #F4F7ED;
                gridline-color: transparent;
                border-radius: 10px;
            }
            QTableWidget::item {
                border: none;
                font: 16pt "Lexend";
            }
            QTableWidget::item:selected {
                background-color: rgba(46, 110, 101, 0.3);
            }
            QTableWidget QHeaderView::section {
                background-color: #2E6E65;
                color: white;
                padding: 5px;
                font: 18px "Lexend Medium";
                border: 2px solid #2E6E65;
            }
            
            Scroll Area CSS
            QScrollBar:vertical {
                 background: transparent;
                 width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                    background: #C0C0C0;
                    border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                    background: #A0A0A0;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical{
                    background: none;
                    border: none;
            }
           """)

        # Ensure horizontal headers are visible
        self.ui.PatientDetails.horizontalHeader().setVisible(True)

        # Align headers to the left
        self.ui.PatientDetails.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Hide the vertical header (row index)
        self.ui.PatientDetails.verticalHeader().setVisible(False)

        # Set selection behavior
        self.ui.PatientDetails.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def load_pending_checkups(self):
        """Fetch and display pending check-ups in the PatientDetails table."""
        try:
            # Fetch pending check-ups from the database
            pending_checkups = CheckUp.get_pending_checkups()

            # Clear the table before populating it
            self.ui.PatientDetails.setRowCount(0)

            # Check if there are no pending check-ups
            if not pending_checkups:
                print("No pending check-ups found.")

                # Add a single row with the message "No Patient Yet"
                self.ui.PatientDetails.insertRow(0)
                no_data_item = QTableWidgetItem("No Patient Yet")
                self.ui.PatientDetails.setItem(0, 0, no_data_item)

                # Span the message across all columns
                column_count = self.ui.PatientDetails.columnCount()
                self.ui.PatientDetails.setSpan(0, 0, 1, column_count)
                return

            # Populate the table with pending check-ups
            for row, checkup in enumerate(pending_checkups):
                pat_id = checkup["pat_id"]
                chck_id = checkup["chck_id"]

                # Fetch patient details
                patient = Patient.get_patient_by_id(pat_id)
                if not patient:
                    print(f"No patient found for pat_id={pat_id}")
                    continue

                # Extract patient name and capitalize the first letter of each word
                full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"

                # Insert data into the table in the new column order (Check Up ID, Patient ID, Name)
                self.ui.PatientDetails.insertRow(row)
                self.ui.PatientDetails.setItem(row, 0, QTableWidgetItem(chck_id))  # Check Up ID
                self.ui.PatientDetails.setItem(row, 1, QTableWidgetItem(str(pat_id)))  # Patient ID
                self.ui.PatientDetails.setItem(row, 2, QTableWidgetItem(full_name))  # Name

            # Resize columns to fit the content
            self.ui.PatientDetails.resizeColumnsToContents()

            # Optionally, set minimum widths for specific columns
            self.ui.PatientDetails.setColumnWidth(0, 150)
            self.ui.PatientDetails.setColumnWidth(1, 150)
            self.ui.PatientDetails.setColumnWidth(2, 200)

        except Exception as e:
            print(f"Error loading pending check-ups: {e}")

    def accept_checkup(self):
        """Handle the Accept Check-Up button click."""
        try:
            # Get the selected row from the check-up table
            selected_row = self.ui.PatientDetails.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a check-up to accept.")
                return

            print("Selected row:", selected_row)

            # Get the check-up ID from the selected row
            chck_id = self.ui.PatientDetails.item(selected_row, 0).text()  # Assuming chck_id is in column 0
            print(f"Selected check-up ID: {chck_id}")

            # Show confirmation dialog
            confirmation_dialog = ConfirmationDialog(self)
            if confirmation_dialog.exec_() == QDialog.Rejected:
                print("Check-up acceptance cancelled by the user.")
                return

            print("User confirmed acceptance.")

            # Update the check-up status to "On going" and assign the doctor's ID
            success = CheckUp.update_doc_id(chck_id, self.doc_id)
            if success:
                print("Check-up accepted successfully in the database.")
                # Open the DoctorDiagnosis form with the selected CheckUp ID
                self.open_diagnosis_form(chck_id)
            else:
                print("Failed to update check-up in the database.")
                QMessageBox.critical(self, "Error", "Failed to accept check-up. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def open_diagnosis_form(self, checkup_id):
        print(f"Opening DoctorDiagnosis form with CheckUp ID: {checkup_id}")
        try:
            diagnosis_window = DoctorDiagnosis(
                checkup_id=checkup_id,
                doc_id=self.doc_id,
                parent=self
            )
            diagnosis_window.show()
            print("DoctorDiagnosis window opened successfully.")
        except Exception as e:
            print(f"Error opening DoctorDiagnosis window: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open diagnosis form: {e}")