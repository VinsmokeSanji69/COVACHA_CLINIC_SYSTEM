import datetime
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt5.QtCore import QDate, QRegExp
from PyQt5.QtGui import QRegExpValidator

from Controllers.ClientSocketController import DataRequest
from Views.Staff_AddCheckUp import Ui_Staff_AddCheckUp as StaffCheckUpUi

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Add Check-Up Creation")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()

        self.message_label = QLabel("Are you sure you want to add this check-up?")
        layout.addWidget(self.message_label)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

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
        self.setLayout(layout)

class StaffAddCheckUp(QMainWindow):
    def __init__(self, parent=None, staff_id = None):
        super().__init__(parent)
        self.parent = parent
        self.staff_id = staff_id
        self.ui = StaffCheckUpUi()
        self.ui.setupUi(self)
        self.initialize_ui()
        self.connect_signals()
        self.setWindowTitle("Check Up")
        self.setFixedSize(800, 700)
        self.is_new_patient = False

    def initialize_ui(self):
        self.ui.CheckType.addItems(["New Check Up", "Follow Up Check Up"])
        self.ui.CheckType.setStyleSheet("QComboBox QAbstractItemView { color: black; }")
        self.ui.CheckType.setCurrentIndex(-1)
        self.ui.DateJoined.setDate(QDate.currentDate())
        self.ui.DateJoined.setReadOnly(True)
        self.ui.DateJoined.setCalendarPopup(True)
        self.ui.Gender.addItems(["Male", "Female"])
        self.ui.Gender.setStyleSheet("QComboBox QAbstractItemView { color: black; }")
        contact_validator = QRegExpValidator(QRegExp("[0-9]{10}"))
        self.ui.Contact.setValidator(contact_validator)
        self.ui.Contact.setPlaceholderText("10 digits (zero not included)")
        self.ui.Contact.setMaxLength(10)
        self.ui.Dob.setDate(QDate(1900, 1, 1))
        self.ui.Dob.dateChanged.connect(self.calculate_age)

    def calculate_age(self):
        dob = self.ui.Dob.date()
        today = QDate.currentDate()
        age = today.year() - dob.year()
        if today.month() < dob.month() or (today.month() == dob.month() and today.day() < dob.day()):
            age -= 1
        self.ui.Age.setText(str(age))

    def connect_signals(self):
        """
        Connect signals to their respective slots.
        """
        self.ui.AddCheckUp.clicked.connect(self.validate_and_submit)
        self.ui.Cancel.clicked.connect(self.cancel_checkup)

        # Use editingFinished instead of textChanged to avoid premature checks
        self.ui.Fname.editingFinished.connect(self.check_fields_and_validate)
        self.ui.Lname.editingFinished.connect(self.check_fields_and_validate)
        self.ui.Dob.dateChanged.connect(self.check_fields_and_validate)

        self.ui.Dob.dateChanged.connect(self.calculate_age)

    def cancel_checkup(self):
        """
        Handles cancel operation. Deletes the newly added patient if not yet saved.
        """
        if self.is_new_patient:
            patient_id = self.ui.ID.text().strip()
            if patient_id:
                try:
                    #success = Patient.delete_patient_by_id(int(patient_id))
                    success = DataRequest.send_command("DELETE_PATIENT",int(patient_id))
                    if success:
                        QMessageBox.information(self, "Cancelled", "New patient entry was discarded.")
                    else:
                        QMessageBox.warning(self, "Warning",
                                            "Attempted to delete new patient. Deletion status is unclear.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete new patient: {str(e)}")
        else:
            QMessageBox.information(self, "Cancelled", "Changes were not saved.")

        self.close()

    def check_fields_and_validate(self):
        # Default DOB check
        default_dob = QDate(1900, 1, 1)
        current_dob = self.ui.Dob.date()

        # Check if all fields are filled and DOB is not default
        if (self.ui.Fname.text().strip() and
                self.ui.Lname.text().strip() and
                not current_dob.isNull() and
                current_dob != default_dob):
            self.check_patient_existence()

    def check_patient_existence(self):
        """
        Check if a patient exists based on Fname and Lname and prefill the form if they do.
        If the patient does not exist, generate a new patient ID.
        """
        fname = self.ui.Fname.text().strip()
        lname = self.ui.Lname.text().strip()
        dob = self.ui.Dob.date().toString()

        # Validate required fields
        if not fname:
            QMessageBox.warning(self, "Missing Information", "Please enter the First Name.")
            return
        if not lname:
            QMessageBox.warning(self, "Missing Information", "Please enter the Last Name.")
            return
        if not dob:  # Check if DOB is not set
            QMessageBox.warning(self, "Missing Information", "Please select a Date of Birth.")
            return

        try:
            # Check if the patient already exists in the database
            #patient = Patient.get_patient_by_name(fname, lname, dob)
            patient = DataRequest.send_command("GET_PATIENT_BY_NAME", [fname, lname, dob])

            if patient:
                # Ensure the response is a dictionary
                self.is_new_patient = False
                if not isinstance(patient, dict):
                    raise ValueError("Unexpected response format from GET_PATIENT_BY_NAME")

                # Prefill all patient information
                self.ui.ID.setText(str(patient.get("id", "")))
                self.ui.Mname.setText(patient.get("middle_name", ""))
                self.ui.Gender.setCurrentText(patient.get("gender", ""))
                # Handle dob formatting
                dob_str = patient.get("dob", "")
                if isinstance(dob_str, datetime.date):
                    dob_str = dob_str.strftime("%Y-%m-%d")
                elif isinstance(dob_str, str):
                    pass
                else:
                    raise ValueError("Invalid date format for DOB")
                self.ui.Dob.setDate(QDate.fromString(dob_str, "yyyy-MM-dd"))
                self.ui.Address.setText(patient.get("address", ""))
                self.ui.Contact.setText(patient.get("contact", ""))
                self.calculate_age()  # Update age based on DOB
                QMessageBox.information(self, "Patient Found",
                                        "Patient already exists. Information has been prefilled.")
            else:
                # Clear fields for a new patient
                self.ui.Mname.clear()
                self.ui.Gender.setCurrentIndex(-1)
                self.ui.Address.clear()
                self.ui.Contact.clear()
                self.ui.Age.clear()

                # Generate a new patient ID
                # new_pat_id = Patient.create_new_patient( {
                #     "first_name": fname,
                #     "last_name": lname,
                #     "middle_name": "",
                #     "gender": "",
                #     "dob": dob,
                #     "address": "",
                #     "contact": ""
                # })
                new_pat_id = DataRequest.send_command("CREATE_PATIENT", {
                    "first_name": fname,
                    "last_name": lname,
                    "middle_name": "",
                    "gender": "",
                    "dob": dob,
                    "address": "",
                    "contact": ""
                })

                if new_pat_id:
                    self.ui.ID.setText(str(new_pat_id))
                    self.is_new_patient = True
                    QMessageBox.information(self, "New Patient", "A new patient ID has been generated.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to generate a new patient ID.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    def validate_form(self):
        errors = []

        # Name validation
        if not self.ui.Fname.text().strip():
            errors.append("First name is required")
            self.ui.Fname.setFocus()
        if not self.ui.Lname.text().strip():
            errors.append("Last name is required")
        if not self.ui.Mname.text().strip():
            errors.append("Middle name is required")

        # Contact validation
        contact = self.ui.Contact.text().strip()
        if not contact:
            errors.append("Contact number is required")
        elif len(contact) != 10 or not contact.isdigit():
            errors.append("Contact number must be exactly 10 digits (zero not included)")

        # ID validation
        if not self.ui.ID.text().strip():
            errors.append("Patient ID is required. Please ensure first and last names, and birthdate are entered.")

        # Display errors
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return False
        return True

    def collect_data(self):
        data = {
            "first_name": self.ui.Fname.text().strip(),
            "last_name": self.ui.Lname.text().strip(),
            "middle_name": self.ui.Mname.text().strip(),
            "gender": self.ui.Gender.currentText(),
            "id": int(self.ui.ID.text().strip()),
            "dob": self.ui.Dob.date().toString("yyyy-MM-dd"),
            "date_joined": self.ui.DateJoined.date().toString("yyyy-MM-dd"),
            "address": self.ui.Address.text().strip(),
            "contact": self.ui.Contact.text().strip(),
            "bloodpressure": self.ui.BP.text().strip(),
            "height": self.ui.Height.text().strip(),
            "weight": self.ui.Weight.text().strip(),
            "temperature": self.ui.Temp.text().strip(),
            "staff_id": int(self.staff_id),
            "checkup_type" : self.ui.CheckType.currentText()
        }
        return data

    def validate_and_submit(self):
        # Validate the form
        if not self.validate_form():
            return

        # Show confirmation dialog
        confirmation_dialog = ConfirmationDialog(self)
        if confirmation_dialog.exec_() == QDialog.Rejected:
            return
        # Collect data
        data = self.collect_data()

        # Save or update patient information
        if DataRequest.send_command("UPDATE_OR_CREATE_PATIENT",data):
            # Save check-up data
            if DataRequest.send_command("CREATE_CHECKUP",data):
                QMessageBox.information(self, "Success", "Check-up added successfully!")
                self.clear_form()

                # Notify the parent window to refresh the PendingTable
                if hasattr(self, 'refresh_callback') and callable(self.refresh_callback):
                    self.refresh_callback()
            else:
                QMessageBox.critical(self, "Error", "Failed to add check-up. Please try again.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save or update patient information.")

    def clear_form(self):
        """
        Clear all form fields and reset the UI.
        """
        self.ui.Fname.clear()
        self.ui.Lname.clear()
        self.ui.Mname.clear()
        self.ui.ID.clear()
        self.ui.Gender.setCurrentIndex(0)
        self.ui.CheckType.setCurrentIndex(0)
        self.ui.Dob.setDate(QDate(1900, 1, 1))
        self.ui.Address.clear()
        self.ui.Contact.clear()
        self.ui.BP.clear()
        self.ui.Height.clear()
        self.ui.Weight.clear()
        self.ui.Temp.clear()
        self.ui.DateJoined.setDate(QDate.currentDate())
        self.ui.Fname.setFocus()