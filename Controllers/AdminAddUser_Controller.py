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


class AdminAddUserController(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = AdminAddUserUI()
        self.ui.setupUi(self)
        # Window settings
        self.setWindowTitle("Staff Registration")
        self.setFixedSize(800, 800)
        self.initialize_ui()
        self.ui.Indicator.setVisible(False)
        self.connect_signals()
        self.apply_styles()
        self.show()
        self.raise_()
        self.activateWindow()


    def initialize_ui(self):
        """Initialize UI components with default values"""
        # Set up staff types
        self.ui.StaffType.addItems(["Doctor", "Staff"])
        self.ui.StaffType.setStyleSheet("QComboBox QAbstractItemView { color: black; }")
        self.ui.StaffType.setCurrentIndex(-1)
        # Set up specialties
        clinic_specialties = [
            "General Practitioner",
            "Family Medicine",
            "Internal Medicine",
            "Endocrinology (Diabetes)",
            "Cardiology (Heart)",
            "Gastroenterology (GI)",
            "Nephrology (Kidney)",
            "Hematology (Blood)",
            "Pulmonology (Lungs)",
            "OB-GYN (Women's Health)",
            "Pediatrics",
            "Infectious Disease",
            "Dermatology (Skin)",
            "Neurology (Brain/Nerves)",
            "Rheumatology (Joints)"
        ]
        self.ui.Specialty.addItems(clinic_specialties)
        self.ui.Specialty.setStyleSheet("QComboBox QAbstractItemView { color: black; }")
        self.ui.Specialty.setCurrentIndex(-1)  # No default selection
        # Set up gender options
        self.ui.Gender.addItems(["Male", "Female"])
        self.ui.Gender.setStyleSheet("QComboBox QAbstractItemView { color: black; }")
        # Set default dates
        self.ui.DateJoined.setDate(QDate.currentDate())
        self.ui.Dob.setDate(QDate(1990, 1, 1))  # Default to reasonable
        # Set up contact number validation (exactly 10 digits, including leading zero)
        contact_validator = QRegExpValidator(QRegExp("[0-9]{10}"))
        self.ui.Contact.setValidator(contact_validator)
        self.ui.Contact.setPlaceholderText("10 digits (zero not included)")
        self.ui.Contact.setMaxLength(10)
        self.ui.Email.setPlaceholderText("example@gmail.com")
        # Hide doctor-specific fields initially
        self.ui.Specialization.setVisible(False)
        self.ui.Title_2.setVisible(False)

    def connect_signals(self):
        """Connect all UI signals to their slots"""
        # Connect buttons
        self.ui.AddStaff.clicked.connect(self.validate_and_submit)
        self.ui.Cancel.clicked.connect(self.close)
        # Connect staff type change
        self.ui.StaffType.currentTextChanged.connect(self.toggle_specialization)
        self.ui.StaffType.currentTextChanged.connect(self.prefill_id_based_on_staff_type)
        # Set initial visibility
        self.toggle_specialization(self.ui.StaffType.currentText())

    def toggle_specialization(self, staff_type):
        is_doctor = (staff_type == "Doctor")
        self.ui.Specialization.setVisible(is_doctor)
        self.ui.Title_2.setVisible(is_doctor)

    def prefill_id_based_on_staff_type(self):
        """Prefill the ID field based on the selected staff type"""
        staff_type = self.ui.StaffType.currentText()

        if staff_type == "Doctor":
            next_id = Doctor.get_next_doctor_id()
        elif staff_type == "Staff":
            next_id = Staff.get_next_staff_id()

        if next_id is not None:
            self.ui.ID.setText(str(next_id))
        else:
            QMessageBox.critical(self, "Database Error", f"Failed to fetch next ID for {staff_type}")


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
                    success = Staff.save_staff(staff_data)
                elif self.ui.StaffType.currentText() == "Doctor":
                    success = Doctor.save_doctor(staff_data)

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
        """Collect all form data into a dictionary"""
        return {
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

    def clear_form(self):
        """Clear all form fields"""
        self.ui.Fname.clear()
        self.ui.Lname.clear()
        self.ui.ID.clear()
        self.ui.Gender.setCurrentIndex(0)
        self.ui.Dob.setDate(QDate(1990, 1, 1))
        self.ui.Address.clear()
        self.ui.Contact.clear()
        self.ui.StaffType.setCurrentIndex(0)
        self.ui.Specialty.setCurrentIndex(-1)
        self.ui.License.clear()
        # Reset to today's date for joined date
        self.ui.DateJoined.setDate(QDate.currentDate())
        # Set focus back to first field
        self.ui.Fname.setFocus()

    def apply_styles(self):
        # # Style for QDateEdit
        # dateedit_style = """
        #     QDateEdit {
        #         background-color: #F4F7ED;
        #         border: 1px solid #2E6E65;
        #         border-radius: 10px;
        #         padding: 5px 10px;
        #         font: 300 12pt "Lexend Light";
        #         color: black; /* Set text color to black */
        #     }
        #     /* Dropdown arrow styling */
        #     QDateEdit::down-arrow {
        #         image: url(:/lucide/icons/calendar.svg);
        #         width: 20px;
        #         height: 20px;
        #     }
        # """
        # self.ui.DateJoined.setStyleSheet(dateedit_style)
        # self.ui.Dob.setStyleSheet(dateedit_style)
        # Style for QComboBox
        combobox_style = """
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid gray;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: lightblue;
                selection-color: black;
            }
        """
        self.ui.StaffType.setStyleSheet(combobox_style)
        self.ui.Specialty.setStyleSheet(combobox_style)
        self.ui.Gender.setStyleSheet(combobox_style)
        # Style for QLineEdit
        lineedit_style = """
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid gray;
                padding: 5px;
            }
        """
        self.ui.Fname.setStyleSheet(lineedit_style)
        self.ui.Lname.setStyleSheet(lineedit_style)
        self.ui.Mname.setStyleSheet(lineedit_style)
        self.ui.ID.setStyleSheet(lineedit_style)
        self.ui.Address.setStyleSheet(lineedit_style)
        self.ui.Email.setStyleSheet(lineedit_style)
        self.ui.Contact.setStyleSheet(lineedit_style)
        self.ui.License.setStyleSheet(lineedit_style)