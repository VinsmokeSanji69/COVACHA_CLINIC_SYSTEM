from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Views.Admin_Patients import Ui_Admin_Patients


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
                return

            patient_id = self.records_ui.PatientTable.item(selected_row, 0)
            if not patient_id:
                raise ValueError(f"No patient ID found in selected row")

            patient_id = patient_id.text().strip()
            if not patient_id:
                raise ValueError(f"ID is empty")

            self.view_patient_details_ui(int(patient_id))

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Failed to select patient: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)

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
                self.records_ui.PatientTable.setSpan(0, 0, 1, 3)  # Span across all columns
                return

            filtered_patients = []
            for patient in patients:
                pat_id = patient['id']
                patient["status"] = "Pending"

                # Only check for status, don't fetch diagnosis or date
                checkup = CheckUp.get_checkup_by_pat_id(pat_id)
                if checkup:
                    patient["status"] = "Complete"

                if search_query in patient["name"].lower():
                    filtered_patients.append(patient)

            self.load_table(filtered_patients)
        except Exception as e:
            pass

    def filter_tables(self):
        try:
            search_query = self.records_ui.Search.text().strip().lower()
            patients = Patient.get_all_patients()

            if not patients:
                self.records_ui.PatientTable.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No Records Found")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.records_ui.PatientTable.setItem(0, 0, no_data_item)
                self.records_ui.PatientTable.setSpan(0, 0, 1, 3)
                return

            filtered_patients = []
            for patient in patients:
                pat_id = patient['id']
                patient["status"] = "Pending"
                checkup = CheckUp.get_checkup_by_pat_id(pat_id)
                if checkup:
                    patient["status"] = "Complete"

                if search_query in patient["name"].lower():
                    filtered_patients.append(patient)

            if not filtered_patients:
                self.records_ui.PatientTable.setRowCount(1)
                no_data_item = QtWidgets.QTableWidgetItem("No Matching Records Found")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.records_ui.PatientTable.setItem(0, 0, no_data_item)
                self.records_ui.PatientTable.setSpan(0, 0, 1, 3)
            else:
                self.load_table(filtered_patients)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to filter tables: {e}")

    def display_no_records_message(self):
        self.records_ui.PatientTable.setRowCount(1)
        self.records_ui.PatientTable.setColumnCount(3)
        self.records_ui.PatientTable.setHorizontalHeaderLabels(["Patient ID", "Name", "Status"])

        no_data_item = QtWidgets.QTableWidgetItem("No matching records found")
        no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
        no_data_item.setFlags(QtCore.Qt.NoItemFlags)

        self.records_ui.PatientTable.setItem(0, 0, no_data_item)

        # Clear other columns to prevent leftover data
        for col in range(1, 3):
            self.records_ui.PatientTable.setItem(0, col, QtWidgets.QTableWidgetItem(""))

        self.records_ui.PatientTable.resizeColumnsToContents()
        self.records_ui.PatientTable.horizontalHeader().setStretchLastSection(True)

    def load_table(self, patients):
        try:
            self.records_ui.PatientTable.setRowCount(0)

            if not patients:
                self.display_no_records_message()
                return

            # Sort by name (optional)
            patients.sort(key=lambda p: p.get("name", "").lower())

            self.records_ui.PatientTable.setColumnCount(3)
            self.records_ui.PatientTable.setHorizontalHeaderLabels(["Patient ID", "Name", "Status"])
            self.records_ui.PatientTable.verticalHeader().setVisible(False)
            self.records_ui.PatientTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

            for row, patient in enumerate(patients):
                id = str(patient.get("id", ""))
                name = patient.get("name", "N/A")
                status = patient.get("status", "Pending")

                self.records_ui.PatientTable.insertRow(row)
                self.records_ui.PatientTable.setItem(row, 0, QtWidgets.QTableWidgetItem(id))
                self.records_ui.PatientTable.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
                self.records_ui.PatientTable.setItem(row, 2, QtWidgets.QTableWidgetItem(status))

            self.records_ui.PatientTable.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            pass

    def view_patient_details_ui(self, patient_id):
        try:
            from Controllers.AdminPatientDetails_Controller import AdminPatientDetailsController
            self.admin_patient_details_controller = AdminPatientDetailsController(patient_id)
            self.admin_patient_details_controller.show()
            self.hide()
        except Exception as e:
            pass

    def view_dashboard_ui(self):
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
            self.hide()
        except Exception as e:
            pass

    def view_staff_ui(self):
        try:
            from Controllers.AdminStaffs_Controller import AdminStaffsController
            self.admin_staff_controller = AdminStaffsController()
            self.admin_staff_controller.show()
            self.hide()
        except Exception as e:
            pass

    def view_charges_ui(self):
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            pass

    def view_transaction_ui(self):
        try:
            from Controllers.AdminTransaction_Controller import AdminTransactionsController
            self.admin_transaction_controller = AdminTransactionsController()
            self.admin_transaction_controller.show()
            self.hide()
        except Exception as e:
            pass