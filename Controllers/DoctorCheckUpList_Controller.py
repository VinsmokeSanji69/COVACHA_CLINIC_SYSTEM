from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Views.Doctor_CheckUpList import Ui_MainWindow as DoctorCheckUpListUI
from Controllers.DoctorCheckUpListView_Controller import DoctorCheckUpListView
from Models.CheckUp import CheckUp
from Models.Patient import Patient

class DoctorCheckUpList(QMainWindow):
    def __init__(self, doc_id):
        super().__init__()
        self.ui = DoctorCheckUpListUI()
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
        self.ui.ViewPatientButton.clicked.connect(self.view_detials_checkup)

    def refresh_tables(self):
        """Reload data into the tables"""
        try:
            self.populate_done_table(self.completed_checkups)  # Pass the completed_checkups
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
            full_name = f"{patient['last_name'].capitalize()}, {patient['first_name'].capitalize()}"

            # Add row to the table
            self.ui.DoneTable.insertRow(row)
            self.ui.DoneTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(chck_id)))
            self.ui.DoneTable.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name))
            self.ui.DoneTable.setItem(row, 2, QtWidgets.QTableWidgetItem(chck_diagnoses))
            self.ui.DoneTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(chck_date)))

    def view_detials_checkup(self):
        """Handle viewing details of the selected check-up."""
        try:
            # Get the currently selected row in the DoneTable
            selected_row = self.ui.DoneTable.currentRow()
            if selected_row == -1:  # No row selected
                QMessageBox.warning(self, "Selection Error", "Please select a check-up from the table.")
                return

            # Retrieve the chck_id from the selected row
            chck_id = self.ui.DoneTable.item(selected_row, 0).text()  # Column 0 contains chck_id
            print(f"Selected Check-Up ID: {chck_id}")

            # Open the DoctorCheckUpListView modal
            self.view_checkUp = DoctorCheckUpListView(checkup_id=chck_id, parent=self)
            self.view_checkUp.show()

        except Exception as e:
            print(f"Error viewing check-up details: {e}")
            QMessageBox.critical(self, "Error", f"Failed to view check-up details: {e}")