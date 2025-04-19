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
        self.accepted_checkups = [checkup for checkup in checkups if checkup['chck_status'] != "Completed"]
        self.completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]

        # Populate the AcceptedCheckUp table
        self.populate_accepted_checkups(self.accepted_checkups)

        # Populate the DoneTable
        self.populate_done_table(self.completed_checkups)

        # Connect buttons
        self.ui.DiagnoseButton.clicked.connect(self.open_doctor_lab_result_modal)

        # Search functionality
        self.ui.SearchButton.clicked.connect(self.filter_tables)

        # Initialize SortBy and SortOrder combo boxes
        SortBy = ["Date", "Name", "Diagnosis"]
        SortOrder = ["Ascending", "Descending"]
        self.ui.SortByBox.addItems(SortBy)  # Add items to the SortBy combo box
        self.ui.SortByBox.setCurrentIndex(0)
        self.ui.SortOrderBox.addItems(SortOrder)
        self.ui.SortOrderBox.setCurrentIndex(0)

        # Connect signals for sorting
        self.ui.SortByBox.currentIndexChanged.connect(self.refresh_tables)
        self.ui.SortOrderBox.currentIndexChanged.connect(self.refresh_tables)

    def refresh_tables(self):
        """Refresh the tables based on the current search query and sorting options."""
        try:
            # Get the search query from the QLineEdit
            search_query = self.ui.Search.text().strip().lower()

            # Get the selected sorting options
            sort_by = self.ui.SortByBox.currentText()
            sort_order = self.ui.SortOrderBox.currentText()

            # Determine the key to sort by
            if sort_by == "Date":
                sort_key = "chck_date"
            elif sort_by == "Name":
                sort_key = "full_name"
            elif sort_by == "Diagnosis":
                sort_key = "chck_diagnoses"
            else:
                sort_key = None

            # Determine the sorting order (ascending or descending)
            reverse_order = True if sort_order == "Descending" else False

            # Fetch all check-ups for the doctor
            checkups = CheckUp.get_all_checkups_by_doc_id(self.doc_id)
            if not checkups:
                print("No check-ups found for this doctor.")
                return

            # Separate check-ups based on status
            accepted_checkups = [checkup for checkup in checkups if checkup['chck_status'] != "Completed"]
            completed_checkups = [checkup for checkup in checkups if checkup['chck_status'] == "Completed"]

            # Filter and sort accepted check-ups
            filtered_accepted_checkups = []
            for checkup in accepted_checkups:
                pat_id = checkup['pat_id']
                patient = Patient.get_patient_details(pat_id)
                if not patient:
                    continue

                # Check if the search query matches the patient's last name or first name
                full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                if search_query in full_name.lower():
                    checkup["full_name"] = full_name  # Add full_name to the checkup dictionary
                    filtered_accepted_checkups.append(checkup)

            # Apply sorting to filtered accepted check-ups
            if sort_key:
                if sort_key == "full_name":
                    # Sort by full_name (case-insensitive)
                    filtered_accepted_checkups.sort(key=lambda x: x[sort_key].lower(), reverse=reverse_order)
                else:
                    # Sort by other keys (e.g., chck_date, chck_diagnoses)
                    filtered_accepted_checkups.sort(key=lambda x: x.get(sort_key, ""), reverse=reverse_order)

            # Filter and sort completed check-ups
            filtered_completed_checkups = []
            for checkup in completed_checkups:
                pat_id = checkup['pat_id']
                patient = Patient.get_patient_details(pat_id)
                if not patient:
                    continue

                # Check if the search query matches the patient's last name or first name
                full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                if search_query in full_name.lower():
                    checkup["full_name"] = full_name  # Add full_name to the checkup dictionary
                    filtered_completed_checkups.append(checkup)

            # Apply sorting to filtered completed check-ups
            if sort_key:
                if sort_key == "full_name":
                    # Sort by full_name (case-insensitive)
                    filtered_completed_checkups.sort(key=lambda x: x[sort_key].lower(), reverse=reverse_order)
                else:
                    # Sort by other keys (e.g., chck_date, chck_diagnoses)
                    filtered_completed_checkups.sort(key=lambda x: x.get(sort_key, ""), reverse=reverse_order)

            # Repopulate the tables with filtered and sorted data
            self.populate_accepted_checkups(filtered_accepted_checkups)
            self.populate_done_table(filtered_completed_checkups)

        except Exception as e:
            print(f"Error refreshing tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh tables: {e}")

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
                refresh_callback=self.refresh_tables
            )
            self.doctor_lab_result.show()
            print("DoctorLabResult modal opened successfully!")

        except Exception as e:
            print(f"Error opening DoctorLabResult modal: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open DoctorLabResult modal: {e}")

    def filter_tables(self):
        """Filter rows in both tables based on the search input and sort them."""
        try:
            # Get the search query from the QLineEdit
            search_query = self.ui.Search.text().strip().lower()

            # Get the selected sorting options
            sort_by = self.ui.SortByBox.currentText()
            sort_order = self.ui.SortOrderBox.currentText()

            # Determine the key to sort by
            if sort_by == "Date":
                sort_key = "chck_date"
            elif sort_by == "Name":
                sort_key = "full_name"
            elif sort_by == "Diagnosis":
                sort_key = "chck_diagnoses"
            else:
                sort_key = None

            # Determine the sorting order (ascending or descending)
            reverse_order = True if sort_order == "Descending" else False

            # Filter accepted check-ups
            filtered_accepted_checkups = []
            for checkup in self.accepted_checkups:
                pat_id = checkup['pat_id']
                patient = Patient.get_patient_details(pat_id)
                if not patient:
                    continue

                # Check if the search query matches the patient's last name or first name
                full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                if search_query in full_name.lower():
                    checkup["full_name"] = full_name  # Add full_name to the checkup dictionary
                    filtered_accepted_checkups.append(checkup)

            # Filter completed check-ups
            filtered_completed_checkups = []
            for checkup in self.completed_checkups:
                pat_id = checkup['pat_id']
                patient = Patient.get_patient_details(pat_id)
                if not patient:
                    continue

                # Check if the search query matches the patient's last name or first name
                full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                if search_query in full_name.lower():
                    checkup["full_name"] = full_name  # Add full_name to the checkup dictionary
                    filtered_completed_checkups.append(checkup)

            # Apply sorting if a valid sort key is selected
            if sort_key:
                if sort_key == "full_name":
                    # Sort by full_name (case-insensitive)
                    filtered_accepted_checkups.sort(key=lambda x: x[sort_key].lower(), reverse=reverse_order)
                    filtered_completed_checkups.sort(key=lambda x: x[sort_key].lower(), reverse=reverse_order)
                else:
                    # Sort by other keys (e.g., chck_date, chck_diagnoses)
                    filtered_accepted_checkups.sort(key=lambda x: x.get(sort_key, ""), reverse=reverse_order)
                    filtered_completed_checkups.sort(key=lambda x: x.get(sort_key, ""), reverse=reverse_order)

            # Handle the case where no matching records are found in AcceptedCheckUp
            if not filtered_accepted_checkups:
                self.ui.AcceptedCheckUp.setRowCount(1)  # Add one row for the message
                no_data_item = QtWidgets.QTableWidgetItem("No matching records found")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.AcceptedCheckUp.setItem(0, 0, no_data_item)
                self.ui.AcceptedCheckUp.setSpan(0, 0, 1, self.ui.AcceptedCheckUp.columnCount())
            else:
                # Repopulate the table with filtered data
                self.populate_accepted_checkups(filtered_accepted_checkups)

            # Handle the case where no matching records are found in DoneTable
            if not filtered_completed_checkups:
                self.ui.DoneTable.setRowCount(1)  # Add one row for the message
                no_data_item = QtWidgets.QTableWidgetItem("No matching records found")
                no_data_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.DoneTable.setItem(0, 0, no_data_item)
                self.ui.DoneTable.setSpan(0, 0, 1, self.ui.DoneTable.columnCount())
            else:
                # Repopulate the table with filtered data
                self.populate_done_table(filtered_completed_checkups)

        except Exception as e:
            print(f"Error filtering tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to filter tables: {e}")

    def ViewCheckUp(self):
        """View info of the selected Check up"""

    def ModifyCheckUp(self):
        """modify the selected check up"""

    def DeleteCheckUp(self):
        """delete selected check up in the database"""
