import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from Views.Admin_AddLabTest import Ui_MainWindow as AdminLabTestUI
from Models.LaboratoryTest import Laboratory

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None, modify=False):
        super().__init__(parent)
        self.modify = modify
        self.setWindowTitle("Confirm Add Laboratory")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        msg = "update" if self.modify else "add"

        self.message_label = QLabel(f"Are you sure you want to {msg} this laboratory test?")
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
    def __init__(self, parent=None, lab_test=None, modify=False):
        super().__init__(parent)
        self.lab_test = lab_test
        self.modify_mode = modify
        self.ui = AdminLabTestUI()
        self.ui.setupUi(self)

        # Window properties
        self.setWindowTitle("Modify Laboratory Test" if modify else "Add Laboratory Test")
        self.setFixedSize(650, 450)

        # Initialize UI
        self.initialize_ui()

        # Connect signals
        self.ui.AddLabTest.clicked.connect(self.validate_and_save_lab)
        self.ui.Cancel.clicked.connect(self.close)

    def initialize_ui(self):
        """Initialize UI components"""
        if self.modify_mode and self.lab_test:
            # Populate fields for modification
            self.ui.LabID.setText(self.lab_test.get("lab_code", ""))
            self.ui.LabID.setReadOnly(True)
            self.ui.LabName.setText(self.lab_test.get("lab_test_name", ""))
            self.ui.Price.setText(str(self.lab_test.get("lab_price", "")))
            self.ui.AddLabTest.setText("Update Test")
        else:
            # New test - generate next ID
            self.prefill_lab_id()

    def prefill_lab_id(self):
        next_id = Laboratory.get_next_lab_id()
        if next_id:
            self.ui.LabID.setText(next_id)
        else:
            QMessageBox.warning(self, "Error", "Could not generate lab test ID")

    def validate_form(self):
        errors = []

        # Lab Name validation
        lab_name = self.ui.LabName.text().strip()
        if not lab_name:
            errors.append("Laboratory name is required")
        elif len(lab_name) > 100:
            errors.append("Laboratory name is too long (max 100 characters)")

        # Price validation
        price = self.ui.Price.text().strip()
        if not price:
            errors.append("Price is required")
        else:
            try:
                price_val = float(price)
                if price_val <= 0:
                    errors.append("Price must be greater than 0")
            except ValueError:
                errors.append("Price must be a valid number")

        # For new tests, check if name exists
        if not self.modify_mode and lab_name:
            if Laboratory.lab_name_exists(lab_name.lower()):
                errors.append("Laboratory name already exists")

        return errors

    def validate_and_save_lab(self):
        """Validate and save/update lab test"""
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Prepare data
        lab_data = {
            "lab_code": self.ui.LabID.text().strip(),
            "lab_test_name": self.ui.LabName.text().strip(),
            "lab_price": float(self.ui.Price.text().strip())
        }

        confirmation_dialog = ConfirmationDialog(self, self.modify_mode)
        result = confirmation_dialog.exec()

        if result == QDialog.Accepted:

            # Save or update based on mode
            if self.modify_mode:
                success = Laboratory.update_lab_test(lab_data)
            else:
                success = Laboratory.save_lab_test(lab_data)

            if success:
                msg = "updated" if self.modify_mode else "added"
                QMessageBox.information(self, "Success", f"Lab Test {msg} successfully!")
                self.clear_form()

                # Notify parent to refresh tables
                if self.parent and hasattr(self.parent, 'refresh_tables'):
                    self.parent.refresh_tables()
            else:
                QMessageBox.critical(self, "Error", "Failed to save data to the database.")
        else:  # User clicked "Cancel"
            msg = "update" if self.modify_mode else "creation"
            QMessageBox.information(self, "Cancelled", f"Lab Test {msg} cancelled.\n( Press any key to close )")

    def clear_form(self):
        """Clear form fields (for new entries)"""
        if not self.modify_mode:
            self.ui.LabName.clear()
            self.ui.Price.clear()
            self.prefill_lab_id()