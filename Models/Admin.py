from PyQt5.QtWidgets import QMessageBox

from Models.DB_Connection import DBConnection

class Admin:
    @staticmethod
    def count_doctor():
        """Count the number of doctors in the database"""
        conn = DBConnection.get_db_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cursor:
                query = "SELECT COUNT(*) FROM doctor;"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                return count

        except Exception as e:
            return 0

        finally:
            if conn:
                conn.close()

    @staticmethod
    def count_staff():
        """Count the number of staff members in the database"""
        conn = DBConnection.get_db_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cursor:
                query = "SELECT COUNT(*) FROM staff;"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                return count

        except Exception as e:
            return 0

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_user(table, user_id):
        conn = None
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                return None

            cursor = conn.cursor()
            if table == "staff":
                cursor.execute(
                    "SELECT staff_id, staff_fname, staff_lname, staff_password FROM staff WHERE staff_id = %s",
                    (user_id,)
                )
            elif table == "doctor":
                cursor.execute(
                    "SELECT doc_id, doc_fname, doc_lname, doc_specialty, doc_password FROM doctor WHERE doc_id = %s",
                    (user_id,)
                )
            return cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(
                None,  # Or pass the appropriate parent window if available
                "Error",
                f"Login error: {str(e)}"
            )
            return None
        finally:
            if conn:
                conn.close()
