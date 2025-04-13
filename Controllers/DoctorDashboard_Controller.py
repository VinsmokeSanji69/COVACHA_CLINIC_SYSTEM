from PyQt5.QtWidgets import QMainWindow
from Views.Doctor_Dashboard import Ui_MainWindow as DoctorDashboardUi

class DoctorDashboardController(QMainWindow):
    def __init__(self, fname, lname, specialty):
        super().__init__()
        self.ui = DoctorDashboardUi()
        self.ui.setupUi(self)

        # Set the doctor's name and specialty in the UI
        self.ui.User.setText(f"{lname}, {fname}")
        self.ui.UserSpecialty.setText(specialty)

        print("Doctor Dashboard UI initialized!")