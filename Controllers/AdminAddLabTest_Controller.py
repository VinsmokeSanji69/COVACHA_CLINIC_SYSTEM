from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from Views.Admin_AddLabTest import Ui_MainWindow as AdminLabTestUI
from Models.LaboratoryTest import Laboratory


class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Add Laboratory")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want to add this laboratory test?")
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


class AdminAddLabTest(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Store reference to the parent (AdminChargesController)
        self.ui = AdminLabTestUI()
        self.ui.setupUi(self)
        self.ui.LabName.setFocus()

        # Set window properties
        self.setWindowTitle("Add Laboratory Test")
        self.setFixedSize(650, 450)

        print("AdminAddLabTest initialized successfully!")

        # Prefill the Lab ID
        self.prefilled_lab_id()

        # Connect buttons
        self.ui.AddLabTest.clicked.connect(self.validate_and_save_lab)
        if hasattr(self.ui, 'Cancel'):
            self.ui.Cancel.clicked.connect(self.close)

    def prefilled_lab_id(self):
        """Prefill the Lab ID field with the next available sequence."""
        next_lab_id = Laboratory.get_next_lab_id()
        self.ui.LabID.setText(next_lab_id)

    def validate_form(self):
        """Validate the form fields."""
        errors = []
        # Validate Lab Name
        lab_name = self.ui.LabName.text().strip()
        if not lab_name:
            errors.append("Laboratory Name is required.")
        elif Laboratory.lab_name_exists(lab_name.lower()):
            errors.append("Laboratory Name already exists.")

        # Validate Price
        price = self.ui.Price.text().strip()
        if not price:
            errors.append("Price is required.")
        elif not price.isdigit():
            errors.append("Price must be a number.")

        return errors

    def validate_and_save_lab(self):
        """Validate the form and save the lab test data."""
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Show confirmation dialog
        confirmation_dialog = ConfirmationDialog(self)
        if confirmation_dialog.exec_() == QDialog.Rejected:
            return

        # Collect data
        lab_data = {
            "lab_code": self.ui.LabID.text().strip(),
            "lab_name": self.ui.LabName.text().strip(),
            "price": float(self.ui.Price.text().strip()),
        }

        # Save data to the database
        success = Laboratory.save_lab_test(lab_data)
        if success:
            QMessageBox.information(self, "Success", "Laboratory test added successfully!")
            self.clear_form()
            self.prefilled_lab_id()  # Update Lab ID for the next entry

            # Notify the parent to refresh the table
            if self.parent:
                self.parent.refresh_tables()
        else:
            QMessageBox.critical(self, "Error", "Failed to add laboratory test.")

    def clear_form(self):
        """Clear the form fields."""
        self.ui.LabName.clear()
        self.ui.Price.clear()