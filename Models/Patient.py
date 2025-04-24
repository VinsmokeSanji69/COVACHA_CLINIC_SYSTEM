from Models.DB_Connection import DBConnection
class Patient:
    @staticmethod
    def get_patient_by_name(fname, lname):
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                # Standardize input names to lowercase for comparison
                fname_lower = fname.strip().lower()
                lname_lower = lname.strip().lower()

                # Query the database using LOWER() to standardize case
                query = """
                    SELECT pat_id, pat_lname, pat_fname, pat_mname, pat_gender, pat_dob, pat_address, pat_contact 
                    FROM patient 
                    WHERE LOWER(pat_fname) = %s AND LOWER(pat_lname) = %s;
                """
                cursor.execute(query, (fname_lower, lname_lower))
                result = cursor.fetchone()

                if result:
                    # Map the result to a dictionary for easier access
                    patient_details = {
                        "id": result[0],
                        "first_name": result[1],
                        "last_name": result[2],
                        "middle_name": result[3],
                        "gender": result[4],
                        "dob": result[5],
                        "address": result[6],
                        "contact": result[7]
                    }
                    print(f"Found existing patient: {patient_details}")
                    return patient_details

                # Patient does not exist
                print("Patient does not exist in the database.")
                return None

        except Exception as e:
            print(f"Error fetching patient details: {e}")
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

    @staticmethod
    def get_patient_by_id(pat_id):
        """Fetch patient details by pat_id."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                query = """
                       SELECT pat_lname, pat_fname FROM patient WHERE pat_id = %s
                   """
                cursor.execute(query, (pat_id,))
                result = cursor.fetchone()

                if result:
                    return {"pat_lname": result[0], "pat_fname": result[1]}
                return None

        except Exception as e:
            print(f"Database error while fetching patient details: {e}")
            return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_patient_details(pat_id):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT pat_lname, pat_fname, pat_mname, pat_dob, pat_gender
                    FROM patient
                    WHERE pat_id = %s;
                """, (pat_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'pat_lname': result[0],
                        'pat_fname': result[1],
                        'pat_mname': result[2],
                        'pat_dob': result[3],
                        'pat_gender': result[4]
                    }
                return None
        except Exception as e:
            print(f"Error fetching patient details: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_or_create_patient(data):
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                pat_id = data.get("id")

                if pat_id:
                    # Update existing patient
                    query = """
                        UPDATE patient 
                        SET 
                            pat_mname = %s, pat_gender = %s, pat_dob = %s, pat_address = %s, pat_contact = %s
                        WHERE pat_id = %s
                    """
                    params = (
                        data["middle_name"], data["gender"], data["dob"], data["address"], data["contact"], pat_id
                    )
                else:
                    # Create new patient
                    query = """
                        INSERT INTO patient (pat_lname, pat_fname, pat_mname, pat_gender, pat_dob, pat_address, pat_contact)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING pat_id
                    """
                    params = (
                        data["last_name"],
                        data["first_name"],
                        data["middle_name"],
                        data["gender"],
                        data["dob"],
                        data["address"],
                        data["contact"]
                    )

                # Execute the query
                cursor.execute(query, params)

                if not pat_id:
                    # If creating a new patient, fetch the generated ID
                    pat_id = cursor.fetchone()[0]

                # Commit the transaction
                conn.commit()

                print(f"Patient {'updated' if pat_id else 'created'} successfully. ID: {pat_id}")
                return pat_id

        except Exception as e:
            print(f"Error updating/creating patient: {e}")
            if conn:
                conn.rollback()  # Rollback in case of error
            return None

        finally:
            if conn:
                conn.close()