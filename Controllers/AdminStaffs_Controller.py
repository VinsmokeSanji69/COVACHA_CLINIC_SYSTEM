from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox, \
    QWidget
from Controllers.AdminModifyUser_Controller import AdminModifyUserController
from Views.Admin_Staffs import Ui_Admin_Staff as AdminStaffsUI
from Controllers.AdminAddUser_Controller import AdminAddUserController
from Models.Staff import Staff
from Models.Doctor import Doctor

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None, staff_id=None, staff_type=None):
        super().__init__(parent)
        self.staff_id = staff_id
        self.staff_type = staff_type
        self.setWindowTitle("Confirm Add Laboratory")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        message = f"Are you sure you want to delete {'doctor' if type == 'doctor' else 'staff'} with ID: {staff_id}?"
        self.message_label = QLabel(message)
        layout.addWidget(self.message_label)

        # Add button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Apply stylesheet to the button box
        self.button_box.setStyleSheet("""
            QPushButton {
                background-color: #2E6E65;
                color: white;
                border-radius: 10px;
                padding: 5px 10px;
                margin-top: 5px
            }
            QPushButton:hover {
                background-color: #235C5A;
            }
        """)
        layout.addWidget(self.button_box)

        # Set layout
        self.setLayout(layout)

class AdminStaffsController(QWidget):
    def __init__(self, staff_ui):
        super().__init__()
        self.staff_details = None
        self.ui = AdminStaffsUI()
        self.staff_ui = staff_ui
        self.ui.setupUi(self)
        self.refresh_tables()
        self.staff_ui.AddUserButton.clicked.connect(self.open_add_user_form)
        self.staff_ui.ChargesButton.clicked.connect(self.view_charges_ui)
        self.staff_ui.TransactionsButton.clicked.connect(self.view_transaction_ui)
        self.staff_ui.PatientsButton.clicked.connect(self.view_patient_ui)
        self.staff_ui.DeleteStaff.clicked.connect(lambda: self.delete_record("staff"))
        self.staff_ui.DeleteDoctor.clicked.connect(lambda: self.delete_record("doctor"))
        self.staff_ui.ModifyStaff.clicked.connect(lambda: self.modify_staff("staff"))
        self.staff_ui.ModifyDoctor.clicked.connect(lambda: self.modify_staff("doctor"))

    def modify_staff(self, table_type=None):
        try:
            # Determine which table to use based on table_type
            if table_type == "doctor":
                table = self.staff_ui.DoctorTable
            else:
                # Optionally handle general staff or raise an error if table_type is None/invalid
                table = self.staff_ui.StaffTable

            selected_row = table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error",
                                    f"Please select a {table_type if table_type else 'staff member'} from the table.")
                return

            # Get the staff ID from the first column of the selected row
            staff_id_item = table.item(selected_row, 0)
            if not staff_id_item:
                raise ValueError(f"No {table_type if table_type else 'staff'} ID found in selected row")

            staff_id = staff_id_item.text().strip()
            if not staff_id:
                raise ValueError(f"{table_type.capitalize() if table_type else 'Staff'} ID is empty")

            # Open the modification form with the correct staff ID and type
            self.modify_user_form(staff_id, table_type)

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Failed to select {table_type if table_type else 'staff'}: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)

    def delete_record(self, record_type="doctor"):
        try:
            table = self.staff_ui.DoctorTable if record_type == "doctor" else self.staff_ui.StaffTable
            model_class = Doctor if record_type == "doctor" else Staff

            # Get selected row
            selected_row = table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error",
                                    f"Please select a {record_type} from the table.")
                return

            # Validate ID exists in the table
            id_item = table.item(selected_row, 0)
            if not id_item:
                raise ValueError(f"No {record_type} ID found in selected row")

            record_id = id_item.text().strip()
            if not record_id:
                raise ValueError(f"{record_type.capitalize()} ID is empty")

            # Show confirmation dialog
            confirmation_dialog = ConfirmationDialog(self, record_id, record_type)
            if confirmation_dialog.exec_() == QDialog.Rejected:
                return

            success = model_class.delete(int(record_id))
            message = (f"{record_type.capitalize()} successfully deleted" if success
                       else f"Failed to delete {record_type}")

            QMessageBox.information(self, "Result", message)
            self.refresh_tables()

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Error deleting {record_type}: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)

    def refresh_tables(self):
        """Reload data into the tables"""
        try:
            self.load_doctor_table()
            self.load_staff_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh tables: {e}")

    def load_doctor_table(self):
        doctors = Doctor.get_all_doctors()
        self.staff_ui.DoctorTable.setRowCount(len(doctors))

        # Remove row numbering
        self.staff_ui.DoctorTable.verticalHeader().setVisible(False)
        self.staff_ui.DoctorTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Populate the table
        for row, doctor in enumerate(doctors):
            self.staff_ui.DoctorTable.setItem(row, 0, QTableWidgetItem(str(doctor["id"])))
            self.staff_ui.DoctorTable.setItem(row, 1, QTableWidgetItem(doctor["name"]))
            self.staff_ui.DoctorTable.setItem(row, 2, QTableWidgetItem(doctor["specialty"]))

    def load_staff_table(self):
        staff_list = Staff.get_all_staff()
        self.staff_ui.StaffTable.setRowCount(len(staff_list))

        # Remove row numbering
        self.staff_ui.StaffTable.verticalHeader().setVisible(False)
        self.staff_ui.StaffTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Populate the table
        for row, staff in enumerate(staff_list):
            self.staff_ui.StaffTable.setItem(row, 0, QTableWidgetItem(str(staff["id"])))
            self.staff_ui.StaffTable.setItem(row, 1, QTableWidgetItem(staff["name"]))

    def modify_user_form(self, staff_id, record_type):
        try:
            if record_type == "doctor":
                # Use the Doctor class's static method
                staff = Doctor.get_doctor(staff_id)
            else:
                # Assume Staff is another class with get_staff() as a static or instance method
                staff = Staff.get_staff(int(staff_id))

            if not staff:
                QMessageBox.critical(self, "Error", f"{record_type.capitalize()} details could not be loaded.")
                return

            # Open the form
            self.add_user_window = AdminModifyUserController(parent=self, staff_details=staff, staff_type=record_type)
            self.add_user_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open modification form: {str(e)}")

    def open_add_user_form(self):
        try:
            self.add_user_window = AdminAddUserController(parent=self)
            self.add_user_window.show()
        except Exception as e:
            pass

    def view_patient_ui(self):
        try:
            from Controllers.AdminPatients_Controller import AdminPatientsController
            self.admin_patients_controller = AdminPatientsController()
            self.admin_patients_controller.show()
            self.hide()
        except Exception as e:
            pass

    def view_transaction_ui(self):
        try:
            from Controllers.AdminTransaction_Controller import AdminTransactionsController
            self.admin_transaction_controller = AdminTransactionsController()
            self.admin_transaction_controller.show()
            self.hide()
        except Exception as e:
            pass
    def view_charges_ui(self):
        try:
            from Controllers.AdminCharges_Controller import AdminChargesController
            self.admin_charges_controller = AdminChargesController()
            self.admin_charges_controller.show()
            self.hide()
        except Exception as e:
            pass
