from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Views.Admin_Patients import Ui_Admin_Patients


def safe_date_format(date_value, date_format="%B %d, %Y"):
    if not date_value:
        return "N/A"
    if isinstance(date_value, str):
        try:
            # Try parsing if it's a date string
            from datetime import datetime
            return datetime.strptime(date_value, "%Y-%m-%d").strftime(date_format)
        except ValueError:
            return date_value  # Return as-is if parsing fails
    elif hasattr(date_value, 'strftime'):  # If it's a date/datetime object
        return date_value.strftime(date_format)
    return "N/A"

class AdminPatientsController(QMainWindow):
    def __init__(self, records_ui):
        super().__init__()
        self.ui = Ui_Admin_Patients()
        self.records_ui = records_ui
        self.ui.setupUi(self)

        self.records_ui.View.clicked.connect(self.view_patient)
        self.records_ui.SearchIcon.clicked.connect(self.filter_tables)
        self.refresh_tables()


    def view_patient(self):
        try:
            selected_row = self.records_ui.PatientTable.currentRow()
            if selected_row == -1:
                print("no row selected")
                return

            patient_id = self.records_ui.PatientTable.item(selected_row, 0)
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
            search_query = self.records_ui.Search.text().strip().lower()
            patients = Patient.get_all_patients()

            # Handle empty database
            if not patients:
                self.records_ui.PatientTable.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No Records Found")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.records_ui.PatientTable.setItem(0, 0, no_data_item)
                self.records_ui.PatientTable.setSpan(0, 0, 1, 4)  # Span across all columns
                return

            filtered_patients = []
            for patient in patients:
                pat_id = patient['id']
                patient["recent_diagnosis"] = "No Diagnosis"
                patient["diagnosed_date"] = ""
                patient["status"] = "Pending"
                checkup = CheckUp.get_checkup_by_pat_id(pat_id)
                if checkup:
                    patient["recent_diagnosis"] = checkup[0]["diagnosis"] if checkup[0]["diagnosis"] else "N/A"
                    date = checkup[0]["date"] if checkup[0]["date"] else "N/A"
                    patient["diagnosed_date"] = safe_date_format(date)
                    patient["status"] = "Complete"

                if search_query in patient["name"].lower():
                    filtered_patients.append(patient)

            self.load_table(filtered_patients)

        except Exception as e:
            print(f"Error refreshing tables: {e}")

    def filter_tables(self):
        try:
            search_query = self.records_ui.Search.text().strip().lower()
            patients = Patient.get_all_patients()

            if not patients:
                self.records_ui.PatientTable.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No Records Found")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.records_ui.PatientTable.setItem(0, 0, no_data_item)
                self.records_ui.PatientTable.setSpan(0, 0, 1, 4)
                return

            filtered_patients = []
            for patient in patients:
                pat_id = patient['id']
                patient["recent_diagnosis"] = "No Diagnosis"
                patient["diagnosed_date"] = ""
                patient["status"] = "Pending"
                checkup = CheckUp.get_checkup_by_pat_id(pat_id)
                if checkup:
                    patient["recent_diagnosis"] = checkup[0]["diagnosis"] if checkup[0]["diagnosis"] else "N/A"
                    date = checkup[0]["date"] if checkup[0]["date"] else "N/A"
                    patient["diagnosed_date"] = safe_date_format(date)
                    patient["status"] = "Complete"

                if search_query in patient["name"].lower():
                    filtered_patients.append(patient)

            if not filtered_patients:
                self.records_ui.PatientTable.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No Matching Records Found")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.records_ui.PatientTable.setItem(0, 0, no_data_item)
                self.records_ui.PatientTable.setSpan(0, 0, 1, 4)
            else:
                self.load_table(filtered_patients)

        except Exception as e:
            print(f"Error filtering tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to filter tables: {e}")

    def display_no_records_message(self):
        self.records_ui.PatientTable.setRowCount(1)
        self.records_ui.PatientTable.setColumnCount(4)
        self.records_ui.PatientTable.setHorizontalHeaderLabels(["Patient ID", "Name", "Recent Diagnosis", "Date"])

        no_data_item = QtWidgets.QTableWidgetItem("No matching records found")
        no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
        no_data_item.setFlags(QtCore.Qt.NoItemFlags)  # Make it non-editable and non-selectable

        self.records_ui.PatientTable.setItem(0, 0, no_data_item)

        # Clear other columns to prevent leftover data
        for col in range(1, 4):
            self.records_ui.PatientTable.setItem(0, col, QtWidgets.QTableWidgetItem(""))

        self.records_ui.PatientTable.resizeColumnsToContents()
        self.records_ui.PatientTable.horizontalHeader().setStretchLastSection(True)

    def load_table(self, patients):
        try:
            self.records_ui.PatientTable.setRowCount(0)

            if not patients:
                self.display_no_records_message()
                return

            # Sort by diagnosed_date as string in descending order (YYYY-MM-DD format)
            patients.sort(key=lambda p: p.get("diagnosed_date", ""), reverse=True)

            self.records_ui.PatientTable.setColumnCount(4)
            self.records_ui.PatientTable.setHorizontalHeaderLabels(["Patient ID", "Name", "Recent Diagnosis", "Date"])
            self.records_ui.PatientTable.verticalHeader().setVisible(False)
            self.records_ui.PatientTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

            for row, patient in enumerate(patients):
                id = str(patient.get("id", ""))
                name = patient.get("name", "N/A")
                diagnosis = patient.get("recent_diagnosis", "No diagnosis")
                date = patient.get("diagnosed_date", "No date")

                self.records_ui.PatientTable.insertRow(row)
                self.records_ui.PatientTable.setItem(row, 0, QtWidgets.QTableWidgetItem(id))
                self.records_ui.PatientTable.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
                self.records_ui.PatientTable.setItem(row, 2, QtWidgets.QTableWidgetItem(diagnosis))
                self.records_ui.PatientTable.setItem(row, 3, QtWidgets.QTableWidgetItem(date))

            self.records_ui.PatientTable.horizontalHeader().setStretchLastSection(True)

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