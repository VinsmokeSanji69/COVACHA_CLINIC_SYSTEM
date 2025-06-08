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
    total = subtotal - discount
    return  total


class AdminTransactionDetailsController(QMainWindow):
    def __init__(self, transaction_id):
        super().__init__()
        self.ui = AdminTransactionDetailsUI()
        self.transaction_id = transaction_id
        self.ui.setupUi(self)

        self.initialize_data()

    def identify_transaction(self):
        try:
            checkup = CheckUp.get_checkup_details(self.transaction_id)
            if not checkup:
                raise ValueError("Checkup not found")

            transaction = Transaction.get_transaction_by_chckid(self.transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")

            patient = Patient.get_patient_by_id(checkup["pat_id"])
            if not patient:
                raise ValueError("Patient not found")

            return checkup, transaction, patient

        except Exception as e:
            return None

    def initialize_data(self):
        checkup, transaction, patient = self.identify_transaction()
        staff = Staff.get_staff(checkup["staff_id"])
        doctor = Doctor.get_doctor(checkup["doc_id"])

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
        from Controllers.DoctorLabResult_Controller import DoctorLabResult
        self.admin_checkup_details_controller = DoctorLabResult(checkup_id=id, parent=self, refresh_callback=None, view=True)
        self.admin_checkup_details_controller.show()
        self.hide()


    def view_transaction_ui(self):
        from Controllers.AdminTransaction_Controller import AdminTransactionsController
        self.admin_transaction_controller = AdminTransactionsController()
        self.admin_transaction_controller.show()
        self.hide()


    def view_patient_ui(self):
        from Controllers.AdminPatients_Controller import AdminPatientsController
        self.admin_patients_controller = AdminPatientsController()
        self.admin_patients_controller.show()
        self.hide()


