from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow
from Views.Admin_Transactions import Ui_MainWindow as AdminTransactionUI

class AdminTransactionsController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AdminTransactionUI()
        self.ui.setupUi(self)

        print("Admin Transactions UI initialized!")

        self.ui.DashboardButton.clicked.connect(self.view_dashboard_ui)
        self.ui.ChargesButton.clicked.connect(self.view_charges_ui)
        self.ui.StaffsButton.clicked.connect(self.view_staff_ui)
        self.ui.PatientsButton.clicked.connect(self.view_patient_ui)


    def view_patient_ui(self):
        try:
            from Controllers.AdminPatients_Controller import AdminPatientsController
            self.admin_patients_controller = AdminPatientsController()
            self.admin_patients_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")

    def view_dashboard_ui(self):
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
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

    def view_charges_ui(self):
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error(charges): {e}")
