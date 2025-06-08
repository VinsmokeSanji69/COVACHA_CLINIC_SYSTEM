from Models.DB_Connection import DBConnection
from psycopg2 import extras

class Prescription:
    @staticmethod
    def add_presscription(chck_id, lab_data):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None
        try:
            # Extract data from the dictionary
            med_name = lab_data.get("med_name")
            dosage = lab_data.get("dosage")
            intake = lab_data.get("intake")

            # Validate required fields
            if not all([med_name, dosage, intake]):
                return False

            if not conn:
                return False

            # SQL query to insert data into the prescription table
            query = """
                INSERT INTO prescription (chck_id, pres_medicine, pres_dosage, pres_intake)
                VALUES (%s, %s, %s, %s)
            """
            cursor = conn.cursor()
            cursor.execute(query, (chck_id, med_name, dosage, intake))
            conn.commit()

            return True  # Successful insertion

        except Exception as e:
            return False  # Failed insertion

        finally:
            # Ensure the database connection is closed
            if conn:
                conn.close()

    @staticmethod
    def display_prescription(chck_id):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None
        try:
            # SQL query to fetch prescriptions for the given check-up ID
            query = """
                SELECT pres_medicine, pres_dosage, pres_intake
                FROM prescription
                WHERE chck_id = %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (chck_id,))
            rows = cursor.fetchall()

            # Convert the result into a list of dictionaries
            prescriptions = []
            for row in rows:
                prescription = {
                    "pres_medicine": row[0],
                    "pres_dosage": row[1],
                    "pres_intake": row[2]
                }
                prescriptions.append(prescription)

            return prescriptions  # Return the list of prescriptions

        except Exception as e:
            return []

        finally:
            # Ensure the database connection is closed
            if conn:
                conn.close()

    @staticmethod
    def get_prescription_by_details(chck_id, med_name, dosage, intake):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None
        try:
            query = """
                SELECT id AS pres_id, pres_medicine, pres_dosage, pres_intake 
                FROM prescription
                WHERE chck_id = %s AND pres_medicine = %s AND pres_dosage = %s AND pres_intake = %s
                LIMIT 1
            """
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(query, (chck_id, med_name, dosage, intake))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_prescription_by_id(pres_id, med_name, dosage, intake):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False
        try:
            query = """
                    UPDATE prescription 
                    SET pres_medicine = %s, pres_dosage = %s, pres_intake = %s
                    WHERE id = %s
                """
            cursor = conn.cursor()
            cursor.execute(query, (med_name, dosage, intake, pres_id))
            conn.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conn:
                conn.close()


    @staticmethod
    def delete_prescription_by_id(pres_id):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False
        try:
            query = "DELETE FROM prescription WHERE id = %s"
            cursor = conn.cursor()
            cursor.execute(query, (pres_id,))
            conn.commit()
            return True
        except Exception as e:
            return False
        finally:
            if conn:
                conn.close()