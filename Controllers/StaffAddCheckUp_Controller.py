from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt5.QtCore import QDate, QRegExp
from PyQt5.QtGui import QRegExpValidator
from Views.Staff_AddCheckUp import Ui_MainWindow as StaffCheckUpUi
from Models.Patient import Patient
from Models.CheckUp import CheckUp

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
        self.ui.Dob.dateChanged.connect(self.calculate_age)

    def calculate_age(self):
        dob = self.ui.Dob.date()
        today = QDate.currentDate()
        age = today.year() - dob.year()
        if today.month() < dob.month() or (today.month() == dob.month() and today.day() < dob.day()):
            age -= 1
        self.ui.Age.setText(str(age))

    def connect_signals(self):
        self.ui.AddCheckUp.clicked.connect(self.validate_and_submit)
        self.ui.Cancel.clicked.connect(self.close)

    def prefill_patient_id(self):
        fname = self.ui.Fname.text().strip()
        lname = self.ui.Lname.text().strip()

        if not fname or not lname:
            QMessageBox.warning(self, "Input Error", "First name and last name are required.")
            return False

        # Check if the patient already exists
        pat_id = Patient.get_patient_id(fname, lname)
        if pat_id:
            self.ui.ID.setText(str(pat_id))  # Prefill the ID field
            print(f"Prefilled existing patient ID: {pat_id}")
            return True
        else:
            # Create a new patient record
            data = {
                "last_name": lname,
                "first_name": fname,
                "middle_name": self.ui.Mname.text().strip(),
                "address": self.ui.Address.text().strip(),
                "contact": self.ui.Contact.text().strip(),
                "dob": self.ui.Dob.date().toString("yyyy-MM-dd"),
                "gender": self.ui.Gender.currentText()
            }

            new_pat_id = Patient.create_new_patient(data)
            if new_pat_id:
                self.ui.ID.setText(str(new_pat_id))  # Prefill the ID field
                print(f"Generated new patient ID: {new_pat_id}")
                return True
            else:
                QMessageBox.critical(self, "Error", "Failed to create new patient.")
                return False

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

        # Medical details validation
        if not self.ui.BP.text().strip():
            errors.append("Blood Pressure is required")
        if not self.ui.Height.text().strip():
            errors.append("Height is required")
        if not self.ui.Weight.text().strip():
            errors.append("Weight is required")
        if not self.ui.Temp.text().strip():
            errors.append("Temperature is required")

        # ID validation
        if not self.ui.ID.text().strip():
            errors.append("Patient ID is required. Please ensure first and last names are entered.")

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
            "staff_id": int(self.staff_id)
        }
        print(f"Collected data: {data}")
        return data

    def validate_and_submit(self):
        # Prefill the patient ID
        if not self.prefill_patient_id():
            return

        # Validate the form
        if not self.validate_form():
            return

        # Show confirmation dialog
        confirmation_dialog = ConfirmationDialog(self)
        if confirmation_dialog.exec_() == QDialog.Rejected:
            return

        # Collect data
        data = self.collect_data()

        # Debug: Print collected data before saving
        print(f"Data to be saved: {data}")

        # Save check-up data
        if CheckUp.save_checkup(data):
            QMessageBox.information(self, "Success", "Check-up added successfully!")
            self.clear_form()
        else:
            QMessageBox.critical(self, "Error", "Failed to add check-up. Please try again.")

    def clear_form(self):
        """
        Clear all form fields and reset the UI.
        """
        self.ui.Fname.clear()
        self.ui.Lname.clear()
        self.ui.Mname.clear()
        self.ui.ID.clear()
        self.ui.Gender.setCurrentIndex(0)
        self.ui.Dob.setDate(QDate(1990, 1, 1))
        self.ui.Address.clear()
        self.ui.Contact.clear()
        self.ui.BP.clear()
        self.ui.Height.clear()
        self.ui.Weight.clear()
        self.ui.Temp.clear()
        self.ui.DateJoined.setDate(QDate.currentDate())
        self.ui.Fname.setFocus()