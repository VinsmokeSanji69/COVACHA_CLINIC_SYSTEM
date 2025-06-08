import sys
import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QLabel, QVBoxLayout, QDialogButtonBox
from PyQt5.QtCore import QDate, QRegExp
from PyQt5.QtGui import QRegExpValidator
from Views.Admin_AddStaff import Ui_MainWindow as AdminAddUserUI
import hashlib
from Models.Staff import Staff
from Models.Doctor import Doctor
# Add this to make other controllers work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Account Creation")
        self.setFixedSize(400, 150)
        # Main layout
        layout = QVBoxLayout()
        # Add message label
        self.message_label = QLabel("Are you sure you want to create this account?")
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


class AdminModifyUserController(QMainWindow):
    def __init__(self, parent=None, staff_details=None, staff_type = None):
        super().__init__(parent)
        self.parent = parent
        self.staff_type = staff_type
        self.staff_details = staff_details
        self.ui = AdminAddUserUI()
        self.ui.setupUi(self)
        # Window settings
        self.setWindowTitle("Staff Registration")
        self.setFixedSize(800, 800)
        self.initialize_ui()
        self.ui.Indicator.setVisible(False)
        self.connect_signals()
        self.show()
        self.raise_()
        self.activateWindow()

    def initialize_ui(self):
        """Initialize UI components with default values"""
        try:
            # Set up staff types combobox (make non-editable)
            self.ui.Subheader.setText("Modify Staff Details")
            self.ui.AddStaff.setText("Update")
            self.ui.StaffType.addItems([self.staff_type.title()])
            self.ui.StaffType.setEditable(False)  # This makes it completely non-editable
            self.ui.StaffType.setCurrentIndex(0)

            # Connect signal after setting up
            self.ui.StaffType.currentTextChanged.connect(
                lambda text: self.toggle_specialization(text.lower())
            )

            # Set up specialties combobox
            clinic_specialties = [
                "General Practitioner", "Family Medicine", "Internal Medicine",
                "Endocrinology (Diabetes)", "Cardiology (Heart)",
                "Gastroenterology (GI)", "Nephrology (Kidney)",
                "Hematology (Blood)", "Pulmonology (Lungs)",
                "OB-GYN (Women's Health)", "Pediatrics", "Infectious Disease",
                "Dermatology (Skin)", "Neurology (Brain/Nerves)",
                "Rheumatology (Joints)"
            ]
            self.ui.Specialty.addItems(clinic_specialties)
            self.ui.Specialty.setCurrentIndex(-1)

            # Set up gender combobox
            self.ui.Gender.addItems(["Male", "Female"])
            self.ui.Gender.setCurrentIndex(-1)

            # Set up validation
            contact_validator = QRegExpValidator(QRegExp(r"^\d{10}$"))  # Exactly 10 digits
            self.ui.Contact.setValidator(contact_validator)
            self.ui.Contact.setPlaceholderText("10 digits (e.g., 9123456789)")
            self.ui.Contact.setMaxLength(10)
            self.ui.Email.setPlaceholderText("example@domain.com")

            # Set default dates first
            self.ui.DateJoined.setDate(QDate.currentDate())
            self.ui.Dob.setDate(QDate(1990, 1, 1))

            # Now populate from staff_details if available
            if hasattr(self, 'staff_details') and self.staff_details:
                self.populate_from_staff_details()

            # Set initial visibility
            self.ui.Specialization.setVisible(False)
            self.ui.Title_2.setVisible(False)

        except Exception as e:
            QMessageBox.critical(self, "Initialization Error",
                                 f"Failed to initialize UI: {str(e)}")

    def populate_from_staff_details(self):
        """Populate fields from staff_details dictionary"""
        try:
            # Set staff type
            if hasattr(self, 'staff_type') and self.staff_type:
                staff_type = self.staff_type.capitalize()  # Ensure proper case
                index = self.ui.StaffType.findText(staff_type)
                if index >= 0:
                    self.ui.StaffType.setCurrentIndex(index)

            # Set basic info
            self.ui.ID.setText(str(self.staff_details.get("id", "")))
            self.ui.Fname.setText(self.staff_details.get("first_name", ""))
            self.ui.Lname.setText(self.staff_details.get("last_name", ""))
            self.ui.Mname.setText(self.staff_details.get("middle_name", ""))
            self.ui.Address.setText(self.staff_details.get("address", ""))
            self.ui.Contact.setText(self.staff_details.get("contact", ""))
            self.ui.Email.setText(self.staff_details.get("email", ""))

            # Set gender
            gender = self.staff_details.get("gender", "")
            if gender:
                index = self.ui.Gender.findText(gender)
                if index >= 0:
                    self.ui.Gender.setCurrentIndex(index)

            # Handle dates - convert string dates to QDate if needed
            dob = self.staff_details.get("dob")
            if dob:
                if isinstance(dob, str):
                    qdate = QDate.fromString(dob, "yyyy-MM-dd")
                    if qdate.isValid():
                        self.ui.Dob.setDate(qdate)
                elif hasattr(dob, 'year'):  # Already a QDate or datetime.date
                    self.ui.Dob.setDate(dob)

            joined_date = self.staff_details.get("joined_date")
            if joined_date:
                if isinstance(joined_date, str):
                    qdate = QDate.fromString(joined_date, "yyyy-MM-dd")
                    if qdate.isValid():
                        self.ui.DateJoined.setDate(qdate)
                elif hasattr(joined_date, 'year'):
                    self.ui.DateJoined.setDate(joined_date)

            # Doctor-specific fields
            if hasattr(self, 'staff_type') and self.staff_type.lower() == "doctor":
                self.ui.License.setText(str(self.staff_details.get("license", "")))
                specialty = self.staff_details.get("specialty", "")
                if specialty:
                    index = self.ui.Specialty.findText(specialty)
                    if index >= 0:
                        self.ui.Specialty.setCurrentIndex(index)

        except Exception as e:
            QMessageBox.warning(self, "Data Error",
                                f"Couldn't load staff details: {str(e)}")
    def connect_signals(self):
        """Connect all UI signals to their slots"""
        # Connect buttons
        self.ui.AddStaff.clicked.connect(self.validate_and_submit)
        self.ui.Cancel.clicked.connect(self.close)
        # Connect staff type change
        self.ui.StaffType.currentTextChanged.connect(self.toggle_specialization)
        # Set initial visibility
        self.toggle_specialization(self.ui.StaffType.currentText())

    def toggle_specialization(self, staff_type):
        is_doctor = (staff_type == "Doctor")
        self.ui.Specialization.setVisible(is_doctor)
        self.ui.Title_2.setVisible(is_doctor)

    def validate_and_submit(self):
        """Validate form, generate password, and submit data"""
        if not self.validate_form():
            return
        try:
            # Collect data
            staff_data = self.collect_form_data()

            # Generate temporary password
            temp_password = f"{staff_data['last_name']}"
            hashed_password = hashlib.sha256(temp_password.encode()).hexdigest()
            staff_data["password"] = hashed_password

            # Show confirmation dialog
            confirmation_dialog = ConfirmationDialog(self)
            result = confirmation_dialog.exec()

            if result == QDialog.Accepted:  # User clicked "Yes"
                # Save to database
                if self.ui.StaffType.currentText() == "Staff":
                    success = Staff.update(staff_data)
                elif self.ui.StaffType.currentText() == "Doctor":
                    success = Doctor.update(staff_data)

                if success:
                    QMessageBox.information(self, "Success", "Account created successfully!")
                    self.clear_form()

                    # Notify parent to refresh tables
                    if self.parent and hasattr(self.parent, 'refresh_tables'):
                        self.parent.refresh_tables()
                else:
                    QMessageBox.critical(self, "Error", "Failed to save data to the database.")
            else:  # User clicked "Cancel"
                QMessageBox.information(self, "Cancelled", "Account creation cancelled.\n( Press any key to close )")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add staff: {str(e)}")
            print(f"Error: {str(e)}")

    def validate_form(self):
        """Validate all form fields"""
        errors = []
        # Name validation
        if not self.ui.Fname.text().strip():
            errors.append("First name is required")
            self.ui.Fname.setFocus()
        if not self.ui.Lname.text().strip():
            errors.append("Last name is required")
            if not errors:  # Only set focus if first name is valid
                self.ui.Lname.setFocus()
        if not self.ui.Mname.text().strip():
            errors.append("Mast name is required")
            if not errors:  # Only set focus if first name is valid
                self.ui.Mname.setFocus()
        # Email validation
        email = self.ui.Email.text().strip()
        if not email:
            errors.append("Email is required")
            if not errors:
                self.ui.Email.setFocus()
        elif "@" not in email:
            errors.append("Please enter a valid email address")
            if not errors:
                self.ui.Email.setFocus()
        # Contact validation
        contact = self.ui.Contact.text().strip()
        if not contact:
            errors.append("Contact number is required")
            if not errors:
                self.ui.Contact.setFocus()
        elif len(contact) != 10 or not contact.isdigit():
            errors.append("Contact number must be exactly 10 digits (zero not included)")
            if not errors:
                self.ui.Contact.setFocus()
        # Doctor-specific validation
        if self.ui.StaffType.currentText() == "Doctor":
            license_number = self.ui.License.text().strip()
            if not license_number:
                errors.append("License number is required for doctors")
                if not errors:
                    self.ui.License.setFocus()
        # Show errors if any
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return False
        return True

    def collect_form_data(self):
        return {
            'id': self.ui.ID.text().strip(),
            'first_name': self.ui.Fname.text().strip(),
            'last_name': self.ui.Lname.text().strip(),
            "middle_name": self.ui.Mname.text().strip(),
            'gender': self.ui.Gender.currentText(),
            'dob': self.ui.Dob.date().toString("yyyy-MM-dd"),
            'date_joined': self.ui.DateJoined.date().toString("yyyy-MM-dd"),
            'address': self.ui.Address.text().strip(),
            "email": self.ui.Email.text().strip(),
            'contact': self.ui.Contact.text().strip(),
            'specialty': self.ui.Specialty.currentText() if self.ui.StaffType.currentText() == "Doctor" else None,
            'license': int(self.ui.License.text().strip()) if self.ui.StaffType.currentText() == "Doctor" else None
        }

