from datetime import date
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialogButtonBox, QDialog

from Controllers.StaffTransactionList_Controllerr import StaffTransactionList
from Views.Staff_TransactionProcess import Ui_MainWindow
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

class StaffTransactionProcess(QtWidgets.QMainWindow):
    def __init__(self, chck_id=None):
        super().__init__()
        self.ui = Ui_MainWindow()  # Replace with your actual UI class
        self.ui.setupUi(self)

        # Store the chck_id
        self.chck_id = chck_id
        # print(f"Staff transaction initialized with chck_id: {self.chck_id}")

        # Apply table styles (if needed)
        self.apply_table_styles()

        # Load transaction details
        self.load_transaction_details()
        self.load_LabCharge_Table()
        self.calculate_total_lab_charge()
        self.calculate_subtotal()

        #save transaction
        self.ui.CompleteButton.clicked.connect(lambda: self.save_transaction_process(self.chck_id))

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

            # Log the fetched checkup data for debugging
            # print(f"Fetched checkup data: {checkup}")

            # Ensure 'chck_id' exists in the checkup dictionary
            if 'chck_id' not in checkup:
                raise KeyError(f"'chck_id' missing in checkup data: {checkup}")

            # Fetch patient details
            pat_id = checkup.get("pat_id")
            if not pat_id:
                raise ValueError("Missing 'pat_id' in checkup data.")
            patient = Patient.get_patient_details(pat_id)
            if not patient:
                raise ValueError(f"No patient found for pat_id={pat_id}")

            # Extract and format patient name
            full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"

            # Fetch doctor details
            doc_id = checkup.get("doc_id")
            if not doc_id:
                raise ValueError("Missing 'doc_id' in checkup data.")
            doctor = Doctor.get_doctor_by_id(doc_id)
            if not doctor:
                raise ValueError(f"No doctor found for doc_id={doc_id}")

            docFullname = f"{doctor['doc_lname'].capitalize()}, {doctor['doc_fname'].capitalize()}"

            # Populate the UI with transaction details
            self.ui.chck_ID.setText(str(checkup["chck_id"]))  # Ensure string conversion
            self.ui.PatID.setText(str(checkup["pat_id"]))  # Ensure string conversion
            self.ui.PatName.setText(full_name)
            self.ui.PatAge.setText(str(calculate_age(patient['pat_dob'])))  # Now returns a string
            self.ui.PatGender.setText(str(patient["pat_gender"]))  # Ensure string conversion
            self.ui.DocID.setText(str(checkup["doc_id"]))  # Ensure string conversion
            self.ui.DocName.setText(docFullname)
            self.ui.DocSpecialty.setText(str(doctor["doc_specialty"]))  # Ensure string conversion
            self.ui.DoctorCharge.setText("₱ " + str(doctor["doc_rate"]))  # Ensure string conversion

            self.ui.Diagnosis.setText(str(checkup.get("chck_diagnoses", "N/A")))  # Ensure string conversion
            self.ui.DiagnosisNotes.setText(str(checkup["chck_notes"]))  # Ensure string conversion

            # print(f"Transaction details loaded successfully for chck_id={self.chck_id}")
        except Exception as e:
            print(f"Error loading transaction details: {e}")
            # QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

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

            # print(f"Loading LabCharge Table for chck_id: {self.chck_id}")

            # Step 1: Fetch all lab codes associated with the chck_id
            lab_tests = CheckUp.get_test_names_by_chckid(self.chck_id)
            if not lab_tests:
                # print("No laboratory tests found for this check-up.")
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
                    # print(f"No details found for lab_code: {lab_code}")
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

            # print("LabCharge Table loaded successfully!")
        except Exception as e:
            # print(f"Error loading LabCharge Table: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load LabCharge Table: {e}")

    def calculate_total_lab_charge(self):
        """Calculate the total lab charge for the current check-up and display it in TotalLabCharge."""
        try:
            # Ensure that self.chck_id is set
            if not self.chck_id:
                raise ValueError("No check-up ID provided.")

            # print(f"Calculating total lab charge for chck_id: {self.chck_id}")

            # Step 1: Fetch all lab codes associated with the chck_id
            lab_tests = CheckUp.get_test_names_by_chckid(self.chck_id)
            if not lab_tests:
                # print("No laboratory tests found for this check-up.")
                self.ui.TotalLabCharge.setText("₱ 0.00")  # Set default value if no lab tests exist
                return

            # Step 2: Fetch lab prices for each lab code and calculate the total
            total_lab_charge = 0.0
            for lab_test in lab_tests:
                lab_code = lab_test['lab_code']

                # Fetch lab details (name and price) from the Laboratory model
                lab_details = Laboratory.get_test_by_labcode(lab_code)
                if not lab_details:
                    # print(f"No details found for lab_code: {lab_code}")
                    continue

                # Extract lab price
                lab_price = lab_details[1]['lab_price']  # Assuming lab_price is in the second dictionary
                if lab_price is not None:
                    total_lab_charge += float(lab_price)

            # Step 3: Format the total lab charge and display it in the QLineEdit
            formatted_total = f"₱ {total_lab_charge:,.2f}"  # Format as currency with two decimal places
            self.ui.TotalLabCharge.setText(formatted_total)
            # print(f"Total lab charge calculated successfully: {formatted_total}")

        except Exception as e:
            # print(f"Error calculating total lab charge: {e}")
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
            # print(f"Subtotal calculated successfully: {formatted_subtotal}")

        except ValueError as ve:
            # print(f"ValueError calculating subtotal: {ve}")
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid value in DoctorCharge or TotalLabCharge.")
        except Exception as e:
            # print(f"Error calculating subtotal: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to calculate subtotal: {e}")

    def save_transaction_process(self, chck_id):
        """Save the transaction after confirming with the user."""
        try:
            # Prepare the transaction data
            trans_data = {
                "discount": 0,  # Store discount as an integer (default is 0)
                "base_charge": int(float(self.ui.DoctorCharge.text().replace("₱", "").replace(",", "").strip())),
                "lab_charge": int(float(self.ui.TotalLabCharge.text().replace("₱", "").replace(",", "").strip())),
            }

            # Show confirmation dialog
            confirmation_dialog = ConfirmationDialog(self)
            if confirmation_dialog.exec_() == QtWidgets.QDialog.Rejected:
                # print("Transaction confirmation cancelled by the user.")
                return

            # Save the transaction
            Transaction.add_transaction(chck_id, trans_data)

            # Optionally, close the modal or refresh the UI after saving
            # print("Transaction saved successfully!")
            QtWidgets.QMessageBox.information(self, "Success", "Transaction has been confirmed and saved successfully!")

            # Open the StaffTransactionList window
            self.staff_transaction_list_window = StaffTransactionList()
            self.staff_transaction_list_window.show()

            # Close the current modal
            self.close()

        except ValueError as ve:
            # print(f"ValueError while preparing transaction data: {ve}")
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid value in DoctorCharge or TotalLabCharge.")
        except Exception as e:
            # print(f"Error saving transaction: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save transaction: {e}")