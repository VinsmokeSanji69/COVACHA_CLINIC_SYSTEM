from Models.DB_Connection import DBConnection
class Patient:
    @staticmethod
    def get_patient_id(fname, lname):
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                query = "SELECT pat_id FROM patient WHERE pat_fname = %s AND pat_lname = %s;"
                cursor.execute(query, (fname, lname))
                result = cursor.fetchone()

                if result:
                    print(f"Found existing patient ID: {result[0]}")
                    return result[0]

                # Patient does not exist
                print("Patient does not exist in the database.")
                return None

        except Exception as e:
            print(f"Error fetching patient ID: {e}")
            return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def create_new_patient(data):
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                # Generate a new patient ID using the sequence
                cursor.execute("SELECT nextval('patient_id_seq');")
                new_pat_id = cursor.fetchone()[0]
                print(f"Generated new patient ID: {new_pat_id}")

                # Insert the new patient record into the database
                query = """
                    INSERT INTO patient (
                        pat_id, pat_lname, pat_fname, pat_mname,
                        pat_address, pat_contact, pat_dob, pat_gender
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    new_pat_id,
                    data["last_name"],
                    data["first_name"],
                    data["middle_name"],
                    data["address"],
                    data["contact"],
                    data["dob"],
                    data["gender"]
                ))

                conn.commit()
                print("New patient data saved successfully.")
                return new_pat_id

        except Exception as e:
            print(f"Database error while creating new patient: {e}")
            conn.rollback()
            return None

        finally:
            if conn:
                conn.close()
