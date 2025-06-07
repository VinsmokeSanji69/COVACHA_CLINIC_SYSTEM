import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox

from Models.Doctor import Doctor
from Views.Admin_AddDoctorCharges import Ui_MainWindow as AdminAddChargesUI
from Models.LaboratoryTest import Laboratory

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Add Laboratory")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want modify doctor charge?")
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


class AdminDoctorCharges(QMainWindow):
    def __init__(self, doc_id ,parent=None):
        super().__init__(parent)
        self.doc_id = doc_id
        self.ui = AdminAddChargesUI()
        self.ui.setupUi(self)

        # Set window properties
        self.setWindowTitle("Add Doctor Charges")
        self.setFixedSize(700, 500)

        self.ui.DocID.setReadOnly(True)
        self.ui.DocName.setReadOnly(True)
        self.ui.Specialty.setReadOnly(True)
        self.initialize_doctor_details()
        self.ui.ModifyCharges.clicked.connect(self.validate_and_save_charges)

        self.ui.Cancel.clicked.connect(self.close)

        print("AdminAddLabTest initialized successfully!")

    def initialize_doctor_details(self):
        try:
            doctors = Doctor.get_all_doctors()
            doctor_details = None

            # Find the matching doctor
            for doctor in doctors:
                if str(self.doc_id) == str(doctor.get("id")):  # Using .get() for safety
                    doctor_details = doctor
                    break

            if not doctor_details:
                raise ValueError(f"No doctor found with ID: {self.doc_id}")

            # Safely set text with .get() and fallback values
            self.ui.DocName.setText(doctor_details.get("name", "N/A"))
            self.ui.Specialty.setText(doctor_details.get("specialty", "N/A"))
            self.ui.DocID.setText(str(doctor_details.get("id", "")))
            self.ui.DocRate.setText(str(doctor_details.get("rate", 0.0)))  # Default to 0.0 if rate missing

        except ValueError as ve:
            print(f"Warning: {str(ve)}")
        except Exception as e:
            print(f"Error initializing doctor details: {e}")

    def validate_form(self):
        errors = []
        # Validate Price
        price = self.ui.DocRate.text().strip()
        if not price:
            errors.append("Price is required.")
        elif not price.isdigit():
            errors.append("Price must be a number.")

        return errors

    def validate_and_save_charges(self):
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Show confirmation dialog
        confirmation_dialog = ConfirmationDialog(self)
        if confirmation_dialog.exec_() == QDialog.Rejected:
            return

        doctor = {
            "doctor_id": self.doc_id ,
            "new_rate": self.ui.DocRate.text().strip()
        }

        # Save data to the database
        success = Doctor.update_doctor_rate(doctor)
        if success:
            QMessageBox.information(self, "Success", "Doctor rate modified successfully!")
            self.view_charges_ui()
        else:
            QMessageBox.critical(self, "Error", "Failed to add laboratory test.")

    def view_charges_ui(self):
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.close()
        except Exception as e:
            print(f"Staff Details Error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")