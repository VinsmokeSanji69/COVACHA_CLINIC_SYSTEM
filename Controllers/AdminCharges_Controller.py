from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from Views.Admin_Charges import Ui_MainWindow as AdminChargesUI
from Controllers.AdminAddLabTest_Controller import AdminAddLabTest
from Models.LaboratoryTest import Laboratory

class AdminChargesController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AdminChargesUI()
        self.ui.setupUi(self)

        # Apply styles to the tables
        self.apply_table_styles()
        self.refresh_tables()

        # Check if the button exists and connect it
        if hasattr(self.ui, 'AddLabTestButton'):
            print("AddLabTestButton exists")
            self.ui.AddLabTestButton.clicked.connect(self.open_add_lab_test_form)
            print("AddLabTestButton connected to open_add_lab_test_form!")
        else:
            print("AddLabTestButton is missing!")

    def refresh_tables(self):
        """Refresh the tables with the latest data."""
        self.populate_laboratory_test_table()

    def populate_laboratory_test_table(self):
        """Populate the LaboratoryTestTable with data from the database."""
        try:
            # Fetch all laboratory tests
            tests = Laboratory.get_all_test()

            # Clear the table before populating it
            self.ui.LaboratoryTestTable.setRowCount(0)

            # Populate the table
            for row, test in enumerate(tests):
                lab_code = test["lab_code"]
                lab_test_name = test["lab_test_name"]  # Already capitalized in the model
                lab_price = test["lab_price"]

                # Insert data into the table
                self.ui.LaboratoryTestTable.insertRow(row)
                self.ui.LaboratoryTestTable.setItem(row, 0, QtWidgets.QTableWidgetItem(lab_code))
                self.ui.LaboratoryTestTable.setItem(row, 1, QtWidgets.QTableWidgetItem(lab_test_name))
                self.ui.LaboratoryTestTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(lab_price)))

            # Resize columns to fit the content
            self.ui.LaboratoryTestTable.resizeColumnsToContents()

        except Exception as e:
            print(f"Error populating LaboratoryTestTable: {e}")

    def apply_table_styles(self):
        """Apply custom styles to the tables and set column headers."""
        # Style for LaboratoryTestTable
        self.ui.LaboratoryTestTable.setStyleSheet("""
              QTableWidget {
                  background-color: #F4F7ED;
                  gridline-color: transparent; 
                  border-radius: 9px;
              }

              QTableWidget::item {
                  color: black;
                  border: none;
              }

              QTableWidget::item:selected {
                  background-color: #CCE3D0;
                  color: #2E6E65;
              }

              QTableWidget QHeaderView::section {
                  background-color: #2E6E65;
                  color: white;
                  padding: 5px;
                  font: 16px "Lexend Medium";
                  border: 2px solid #2E6E65;
                  text-align: left;
              }
          """)

        # Set column headers
        self.ui.LaboratoryTestTable.setHorizontalHeaderLabels(["Test Code", "Laboratory Test", "Charge"])
        self.ui.LaboratoryTestTable.verticalHeader().setVisible(False)
        # Set selection behavior
        self.ui.LaboratoryTestTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def open_add_lab_test_form(self):
        print("Opening Add Lab Test Form...")
        try:
            self.add_lab_test_window = AdminAddLabTest(parent=self)
            self.add_lab_test_window.show()
            print("Add Lab Test Form shown successfully!")
        except Exception as e:
            print(f"Error opening Add Lab Test Form: {e}")