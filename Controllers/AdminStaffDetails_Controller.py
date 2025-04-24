from datetime import datetime, date
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from Models.Doctor import Doctor
from Models.Staff import Staff
from Views.Admin_DoctorDetails import Ui_MainWindow as AdminStaffDetailsUI


def calculate_age(birth_date):
    """Calculate age from date of birth (dob)"""
    today = datetime.now().date()
    age = today.year - birth_date.year
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


class AdminStaffDetailsController(QMainWindow):
    def __init__(self, staff_id):
        super().__init__()
        self.staff_id = staff_id
        self.ui = AdminStaffDetailsUI()
        self.ui.setupUi(self)

        self.ui.DashboardButton.clicked.connect(self.view_dashboard_ui)
        self.ui.ChargesButton.clicked.connect(self.view_charges_ui)
        self.ui.BackButton.clicked.connect(self.view_staff_ui)
        self.ui.StaffsButton.clicked.connect(self.view_staff_ui)

        self.initialize_staff_details()


    def identify_staff(self):
        staff_details = None
        try:
            # Find the matching doctor
            doctors = Doctor.get_all_doctors()
            staffs = Staff.get_all_staff()
            for doctor in doctors:
                if str(self.staff_id) == str(doctor.get("id")):  # Using .get() for safety
                    staff_details = doctor
                    break

            for staff in staffs:
                if str(self.staff_id) == str(staff.get("id")):  # Using .get() for safety
                    staff_details = staff
                    break

            if not staff_details:
                raise ValueError(f"No doctor found with ID: {self.staff_id}")

            return  staff_details
        except Exception as e:
            print(f"Error Identifying Staff: {e}")


    def initialize_staff_details(self):
        try:
            doctor_details = self.identify_staff()

            def safe_calculate_age(dob):
                from datetime import datetime
                if not dob:
                    return "N/A"
                try:
                    if isinstance(dob, str):
                        dob = datetime.strptime(dob, "%Y-%m-%d").date()
                    today = datetime.today().date()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return str(age)
                except Exception:
                    return "N/A"

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

            # Set UI fields
            self.ui.DocName.setText(doctor_details.get("name", "N/A"))
            self.ui.DocID.setText(str(doctor_details.get("id", "N/A")))
            self.ui.DocAge.setText(safe_calculate_age(doctor_details.get("dob")))
            self.ui.DocSpecialty.setText(doctor_details.get("specialty", "N/A"))
            self.ui.DocAbout.setText(safe_date_format(doctor_details.get("joined_date")))
            self.ui.DocContact.setText(doctor_details.get("contact", "N/A"))
            self.ui.DocEmail.setText(doctor_details.get("email", "N/A"))
            self.ui.DocAddress.setText(doctor_details.get("address", "N/A"))

        except Exception as e:
            print(f"Error initializing staff details: {e}")
            # Clear fields if error occurs
            for widget in [self.ui.DocName, self.ui.DocID, self.ui.DocAge,
                           self.ui.DocSpecialty, self.ui.DocAbout,
                           self.ui.DocContact, self.ui.DocEmail, self.ui.DocAddress]:
                widget.clear()


    def view_staff_ui(self):
        print("StaffButton clicked!")
        try:
            from Controllers.AdminStaffs_Controller import AdminStaffsController
            self.admin_staff_controller = AdminStaffsController()
            self.admin_staff_controller.show()
            self.hide()
        except Exception as e:
            print(f"Dashboard Error(staffs): {e}")

    def view_dashboard_ui(self):
        print("DashboardButton clicked!")
        try:
            from Controllers.AdminDashboard_Controller import AdminDashboardController
            self.admin_dashboard_controller = AdminDashboardController()
            self.admin_dashboard_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")

    def view_charges_ui(self):
        print("ChargesButton clicked!")
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Details Error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")