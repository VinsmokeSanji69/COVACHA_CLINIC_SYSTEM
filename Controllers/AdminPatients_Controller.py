from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow
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


    def load_table(self):
        try:
            tests = Patient.get_all_test()
            self.ui.LaboratoryTestTable.setRowCount(0)

            # Populate the table
            for row, test in enumerate(tests):
                lab_code = test["lab_code"]
                lab_test_name = test["lab_test_name"]  # Already capitalized in the model
                lab_price = test["lab_price"]

                # Insert data into the table
                self.ui.LaboratoryTestTable.insertRow(row)
                self.ui.LaboratoryTestTable.setItem(row, 0, QtWidgets.QTableWidgetItem(lab_code))
                self.ui.LaboratoryTestTable.setItem(row, 1, QtWidgets.QTableWidgetItem(lab_test_name))
                self.ui.LaboratoryTestTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(lab_price)))

            # Resize columns to fit the content
            self.ui.LaboratoryTestTable.resizeColumnsToContents()

        except Exception as e:
        print(f"Error populating LaboratoryTestTable: {e}")
















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
