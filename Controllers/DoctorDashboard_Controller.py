from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox, \
    QWidget, QSizePolicy, QHeaderView, QStackedWidget, QMainWindow
from Controllers.DoctorCheckUpList_Controller import DoctorCheckUpList
from Controllers.DoctorDiagnosis_Controller import DoctorDiagnosis
from Controllers.DoctorPatientList_Controller import DoctorPatientList
from Controllers.DoctorRecords_Controller import DoctorRecords
from Views.Doctor_CheckUpList import Ui_Doctor_CheckUpList
from Views.Doctor_Dashboard import Ui_Doctor_Dashboard
from Models.CheckUp import CheckUp
from Models.Patient import Patient
from Views.Doctor_Records import Ui_Doctor_Records
import datetime



class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Check Up")
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Add message label
        self.message_label = QLabel("Are you sure you want to accept this check up?")
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


class DoctorDashboardController(QMainWindow):
    def __init__(self, doc_id, fname, lname, specialty, login_window=None):
        super().__init__()
        self.login_window = login_window
        self.doc_id = doc_id
        self.setWindowTitle("Doctor Dashboard")

        # Store doctor ID
        self.doc_id = doc_id
        self.fname = fname
        self.lname = lname
        self.specialty = specialty

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout for central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create a shared single navbar
        self.navbar_ui = Ui_Doctor_Dashboard()

        # Create stacked widget for page content (navbar + content area for each page)
        self.page_stack = QStackedWidget()
        self.main_layout.addWidget(self.page_stack)

        # Initialize pages
        self.setup_pages()

        # Setup timer for time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_labels)
        self.timer.start(1000)

        # Connect navigation buttons - will be connected for each page
        self.connect_all_buttons()

        # Start with dashboard view
        self.go_to_dashboard()

        # Responsive table for Record Page
        # DoneTable
        header = self.records_ui.DoneTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.records_ui.DoneTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.records_ui.DoneTable.setWordWrap(True)
        self.records_ui.DoneTable.resizeRowsToContents()

        # AcceptedCheckUp
        header = self.checkup_ui.AcceptedCheckUp.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.checkup_ui.AcceptedCheckUp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.checkup_ui.AcceptedCheckUp.setWordWrap(True)
        self.checkup_ui.AcceptedCheckUp.resizeRowsToContents()

        # Responsive table for Dashboard Page
        # PatientDetails (?)
        header = self.dashboard_ui.PatientDetails.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.dashboard_ui.PatientDetails.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dashboard_ui.PatientDetails.setWordWrap(True)
        self.dashboard_ui.PatientDetails.resizeRowsToContents()

        # Responsive table for Dashboard Page
        # PatientDetails (?)
        header = self.checkup_ui.DoneTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.checkup_ui.DoneTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.checkup_ui.DoneTable.setWordWrap(True)
        self.checkup_ui.DoneTable.resizeRowsToContents()

        # self.checkups = []
        self.doctor_records = DoctorRecords(self.doc_id, self.checkup_ui)
        self.doctor_checkup = DoctorCheckUpList(self.doc_id, self.records_ui)

        self.load_pending_checkups()

        self.apply_table_styles(self.dashboard_ui.PatientDetails)
        self.apply_table_styles(self.checkup_ui.AcceptedCheckUp)
        self.apply_table_styles(self.checkup_ui.DoneTable)
        self.apply_table_styles(self.records_ui.DoneTable)


    def setup_pages(self):
        """Set up complete pages with navbar and content"""
        # Dashboard page
        self.dashboard_page = QWidget()
        self.dashboard_ui = Ui_Doctor_Dashboard()
        self.dashboard_ui.setupUi(self.dashboard_page)
        self.page_stack.addWidget(self.dashboard_page)

        # Records page
        self.records_page = QWidget()
        self.records_ui = Ui_Doctor_CheckUpList()
        self.records_ui.setupUi(self.records_page)
        self.page_stack.addWidget(self.records_page)

        # Patient page
        self.checkup_page = QWidget()
        self.checkup_ui = Ui_Doctor_Records()
        self.checkup_ui.setupUi(self.checkup_page)
        self.page_stack.addWidget(self.checkup_page)

    def connect_all_buttons(self):
        """Connect navigation buttons for all pages"""
        # Connect dashboard page buttons
        self.dashboard_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.dashboard_ui.CheckUpButton.clicked.connect(self.go_to_checkup_list)
        self.dashboard_ui.RecordsButton.clicked.connect(self.go_to_records)
        self.dashboard_ui.LogOutButton.clicked.connect(self.logout)

        # Connect checkup  page buttons
        self.checkup_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.checkup_ui.CheckUpButton.clicked.connect(self.go_to_checkup_list)
        self.checkup_ui.RecordsButton.clicked.connect(self.go_to_records)
        self.checkup_ui.LogOutButton.clicked.connect(self.logout)

        # Connect records page buttons
        self.records_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.records_ui.CheckUpButton.clicked.connect(self.go_to_checkup_list)
        self.records_ui.RecordsButton.clicked.connect(self.go_to_records)
        self.records_ui.LogOutButton.clicked.connect(self.logout)

        # Connect the Accept Check-Up button
        self.dashboard_ui.AcceptCheckUp.clicked.connect(self.accept_checkup)

    @pyqtSlot()
    def logout(self):
        """Return to the login screen and clear the credentials."""
        try:
            # 1. Cleanup and delete all tracked windows
            for window in getattr(self, "open_windows", []):
                if window and hasattr(window, "deleteLater"):
                    window.deleteLater()

            # 2. Close and delete dashboard safely
            if hasattr(self, "cleanup"):
                self.cleanup()
            if hasattr(self, "hide"):
                self.hide()  # Prefer hide over deleteLater to avoid premature deletion
            if hasattr(self, "deleteLater"):
                QTimer.singleShot(0, self.deleteLater)  # Delay deletion

            # 3. Show login window
            if hasattr(self, "login_window") and self.login_window:
                self.login_window.ui.UserIDInput.clear()
                self.login_window.ui.PasswordInput.clear()
                self.login_window.show()
            else:
                from Views.LogIn import LogInWindow
                from Controllers.LogIn_Controller import LoginController

                login_window = LogInWindow()
                LoginController(login_window)
                login_window.show()

        except Exception as e:
            print("Logout error:", e)

    @pyqtSlot()
    def go_to_dashboard(self):
        """Switch to the dashboard page"""
        print("Navigating to Dashboard")
        self.page_stack.setCurrentWidget(self.dashboard_page)
        self.load_pending_checkups()
        self.update_time_labels()

    @pyqtSlot()
    def go_to_checkup_list(self):
        """Switch to the transactions page"""
        print("Navigating to Check Up List")
        self.page_stack.setCurrentWidget(self.checkup_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_records(self):
        """Switch to the records page"""
        print("Navigating to Records")
        self.page_stack.setCurrentWidget(self.records_page)
        self.update_time_labels()

    def ViewPatient(self):
        print("PatientButton clicked!")
        try:
            # Instantiate and show the AdminStaffsController window
            self.patient_controller = DoctorPatientList(self.doc_id)
            self.patient_controller.show()
            self.hide()
        except Exception as e:
            print(f"Error loading tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")

    def update_time_labels(self):
        """Update time labels on the current page"""
        now = datetime.datetime.now()
        current_page_index = self.page_stack.currentIndex()

        if current_page_index == 0:  # Dashboard
            ui = self.dashboard_ui
        elif current_page_index == 1:  # Transactions
            ui = self.checkup_ui
        elif current_page_index == 2:
            ui = self.records_ui
        else:
            return

        if hasattr(ui, 'Time'):
            ui.Time.setText(now.strftime("%I:%M %p"))
        if hasattr(ui, 'Day'):
            ui.Day.setText(now.strftime("%A"))
        if hasattr(ui, 'Month'):
            ui.Month.setText(f"{now.strftime('%B')} {now.day}, {now.year}")

    def ViewRecord(self):
        print("RecordButton clicked!")
        try:
            # Instantiate and show the AdminStaffsController window
            self.record_controller = DoctorRecords(self.doc_id)
            self.record_controller.show()
            self.hide()
        except Exception as e:
            print(f"Error loading tables: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load tables: {e}")

    def apply_table_styles(self, table_widget):
        # Ensure horizontal headers are visible
        table_widget.horizontalHeader().setVisible(True)

        # Align headers to the left
        table_widget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # Hide the vertical header (row index)
        table_widget.verticalHeader().setVisible(False)

        # Set selection behavior
        table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def load_pending_checkups(self):
        """Fetch and display pending check-ups in the PatientDetails table."""
        try:
            # Fetch pending check-ups from the database
            pending_checkups = CheckUp.get_pending_checkups()

            # self.checkups = CheckUp.get_all_checkups()

            # Clear the table before populating it
            self.dashboard_ui.PatientDetails.setRowCount(0)

            # Check if there are no pending check-ups
            if not pending_checkups:
                print("No pending check-ups found.")

                # Add a single row with the message "No Patient Yet"
                self.dashboard_ui.PatientDetails.insertRow(0)
                no_data_item = QTableWidgetItem("No Patient Yet")
                self.dashboard_ui.PatientDetails.setItem(0, 0, no_data_item)

                # Span the message across all columns
                column_count = self.dashboard_ui.PatientDetails.columnCount()
                self.dashboard_ui.PatientDetails.setSpan(0, 0, 1, column_count)
                return

            # Populate the table with pending check-ups
            for row, checkup in enumerate(pending_checkups):
                pat_id = checkup["pat_id"]
                chck_id = checkup["chck_id"]

                # Fetch patient details
                patient = Patient.get_patient_by_id(pat_id)
                if not patient:
                    print(f"No patient found for pat_id={pat_id}")
                    continue

                # Extract patient name and capitalize the first letter of each word
                full_name = f"{patient['last_name'].capitalize()}, {patient['first_name'].capitalize()}"

                # Insert data into the table in the new column order (Check Up ID, Patient ID, Name)
                self.dashboard_ui.PatientDetails.insertRow(row)
                self.dashboard_ui.PatientDetails.setItem(row, 0, QTableWidgetItem(chck_id))  # Check Up ID
                self.dashboard_ui.PatientDetails.setItem(row, 1, QTableWidgetItem(str(pat_id)))  # Patient ID
                self.dashboard_ui.PatientDetails.setItem(row, 2, QTableWidgetItem(full_name))  # Name

            # Resize columns to fit the content
            self.dashboard_ui.PatientDetails.resizeColumnsToContents()

            # Optionally, set minimum widths for specific columns
            self.dashboard_ui.PatientDetails.setColumnWidth(0, 150)
            self.dashboard_ui.PatientDetails.setColumnWidth(1, 150)
            self.dashboard_ui.PatientDetails.setColumnWidth(2, 200)

        except Exception as e:
            print(f"Error loading pending check-ups: {e}")

    def accept_checkup(self):
        """Handle the Accept Check-Up button click."""
        try:
            # Get the selected row from the check-up table
            selected_row = self.dashboard_ui.PatientDetails.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a check-up to accept.")
                return

            print("Selected row:", selected_row)

            # Get the check-up ID from the selected row
            chck_id = self.dashboard_ui.PatientDetails.item(selected_row, 0).text()  # Assuming chck_id is in column 0
            print(f"Selected check-up ID: {chck_id}")

            # Show confirmation dialog
            confirmation_dialog = ConfirmationDialog(self)
            if confirmation_dialog.exec_() == QDialog.Rejected:
                print("Check-up acceptance cancelled by the user.")
                return

            print("User confirmed acceptance.")

            # Update the check-up status to "On going" and assign the doctor's ID
            success = CheckUp.update_doc_id(chck_id, self.doc_id)
            if success:
                print("Check-up accepted successfully in the database.")
                # Open the DoctorDiagnosis form with the selected CheckUp ID
                self.open_diagnosis_form(chck_id)
            else:
                print("Failed to update check-up in the database.")
                QMessageBox.critical(self, "Error", "Failed to accept check-up. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def open_diagnosis_form(self, checkup_id):
        print(f"Opening DoctorDiagnosis form with CheckUp ID: {checkup_id}")
        try:
            diagnosis_window = DoctorDiagnosis(
                checkup_id=checkup_id,
                doc_id=self.doc_id,
                parent=self
            )
            diagnosis_window.show()
            print("DoctorDiagnosis window opened successfully.")
        except Exception as e:
            print(f"Error opening DoctorDiagnosis window: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open diagnosis form: {e}")

