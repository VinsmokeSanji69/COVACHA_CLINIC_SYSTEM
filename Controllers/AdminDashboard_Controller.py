from itertools import count

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QHeaderView, QSizePolicy

from Controllers.AdminPatients_Controller import AdminPatientsController
from Controllers.AdminStaffs_Controller import AdminStaffsController
from Controllers.AdminTransaction_Controller import AdminTransactionsController
from Controllers.AdminCharges_Controller import AdminChargesController  # Add this import
from Controllers.AdminPatientDetails_Controller import AdminPatientDetailsController

from Models.CheckUp import CheckUp
from Models.Doctor import Doctor
from Models.Patient import Patient
from Models.Staff import Staff
from Views.Admin_Charges import Ui_Admin_Charges
from Views.Admin_Dashboard import Ui_Admin_Dashboard as AdminDashboardUI, Ui_Admin_Dashboard
from Models.Admin import Admin
import datetime
from Views.Admin_Patients import Ui_Admin_Patients
from Views.Admin_Staffs import Ui_Admin_Staff
from Views.Admin_Transactions import Ui_Admin_Transactions

class AdminDashboardController(QMainWindow):
    def __init__(self, login_window=None):
        super().__init__()
        self.ui = AdminDashboardUI()
        self.login_window = login_window
        self.ui.setupUi(self)

        print("Admin Dashboard UI initialized!")


        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout for central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create a shared single navbar
        self.navbar_ui = Ui_Admin_Dashboard()

        # Create stacked widget for page content (navbar + content area for each page)
        self.page_stack = QStackedWidget()
        self.main_layout.addWidget(self.page_stack)

        # Initialize pages
        self.setup_pages()
        self.initialize_overview()

        # Setup timer for time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_labels)
        self.timer.start(1000)

        # Connect navigation buttons - will be connected for each page
        self.connect_all_buttons()
        self.initialize_overview()
        # Initialize controller instances AFTER setting up pages
        self.admin_staff = AdminStaffsController(self.staff_ui)
        self.admin_records = AdminPatientsController(self.records_ui)
        self.admin_transactions = AdminTransactionsController(self.transactions_ui)
        self.admin_charges = AdminChargesController(self.charges_ui)  # Add this line

        # Start with dashboard view
        self.go_to_dashboard()

        # Responsive for Admin Staffs View Page
        header = self.staff_ui.DoctorTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.staff_ui.DoctorTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.staff_ui.DoctorTable.setWordWrap(True)
        self.staff_ui.DoctorTable.resizeRowsToContents()

        header = self.staff_ui.StaffTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.staff_ui.StaffTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.staff_ui.StaffTable.setWordWrap(True)
        self.staff_ui.StaffTable.resizeRowsToContents()

        # Responsive for Admin Records
        header = self.records_ui.PatientTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.records_ui.PatientTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.records_ui.PatientTable.setWordWrap(True)
        self.records_ui.PatientTable.resizeRowsToContents()

        # Responsive for Admin Transactions
        header = self.transactions_ui.TransactionTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.transactions_ui.TransactionTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.transactions_ui.TransactionTable.setWordWrap(True)
        self.transactions_ui.TransactionTable.resizeRowsToContents()

        # Responsive for Admin Charges
        header = self.charges_ui.DoctorTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.charges_ui.DoctorTable.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.charges_ui.DoctorTable.setWordWrap(True)
        self.charges_ui.DoctorTable.resizeRowsToContents()

        header = self.charges_ui.LaboratoryTestTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.charges_ui.LaboratoryTestTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.charges_ui.LaboratoryTestTable.setWordWrap(True)
        self.charges_ui.LaboratoryTestTable.resizeRowsToContents()

    def setup_pages(self):
        """Set up complete pages with navbar and content"""
        # Dashboard page
        self.dashboard_page = QWidget()
        self.dashboard_ui = Ui_Admin_Dashboard()
        self.dashboard_ui.setupUi(self.dashboard_page)
        self.page_stack.addWidget(self.dashboard_page)

        # Staff page
        self.staff_page = QWidget()
        self.staff_ui = Ui_Admin_Staff()
        self.staff_ui.setupUi(self.staff_page)
        self.page_stack.addWidget(self.staff_page)

        # Records page - Patients
        self.records_page = QWidget()
        self.records_ui = Ui_Admin_Patients()
        self.records_ui.setupUi(self.records_page)
        self.page_stack.addWidget(self.records_page)

        # Transactions page
        self.transactions_page = QWidget()
        self.transactions_ui = Ui_Admin_Transactions()
        self.transactions_ui.setupUi(self.transactions_page)
        self.page_stack.addWidget(self.transactions_page)

        # Charges page
        self.charges_page = QWidget()
        self.charges_ui = Ui_Admin_Charges()
        self.charges_ui.setupUi(self.charges_page)
        self.page_stack.addWidget(self.charges_page)

    def connect_all_buttons(self):
        """Connect navigation buttons for all pages"""
        # Connect dashboard page buttons
        self.dashboard_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.dashboard_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.dashboard_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.dashboard_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.dashboard_ui.ChargesButton.clicked.connect(self.go_to_charges)
        self.dashboard_ui.LogOutButton.clicked.connect(self.logout)


        # Connect staff page buttons
        self.staff_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.staff_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.staff_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.staff_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.staff_ui.ChargesButton.clicked.connect(self.go_to_charges)
        self.staff_ui.LogOutButton.clicked.connect(self.logout)

        # Connect records page buttons
        self.records_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.records_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.records_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.records_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.records_ui.ChargesButton.clicked.connect(self.go_to_charges)
        self.records_ui.LogOutButton.clicked.connect(self.logout)


        # Connect transactions page buttons
        self.transactions_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.transactions_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.transactions_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.transactions_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.transactions_ui.ChargesButton.clicked.connect(self.go_to_charges)
        self.transactions_ui.LogOutButton.clicked.connect(self.logout)


        # Connect charges page buttons
        self.charges_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.charges_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.charges_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.charges_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.charges_ui.ChargesButton.clicked.connect(self.go_to_charges)
        self.charges_ui.LogOutButton.clicked.connect(self.logout)


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
        self.page_stack.setCurrentWidget(self.dashboard_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_staffs(self):
        self.page_stack.setCurrentWidget(self.staff_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_records(self):
        self.page_stack.setCurrentWidget(self.records_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_transactions(self):
        self.page_stack.setCurrentWidget(self.transactions_page)
        self.update_time_labels()

    @pyqtSlot()
    def go_to_charges(self):
        self.page_stack.setCurrentWidget(self.charges_page)
        self.update_time_labels()
        # Refresh the charges tables when navigating to charges page
        if hasattr(self, 'admin_charges'):
            self.admin_charges.refresh_tables()

    def update_time_labels(self):
        now = datetime.datetime.now()
        current_page_index = self.page_stack.currentIndex()

        if current_page_index == 0:  # Dashboard
            ui = self.dashboard_ui
        elif current_page_index == 1:  # Staff
            ui = self.staff_ui
        elif current_page_index == 2:   # Records - Patients
            ui = self.records_ui
        elif current_page_index == 3:   # Transactions
            ui = self.transactions_ui
        elif current_page_index == 4:   # Charges
            ui = self.charges_ui
        else:
            return

        if hasattr(ui, 'Time'):
            ui.Time.setText(now.strftime("%I:%M %p"))
        if hasattr(ui, 'Day'):
            ui.Day.setText(now.strftime("%A"))
        if hasattr(ui, 'Month'):
            ui.Month.setText(f"{now.strftime('%B')} {now.day}, {now.year}")

    def initialize_overview(self):
        try:
            patients = Patient.get_all_patients()
            staffs = Staff.get_all_staff()
            doctors = Doctor.get_all_doctors()
            checkups = CheckUp.get_all_checkups()

            patient_count = len(patients)
            staff_count = len(staffs)
            doctor_count = len(doctors)

            print(patient_count, staff_count, doctor_count)

            self.dashboard_ui.TotalPatient.setText(str(patient_count))
            self.dashboard_ui.TotalDoctor.setText(str(doctor_count))
            self.dashboard_ui.TotalStaff.setText(str(staff_count))

            if not patients:
                return

            child = adult = elderly = 0

            for p in patients:
                age = p.get('age', 0)
                if age < 18:
                    child += 1
                elif age < 60:
                    adult += 1
                else:
                    elderly += 1

            total = len(patients)
            self.dashboard_ui.ChildPercent.setText(f"{child * 100 // total}%")
            self.dashboard_ui.AdultPercent.setText(f"{adult * 100 // total}%")
            self.dashboard_ui.ElderlyPercent.setText(f"{elderly * 100 // total}%")

            # TOP 3 DIAGNOSES LOGIC
            diagnosis_counts = {}

            # Count occurrences of each diagnosis
            for checkup in checkups:
                diagnosis = checkup.get('chck_diagnoses')
                if diagnosis:  # Only count if diagnosis exists
                    diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1

            # Sort diagnoses by count (descending) and get top 3
            # Get top 3 diagnoses (sorted by frequency)
            top_diagnoses = sorted(
                [(d, c) for d, c in diagnosis_counts.items() if d],  # Filter out empty diagnoses
                key=lambda x: x[1],
                reverse=True
            )[:3]

            # Initialize all values as empty strings
            diagnosis_data = [
                {"name": " ", "percent": " "},  # Diagnosis 1
                {"name": " ", "percent": " "},  # Diagnosis 2
                {"name": " ", "percent": " "}  # Diagnosis 3
            ]

            # Fill available diagnoses
            for i, (diagnosis, count) in enumerate(top_diagnoses):
                if i < 3:  # Only fill up to 3 slots
                    diagnosis_data[i] = {
                        "name": diagnosis if diagnosis else " ",
                        "percent": f"{round((count / len(checkups)) * 100)}%" if len(checkups) > 0 else " "
                    }

            # Update UI
            self.dashboard_ui.Diagnosis1.setText(diagnosis_data[0]["name"])
            self.dashboard_ui.Diagnosis1Percent.setText(diagnosis_data[0]["percent"])
            self.dashboard_ui.Diagnosis2.setText(diagnosis_data[1]["name"])
            self.dashboard_ui.Diagnosis2Percent.setText(diagnosis_data[1]["percent"])
            self.dashboard_ui.Diagnosis3.setText(diagnosis_data[2]["name"])
            self.dashboard_ui.Diagnosis3Percent.setText(diagnosis_data[2]["percent"])

            # Count patients per doctor
            doctor_patient_counts = {}
            for checkup in checkups:
                doc_id = checkup.get('doc_id')
                if doc_id:
                    doctor_patient_counts[doc_id] = doctor_patient_counts.get(doc_id, 0) + 1

            # Create list of (doctor, patient_count) tuples
            doctor_stats = []
            for doctor in doctors:
                doc_id = doctor.get('id')
                if doc_id in doctor_patient_counts:
                    doctor_stats.append({
                        'doctor': doctor,
                        'patient_count': doctor_patient_counts[doc_id]
                    })

            # Sort by patient count (descending) and get top 3
            top_doctors = sorted(doctor_stats,
                                 key=lambda x: x['patient_count'],
                                 reverse=True)[:3]

            # Prepare UI data (3 slots)
            doctor_ui_data = [
                {'name': " ", 'specialty': " ", 'count': " ", 'percent': " "},
                {'name': " ", 'specialty': " ", 'count': " ", 'percent': " "},
                {'name': " ", 'specialty': " ", 'count': " ", 'percent': " "}
            ]

            # Calculate total patients for percentage
            total_patients = sum(doctor_patient_counts.values()) or 1  # Avoid division by zero

            # Fill available data
            for i, doc_data in enumerate(top_doctors):
                if i >= 3:
                    break

                doctor = doc_data['doctor']
                count = doc_data['patient_count']

                # Extract last name (from "Last, First M")
                full_name = doctor.get('name', ', ')
                last_name = full_name.split(',')[0].strip()

                doctor_ui_data[i] = {
                    'name': "Dr. "+last_name,
                    'specialty': doctor.get('specialty', ' '),
                    'count': str(count),
                    'percent': f"{round((count / total_patients) * 100)}%"
                }

            # Update UI - Doctor 1
            self.dashboard_ui.DoctorName1.setText(doctor_ui_data[0]['name'])
            self.dashboard_ui.Specialty1.setText(doctor_ui_data[0]['specialty'])
            self.dashboard_ui.PatientCount1.setText(doctor_ui_data[0]['count'])
            self.dashboard_ui.PatientPercentage1.setText(doctor_ui_data[0]['percent'])

            # Update UI - Doctor 2
            self.dashboard_ui.DoctorName2.setText(doctor_ui_data[1]['name'])
            self.dashboard_ui.Specialty2.setText(doctor_ui_data[1]['specialty'])
            self.dashboard_ui.PatientCount2.setText(doctor_ui_data[1]['count'])
            self.dashboard_ui.PatientPercentage2.setText(doctor_ui_data[1]['percent'])

            # Update UI - Doctor 3
            self.dashboard_ui.DoctorName3.setText(doctor_ui_data[2]['name'])
            self.dashboard_ui.Specialty3.setText(doctor_ui_data[2]['specialty'])
            self.dashboard_ui.PatientCount3.setText(doctor_ui_data[2]['count'])
            self.dashboard_ui.PatientPercentage3.setText(doctor_ui_data[2]['percent'])

            print("Overviews Initialized")
        except Exception as e:
            print(f"Dashboard: {e}")