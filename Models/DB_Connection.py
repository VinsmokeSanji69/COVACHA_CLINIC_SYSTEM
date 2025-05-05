import psycopg2
from PyQt5.QtWidgets import QMessageBox

class DBConnection:
    @staticmethod
    def get_db_connection():
        try:
            conn = psycopg2.connect(
                dbname="ClinicSystemF",
                user="postgres",
                password="12345",
                host="localhost",
                port="5432"
            )
            return conn
        except psycopg2.OperationalError as e:
            QMessageBox.critical(
                None, 
                "Database Error", 
                f"Could not connect to database:\n{str(e)}"
            )
            return None
        except Exception as e:
            QMessageBox.critical(
                None, 
                "Unexpected Error", 
                f"Database connection error:\n{str(e)}"
            )
            return None

    @staticmethod
    def test_connection():
        """Test if database is reachable"""
        conn = DBConnection.get_db_connection()
        if conn:
            conn.close()
            return True
        return False