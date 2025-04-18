from Models.DB_Connection import DBConnection

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
                print("Error: Missing required fields in lab_data.")
                return False

            if not conn:
                print("Error: Failed to establish a database connection.")
                return False

            # SQL query to insert data into the prescription table
            query = """
                INSERT INTO prescription (chck_id, pres_medicine, pres_dosage, pres_intake)
                VALUES (%s, %s, %s, %s)
            """
            cursor = conn.cursor()
            cursor.execute(query, (chck_id, med_name, dosage, intake))
            conn.commit()

            print("Prescription added successfully!")
            return True  # Successful insertion

        except Exception as e:
            print(f"Error adding prescription: {e}")
            return False  # Failed insertion

        finally:
            # Ensure the database connection is closed
            if conn:
                conn.close()
                print("Database connection closed.")

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

            print(f"Prescriptions retrieved successfully for chck_id: {chck_id}")
            return prescriptions  # Return the list of prescriptions

        except Exception as e:
            print(f"Error retrieving prescriptions: {e}")
            return []  # Return an empty list in case of an error

        finally:
            # Ensure the database connection is closed
            if conn:
                conn.close()
                print("Database connection closed.")