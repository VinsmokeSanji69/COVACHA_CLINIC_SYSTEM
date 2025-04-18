from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QCheckBox, QMessageBox
from Controllers.DoctorLabResult_Controller import DoctorLabResult
from Views.Doctor_Diagnosis import Ui_MainWindow as DoctorDiagnosisUI
from Controllers.DoctorRecords_Controller import DoctorRecords
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Models.LaboratoryTest import Laboratory
from datetime import datetime, date

class DoctorDiagnosis(QMainWindow):
    def __init__(self, checkup_id, doc_id, parent=None, doctor_dashboard=None):
        super().__init__(parent)
        self.ui = DoctorDiagnosisUI()
        self.ui.setupUi(self)

        # Store the checkup ID, doc_id, and reference to the DoctorDashboard
        self.checkup_id = checkup_id
        self.doc_id = doc_id
        self.doctor_dashboard = doctor_dashboard

        print(f"DoctorDiagnosis initialized successfully with CheckUp ID: {checkup_id} and doc_id: {doc_id}")

        # Load and display data related to the checkup ID
        self.load_data()

        # Display lab tests in two frames
        self.display_lab_tests()

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
            chck_height = checkup_details['chck_height']
            chck_weight = checkup_details['chck_weight']

            # Step 2: Fetch patient details
            patient_details = Patient.get_patient_details(pat_id)
            if not patient_details:
                raise ValueError("No patient details found for the given ID.")

            # Extract patient data
            pat_lname = patient_details['pat_lname']
            pat_fname = patient_details['pat_fname']
            pat_mname = patient_details['pat_mname']
            pat_dob = patient_details['pat_dob']
            pat_gender = patient_details['pat_gender']

            # Calculate age based on date of birth
            age = self.calculate_age(pat_dob)

            # Convert pat_dob to a string for display
            Birthday = pat_dob.strftime("%Y-%m-%d")

            # Step 3: Populate the UI
            self.populate_patient_info(pat_lname, pat_fname, pat_mname, Birthday, age, pat_gender)
            self.populate_checkup_info(chck_bp, chck_temp, chck_height, chck_weight)

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

    def populate_patient_info(self, pat_lname, pat_fname, pat_mname, pat_dob, age, gender):
        """Populate the patient information fields."""
        self.ui.PatName.setText(f"{pat_lname}, {pat_fname} {pat_mname}")
        self.ui.Dob.setText(pat_dob)
        self.ui.Age.setText(str(age))

    def populate_checkup_info(self, chck_bp, chck_temp, chck_height, chck_weight):
        """Populate the check-up information fields."""
        self.ui.BP.setText(chck_bp)
        self.ui.Temperature.setText(chck_temp)
        self.ui.Height.setText(chck_height)
        self.ui.Weight.setText(chck_weight)

    def display_lab_tests(self):
        """Display lab tests in two frames."""
        try:
            # Fetch all lab tests
            tests = Laboratory.get_all_test()

            # Count the total number of lab tests
            total_tests = Laboratory.count_all_test()

            # Divide the tests into two groups
            half = (total_tests + 1) // 2
            first_group = tests[:half]
            second_group = tests[half:]

            # Clear existing layouts in the frames
            self.clear_layout(self.ui.FirstFrame.layout())
            self.clear_layout(self.ui.SecondFrame.layout())

            # Add checkboxes to the first frame
            self.add_checkboxes_to_frame(first_group, self.ui.FirstFrame)

            # Add checkboxes to the second frame
            self.add_checkboxes_to_frame(second_group, self.ui.SecondFrame)

            # Connect the ProceedButton to process_selected_tests
            if hasattr(self.ui, 'ProceedButton'):
                self.ui.ProceedButton.clicked.connect(self.process_selected_tests)
            else:
                QMessageBox.warning(self, "Missing Button", "ProceedButton is missing in the UI.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display lab tests: {e}")

    def ViewRecords(self):
        print("Opening Doctor Records...")
        try:
            # Close the DoctorDashboard window if it exists
            if self.doctor_dashboard:
                self.doctor_dashboard.close()
            # Close the current DoctorDiagnosis window
            self.close()
            # Instantiate and show the DoctorRecords window with the doc_id
            self.doctor_records = DoctorRecords(doc_id=self.doc_id)
            self.doctor_records.show()
        except Exception as e:
            print(f"Error loading Doctor Records: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load Doctor Records: {e}")

    def clear_layout(self, layout):
        """Clear all widgets from a layout."""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def add_checkboxes_to_frame(self, tests, frame):
        """Add checkboxes for the given tests to the specified frame."""
        layout = frame.layout()
        if layout is None:
            layout = QVBoxLayout(frame)
            frame.setLayout(layout)

        for test in tests:
            lab_code = test["lab_code"]
            lab_name = test["lab_test_name"]

            # Create a QCheckBox for each test
            checkbox = QCheckBox(f"{lab_name}")
            checkbox.setProperty("lab_code", lab_code)
            layout.addWidget(checkbox)

    def process_selected_tests(self):
        """Process the selected checkboxes and store the lab codes."""
        # Collect selected lab codes from both frames
        selected_lab_codes = []

        for frame in [self.ui.FirstFrame, self.ui.SecondFrame]:
            layout = frame.layout()
            if layout:
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if isinstance(widget, QCheckBox) and widget.isChecked():
                        lab_code = widget.property("lab_code")
                        selected_lab_codes.append(lab_code)

        # Check if OtherText has a value
        other_text_value = self.ui.OtherText.text().strip()  # Get the value and remove extra spaces

        # Add the OtherText value to the list if it exists
        if other_text_value:
            selected_lab_codes.append(other_text_value)

        # Join selected lab codes with a comma (empty string if no selections)
        selected_lab_codes_str = ", ".join(selected_lab_codes) if selected_lab_codes else ""

        # Update the checkup table with the selected lab codes
        success = CheckUp.update_lab_codes(self.checkup_id, selected_lab_codes_str)
        if not success:
            QMessageBox.critical(self, "Error", "Failed to update lab codes.")
            return

        # Check if no checkboxes are selected and OtherText is empty
        if not selected_lab_codes and not other_text_value:
            # Open the DoctorLabResult modal
            self.open_doctor_lab_result_modal()
        else:
            # Proceed to ViewRecords
            QMessageBox.information(self, "Success", f"Selected Lab Codes: {selected_lab_codes_str}")
            self.ViewRecords()

    def open_doctor_lab_result_modal(self):
        """Open the DoctorLabResult modal."""
        try:
            # Instantiate and show the DoctorLabResult modal
            self.doctor_lab_result = DoctorLabResult(checkup_id=self.checkup_id)
            self.doctor_lab_result.show()
            self.close()
            self.doctor_dashboard.close()
        except Exception as e:
            print(f"Error opening DoctorLabResult modal: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open DoctorLabResult modal: {e}")