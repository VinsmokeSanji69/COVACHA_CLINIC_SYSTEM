from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from PyQt5.uic.Compiler.qtproxies import QtCore
from Models import LaboratoryTest
from Models.Doctor import Doctor
from Views.Admin_Charges import Ui_MainWindow  as AdminChargesUI
from Controllers.AdminAddLabTest_Controller import AdminAddLabTest
from Controllers.AdminAddDoctorCharges_Controller import AdminDoctorCharges
from Models.LaboratoryTest import Laboratory

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Add Laboratory")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want delete the lab test?")
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

class AdminChargesController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AdminChargesUI()
        self.ui.setupUi(self)

        print("Admin Charges UI initialized!")

        # Apply styles to the tables
        self.apply_table_styles()
        self.refresh_tables()

        #NavBar Buttons
        self.ui.DashboardButton.clicked.connect(self.view_dashboard_ui)
        self.ui.StaffsButton.clicked.connect(self.view_staff_ui)
        self.ui.TransactionsButton.clicked.connect(self.view_transaction_ui)
        self.ui.PatientsButton.clicked.connect(self.view_patient_ui)

        #Table Buttons
        self.ui.Modify.clicked.connect(self.modify_charges)
        self.ui.Delete.clicked.connect(self.delete_lab_test)
        self.ui.AddLabTestButton.clicked.connect(self.open_add_user_form)

    def delete_lab_test(self):
        try:
            print("Modify button clicked!")
            selected_row = -1
            row_id = None

            if self.ui.LaboratoryTestTable.currentRow() != -1:
                selected_row = self.ui.LaboratoryTestTable.currentRow()
                row_id = self.ui.LaboratoryTestTable.item(selected_row, 0).text()

            if selected_row == -1:
                raise ValueError("No row selected in either table")
            if not row_id:
                raise ValueError("Could not determine row ID")
            confirmation_dialog = ConfirmationDialog(self)
            if confirmation_dialog.exec_() == QDialog.Rejected:
                return

            success = Laboratory.delete(row_id)
            if success:
                QMessageBox.information(self, "Success", "Lab Test deleted successfully!")
                self.view_charges_ui()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete laboratory test.")

        except Exception as e:
            error_msg = f"Failed to delete charge: {str(e)}"

    def modify_charges(self):
        try:
            print("Modify button clicked!")
            # Determine which table has the current selection
            current_table = None
            selected_row = -1
            row_id = None

            if self.ui.DoctorTable.currentRow() != -1:
                current_table = "DoctorTable"
                selected_row = self.ui.DoctorTable.currentRow()
                doc_name = self.ui.DoctorTable.item(selected_row, 0).text()
                row_id = self.find_doc_id(doc_name)

            elif self.ui.LaboratoryTestTable.currentRow() != -1:
                current_table = "LaboratoryTestTable"
                selected_row = self.ui.LaboratoryTestTable.currentRow()
                row_id = self.ui.LaboratoryTestTable.item(selected_row, 0).text()

            # Check if a valid selection exists
            if selected_row == -1:
                raise ValueError("No row selected in either table")
            if not row_id:
                raise ValueError("Could not determine row ID")

            # Get the data from the appropriate table
            if current_table == "DoctorTable":
                self.open_add_charges_form(row_id)
            elif current_table == "LaboratoryTestTable":
                self.modify_charges_form(row_id)

        except ValueError as ve:
            error_msg = f"Selection Error: {str(ve)}"
        except Exception as e:
            error_msg = f"Failed to modify charges: {str(e)}"

    @staticmethod
    def find_doc_id(doc_name):
        if not doc_name or not isinstance(doc_name, str):
            print("Invalid doctor name provided")
            return None

        try:
            doctors = Doctor.get_all_doctors()
            doc_name_clean = doc_name.strip().lower()

            for doctor in doctors:
                # Case-insensitive comparison with stripped whitespace
                current_name = str(doctor.get("name", "")).strip().lower()
                if doc_name_clean == current_name:
                    doc_id = doctor.get("id")
                    if doc_id is not None:
                        return int(doc_id)  # Ensure ID is returned as integer
                    break

            print(f"No doctor found with name: {doc_name}")
            return None

        except Exception as e:
            print(f"Error finding doctor ID: {e}")
            return None

    def refresh_tables(self):
        self.populate_laboratory_test_table()
        self.load_doctor_table()

    def populate_laboratory_test_table(self):
        try:
            tests = Laboratory.get_all_test()
            self.ui.LaboratoryTestTable.setRowCount(0)

            for row, test in enumerate(tests):
                lab_code = test["lab_code"]
                lab_test_name = test["lab_test_name"]
                lab_price = test["lab_price"]

                self.ui.LaboratoryTestTable.insertRow(row)
                self.ui.LaboratoryTestTable.setItem(row, 0, QtWidgets.QTableWidgetItem(lab_code))
                self.ui.LaboratoryTestTable.setItem(row, 1, QtWidgets.QTableWidgetItem(lab_test_name))
                self.ui.LaboratoryTestTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(lab_price)))

            self.ui.LaboratoryTestTable.resizeColumnsToContents()
            self.ui.LaboratoryTestTable.viewport().update()

        except Exception as e:
            print(f"Error populating LaboratoryTestTable: {e}")

    def load_doctor_table(self):
        doctors = Doctor.get_all_doctors()
        self.ui.DoctorTable.setRowCount(0)

        # Populate the table
        for row, doctor in enumerate(doctors):
            self.ui.DoctorTable.insertRow(row)
            formatted_rate = f"{float(doctor['rate']):,.2f}" if doctor["rate"] is not None else "0.00"
            self.ui.DoctorTable.setItem(row, 0, QTableWidgetItem(str(doctor["name"])))
            self.ui.DoctorTable.setItem(row, 1, QTableWidgetItem(formatted_rate))

        self.ui.DoctorTable.resizeColumnsToContents()

    def apply_table_styles(self):
        # Configure Laboratory Test Table
        self.ui.LaboratoryTestTable.setHorizontalHeaderLabels(["Test Code", "Laboratory Test", "Charge"])
        self.ui.LaboratoryTestTable.verticalHeader().setVisible(False)
        self.ui.LaboratoryTestTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Configure Doctor Table (add your specific headers)
        self.ui.DoctorTable.setHorizontalHeaderLabels(["Doctor Name", "Rate"])  # Update with your actual headers
        self.ui.DoctorTable.verticalHeader().setVisible(False)
        self.ui.DoctorTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Optional: Set column width policies
        for table in [self.ui.LaboratoryTestTable, self.ui.DoctorTable]:
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            table.horizontalHeader().setStretchLastSection(True)

        # Connect signals to enforce single-table selection
        self.ui.LaboratoryTestTable.itemSelectionChanged.connect(lambda: self.clear_other_table_selection(self.ui.DoctorTable))
        self.ui.DoctorTable.itemSelectionChanged.connect(lambda: self.clear_other_table_selection(self.ui.LaboratoryTestTable))

    def clear_other_table_selection(self, table):
        if self.sender().selectedItems():  # If current table has a selection
            table.clearSelection()  # Clear the other table

    def modify_charges_form(self, lab_id):
        try:
            lab_test_details = Laboratory.get_lab_test(lab_id)

            lab_test_details = Laboratory.get_lab_test(lab_id)
            self.add_user_window = AdminAddLabTest(parent=self, lab_test=lab_test_details, modify=True)
            self.add_user_window.show()
            print("Add Test Form shown successfully!")
        except Exception as e:
            print(f"Error opening Add Test Form: {e}")


    def open_add_user_form(self):
        try:
            self.add_lab_test_window = AdminAddLabTest(parent=self)
            self.add_lab_test_window.show()
        except Exception as e:
            print(f"Error opening Add Test Form: {e}")

    def open_add_charges_form(self, doc_id):
        print("Opening Add Charges Form...")
        try:
            self.add_user_window = AdminDoctorCharges(doc_id, parent=self)
            self.add_user_window.show()
            print("Modify Doctor Charges shown successfully!")
        except Exception as e:
            print(f"Error opening Add Charges Form: {e}")

    def view_staff_ui(self):
        print("StaffButton clicked!")
        try:
            from Controllers.AdminStaffs_Controller import AdminStaffsController
            self.admin_staff_controller = AdminStaffsController()
            self.admin_staff_controller.show()
            self.hide()
        except Exception as e:
            print(f"Dashboard Error(staffs): {e}")

    def view_transaction_ui(self):
        print("TransactionButton clicked!")
        try:
            from Controllers.AdminTransaction_Controller import AdminTransactionsController
            self.admin_transaction_controller = AdminTransactionsController()
            self.admin_transaction_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error(charges): {e}")

    def view_dashboard_ui(self):
        print("DashboardButton clicked!")
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")

    def view_patient_ui(self):
        print("RecordButton clicked!")
        try:
            from Controllers.AdminPatients_Controller import AdminPatientsController
            self.admin_patients_controller = AdminPatientsController()
            self.admin_patients_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")
