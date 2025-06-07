from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Views.Doctor_PatientDetailsView import Ui_Doctor_PatientDetails_View


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
            return datetime.strptime(date_value, "%Y-%m-%d").strftime(date_format)
        except ValueError:
            return date_value  # Return as-is if parsing fails
    elif hasattr(date_value, 'strftime'):  # If it's a date/datetime object
        return date_value.strftime(date_format)
    return "N/A"


class DoctorPatientDetailsViewController(QMainWindow):
    def __init__(self, patient_id=None):
        super().__init__()
        self.patient_id = patient_id
        self.ui = Ui_Doctor_PatientDetails_View()
        self.ui.setupUi(self)

        self.ui.ViewCheckupButton.clicked.connect(self.view_checkup_details)

        self.initialize_patient_details()

    def view_checkup_details(self):
        try:
            selected_row = self.ui.TransactionTable.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a check-up row.")
                return

            check_id_item = self.ui.TransactionTable.item(selected_row, 0)
            if not check_id_item:
                raise ValueError("No Checkup ID found in selected row")

            check_id = check_id_item.text().strip()
            if not check_id:
                raise ValueError("Checkup ID is empty")

            self.view_checkup_details_ui(check_id)

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Failed to open checkup details: {e}"
            QMessageBox.critical(self, "Error", error_msg)
            print(error_msg)

    def identify_patient(self):
        try:
            if not self.patient_id:
                raise ValueError("No patient ID provided.")

            patient_details = Patient.get_patient_by_id(int(self.patient_id))
            if not patient_details:
                raise ValueError(f"No patient found for ID: {self.patient_id}")

            dob_str = patient_details.get("dob")
            if dob_str and isinstance(dob_str, str):
                try:
                    patient_details["dob"] = datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Invalid date format for DOB: {dob_str}")

            checkups = CheckUp.get_checkup_by_pat_id(int(self.patient_id)) or []

            return patient_details, checkups

        except Exception as e:
            print(f"Error identifying patient: {e}")
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

            name_parts = [patient_details.get('last_name'), patient_details.get('first_name'),
                          patient_details.get('middle_name')]
            name = ", ".join(filter(None, name_parts)) or "N/A"

            last_weight = "N/A"
            last_height = "N/A"
            if checkups:
                last_weight = str(checkups[0]['weight']) if checkups[0].get('weight') else "N/A"
                last_height = str(checkups[0]['height']) if checkups[0].get('height') else "N/A"

            self.ui.PatName.setText(name)
            self.ui.PatID.setText(str(patient_details.get("id", "N/A")))
            dob = patient_details.get("dob")
            self.ui.PatAge.setText(str(calculate_age(dob)))
            self.ui.PatGender.setText(str(patient_details.get("gender", "N/A")))
            self.ui.PatDoB.setText(safe_date_format(dob))
            self.ui.PatAddress.setText(str(patient_details.get("address", "N/A")))
            self.ui.PatContact.setText(str(patient_details.get("contact", "N/A")))
            self.ui.PatHeight.setText(last_height)
            self.ui.PatWeight.setText(last_weight)

            self.load_checkups(checkups)

        except Exception as e:
            print(f"Error initializing patient details: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load patient details: {e}")

    def load_checkups(self, checkups):
        try:
            self.ui.TransactionTable.setRowCount(len(checkups))

            self.ui.TransactionTable.verticalHeader().setVisible(False)
            self.ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.ui.TransactionTable.setHorizontalHeaderLabels(["Checkup ID", "Diagnosis", "Date"])

            for row, checkup in enumerate(checkups):
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

    def view_checkup_details_ui(self, checkup_id):
        try:
            from Controllers.DoctorLabResult_Controller import DoctorLabResult
            self.checkup_detail_window = DoctorLabResult(checkup_id=checkup_id, view=True)
            self.checkup_detail_window.show()
            self.hide()
        except Exception as e:
            print(f"Error opening checkup detail: {e}")
            QMessageBox.critical(self, "Error", f"Could not open checkup details: {e}")