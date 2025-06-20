import psycopg2
from PyQt5.QtWidgets import QMessageBox

class DBConnection:
    @staticmethod
    def get_db_connection():
        try:
            conn = psycopg2.connect(
                dbname="ClinicSystem",
                user="postgres",
                password="admin123",
                host="localhost",
                port="5432"
            )
            return conn

        except psycopg2.OperationalError as e:
            error_msg = ""
            if "does not exist" in str(e):
                error_msg = (
                    "Database 'ClinicSystem' not found.\n\n"
                )
            elif "connection refused" in str(e).lower():
                error_msg = (
                    "Cannot connect to PostgreSQL server.\n\n"
                )
            else:
                error_msg = f"Database connection failed:\n{str(e)}"

            QMessageBox.critical(
                None,
                "Database Connection Error",
                error_msg
            )
            return None

        except psycopg2.Error as e:
            QMessageBox.critical(
                None,
                "Database Error",
                f"A database error occurred:\n{str(e)}"
            )
            return None

        except Exception as e:
            QMessageBox.critical(
                None,
                "System Error",
                f"An unexpected error occurred:\n{str(e)}"
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