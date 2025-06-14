from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget

from Controllers.ClientSocketController import DataRequest
from Views.Doctor_CheckUpList import Ui_Doctor_CheckUpList as DoctorCheckUpListUI
from Controllers.DoctorCheckUpListView_Controller import DoctorCheckUpListView
from Models.CheckUp import CheckUp
from Models.Patient import Patient
import datetime


class DoctorCheckUpList(QWidget):
    def __init__(self, doc_id, records_ui):
        super().__init__()
        self.ui = DoctorCheckUpListUI()
        self.records_ui = records_ui
        self.ui.setupUi(self)

        # Store the doc_id
        self.doc_id = str(doc_id)

        # Fetch all check-ups for the doctor
        self.checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
        # self.checkups = DataRequest.send_command("GET_CHECKUP_BY_DOC_ID", self.doc_id)

        if not self.checkups:
            return

        self.completed_checkups = [checkup for checkup in self.checkups if checkup['chck_status'] == "Completed"]

        # Apply table styles
        self.apply_table_styles()

        self.records_ui.SearchIcon.clicked.connect(self.filter_table)
        self.is_filtering = False

        # Populate the DoneTable
        self.refresh_tables()

        # Connect the ViewPatientButton to the view_detials_checkup method
        self.records_ui.ViewPatientButton.clicked.connect(self.view_patient)

        # ✅ Initialize safe QTimer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_tables)
        self.refresh_timer.start(5000)

    def view_patient_details_ui(self, patient_id):
        try:
            from Controllers.DoctorPatientDetailsView_Controller import DoctorPatientDetailsViewController
            self.doctor_patient_details_controller = DoctorPatientDetailsViewController(patient_id)
            self.doctor_patient_details_controller.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load patient details: {e}")

    def filter_table(self):
        keyword = self.records_ui.Search.text().strip().lower()
        self.is_filtering = True  # ⛔ Pause auto-refresh

        if not keyword:
            self.is_filtering = False
            self.populate_done_table(self.completed_checkups)
            return

        filtered = []

        for checkup in self.completed_checkups:
            pat_id = checkup['pat_id']
            chck_diagnoses = checkup['chck_diagnoses']
            chck_date = checkup['chck_date']

            if isinstance(chck_date, str):
                try:
                    chck_date = datetime.datetime.strptime(chck_date, "%Y-%m-%d")
                except ValueError:
                    pass

            patient = Patient.get_patient_details(pat_id)
            # patient = DataRequest.send_command("GET_PATIENT_DETAILS", pat_id)
            if not patient:
                continue

            full_name = f"{patient['pat_lname']}, {patient['pat_fname']}"
            values_to_check = [
                str(pat_id).lower(),
                full_name.lower(),
                str(chck_diagnoses).lower(),
                chck_date.strftime("%Y-%m-%d").lower() if isinstance(chck_date, datetime.datetime) else str(
                    chck_date).lower()
            ]

            if any(keyword in value for value in values_to_check):
                filtered.append(checkup)

        if not filtered:
            self.show_no_records_message()
        else:
            self.populate_done_table(filtered)

    def show_no_records_message(self):
        self.records_ui.DoneTable.clearContents()
        self.records_ui.DoneTable.setRowCount(1)
        self.records_ui.DoneTable.setColumnCount(4)

        no_data_item = QtWidgets.QTableWidgetItem("No records found.")
        no_data_item.setTextAlignment(Qt.AlignCenter)
        self.records_ui.DoneTable.setItem(0, 0, no_data_item)

        # Merge cells visually (optional)
        self.records_ui.DoneTable.setSpan(0, 0, 1, 4)

    def refresh_tables(self):
        if self.is_filtering:
            return  # ✅ Skip auto-refresh when filtering

        try:
            if not self.records_ui or not hasattr(self.records_ui, 'DoneTable') or not self.records_ui.DoneTable:
                return

            checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
            # checkups = DataRequest.send_command("GET_CHECKUP_BY_DOC_ID", self.doc_id)

            if not checkups:
                return

            self.completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]
            self.records_ui.DoneTable.setRowCount(0)
            self.populate_done_table(self.completed_checkups)

        except RuntimeError as e:
            pass
        except Exception as e:
            pass


    def cleanup(self):
        if hasattr(self, 'refresh_timer') and self.refresh_timer.isActive():
            self.refresh_timer.stop()

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
        self.records_ui.DoneTable.clearContents()
        self.records_ui.DoneTable.setRowCount(0)

        latest_checkups = {}

        for checkup in checkups:
            pat_id = checkup['pat_id']
            chck_date = checkup['chck_date']
            chck_id = checkup['chck_id']

            # Convert date string to datetime object if needed
            if isinstance(chck_date, str):
                chck_date = datetime.datetime.strptime(chck_date, "%Y-%m-%d")

            if pat_id not in latest_checkups:
                latest_checkups[pat_id] = checkup
            else:
                existing = latest_checkups[pat_id]
                existing_date = existing['chck_date']
                existing_id = existing['chck_id']

                # Convert existing date string if needed
                if isinstance(existing_date, str):
                    existing_date = datetime.datetime.strptime(existing_date, "%Y-%m-%d")

                # Compare dates first
                if chck_date > existing_date:
                    latest_checkups[pat_id] = checkup
                elif chck_date == existing_date:
                    # Same date, compare chck_id lexicographically
                    if chck_id > existing_id:
                        latest_checkups[pat_id] = checkup
        for row, checkup in enumerate(latest_checkups.values()):
            pat_id = checkup['pat_id']
            chck_diagnoses = checkup['chck_diagnoses']
            chck_date = checkup['chck_date']

            patient = Patient.get_patient_details(pat_id)
            # patient = DataRequest.send_command("GET_PATIENT_DETAILS", pat_id)

            if not patient:
                continue
            full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
            self.records_ui.DoneTable.insertRow(row)

            # Store full checkup object in UserRole
            id_item = QtWidgets.QTableWidgetItem(str(pat_id))
            id_item.setData(Qt.UserRole, checkup)
            self.records_ui.DoneTable.setItem(row, 0, id_item)

            self.records_ui.DoneTable.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name))
            self.records_ui.DoneTable.setItem(row, 2, QtWidgets.QTableWidgetItem(chck_diagnoses))
            self.records_ui.DoneTable.setItem(row, 3, QtWidgets.QTableWidgetItem(chck_date.strftime("%Y-%m-%d")))



    def view_patient(self):
        try:
            selected_row = self.records_ui.DoneTable.currentRow()
            if selected_row == -1:
                QMessageBox.information(self, "Selection Required", "Please select a row.")
                return

            # Get the QTableWidgetItem from column 0 (which holds pat_id and user data)
            item = self.records_ui.DoneTable.item(selected_row, 0)
            if not item:
                raise ValueError("No data found in selected row.")

            # Retrieve the full checkup object stored in UserRole
            checkup = item.data(Qt.UserRole)
            if not checkup:
                raise ValueError("No checkup data found for selected row.")

            # Extract chck_id and pat_id from the checkup dict
            chck_id = checkup.get('chck_id')
            patient_id = checkup.get('pat_id')

            if not chck_id or not patient_id:
                raise ValueError("Incomplete checkup data: missing chck_id or pat_id")

            # Open the patient details UI with the correct patient ID
            self.view_patient_details_ui(int(patient_id))

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
        except Exception as e:
            error_msg = f"Failed to select patient: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)

    def view_detials_checkup(self):
        """Handle viewing details of the selected check-up."""
        try:
            # Get the currently selected row in the DoneTable
            selected_row = self.records_ui.DoneTable.currentRow()
            if selected_row == -1:  # No row selected
                QMessageBox.warning(self, "Selection Error", "Please select a check-up from the table.")
                return

            # Retrieve the chck_id from the selected row
            chck_id = self.records_ui.DoneTable.item(selected_row, 0).text()

            # Open the DoctorCheckUpListView modal
            self.view_checkUp = DoctorCheckUpListView(checkup_id=chck_id, parent=self)
            self.view_checkUp.show()

        except Exception as e:
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
            pass
