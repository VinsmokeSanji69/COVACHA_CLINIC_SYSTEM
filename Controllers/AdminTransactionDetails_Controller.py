from distutils.command.check import check
from sre_parse import parse_template

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem

from Models.CheckUp import CheckUp
from Models.Doctor import Doctor
from Models.Patient import Patient
from Models.Staff import Staff
from Models.Transaction import Transaction
from Views.Admin_TransactionDetails import Ui_MainWindow as AdminTransactionDetailsUI

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


def calculate_transaction(transaction):
    discount = transaction["tran_discount"]
    base = transaction["tran_base_charge"]
    lab = transaction["tran_lab_charge"]

    subtotal = base + lab
    total = subtotal - (subtotal * discount /100)
    return  total


class AdminTransactionDetailsController(QMainWindow):
    def __init__(self, transaction_id):
        super().__init__()
        self.ui = AdminTransactionDetailsUI()
        self.transaction_id = transaction_id
        self.ui.setupUi(self)

        self.ui.DashboardButton.clicked.connect(self.view_dashboard_ui)
        self.ui.ChargesButton.clicked.connect(self.view_charges_ui)
        self.ui.StaffsButton.clicked.connect(self.view_staff_ui)
        self.ui.PatientsButton.clicked.connect(self.view_patient_ui)
        self.ui.TransactionsButton.clicked.connect(self.view_transaction_ui)
        self.initialize_data()


    def identify_transaction(self):
        try:
            print(self.transaction_id)
            checkup = CheckUp.get_checkup_details(self.transaction_id)

            transaction = Transaction.get_transaction_by_id(self.transaction_id)

            patient = Patient.get_patient_by_id(checkup["pat_id"])
            return checkup, transaction, patient
        except Exception as e:
            print("Error: ", e)
            return None

    def initialize_data(self):
        checkup, transaction, patient = self.identify_transaction()
        print(type(checkup), type(transaction), type(patient))
        print(checkup, transaction, patient)

        staff = Staff.get_staff(checkup["staff_id"])
        print(staff)
        doctor = Doctor.get_doctor(checkup["doc_id"])
        print(doctor)

        staff_name = f"{staff['last_name']}, {staff['first_name']}"
        doc_name = f"{doctor['last_name']}, {doctor['first_name']}"
        pat_name = f"{patient['last_name']}, {patient['first_name']}"
        transaction_date = safe_date_format(checkup["chck_date"])
        fee = calculate_transaction(transaction)


        self.ui.PatientID.setText(str(patient["id"]))
        self.ui.PatientName.setText(pat_name)
        self.ui.PatientGender.setText(patient["gender"])
        self.ui.PatientAge.setText(str(patient["age"]))

        self.ui.DoctorName.setText(doc_name)
        self.ui.DoctorID.setText(str(doctor["id"]))
        self.ui.DoctorSpecialty.setText(doctor["specialty"])

        self.ui.StaffID.setText(str(staff["id"]))
        self.ui.StaffName.setText(staff_name)

        self.ui.Diagnosis.setText(checkup["chck_diagnoses"])
        self.ui.TransactionID.setText(transaction["chck_id"])
        self.ui.TransactionFee.setText(str(fee))
        self.ui.TransactionDate.setText(transaction_date)
        self.ui.ViewDiagnosis.clicked.connect(lambda: self.view_diagnosis_details_ui(self.transaction_id))

    def view_diagnosis_details_ui(self, id):
        try:
            from Controllers.DoctorLabResult_Controller import DoctorLabResult
            self.admin_checkup_details_controller = DoctorLabResult(checkup_id=id, parent=self, refresh_callback=None, view=True)
            self.admin_checkup_details_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")

    def view_transaction_ui(self):
        try:
            from Controllers.AdminTransaction_Controller import AdminTransactionsController
            self.admin_transaction_controller = AdminTransactionsController()
            self.admin_transaction_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error(charges): {e}")

    def view_patient_ui(self):
        try:
            from Controllers.AdminPatients_Controller import AdminPatientsController
            self.admin_patients_controller = AdminPatientsController()
            self.admin_patients_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction Details Error: {e}")

    def view_dashboard_ui(self):
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction Details Error: {e}")

    def view_staff_ui(self):
        try:
            from Controllers.AdminStaffs_Controller import AdminStaffsController
            self.admin_staff_controller = AdminStaffsController()
            self.admin_staff_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction Details Error(staffs): {e}")

    def view_charges_ui(self):
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            print(f"Transaction Details Error: {e}")

