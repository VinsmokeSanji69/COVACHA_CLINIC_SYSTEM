from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout, \
    QWidget
from PyQt5.uic.Compiler.qtproxies import QtCore
from Models import LaboratoryTest
from Models.Doctor import Doctor
from Views.Admin_Charges import Ui_Admin_Charges as AdminChargesUI
from Controllers.AdminAddLabTest_Controller import AdminAddLabTest
from Controllers.AdminAddDoctorCharges_Controller import AdminDoctorCharges
from Models.LaboratoryTest import Laboratory

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Add Laboratory")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want delete the lab test?")
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

class AdminChargesController(QWidget):
    def __init__(self, charges_ui):
        super().__init__()
        self.ui = AdminChargesUI()
        self.charges_ui = charges_ui
        self.ui.setupUi(self)

        print("Admin Charges UI initialized!")

        self.refresh_tables()

        # Table Buttons - using the passed charges_ui instead of self.ui
        self.charges_ui.Modify.clicked.connect(self.modify_charges)
        self.charges_ui.Delete.clicked.connect(self.delete_lab_test)
        self.charges_ui.AddLabTestButton.clicked.connect(self.open_add_user_form)

        self.populate_laboratory_test_table()

    def delete_lab_test(self):
        try:
            print("Delete button clicked!")

            # Try getting selection from DoctorTable
            doctor_table = self.charges_ui.DoctorTable
            lab_table = self.charges_ui.LaboratoryTestTable

            selected_row_doctor = doctor_table.currentRow()
            selected_row_lab = lab_table.currentRow()

            if selected_row_doctor != -1:
                row_id_item = doctor_table.item(selected_row_doctor, 0)
                if not row_id_item:
                    raise ValueError("No doctor ID found in selected row")
                row_id = row_id_item.text().strip()
                confirmation_dialog = ConfirmationDialog(self)
                confirmation_dialog.message_label.setText(f"Are you sure you want to delete the doctor with ID: {row_id}?")
                if confirmation_dialog.exec_() == QDialog.Rejected:
                    return
                success = Doctor.delete(int(row_id))
                message = "Doctor deleted successfully!" if success else "Failed to delete doctor."
                QMessageBox.information(self, "Result", message)
                if success:
                    self.refresh_tables()
                return

            elif selected_row_lab != -1:
                row_id_item = lab_table.item(selected_row_lab, 0)
                if not row_id_item:
                    raise ValueError("No lab test ID found in selected row")
                row_id = row_id_item.text().strip()
                confirmation_dialog = ConfirmationDialog(self)
                confirmation_dialog.message_label.setText(f"Are you sure you want to delete the lab test with ID: {row_id}?")
                if confirmation_dialog.exec_() == QDialog.Rejected:
                    return
                success = Laboratory.delete(row_id)
                message = "Lab Test deleted successfully!" if success else "Failed to delete lab test."
                QMessageBox.information(self, "Result", message)
                if success:
                    self.refresh_tables()
                return

            else:
                QMessageBox.warning(self, "Selection Error", "Please select an item from either table.")

        except Exception as e:
            error_msg = f"Failed to delete record: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(error_msg)

    def modify_charges(self):
        try:
            print("Modify button clicked!")

            doctor_table = self.charges_ui.DoctorTable
            lab_table = self.charges_ui.LaboratoryTestTable

            selected_row_doctor = doctor_table.currentRow()
            selected_row_lab = lab_table.currentRow()

            if selected_row_doctor != -1:
                doc_name = doctor_table.item(selected_row_doctor, 0).text()
                doc_id = self.find_doc_id(doc_name)
                if not doc_id:
                    raise ValueError("Could not find doctor ID.")
                self.open_add_charges_form(doc_id)
                return

            elif selected_row_lab != -1:
                lab_id_item = lab_table.item(selected_row_lab, 0)
                if not lab_id_item:
                    raise ValueError("Could not find lab test ID.")
                lab_id = lab_id_item.text()
                self.modify_charges_form(lab_id)
                return

            else:
                QMessageBox.warning(self, "Selection Error", "Please select an item to modify.")

        except Exception as e:
            error_msg = f"Failed to modify charges: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(error_msg)

    @staticmethod
    def find_doc_id(doc_name):
        if not doc_name or not isinstance(doc_name, str):
            print("Invalid doctor name provided")
            return None

        try:
            doctors = Doctor.get_all_doctors()
            doc_name_clean = doc_name.strip().lower()

            for doctor in doctors:
                # Case-insensitive comparison with stripped whitespace
                current_name = str(doctor.get("name", "")).strip().lower()
                if doc_name_clean == current_name:
                    doc_id = doctor.get("id")
                    if doc_id is not None:
                        return int(doc_id)
                    break

            print(f"No doctor found with name: {doc_name}")
            return None

        except Exception as e:
            print(f"Error finding doctor ID: {e}")
            return None

    def refresh_tables(self):
        self.populate_laboratory_test_table()
        self.load_doctor_table()

    def populate_laboratory_test_table(self):
        try:
            tests = Laboratory.get_all_test()
            self.charges_ui.LaboratoryTestTable.setRowCount(0)

            for row, test in enumerate(tests):
                lab_code = test["lab_code"]
                lab_test_name = test["lab_test_name"]
                lab_price = test["lab_price"]

                self.charges_ui.LaboratoryTestTable.insertRow(row)
                self.charges_ui.LaboratoryTestTable.setItem(row, 0, QtWidgets.QTableWidgetItem(lab_code))
                self.charges_ui.LaboratoryTestTable.setItem(row, 1, QtWidgets.QTableWidgetItem(lab_test_name))
                self.charges_ui.LaboratoryTestTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(lab_price)))

            self.charges_ui.LaboratoryTestTable.viewport().update()
            self.charges_ui.LaboratoryTestTable.verticalHeader().setVisible(False)

        except Exception as e:
            print(f"Error populating LaboratoryTestTable: {e}")

    def load_doctor_table(self):
        try:
            doctors = Doctor.get_all_doctors()
            self.charges_ui.DoctorTable.setRowCount(0)

            # Populate the table
            for row, doctor in enumerate(doctors):
                self.charges_ui.DoctorTable.insertRow(row)
                formatted_rate = f"{float(doctor['rate']):,.2f}" if doctor["rate"] is not None else "0.00"
                self.charges_ui.DoctorTable.setItem(row, 0, QTableWidgetItem(str(doctor["name"])))
                self.charges_ui.DoctorTable.setItem(row, 1, QTableWidgetItem(formatted_rate))

            self.charges_ui.DoctorTable.verticalHeader().setVisible(False)
        except Exception as e:
            print(f"Error loading doctor table: {e}")

    def clear_other_table_selection(self, table):
        if self.sender().selectedItems():  # If current table has a selection
            table.clearSelection()  # Clear the other table

    def modify_charges_form(self, lab_id):
        try:
            lab_test_details = Laboratory.get_lab_test(lab_id)
            self.add_user_window = AdminAddLabTest(parent=self, lab_test=lab_test_details, modify=True)
            self.add_user_window.show()
            print("Add Test Form shown successfully!")
        except Exception as e:
            print(f"Error opening Add Test Form: {e}")

    def open_add_user_form(self):
        try:
            self.add_lab_test_window = AdminAddLabTest(parent=self)
            self.add_lab_test_window.show()
        except Exception as e:
            print(f"Error opening Add Test Form: {e}")

    def open_add_charges_form(self, doc_id):
        print("Opening Add Charges Form...")
        try:
            self.add_user_window = AdminDoctorCharges(doc_id, parent=self)
            self.add_user_window.show()
            print("Modify Doctor Charges shown successfully!")
        except Exception as e:
            print(f"Error opening Add Charges Form: {e}")