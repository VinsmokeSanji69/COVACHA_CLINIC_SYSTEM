from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from Views.Admin_Dashboard import Ui_MainWindow as AdminDashboardUI
from Models.Admin import Admin

class AdminDashboardController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AdminDashboardUI()
        self.ui.setupUi(self)

        print("Admin Dashboard UI initialized!")

        self.load_counts()
        self.ui.StaffButton.clicked.connect(self.view_staff_ui)
        self.ui.ChargesButton.clicked.connect(self.view_charges_ui)
        self.ui.TransactionsButton.clicked.connect(self.view_transaction_ui)
        self.ui.PatientsButton.clicked.connect(self.view_patient_ui)

    def load_counts(self):
        try:
            # Count doctors
            doctor_count = Admin.count_doctor()
            self.ui.TotalDoctor.setText(str(doctor_count))

            # Count staff
            staff_count = Admin.count_staff()
            self.ui.TotalStaff.setText(str(staff_count))

            print(f"Loaded counts - Doctors: {doctor_count}, Staff: {staff_count}")

        except Exception as e:
            print(f"Dashboard: {e}")

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

    def view_patient_ui(self):
        print("RecordButton clicked!")
        try:
            print("inside Records")
            from Controllers.AdminPatients_Controller import AdminPatientsController
            self.admin_patients_controller = AdminPatientsController()
            self.admin_patients_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")