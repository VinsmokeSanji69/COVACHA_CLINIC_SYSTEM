from PyQt5.QtWidgets import QMainWindow
from Views.Admin_Charges import Ui_MainWindow  as AdminChargesUI

class AdminChargesController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AdminChargesUI()
        self.ui.setupUi(self)