from datetime import date
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialogButtonBox, QDialog
from Views.Staff_TransactionProcess import Ui_Staff_Transaction_Process
from Models.CheckUp import CheckUp
from Models.Doctor import Doctor, calculate_age
from Models.Patient import Patient
from Models.LaboratoryTest import Laboratory
from Models.Transaction import Transaction


class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Transaction")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want to Confirm Transaction ?")
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


class StaffTransactionProcess(QtWidgets.QDialog):
    def __init__(self, chck_id=None):
        super().__init__()
        self.ui = Ui_Staff_Transaction_Process()
        self.ui.setupUi(self)

        # Store the chck_id
        self.chck_id = chck_id
        self.existing_transaction = None  # Store existing transaction data

        # Apply table styles (if needed)
        self.apply_table_styles()

        # Load transaction details
        self.load_transaction_details()
        self.load_LabCharge_Table()
        self.calculate_total_lab_charge()
        self.calculate_subtotal()

        # save transaction
        self.ui.CompleteButton.clicked.connect(lambda: self.save_transaction_process(self.chck_id))
        self.ui.PartialButton.clicked.connect(lambda: self.save_partial_transaction_process(self.chck_id))
        self.ui.SeniorCheckBox.stateChanged.connect(self.apply_discount_if_senior)

    def save_partial_transaction_process(self, chck_id):
        """Save the transaction as Partial after confirming with the user."""
        try:
            # Parse discount and total
            discount = float(self.ui.DiscountedAmount.text().replace("₱", "").replace(",", "").strip() or 0)
            total_amount = float(self.ui.TotalAmount.text().replace("₱", "").replace(",", "").strip() or 0)

            # Prepare the transaction data
            trans_data = {
                "discount": int(discount),
                "base_charge": int(float(self.ui.DoctorCharge.text().replace("₱", "").replace(",", "").strip())),
                "lab_charge": int(float(self.ui.TotalLabCharge.text().replace("₱", "").replace(",", "").strip())),
                "total": int(total_amount),
                "status": "Partial"
            }

            # Show confirmation dialog
            confirmation_dialog = ConfirmationDialog(self)
            if confirmation_dialog.exec_() == QtWidgets.QDialog.Rejected:
                return

            # Save the transaction with status Partial
            Transaction.add_transaction(chck_id, trans_data)

            QtWidgets.QMessageBox.information(self, "Saved", "Transaction has been saved as Partial.")

            self.close()

        except ValueError as ve:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid value in DoctorCharge or TotalLabCharge.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save transaction: {e}")

    def apply_discount_if_senior(self):
        try:
            # Get subtotal
            subtotal_text = self.ui.SubtotalAmount.text().replace("₱", "").replace(",", "").strip()
            if not subtotal_text:
                subtotal = 0.0
            else:
                subtotal = float(subtotal_text)

            # Apply 20% discount if checkbox is checked
            discount = 0.0
            if self.ui.SeniorCheckBox.isChecked():
                discount = subtotal * 0.20

            # Calculate total after discount
            total = subtotal - discount

            # Update UI
            self.ui.DiscountedAmount.setText(f"₱ {discount:,.2f}")
            self.ui.TotalAmount.setText(f"₱ {total:,.2f}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to apply discount: {e}")

    def apply_table_styles(self):
        """Apply custom styles to the tables."""
        self.ui.LabChargeTable.setStyleSheet("""
            QTableWidget {
                background-color: #F4F7ED;
                gridline-color: transparent;
                border-radius: 10px;
            }
            QTableWidget::item {
                border: none;
                font: 16pt "Lexend";
            }
            QTableWidget::item:selected {
                background-color: rgba(46, 110, 101, 0.3);
            }
            QTableWidget QHeaderView::section {
                background-color: #2E6E65;
                color: white;
                padding: 5px;
                font: 18px "Lexend Medium";
                border: 2px solid #2E6E65;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
        """)
        self.ui.LabChargeTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.LabChargeTable.horizontalHeader().setVisible(True)
        self.ui.LabChargeTable.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.ui.LabChargeTable.verticalHeader().setVisible(False)

    def load_transaction_details(self):
        try:
            if not self.chck_id:
                raise ValueError("No check-up ID provided.")

            # Fetch check-up details from the database
            checkup = CheckUp.get_checkup_details(self.chck_id)
            if not checkup:
                raise ValueError(f"No check-up found for chck_id={self.chck_id}")

            print(f"Fetched checkup data: {checkup}")

            if 'chck_id' not in checkup:
                raise KeyError(f"'chck_id' missing in checkup data: {checkup}")

            # Fetch patient details
            pat_id = checkup.get("pat_id")
            if not pat_id:
                raise ValueError("Missing 'pat_id' in checkup data.")
            patient = Patient.get_patient_details(pat_id)
            if not patient:
                raise ValueError(f"No patient found for pat_id={pat_id}")

            full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"

            # Fetch doctor details
            doc_id = checkup.get("doc_id")
            if not doc_id:
                raise ValueError("Missing 'doc_id' in checkup data.")
            doctor = Doctor.get_doctor_by_id(doc_id)
            if not doctor:
                raise ValueError(f"No doctor found for doc_id={doc_id}")

            docFullname = f"{doctor['doc_lname'].capitalize()}, {doctor['doc_fname'].capitalize()}"

            # Populate UI fields
            self.ui.chck_ID.setText(str(checkup["chck_id"]))
            self.ui.PatID.setText(str(checkup["pat_id"]))
            self.ui.PatName.setText(full_name)
            self.ui.PatAge.setText(str(calculate_age(patient['pat_dob'])))
            self.ui.PatGender.setText(str(patient["pat_gender"]))
            self.ui.DocID.setText(str(checkup["doc_id"]))
            self.ui.DocName.setText(docFullname)
            self.ui.DoctorCharge.setText("₱ " + str(doctor["doc_rate"]))
            self.ui.Diagnosis.setText(str(checkup.get("chck_diagnoses", "N/A")))
            self.ui.DiagnosisNotes.setText(str(checkup["chck_notes"]))

            # ✅ Check transaction
            transaction = Transaction.get_transaction_by_chckid(self.chck_id)

            if transaction:
                # Store existing transaction data
                self.existing_transaction = transaction

                # Transaction exists - check status
                current_status = transaction.get("tran_status", "").strip()

                if current_status.lower() == "completed":
                    # Transaction is already completed - disable both buttons
                    self.ui.PartialButton.setVisible(False)
                    self.ui.CompleteButton.setEnabled(False)
                    self.ui.CompleteButton.setText("Already Completed")
                else:
                    # Transaction exists but not completed (partial) - allow completion
                    self.ui.PartialButton.setVisible(False)  # Hide partial button
                    self.ui.CompleteButton.setEnabled(True)
                    self.ui.CompleteButton.setText("Complete Transaction")

                # Set discount checkbox based on existing transaction
                discount = transaction.get("tran_discount", 0.0)
                if discount > 0:
                    self.ui.SeniorCheckBox.setChecked(True)
                    self.ui.SeniorCheckBox.setEnabled(False)  # Make read-only
                else:
                    self.ui.SeniorCheckBox.setChecked(False)
                    self.ui.SeniorCheckBox.setEnabled(True)
            else:
                # No transaction exists - show both buttons
                self.existing_transaction = None
                self.ui.PartialButton.setVisible(True)
                self.ui.CompleteButton.setEnabled(True)
                self.ui.CompleteButton.setText("Complete Transaction")
                self.ui.SeniorCheckBox.setEnabled(True)
                self.ui.SeniorCheckBox.setChecked(False)

        except Exception as e:
            print(f"Error loading transaction details: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

    def calculate_age(dob):
        if not dob:
            return None
        today = date.today()
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1
        return age

    def load_LabCharge_Table(self):
        """Display the lab name and charge based on the chck_id."""
        try:
            # Ensure that self.chck_id is set
            if not self.chck_id:
                raise ValueError("No check-up ID provided.")

            # Step 1: Fetch all lab codes associated with the chck_id
            lab_tests = CheckUp.get_test_names_by_chckid(self.chck_id)
            if not lab_tests:
                return

            # Clear the table before populating it
            self.ui.LabChargeTable.clearContents()
            self.ui.LabChargeTable.setRowCount(0)

            # Step 2: Fetch lab name and price for each lab code
            for row, lab_test in enumerate(lab_tests):
                lab_code = lab_test['lab_code']
                lab_attachment = lab_test['lab_attachment']  # Optional: Handle attachments if needed

                # Fetch lab details (name and price) from the Laboratory model
                lab_details = Laboratory.get_test_by_labcode(lab_code)
                if not lab_details:
                    continue

                # Extract lab name and price
                lab_name = lab_details[0]['lab_test_name']
                lab_price = lab_details[1]['lab_price']

                # Insert data into the table
                self.ui.LabChargeTable.insertRow(row)
                self.ui.LabChargeTable.setItem(row, 0, QtWidgets.QTableWidgetItem(lab_name))  # Lab Name
                self.ui.LabChargeTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(lab_price)))  # Lab Price

            # Resize columns to fit content
            self.ui.LabChargeTable.resizeColumnsToContents()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load LabCharge Table: {e}")

    def calculate_total_lab_charge(self):
        """Calculate the total lab charge for the current check-up and display it in TotalLabCharge."""
        try:
            # Ensure that self.chck_id is set
            if not self.chck_id:
                raise ValueError("No check-up ID provided.")

            # Step 1: Fetch all lab codes associated with the chck_id
            lab_tests = CheckUp.get_test_names_by_chckid(self.chck_id)
            if not lab_tests:
                self.ui.TotalLabCharge.setText("₱ 0.00")  # Set default value if no lab tests exist
                return

            # Step 2: Fetch lab prices for each lab code and calculate the total
            total_lab_charge = 0.0
            for lab_test in lab_tests:
                lab_code = lab_test['lab_code']

                # Fetch lab details (name and price) from the Laboratory model
                lab_details = Laboratory.get_test_by_labcode(lab_code)
                if not lab_details:
                    continue

                # Extract lab price
                lab_price = lab_details[1]['lab_price']  # Assuming lab_price is in the second dictionary
                if lab_price is not None:
                    total_lab_charge += float(lab_price)

            # Step 3: Format the total lab charge and display it in the QLineEdit
            formatted_total = f"₱ {total_lab_charge:,.2f}"  # Format as currency with two decimal places
            self.ui.TotalLabCharge.setText(formatted_total)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to calculate total lab charge: {e}")

    def calculate_subtotal(self):
        """Calculate the subtotal by adding DoctorCharge and TotalLabCharge."""
        try:
            # Retrieve the DoctorCharge value
            doctor_charge_text = self.ui.DoctorCharge.text().strip()
            if not doctor_charge_text or doctor_charge_text == "₱ 0.00":
                doctor_charge = 0.0
            else:
                # Remove the currency symbol and commas, then convert to float
                doctor_charge = float(doctor_charge_text.replace("₱", "").replace(",", "").strip())

            # Retrieve the TotalLabCharge value
            total_lab_charge_text = self.ui.TotalLabCharge.text().strip()
            if not total_lab_charge_text or total_lab_charge_text == "₱ 0.00":
                total_lab_charge = 0.0
            else:
                # Remove the currency symbol and commas, then convert to float
                total_lab_charge = float(total_lab_charge_text.replace("₱", "").replace(",", "").strip())

            # Calculate the subtotal
            subtotal = doctor_charge + total_lab_charge

            # Format the subtotal as currency and display it in the SubtotalAmount QLineEdit
            formatted_subtotal = f"₱ {subtotal:,.2f}"
            self.ui.SubtotalAmount.setText(formatted_subtotal)
            self.ui.TotalAmount.setText(formatted_subtotal)
            self.apply_discount_if_senior()

        except ValueError as ve:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid value in DoctorCharge or TotalLabCharge.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to calculate subtotal: {e}")

    def save_transaction_process(self, chck_id):
        """Save the transaction as Completed after confirming with the user."""
        try:
            # Parse discount and total
            discount = float(self.ui.DiscountedAmount.text().replace("₱", "").replace(",", "").strip() or 0)
            total_amount = float(self.ui.TotalAmount.text().replace("₱", "").replace(",", "").strip() or 0)

            # Prepare the transaction data
            trans_data = {
                "discount": int(discount),
                "base_charge": int(float(self.ui.DoctorCharge.text().replace("₱", "").replace(",", "").strip())),
                "lab_charge": int(float(self.ui.TotalLabCharge.text().replace("₱", "").replace(",", "").strip())),
                "total": int(total_amount),
                "status": "Completed"
            }

            # Show confirmation dialog
            confirmation_dialog = ConfirmationDialog(self)
            if confirmation_dialog.exec_() == QtWidgets.QDialog.Rejected:
                return

            # Check if we're updating an existing transaction or creating a new one
            if self.existing_transaction:
                # Update existing transaction to "Completed"
                Transaction.update_transaction_status(chck_id, trans_data)
                QtWidgets.QMessageBox.information(self, "Success", "Transaction updated to Completed successfully!")
            else:
                # Create new transaction with "Completed" status
                Transaction.add_transaction(chck_id, trans_data)
                QtWidgets.QMessageBox.information(self, "Success", "Transaction completed and saved successfully!")

            # Redirect to Transactions page in StaffDashboard
            if self.parent() and hasattr(self.parent(), 'go_to_transactions'):
                self.parent().go_to_transactions()
                self.parent().staff_transactions.load_transaction_details()

            # Close this modal
            self.accept()  # Use accept() for QDialog

        except ValueError as ve:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid value in DoctorCharge or TotalLabCharge.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save transaction: {e}")