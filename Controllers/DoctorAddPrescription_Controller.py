from PyQt5.QtWidgets import QMainWindow, QDialogButtonBox, QVBoxLayout, QLabel, QDialog, QMessageBox
from Models.Prescription import Prescription
from Views.Doctor_AddPrescription import Ui_MainWindow as DoctorAddPrescriptionUI

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Add Medication")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()
        self.message_label = QLabel("Are you sure you want to add this medication?")
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

class DoctorAddPrescription(QMainWindow):
    def __init__(self, chck_id=None, parent=None, refresh_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.chck_id = chck_id
        self.refresh_callback = refresh_callback  # Store the refresh callback
        self.ui = DoctorAddPrescriptionUI()
        self.ui.setupUi(self)
        self.ui.MedName.setFocus()

        # Set window properties
        self.setWindowTitle("Add Laboratory Test")
        self.setFixedSize(650, 450)

        print("Doctor AddPrescription initialized successfully!")

        # Connect buttons
        self.ui.Cancel.clicked.connect(self.close)
        self.ui.Addprescription.clicked.connect(self.validate_and_save_lab)

    def validate_form(self):
        """Validate the form fields."""
        errors = []
        med_name = self.ui.MedName.text().strip()
        if not med_name:
            errors.append("Medication Name is required.")

        dosage = self.ui.Dosage.text().strip()
        if not dosage:
            errors.append("Dosage is required.")

        intake = self.ui.Intake.text().strip()
        if not intake:
            errors.append("Intake is required.")

        print(f"Validation Errors: {errors}")
        return errors

    def validate_and_save_lab(self):
        """Validate the form and save the lab test data."""
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        confirmation_dialog = ConfirmationDialog(self)
        if confirmation_dialog.exec_() == QDialog.Rejected:
            return

        med_data = {
            "med_name": self.ui.MedName.text().strip(),
            "dosage": self.ui.Dosage.text().strip(),
            "intake": self.ui.Intake.text().strip()
        }

        success = Prescription.add_presscription(self.chck_id, med_data)
        if success:
            QMessageBox.information(self, "Success", "Medication added successfully!")
            self.clear_form()

            # Notify the parent to refresh the table using the callback
            if self.refresh_callback:
                self.refresh_callback()
        else:
            QMessageBox.critical(self, "Error", "Failed to add medication.")

    def clear_form(self):
        """Clear all input fields in the form."""
        self.ui.MedName.clear()
        self.ui.Dosage.clear()
        self.ui.Intake.clear()