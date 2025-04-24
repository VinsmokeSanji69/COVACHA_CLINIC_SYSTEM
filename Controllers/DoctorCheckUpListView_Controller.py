import os
import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Views.Doctor_LabResult import Ui_MainWindow as DoctorLabResultUI
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Models.LaboratoryTest import Laboratory
from Models.Prescription import Prescription
from datetime import datetime, date

class DoctorCheckUpListView(QMainWindow):
    def __init__(self, checkup_id=None, parent=None):
        super().__init__(parent)
        self.ui = DoctorLabResultUI()
        self.ui.setupUi(self)
        self.checkup_id = checkup_id
        print(f"Check_Up Id: {self.checkup_id}")

        # Load and display data related to the checkup ID
        self.load_data()
        self.apply_table_styles()
        self.refresh_all_tables()
        # Hide unnecessary buttons
        self.hide_buttons()

        # Modify the DiagnoseButton to act as a Close button
        self.ui.DiagnoseButton.setText("Close")
        self.ui.DiagnoseButton.clicked.connect(self.close_this)
        self.ui.ViewLabResult.clicked.connect(self.view_file)

    def close_this(self):
        self.close()

    def refresh_all_tables(self):
        try:
            print("Refreshing all tables...")
            self.load_labattach_table()
            self.load_prescription_table()
            print("All tables refreshed successfully!")
        except Exception as e:
            print(f"Error refreshing all tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh tables: {e}")

    def apply_table_styles(self):
        self.ui.LabTestTabe.setStyleSheet("""
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
        self.ui.LabTestTabe.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # Ensure horizontal headers are visible
        self.ui.LabTestTabe.horizontalHeader().setVisible(True)

        # Align headers to the left
        self.ui.LabTestTabe.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Hide the vertical header (row index)
        self.ui.LabTestTabe.verticalHeader().setVisible(False)

        self.ui.LabTestTabe_2.setStyleSheet("""
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
        self.ui.LabTestTabe_2.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # Ensure horizontal headers are visible
        self.ui.LabTestTabe_2.horizontalHeader().setVisible(True)

        # Align headers to the left
        self.ui.LabTestTabe_2.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Hide the vertical header (row index)
        self.ui.LabTestTabe_2.verticalHeader().setVisible(False)

    def load_labattach_table(self):
        try:
            # Clear the table before populating it
            self.ui.LabTestTabe.setRowCount(0)

            # Fetch lab codes and attachments for the given check-up ID
            lab_tests = CheckUp.get_test_names_by_chckid(self.checkup_id)
            if not lab_tests:
                print(f"No lab tests found for chck_id: {self.checkup_id}")

                # Add a single row with "No Lab Test Request"
                row_position = self.ui.LabTestTabe.rowCount()
                self.ui.LabTestTabe.insertRow(row_position)
                self.ui.LabTestTabe.setItem(row_position, 0, QtWidgets.QTableWidgetItem("No Lab Test Request"))
                self.ui.LabTestTabe.setItem(row_position, 1, QtWidgets.QTableWidgetItem(""))  # Empty attachment status
                return

            # Populate the table with lab test details
            for lab_test in lab_tests:
                # Debug: Log the type and contents of lab_test
                print(f"Processing lab_test: {lab_test}, Type: {type(lab_test)}")

                # Handle both dictionaries and tuples
                if isinstance(lab_test, dict):
                    lab_code = lab_test.get('lab_code')
                    lab_attachment = lab_test.get('lab_attachment')
                elif isinstance(lab_test, tuple):
                    # Assume the tuple structure is (lab_code, lab_attachment)
                    if len(lab_test) < 2:
                        print(f"Invalid tuple structure: {lab_test}, Skipping...")
                        continue
                    lab_code, lab_attachment = lab_test[:2]
                else:
                    print(f"Unexpected data type for lab_test: {type(lab_test)}, Skipping...")
                    continue

                # Validate lab_code
                if not lab_code:
                    print(f"Missing lab_code in lab_test: {lab_test}")
                    continue

                # Fetch the lab test name using the lab code
                lab_test_details = Laboratory.get_test_by_labcode(lab_code)
                if not lab_test_details:
                    print(f"No lab test details found for lab_code: {lab_code}")
                    continue

                # Handle the case where get_test_by_labcode returns a tuple
                if isinstance(lab_test_details, tuple):
                    # Assume the first element of the tuple contains 'lab_test_name'
                    if len(lab_test_details) > 0 and isinstance(lab_test_details[0], dict):
                        lab_test_details = lab_test_details[0]
                    else:
                        print(f"Invalid tuple structure for lab_code '{lab_code}', Skipping...")
                        continue

                # Validate lab_test_details
                if not isinstance(lab_test_details, dict):
                    print(f"Unexpected return type from get_test_by_labcode: {type(lab_test_details)}, Skipping...")
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
                row_position = self.ui.LabTestTabe.rowCount()
                self.ui.LabTestTabe.insertRow(row_position)

                # Insert data into the table
                self.ui.LabTestTabe.setItem(row_position, 0, QtWidgets.QTableWidgetItem(lab_test_name))
                self.ui.LabTestTabe.setItem(row_position, 1, QtWidgets.QTableWidgetItem(attachment_status))

            print("Lab Attach Table loaded successfully!")

        except Exception as e:
            print(f"Error loading lab attach table: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load lab attach table: {e}")

    def load_prescription_table(self):
        """Load and display prescription data in the LabTestTabe_2 table."""
        try:
            # Clear existing rows in the table
            self.ui.LabTestTabe_2.setRowCount(0)

            # Fetch prescriptions for the given check-up ID
            prescriptions = Prescription.display_prescription(self.checkup_id)
            if not prescriptions:
                print(f"No prescriptions found for chck_id: {self.checkup_id}")
                # Add a single row with "No Prescriptions"
                row_position = self.ui.LabTestTabe_2.rowCount()
                self.ui.LabTestTabe_2.insertRow(row_position)
                self.ui.LabTestTabe_2.setItem(row_position, 0, QtWidgets.QTableWidgetItem("No Prescriptions"))
                return

            # Populate the table with prescription details
            for prescription in prescriptions:
                # Extract prescription data
                med_name = prescription.get("pres_medicine", "")
                dosage = prescription.get("pres_dosage", "")
                intake = prescription.get("pres_intake", "")

                # Add a new row to the table
                row_position = self.ui.LabTestTabe_2.rowCount()
                self.ui.LabTestTabe_2.insertRow(row_position)

                # Insert data into the table
                self.ui.LabTestTabe_2.setItem(row_position, 0, QtWidgets.QTableWidgetItem(med_name))
                self.ui.LabTestTabe_2.setItem(row_position, 1, QtWidgets.QTableWidgetItem(dosage))
                self.ui.LabTestTabe_2.setItem(row_position, 2, QtWidgets.QTableWidgetItem(intake))

            print("Prescription Table loaded successfully!")
        except Exception as e:
            print(f"Error loading prescription table: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load prescription table: {e}")

    def hide_buttons(self):
        """Hide unnecessary buttons."""
        self.ui.AddPrescription.hide()  # Hide AddPrescription button
        self.ui.EditPrescription.hide()  # Hide EditPrescription button
        self.ui.ViewLabResult_4.hide()  # Hide ViewLabResult_4 button
        self.ui.Cancel.hide()


    def load_data(self):
        """Load both check-up and patient details and populate the UI."""
        try:
            # Step 1: Fetch check-up details
            checkup_details = CheckUp.get_checkup_details(self.checkup_id)
            if not checkup_details:
                raise ValueError("No check-up details found for the given ID.")

            # Extract check-up data
            pat_id = checkup_details['pat_id']
            chck_bp = checkup_details['chck_bp']
            chck_temp = checkup_details['chck_temp']
            chck_height = checkup_details['chck_height' ]
            chck_weight = checkup_details['chck_weight']
            chck_diagnose = checkup_details['chck_diagnoses']
            chck_notes = checkup_details ['chck_notes']

            # Step 2: Fetch patient details
            patient_details = Patient.get_patient_details(pat_id)
            if not patient_details:
                raise ValueError("No patient details found for the given ID.")

            # Extract patient data
            pat_lname = patient_details['pat_lname' ]
            pat_fname = patient_details['pat_fname']
            pat_mname = patient_details['pat_mname']
            pat_dob = patient_details['pat_dob']
            pat_gender = patient_details['pat_gender']

            # Calculate age based on date of birth
            age = self.calculate_age(pat_dob)

            # Convert pat_dob to a string for display
            Birthday = pat_dob.strftime("%Y-%m-%d")

            # Step 3: Populate the UI
            self.populate_patient_info(pat_id,pat_lname, pat_fname, pat_mname, Birthday, age , pat_gender)
            self.populate_checkup_info(chck_bp, chck_temp, chck_height, chck_weight, chck_diagnose, chck_notes)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

    def calculate_age(self, dob):
        """Calculate the age based on the date of birth."""
        today = datetime.today()
        if isinstance(dob, date):  # Use the explicitly imported 'date'
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        else:
            raise ValueError("DOB must be a datetime.date object or a valid date string.")

    def populate_patient_info(self, pat_id ,pat_lname, pat_fname, pat_mname, pat_dob, age, gender):
        """Populate the patient information fields."""
        self.ui.PatID.setText(str(pat_id))
        self.ui.PatName.setText(f"{pat_lname.capitalize()}, {pat_fname.capitalize()} {pat_mname.capitalize()}")
        self.ui.PatDoB.setText(pat_dob)
        self.ui.PatAge.setText(str(age))
        self.ui.PatGender.setText(gender)

    def populate_checkup_info(self, chck_bp, chck_temp, chck_height, chck_weight, chck_diagnose, chck_notes):
        """Populate the check-up information fields."""
        self.ui.BloodPressure.setText(str(chck_bp + " bpm"))
        self.ui.Temperature.setText(str(chck_temp  + " °C"))
        self.ui.Heights.setText(str(chck_height + " cm"))
        self.ui.Weight.setText(str(chck_weight + " kg"))
        self.ui.CheckUpID.setText(self.checkup_id)
        self.ui.DiagnoseText.setText(chck_diagnose)
        self.ui.DiagnoseNotes.setText(chck_notes)

    def view_file(self):
        """Handle viewing the attached file for the selected lab test."""
        print("View button clicked!")

        # Get the currently selected row in the LabTable
        selected_row = self.ui.LabTestTabe.currentRow()
        if selected_row == -1:  # No row selected
            QMessageBox.warning(self, "Selection Error", "Please select a lab test from the table.")
            return

        # Retrieve the lab_test_name from the selected row
        lab_test_name = self.ui.LabTestTabe.item(selected_row, 0).text()

        # Normalize the lab_test_name: strip whitespace and convert to lowercase
        lab_test_name = lab_test_name.strip().lower()

        # Retrieve the lab_code using the normalized lab_test_name
        lab_code = Laboratory.get_lab_code_by_name(lab_test_name)
        if not lab_code:
            QMessageBox.critical(self, "Error", "Failed to retrieve lab code.")
            return

        print(f"Retrieved lab code: {lab_code}")

        # Fetch the file path from the CheckUp model
        file_path = CheckUp.get_lab_attachment(self.checkup_id, lab_code)
        if not file_path:
            QMessageBox.warning(self, "No Attachment", "No file is attached to this lab test.")
            return

        print(f"File path to open: {file_path}")

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


