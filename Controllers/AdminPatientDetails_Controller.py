from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Views.Admin_PatientDetails import Ui_MainWindow as AdminPatientDetailsUI


def calculate_age(birth_date):
    """Calculate age from date of birth (dob)"""
    if not birth_date:
        return "N/A"
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

        self.ui.BackButton.clicked.connect(self.view_staff_ui)
        self.ui.ViewCheckupButton.clicked.connect(self.view_checkup_details)
        self.initialize_patient_details()

        self.ui.BackButton.clicked.connect(self.close)

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
            if not self.patient_id:
                raise ValueError("No patient ID provided.")

            # Fetch patient details
            patient_details = Patient.get_patient_by_id(int(self.patient_id))
            if not patient_details:
                raise ValueError(f"No patient found with ID {self.patient_id}")

            # Parse dob into datetime.date
            dob_str = patient_details.get("dob")
            if dob_str:
                try:
                    patient_details["dob"] = datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Invalid date format for DOB: {dob_str}")
            else:
                patient_details["dob"] = None

            # Fetch checkups
            checkups = CheckUp.get_checkup_by_pat_id(int(self.patient_id)) or []

            return patient_details, checkups

        except Exception as e:
            print(f"Error Identifying Patient: {e}")
            QMessageBox.critical(self, "Error", f"Failed to fetch patient details: {e}")
            return None, []

    def initialize_patient_details(self):
        try:
            patient_details, checkups = self.identify_patient()

            if not patient_details:
                self.ui.PatName.setText("N/A")
                self.ui.PatID.setText("N/A")
                self.ui.PatAge.setText("N/A")
                self.ui.PatGender.setText("N/A")
                self.ui.PatDoB.setText("N/A")
                self.ui.PatAddress.setText("N/A")
                self.ui.PatContact.setText("N/A")
                self.ui.PatHeight.setText("N/A")
                self.ui.PatWeight.setText("N/A")
                self.load_checkups([])
                return

            # Extract and format patient details
            name_parts = [patient_details.get('last_name'), patient_details.get('first_name'),
                          patient_details.get('middle_name')]
            name = ", ".join(filter(None, name_parts)) or "N/A"

            last_weight = "N/A"
            last_height = "N/A"
            if checkups:
                last_weight = str(checkups[0]['weight']) if checkups[0]['weight'] else "N/A"
                last_height = str(checkups[0]['height']) if checkups[0]['height'] else "N/A"

            # Set UI fields
            self.ui.PatName.setText(name)
            self.ui.PatID.setText(str(patient_details.get("id", "N/A")))
            dob = patient_details.get("dob")
            age = calculate_age(dob) if dob else "N/A"
            self.ui.PatAge.setText(str(age))
            self.ui.PatGender.setText(str(patient_details.get("gender", "N/A")))
            self.ui.PatDoB.setText(safe_date_format(dob))
            self.ui.PatAddress.setText(str(patient_details.get("address", "N/A")))
            self.ui.PatContact.setText(str(patient_details.get("contact", "N/A")))
            self.ui.PatHeight.setText(last_height)
            self.ui.PatWeight.setText(last_weight)

            # Load checkups
            self.load_checkups(checkups)

        except Exception as e:
            print(f"Error initializing patient details: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load patient details: {e}")

    def load_checkups(self, checkups):
        try:
            # Sort by ID in descending order (latest first)
            sorted_checkups = sorted(
                checkups,
                key=lambda c: c.get("id", ""),
                reverse=True
            )

            self.ui.TransactionTable.setRowCount(len(sorted_checkups))
            self.ui.TransactionTable.verticalHeader().setVisible(False)
            self.ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.ui.TransactionTable.setHorizontalHeaderLabels(["Checkup ID", "Diagnosis", "Date"])

            for row, checkup in enumerate(sorted_checkups):
                chck_id = str(checkup.get("id", "N/A"))
                diagnosis = checkup.get("diagnosis", "N/A")
                date = safe_date_format(checkup.get("date"))

                self.ui.TransactionTable.setItem(row, 0, QtWidgets.QTableWidgetItem(chck_id))
                self.ui.TransactionTable.setItem(row, 1, QtWidgets.QTableWidgetItem(diagnosis))
                self.ui.TransactionTable.setItem(row, 2, QtWidgets.QTableWidgetItem(date))

            self.ui.TransactionTable.resizeColumnsToContents()
            self.ui.TransactionTable.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            print(f"Error populating Transaction Table: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load checkups: {e}")

    def view_checkup_details_ui(self, id):
        try:
            from Controllers.DoctorLabResult_Controller import DoctorLabResult
            self.admin_checkup_details_controller = DoctorLabResult(checkup_id=id, parent=self, refresh_callback=None, view=True)
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
