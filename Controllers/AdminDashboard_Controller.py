from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Views.Admin_Dashboard import Ui_MainWindow as AdminDashboardUI
from Models.AdminDashboardModel import AdminDashboardModel
from Controllers.AdminStaffs_Controller import AdminStaffsController
from Controllers.AdminCharges_Controller import AdminChargesController

class AdminDashboardController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AdminDashboardUI()
        self.ui.setupUi(self)

        print("Admin Dashboard UI initialized!")

        # Load counts into the UI
        self.load_counts()

        # Connect buttons to staff views
        if hasattr(self.ui, 'StaffButton'):
            print("StaffButton exists")
            self.ui.StaffButton.clicked.connect(self.ViewStaff)
            print("StaffButton connected to button_clicked method!")
        else:
            print("StaffButton is missing!")

        #connect button to charges views
        if hasattr(self.ui, 'ChargesButton'):
            print("ChargesButton exists")
            self.ui.ChargesButton.clicked.connect(self.ViewCharges)
            print("Charges button connected to button click method!")
        else:
            print("Charges Button is missing")

    def load_counts(self):
        try:
            # Count doctors
            doctor_count = AdminDashboardModel.count_doctor()
            self.ui.TotalDoctor.setText(str(doctor_count))

            # Count staff
            staff_count = AdminDashboardModel.count_staff()
            self.ui.TotalStaff.setText(str(staff_count))

            print(f"Loaded counts - Doctors: {doctor_count}, Staff: {staff_count}")

        except Exception as e:
            print(f"Error loading counts: {e}")

    def ViewStaff(self):
        print("StaffButton clicked!")
        try:
            # Instantiate and show the AdminStaffsController window
            self.admin_staffs_controller = AdminStaffsController()
            self.admin_staffs_controller.show()
            self.hide()  # Hide the current dashboard window
        except Exception as e:
            print(f"Error loading tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")

    def ViewCharges(self):
        print("StaffButton clicked!")
        try:
            # Instantiate and show the AdminStaffsController window
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()  # Hide the current dashboard window
        except Exception as e:
            print(f"Error loading tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")