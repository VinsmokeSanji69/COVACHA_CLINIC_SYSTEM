from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Views.Doctor_Records import Ui_MainWindow as DoctorRecordsUI
from Controllers.DoctorLabResult_Controller import DoctorLabResult
from Models.CheckUp import CheckUp
from Models.Patient import Patient


class DoctorRecords(QMainWindow):
    def __init__(self, doc_id):
        super().__init__()
        self.ui = DoctorRecordsUI()
        self.ui.setupUi(self)

        # Store the doc_id
        self.doc_id = str(doc_id)
        print(f"Doctor Records UI initialized with doc_id: {self.doc_id}")

        # Apply table styles
        self.apply_table_styles()

        # Fetch all check-ups for the doctor
        checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
        if not checkups:
            print("No check-ups found for this doctor.")
            return

        # Separate check-ups based on status
        accepted_checkups = [checkup for checkup in checkups if checkup['chck_status'] != "Completed"]
        completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]

        # Populate the AcceptedCheckUp table
        self.populate_accepted_checkups(accepted_checkups)

        # Populate the DoneTable
        self.populate_done_table(completed_checkups)

        # Connect buttons
        self.ui.DiagnoseButton.clicked.connect(self.open_doctor_lab_result_modal)

    def refresh_tables(self):
        checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
        if not checkups:
            print("No check-ups found for this doctor.")
            return

        accepted_checkups = [checkup for checkup in checkups if checkup['chck_status'] != "Completed"]
        completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]

        self.populate_accepted_checkups(accepted_checkups)
        self.populate_done_table(completed_checkups)

    def apply_table_styles(self):
        """Apply custom styles to the tables."""
        self.ui.AcceptedCheckUp.setStyleSheet("""
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
        self.ui.AcceptedCheckUp.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.AcceptedCheckUp.horizontalHeader().setVisible(True)
        self.ui.AcceptedCheckUp.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.ui.AcceptedCheckUp.verticalHeader().setVisible(False)

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

    def populate_accepted_checkups(self, checkups):
        # Clear existing rows
        self.ui.AcceptedCheckUp.clearContents()
        self.ui.AcceptedCheckUp.setRowCount(0)

        # Populate the table
        for row, checkup in enumerate(checkups):
            pat_id = checkup['pat_id']
            chck_id = checkup['chck_id']
            chck_status = checkup['chck_status']
            chckup_type = checkup['chckup_type']

            # Fetch patient details
            patient = Patient.get_patient_details(pat_id)
            if not patient:
                print(f"No patient found for pat_id={pat_id}")
                continue

            # Extract and format patient name
            full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"

            # Add row to the table
            self.ui.AcceptedCheckUp.insertRow(row)
            self.ui.AcceptedCheckUp.setItem(row, 0, QtWidgets.QTableWidgetItem(str(chck_id)))
            self.ui.AcceptedCheckUp.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name))
            self.ui.AcceptedCheckUp.setItem(row, 2, QtWidgets.QTableWidgetItem(chck_status))
            self.ui.AcceptedCheckUp.setItem(row, 3, QtWidgets.QTableWidgetItem(chckup_type))

    def populate_done_table(self, checkups):
        # Clear existing rows
        self.ui.DoneTable.clearContents()
        self.ui.DoneTable.setRowCount(0)

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
            self.ui.DoneTable.insertRow(row)
            self.ui.DoneTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(chck_id)))
            self.ui.DoneTable.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name))
            self.ui.DoneTable.setItem(row, 2, QtWidgets.QTableWidgetItem(chck_diagnoses))
            self.ui.DoneTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(chck_date)))

    def open_doctor_lab_result_modal(self):
        """Open the DoctorLabResult modal."""
        try:
            # Get the selected row
            selected_row = self.ui.AcceptedCheckUp.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a row to diagnose.")
                return

            # Retrieve the chck_id from the selected row
            chck_id_item = self.ui.AcceptedCheckUp.item(selected_row, 0)
            if not chck_id_item:
                QMessageBox.critical(self, "Error", "Failed to retrieve check-up ID.")
                return

            chck_id = chck_id_item.text()

            # Open the modal with the selected chck_id
            print(f"Attempting to open DoctorLabResult modal with chck_id: {chck_id}")
            self.doctor_lab_result = DoctorLabResult(
                checkup_id=chck_id,
                parent=self,
                refresh_callback=self.display_check_up
            )
            self.doctor_lab_result.show()
            print("DoctorLabResult modal opened successfully!")

        except Exception as e:
            print(f"Error opening DoctorLabResult modal: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open DoctorLabResult modal: {e}")

    def ViewCheckUp(self):
        """View info of the selected Check up"""

    def ModifyCheckUp(self):
        """modify the selected check up"""

    def DeleteCheckUp(self):
        """delete selected check up in the database"""
