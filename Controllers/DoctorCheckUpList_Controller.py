from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget
from Views.Doctor_CheckUpList import Ui_Doctor_CheckUpList as DoctorCheckUpListUI
from Controllers.DoctorCheckUpListView_Controller import DoctorCheckUpListView
from Models.CheckUp import CheckUp
from Models.Patient import Patient

class DoctorCheckUpList(QWidget):
    def __init__(self, doc_id, records_ui):
        super().__init__()
        self.ui = DoctorCheckUpListUI()
        self.records_ui = records_ui
        self.ui.setupUi(self)

        # Store the doc_id
        self.doc_id = str(doc_id)
        print(f"Doctor Records UI initialized with doc_id: {self.doc_id}")

        # Fetch all check-ups for the doctor
        self.checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)  # Store as an instance variable
        if not self.checkups:
            print("No check-ups found for this doctor.")
            return

        self.completed_checkups = [checkup for checkup in self.checkups if checkup['chck_status'] == "Completed"]

        # Apply table styles
        self.apply_table_styles()

        # Populate the DoneTable
        self.refresh_tables()

        # Connect the ViewPatientButton to the view_detials_checkup method
        self.records_ui.ViewPatientButton.clicked.connect(self.view_patient)

        # Initialize a QTimer for automatic refresh
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_tables)  # Connect to refresh_tables method
        self.refresh_timer.start(30000)  # Refresh every 30 seconds (30000 ms)

    def view_patient_details_ui(self, patient_id):
        print("View Patient Button clicked!")
        try:
            from Controllers.AdminPatientDetails_Controller import AdminPatientDetailsController
            self.admin_patient_details_controller = AdminPatientDetailsController(patient_id)
            self.admin_patient_details_controller.show()
            self.hide()
        except Exception as e:
            print(f"Staff Error: {e}")

    def view_patient(self):
        try:
            selected_row = self.records_ui.DoneTable.currentRow()
            if selected_row == -1:
                print("no row selected")
                return

            patient_id = self.records_ui.DoneTable.item(selected_row, 0)
            if not patient_id:
                raise ValueError(f"No patient ID found in selected row")

            patient_id = patient_id.text().strip()
            if not patient_id:
                raise ValueError(f" ID is empty")

            self.view_patient_details_ui(int(patient_id))

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Failed to select patient: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(error_msg)

    def refresh_tables(self):
        """Reload data into the tables."""
        try:
            # Fetch fresh data from the database
            checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
            if not checkups:
                print("No check-ups found for this doctor.")
                return

            # Filter completed check-ups
            self.completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]

            # Repopulate the DoneTable with fresh data
            self.populate_done_table(self.completed_checkups)

            print("Tables refreshed successfully!")
        except Exception as e:
            print(f"Error refreshing tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh tables: {e}")

    def apply_table_styles(self):
        self.ui.DoneTable.setStyleSheet("""
                            QTableWidget {
                                background-color: #F4F7ED;
                                gridline-color: transparent;
                                border-radius: 10px;
                            }
                            QTableWidget::item {
                                border: none;
                                font: 16pt "Lexend";
                            }
                            QTableWidget::item:selected {
                                background-color: rgba(46, 110, 101, 0.3);
                            }
                            QTableWidget QHeaderView::section {
                                background-color: #2E6E65;
                                color: white;
                                padding: 5px;
                                font: 18px "Lexend Medium";
                                border: 2px solid #2E6E65;
                            }
                            QScrollBar:vertical {
                                background: transparent;
                                width: 10px;
                                border-radius: 5px;
                            }
                            QScrollBar::handle:vertical {
                                background: #C0C0C0;
                                border-radius: 5px;
                            }
                            QScrollBar::handle:vertical:hover {
                                background: #A0A0A0;
                            }
                            QScrollBar::add-line:vertical,
                            QScrollBar::sub-line:vertical {
                                background: none;
                                border: none;
                            }
                        """)
        self.ui.DoneTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.DoneTable.horizontalHeader().setVisible(True)
        self.ui.DoneTable.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.ui.DoneTable.verticalHeader().setVisible(False)

    def populate_done_table(self, checkups):
        # Clear existing rows
        self.records_ui.DoneTable.clearContents()
        self.records_ui.DoneTable.setRowCount(0)

        # Populate the table
        for row, checkup in enumerate(checkups):
            chck_id = checkup['chck_id']
            pat_id = checkup['pat_id']
            chck_diagnoses = checkup['chck_diagnoses']
            chck_date = checkup['chck_date']

            # Fetch patient details
            patient = Patient.get_patient_details(pat_id)
            if not patient:
                print(f"No patient found for pat_id={pat_id}")
                continue

            # Extract and format patient name
            full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"

            # Add row to the table
            self.records_ui.DoneTable.insertRow(row)
            self.records_ui.DoneTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(chck_id)))
            self.records_ui.DoneTable.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name))
            self.records_ui.DoneTable.setItem(row, 2, QtWidgets.QTableWidgetItem(chck_diagnoses))
            self.records_ui.DoneTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(chck_date)))

    def view_detials_checkup(self):
        """Handle viewing details of the selected check-up."""
        try:
            # Get the currently selected row in the DoneTable
            selected_row = self.records_ui.DoneTable.currentRow()
            if selected_row == -1:  # No row selected
                QMessageBox.warning(self, "Selection Error", "Please select a check-up from the table.")
                return

            # Retrieve the chck_id from the selected row
            chck_id = self.records_ui.DoneTable.item(selected_row, 0).text()  # Column 0 contains chck_id
            print(f"Selected Check-Up ID: {chck_id}")

            # Open the DoctorCheckUpListView modal
            self.view_checkUp = DoctorCheckUpListView(checkup_id=chck_id, parent=self)
            self.view_checkUp.show()

        except Exception as e:
            print(f"Error viewing check-up details: {e}")
            QMessageBox.critical(self, "Error", f"Failed to view check-up details: {e}")

    def load_table(self, patients):
        try:
            self.records_ui.DoneTable.setRowCount(0)
            self.records_ui.DoneTable.setRowCount(len(patients))

            # Configure table properties first
            self.records_ui.DoneTable.verticalHeader().setVisible(False)
            self.records_ui.DoneTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.records_ui.DoneTable.setHorizontalHeaderLabels(["Patient ID", "Name", "Recent Diagnosis", "Date"])

            # Populate the table
            for row, patient in enumerate(patients):
                id = str(patient.get("id", ""))
                name = patient.get("name", "N/A")
                diagnosis = patient.get("recent_diagnosis", "No diagnosis")
                date = patient.get("diagnosed_date", "No date") if patient.get("diagnosed_date") else "No date"

                # Insert row items
                self.records_ui.DoneTable.insertRow(row)
                self.records_ui.DoneTable.setItem(row, 0, QtWidgets.QTableWidgetItem(id))
                self.records_ui.DoneTable.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
                self.records_ui.DoneTable.setItem(row, 2, QtWidgets.QTableWidgetItem(diagnosis))
                self.records_ui.DoneTable.setItem(row, 3, QtWidgets.QTableWidgetItem(date))

            # Adjust table appearance
            self.records_ui.DoneTable.resizeColumnsToContents()
            self.records_ui.DoneTable.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            print(f"Error populating Patient Table: {e}")