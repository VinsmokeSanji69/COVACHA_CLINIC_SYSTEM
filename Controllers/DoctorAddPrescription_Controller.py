from PyQt5.QtWidgets import QMainWindow, QDialogButtonBox, QVBoxLayout, QLabel, QDialog, QMessageBox
from Models.Prescription import Prescription
from Views.Doctor_AddPrescription import Ui_MainWindow as DoctorAddPrescriptionUI

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Medication")
        self.setFixedSize(400, 150)
        layout = QVBoxLayout()
        self.message_label = QLabel("Are you sure you want to proceed?")
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
    def __init__(self, chck_id=None, parent=None, refresh_callback=None, prescription_data=None):
        super().__init__(parent)
        self.parent = parent
        self.chck_id = chck_id
        self.refresh_callback = refresh_callback
        self.prescription_data = prescription_data
        self.ui = DoctorAddPrescriptionUI()
        self.ui.setupUi(self)
        self.ui.MedName.setFocus()
        # Set window properties
        self.setWindowTitle("Add/Update Medication")
        # Connect buttons
        self.ui.Cancel.clicked.connect(self.close)
        self.ui.Addprescription.clicked.connect(self.validate_and_save_or_update)
        if self.prescription_data:
            self.populate_form()
            self.ui.Addprescription.setText("Update")

    def validate_form(self):
        """Validate the form fields."""
        errors = []
        med_name = self.ui.MedName.text().strip()
        if not med_name:
            errors.append("Medication Name is required.")
        return errors

    def populate_form(self):
        """Populate form fields with existing prescription data."""
        if not self.prescription_data:
            return
        self.ui.MedName.setText(self.prescription_data.get("pres_medicine", ""))
        self.ui.Dosage.setText(self.prescription_data.get("pres_dosage", ""))
        self.ui.Intake.setText(self.prescription_data.get("pres_intake", ""))
        self.ui.Tablets.setText(self.prescription_data.get("pres_tablets",""))

    def validate_and_save_or_update(self):
        """Validate and either save or update the prescription."""
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        confirmation_dialog = ConfirmationDialog(self)
        if confirmation_dialog.exec_() == QDialog.Rejected:
            return

        med_data = {
            "med_name": self.ui.MedName.text().strip(),
            "dosage": self.ui.Dosage.text().strip() or None,
            "intake": self.ui.Intake.text().strip() or None,
            "tablets": self.ui.Tablets.text().strip() or None
        }

        if self.prescription_data:
            # Edit mode: update existing prescription
            pres_id = self.prescription_data.get("pres_id")
            success = Prescription.update_prescription_by_id(
                pres_id,
                med_data["med_name"],
                med_data["dosage"],
                med_data["intake"],
                med_data["tablets"]
            )
            action = "updated"
        else:
            # Add mode: insert new prescription
            success = Prescription.add_presscription(self.chck_id, med_data)
            action = "added"

        if success:
            QMessageBox.information(self, "Success", f"Medication {action} successfully!")
            self.clear_form()

            # Notify the parent to refresh the table using the callback
            if self.refresh_callback:
                self.refresh_callback()
            self.close()
        else:
            QMessageBox.critical(self, "Error", f"Failed to {action} medication.")

    def clear_form(self):
        """Clear all input fields in the form."""
        self.ui.MedName.clear()
        self.ui.Dosage.clear()
        self.ui.Intake.clear()