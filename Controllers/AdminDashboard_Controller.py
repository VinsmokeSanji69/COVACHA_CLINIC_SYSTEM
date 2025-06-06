from itertools import count

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QHeaderView, QSizePolicy

from Controllers.AdminPatients_Controller import AdminPatientsController
from Controllers.AdminStaffs_Controller import AdminStaffsController
from Controllers.AdminTransaction_Controller import AdminTransactionsController
from Controllers.AdminCharges_Controller import AdminChargesController  # Add this import
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
    def __init__(self):
        super().__init__()
        self.ui = AdminDashboardUI()
        self.ui.setupUi(self)

        print("Admin Dashboard UI initialized!")

        self.load_counts()

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

        # Setup timer for time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_labels)
        self.timer.start(1000)

        # Connect navigation buttons - will be connected for each page
        self.connect_all_buttons()

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

        # Connect staff page buttons
        self.staff_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.staff_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.staff_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.staff_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.staff_ui.ChargesButton.clicked.connect(self.go_to_charges)

        # Connect records page buttons
        self.records_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.records_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.records_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.records_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.records_ui.ChargesButton.clicked.connect(self.go_to_charges)

        # Connect transactions page buttons
        self.transactions_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.transactions_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.transactions_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.transactions_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.transactions_ui.ChargesButton.clicked.connect(self.go_to_charges)

        # Connect charges page buttons
        self.charges_ui.DashboardButton.clicked.connect(self.go_to_dashboard)
        self.charges_ui.StaffsButton.clicked.connect(self.go_to_staffs)
        self.charges_ui.PatientsButton.clicked.connect(self.go_to_records)
        self.charges_ui.TransactionsButton.clicked.connect(self.go_to_transactions)
        self.charges_ui.ChargesButton.clicked.connect(self.go_to_charges)

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

    def load_counts(self):
        try:
            # Count doctors
            doctor_count = Admin.count_doctor()
            self.ui.TotalDoctor.setText(str(doctor_count))

            # Count staff
            staff_count = Admin.count_staff()
            self.ui.TotalStaff.setText(str(staff_count))

            print(f"Loaded counts - Doctors: {doctor_count}, Staff: {staff_count}")

        except Exception as e:
            print(f"Dashboard: {e}")

    def initialize_overview(self):
        try:
            patients = Patient.get_all_patients()
            staffs = Staff.get_all_staff()
            doctors = Doctor.get_all_doctors()
            checkups = CheckUp.get_all_checkups()

            patient_count = count(patients)
            staff_count = count(staffs)
            doctor_count = count(doctors)
            self.ui.TotalPatient.setText(str(patient_count))
            self.ui.TotalDoctor.setText(str(staff_count))
            self.ui.TotalStaff.setText(str(doctor_count))

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
            self.ui.ChildPercent.setText(f"{child * 100 // total}%")
            self.ui.AdultPercent.setText(f"{adult * 100 // total}%")
            self.ui.ElderlyPercent.setText(f"{elderly * 100 // total}%")

            diagnosis_1 = count()
            diagnosis_percent_1 = count()
            diagnosis_2 = count()
            diagnosis_percent_2 = count()
            self.ui.Diagnosis1.setText(str(diagnosis_1))
            self.ui.Diagnose1Percent.setText(str(diagnosis_percent_1))
            self.ui.Diagnosis2.setText(str(diagnosis_2))
            self.ui.DiagnosePercent2.setText(str(diagnosis_percent_2))


            self.ui.DocName1.setText(str())
            self.ui.Specialty1.setText(str())
            self.ui.PatCount1.setText(str())
            self.ui.PatPercent1.setText(str())

            self.ui.DocName2.setText(str())
            self.ui.Specialty2.setText(str())
            self.ui.PatCount2.setText(str())
            self.ui.PatPercent2.setText(str())

            self.ui.DocName3.setText(str())
            self.ui.Specialty3.setText(str())
            self.ui.PatCount3.setText(str())
            self.ui.PatPercent3.setText(str())

        except Exception as e:
            print(f"Dashboard: {e}")