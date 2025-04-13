from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from Views.Staff_Dashboard import Ui_MainWindow as StaffDashboardUi
from Controllers.StaffAddCheckUp_Controller import StaffAddCheckUp
import datetime

class StaffDashboardController(QMainWindow):
    def __init__(self, staff_id = None):
        super().__init__()
        self.ui = StaffDashboardUi()
        self.ui.setupUi(self)

        # Initialize dynamic date and time labels
        self.update_time_labels()

        # Set up a timer to update the labels every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_labels)
        self.timer.start(1000)

        # Store the staff ID
        self.staff_id = staff_id
        print(f"StaffDashboard initialized for staff ID: {self.staff_id}")

        print("StaffDashboard UI initialized!")

        # Connect buttons
        if hasattr(self.ui, 'AddCheckUp'):
            print("AddCheckUp exists")
            self.ui.AddCheckUp.clicked.connect(self.open_checkup_user_form)
            print("AddCheckUp connected to open_add_user_form!")
        else:
            print("AddUserButton is missing!")

    def open_checkup_user_form(self):
        print("Opening Add Check-Up Form...")
        try:
            # Pass the staff_id to the AddCheckUp form
            self.add_checkup_window = StaffAddCheckUp(parent=self, staff_id=self.staff_id)
            self.add_checkup_window.show()
            print("Add Check-Up Form shown successfully!")
        except Exception as e:
            print(f"Error opening Add Check-Up Form: {e}")

    def setup_ui(self):
        self.update_time_labels()

    def update_time_labels(self):
        """Update the Time, Day, and Month labels with current values."""
        now = datetime.datetime.now()

        # Format time (e.g., 03:45 PM)
        time_format = now.strftime("%I:%M %p")
        self.ui.Time.setText(time_format)

        # Format day (e.g., Sunday)
        day_format = now.strftime("%A")
        self.ui.Day.setText(day_format)

        # Format month and year (e.g., October 15, 2023)
        month_year_format = f"{now.strftime('%B')} {now.day}, {now.year}"
        self.ui.Month.setText(month_year_format)

        # Force refresh the UI
        self.repaint()

