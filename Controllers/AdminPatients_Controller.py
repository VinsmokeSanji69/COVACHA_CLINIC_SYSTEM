from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Views.Admin_Patients import Ui_MainWindow as AdminPatientsUI

class AdminPatientsController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AdminPatientsUI()
        self.ui.setupUi(self)

        print("Admin Patients UI initialized!")

        self.ui.DashboardButton.clicked.connect(self.view_dashboard_ui)
        self.ui.ChargesButton.clicked.connect(self.view_charges_ui)
        self.ui.TransactionsButton.clicked.connect(self.view_transaction_ui)
        self.ui.StaffsButton.clicked.connect(self.view_staff_ui)

        self.ui.View.clicked.connect(self.view_patient)
        self.refresh_tables()



    def view_patient(self):
        try:
            selected_row = self.ui.PatientTable.currentRow()
            if selected_row == -1:
                print("no row selected")
                return

            patient_id = self.ui.PatientTable.item(selected_row, 0)
            if not patient_id:
                raise ValueError(f"No patient ID found in selected row")

            patient_id = patient_id.text().strip()
            if not patient_id:
                raise ValueError(f" ID is empty")

            self.view_patient_details_ui(int(patient_id))

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Failed to select patient: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(error_msg)


    def refresh_tables(self):
        try:
            self.load_table()
        except Exception as e:
            print(f"Error refreshing tables: {e}")

    def load_table(self):
        try:
            patients = Patient.get_all_patients()
            self.ui.PatientTable.setRowCount(len(patients))

            # Configure table properties first
            self.ui.PatientTable.verticalHeader().setVisible(False)
            self.ui.PatientTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Moved up
            self.ui.PatientTable.setHorizontalHeaderLabels(["Patient ID", "Name", "Recent Diagnosis", "Date"])

            # Populate the table
            for row, patient in enumerate(patients):
                id = str(patient.get("id", ""))
                name = patient.get("name", "N/A")

                # Get checkup data with proper defaults
                diagnosis = "No diagnosis"
                date = "No records"

                patient_checkups = CheckUp.get_checkup_by_pat_id(patient["id"])
                if patient_checkups and len(patient_checkups) > 0:
                    diagnosis = patient_checkups[0].get("diagnosis", "No diagnosis")
                    date = patient_checkups[0].get("date", "No date").strftime('%Y-%m-%d') if patient_checkups[0].get(
                        "date") else "No date"

                # Insert row items
                self.ui.PatientTable.insertRow(row)
                self.ui.PatientTable.setItem(row, 0, QtWidgets.QTableWidgetItem(id))
                self.ui.PatientTable.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
                self.ui.PatientTable.setItem(row, 2, QtWidgets.QTableWidgetItem(diagnosis))
                self.ui.PatientTable.setItem(row, 3, QtWidgets.QTableWidgetItem(date))  # Fixed column index

            # Adjust table appearance
            self.ui.PatientTable.resizeColumnsToContents()
            self.ui.PatientTable.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            print(f"Error populating Patient Table: {e}")


    def view_patient_details_ui(self, patient_id):
        print("View Patient Button clicked!")
        try:
            from Controllers.AdminPatientDetails_Controller import AdminPatientDetailsController
            self.admin_patient_details_controller = AdminPatientDetailsController(patient_id)
            self.admin_patient_details_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")

    def view_dashboard_ui(self):
        print("DashboardButton clicked!")
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")

    def view_staff_ui(self):
        print("StaffButton clicked!")
        try:
            from Controllers.AdminStaffs_Controller import AdminStaffsController
            self.admin_staff_controller = AdminStaffsController()
            self.admin_staff_controller.show()
            self.hide()
        except Exception as e:
            print(f"Dashboard Error(staffs): {e}")

    def view_charges_ui(self):
        print("ChargesButton clicked!")
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error(charges): {e}")

    def view_transaction_ui(self):
        print("TransactionButton clicked!")
        try:
            from Controllers.AdminTransaction_Controller import AdminTransactionsController
            self.admin_transaction_controller = AdminTransactionsController()
            self.admin_transaction_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error(charges): {e}")