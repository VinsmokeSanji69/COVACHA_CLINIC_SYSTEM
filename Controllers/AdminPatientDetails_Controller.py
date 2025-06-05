from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Views.Admin_PatientDetails import Ui_MainWindow as AdminPatientDetailsUI


def calculate_age(birth_date):
    """Calculate age from date of birth (dob)"""
    today = datetime.now().date()
    age = today.year - birth_date.year
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


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

class AdminPatientDetailsController(QMainWindow):
    def __init__(self, patient_id=None):
        super().__init__()
        self.patient_id = patient_id
        self.ui = AdminPatientDetailsUI()
        self.ui.setupUi(self)

        # self.ui.DashboardButton.clicked.connect(self.view_dashboard_ui)
        # self.ui.ChargesButton.clicked.connect(self.view_charges_ui)
        # self.ui.BackButton.clicked.connect(self.view_staff_ui)
        # self.ui.StaffsButton.clicked.connect(self.view_staff_ui)
        self.ui.ViewCheckupButton.clicked.connect(self.view_checkup_details)

        self.initialize_patient_details()

    def view_checkup_details(self):
        try:
            selected_row = self.ui.TransactionTable.currentRow()
            if selected_row == -1:
                print("no row selected")
                return

            check_id = self.ui.TransactionTable.item(selected_row, 0)
            if not check_id:
                raise ValueError(f"No patient ID found in selected row")

            check_id = check_id.text().strip()
            if not check_id:
                raise ValueError(f" ID is empty")

            self.view_checkup_details_ui(check_id)

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))

        except Exception as e:
            error_msg = f"Failed to select patient: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(error_msg)

    def identify_patient(self):
        try:
            patient_details = Patient.get_patient_by_id(int(self.patient_id))
            checkup_list = CheckUp.get_checkup_by_pat_id(int(self.patient_id))

            return  patient_details, checkup_list
        except Exception as e:
            print(f"Error Identifying Staff: {e}")

    def initialize_patient_details(self):
        try:
            patient_details, checkups = self.identify_patient()
            name = f"{patient_details.get('last_name')}, {patient_details.get('first_name')} {patient_details.get('middle_name')}"

            last_weight = "N/A"
            last_height = "N/A"
            if checkups and len(checkups) > 0:
                last_weight = str(checkups[0]['weight'])
                last_height = str(checkups[0]['height'])

            self.ui.PatName.setText(name)
            self.ui.PatID.setText(str(patient_details.get("id", "N/A")))
            self.ui.PatAge.setText(str(calculate_age(patient_details.get("dob"))))
            self.ui.PatGender.setText(str(patient_details.get("gender", "N/A")))
            self.ui.PatDoB.setText(str(safe_date_format(patient_details.get("dob"))))
            self.ui.PatAddress.setText(str(patient_details.get("address", "N/A")))
            self.ui.PatContact.setText(str(patient_details.get("contact", "N/A")))
            self.ui.PatHeight.setText(last_height)
            self.ui.PatWeight.setText(last_weight)
            self.load_checkups(checkups)

        except Exception as e:
            print(f"Error initializing staff details: {e}")

    def load_checkups(self, checkups):
        try:

            self.ui.TransactionTable.setRowCount(len(checkups))

            # Configure table properties first
            self.ui.TransactionTable.verticalHeader().setVisible(False)
            self.ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)  # Moved up
            self.ui.TransactionTable.setHorizontalHeaderLabels(["Checkup ID", "Diagnosis", "Date"])

            # Populate the table
            for row, checkup in enumerate(checkups):
                id = str(checkup.get("id", ""))
                diagnosis = checkup.get("diagnosis", "N/A")
                date = checkup.get("date", "No date").strftime('%Y-%m-%d') if checkup.get("date") else "No date"

                # Insert row items
                self.ui.TransactionTable.insertRow(row)
                self.ui.TransactionTable.setItem(row, 0, QtWidgets.QTableWidgetItem(id))
                self.ui.TransactionTable.setItem(row, 1, QtWidgets.QTableWidgetItem(diagnosis))
                self.ui.TransactionTable.setItem(row, 2, QtWidgets.QTableWidgetItem(date))

            # Adjust table appearance
            self.ui.TransactionTable.resizeColumnsToContents()
            self.ui.TransactionTable.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            print(f"Error populating Patient Table: {e}")

    def view_checkup_details_ui(self, id):
        try:
            from Controllers.DoctorLabResult_Controller import DoctorLabResult
            self.admin_checkup_details_controller = DoctorLabResult(checkup_id=id, refresh_callback=None, view=True)
            self.admin_checkup_details_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")

    def view_staff_ui(self):
        try:
            from Controllers.AdminStaffs_Controller import AdminStaffsController
            self.admin_staff_controller = AdminStaffsController()
            self.admin_staff_controller.show()
            self.hide()
        except Exception as e:
            print(f"Dashboard Error(staffs): {e}")

    def view_dashboard_ui(self):
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error: {e}")

    def view_charges_ui(self):
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error: {e}")