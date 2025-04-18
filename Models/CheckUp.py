from Models.DB_Connection import DBConnection
from Models.LaboratoryTest import Laboratory

class CheckUp:
    @staticmethod
    def get_next_sequence_number(checkup_date):
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Database connection is None. Check your connection settings.")
            return None

        try:
            with conn.cursor() as cursor:
                # Enable autocommit
                conn.autocommit = True

                # Debug: Log the INSERT query
                print(f"Executing INSERT query for date: {checkup_date}")
                cursor.execute("""
                    INSERT INTO checkup_sequence (checkup_date, last_sequence)
                    VALUES (%s, 0)
                    ON CONFLICT (checkup_date) DO NOTHING;
                """, (checkup_date,))

                # Debug: Log the UPDATE query
                print(f"Executing UPDATE query for date: {checkup_date}")
                cursor.execute("""
                    UPDATE checkup_sequence
                    SET last_sequence = last_sequence + 1
                    WHERE checkup_date = %s
                    RETURNING last_sequence;
                """, (checkup_date,))
                next_val = cursor.fetchone()[0]
                print(f"Fetched next sequence: {next_val}")

                # Format the sequence number (e.g., "001", "002", etc.)
                formatted_sequence = f"{next_val:03d}"
                chck_id = f"{checkup_date}-{formatted_sequence}"

                # Debug: Log the generated chck_id
                print(f"Generated chck_id: {chck_id}")

                # Return the formatted chck_id
                return chck_id

        except Exception as e:
            print(f"Error fetching sequence number: {e}")
            return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def save_checkup(data):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                print(f"Inserting check-up data: {data}")

                checkup_date = data["date_joined"].replace("-", "")
                sequence_number = CheckUp.get_next_sequence_number(checkup_date)
                if not sequence_number:
                    raise ValueError("Failed to generate sequence number.")

                chck_id = f"{sequence_number}"


                query = """
                    INSERT INTO checkup (
                        chck_id, chck_date, chck_status, pat_id,
                        chck_bp, chck_height, chck_weight, chck_temp, staff_id, chckup_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    chck_id,
                    data["date_joined"],
                    "Pending",
                    int(data["id"]),
                    data["bloodpressure"],
                    data["height"],
                    data["weight"],
                    data["temperature"],
                    int(data["staff_id"]),
                    data["checkup_type"]
                ))

                conn.commit()
                return True

        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_pending_checkups():
        """Fetch all pending check-ups from the database."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                query = """
                        SELECT chck_id, pat_id, chckup_type 
                        FROM checkup 
                        WHERE chck_status = %s
                    """
                cursor.execute(query, ("Pending",))
                results = cursor.fetchall()

                # Convert results to a list of dictionaries
                checkups = [{"chck_id": row[0], "pat_id": row[1], "chckup_type": row[2]} for row in results]
                return checkups

        except Exception as e:
            print(f"Database error while fetching pending check-ups: {e}")
            return []

        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_checkup_status(chck_id, new_status):
        """Update the status of a check-up."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                query = """
                        UPDATE checkup SET chck_status = %s WHERE chck_id = %s
                    """
                cursor.execute(query, (new_status, chck_id))
                conn.commit()
                return True

        except Exception as e:
            print(f"Database error while updating check-up status: {e}")
            conn.rollback()
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_checkup_details(checkup_id):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT chck_bp, chck_height, chck_weight, chck_temp, pat_id,
                     chck_status, doc_id, chckup_type, chck_date, chck_diagnoses
                    FROM checkup
                    WHERE chck_id = %s;
                """, (checkup_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'chck_bp': result[0],
                        'chck_height': result[1],
                        'chck_weight': result[2],
                        'chck_temp': result[3],
                        'pat_id': result[4],
                        'chck_status': result[5],
                        'doc_id': result[6],
                        'chckup_type': result[7],
                        'chck_date': result[8],
                        'chck_diagnoses': result[9]
                    }
                return None
        except Exception as e:
            print(f"Error fetching check-up details: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_checkups_by_doc_id(doc_id):
        """Fetch all check-ups for the given doctor ID."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT chck_id, chck_status, chckup_type, pat_id, chck_diagnoses, chck_date
                    FROM checkup
                    WHERE doc_id = %s;
                """, (doc_id,))
                results = cursor.fetchall()

                # Convert results to a list of dictionaries
                checkups = []
                for row in results:
                    checkups.append({
                        'chck_id': row[0],
                        'chck_status': row[1],
                        'chckup_type': row[2],
                        'pat_id': row[3],
                        'chck_diagnoses':row[4],
                        'chck_date': row[5]
                    })
                return checkups

        except Exception as e:
            print(f"Error fetching check-ups by doc_id: {e}")
            return []

        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_doc_id(chck_id, doc_id):
        """Update the doc_id and set the status to 'On going' for the given check-up."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                query = """
                       UPDATE checkup
                       SET doc_id = %s, chck_status = 'On going'
                       WHERE chck_id = %s;
                   """
                cursor.execute(query, (doc_id, chck_id))
                conn.commit()
                return True

        except Exception as e:
            print(f"Database error while updating doc_id: {e}")
            conn.rollback()
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_lab_codes(checkup_id, lab_codes):
        """Update the lab_codes field in the checkup table."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                if lab_codes:
                    # Update the lab_code column only if lab_codes is not empty
                    cursor.execute("""
                        UPDATE checkup_lab_tests
                        SET lab_code = %s
                        WHERE chck_id = %s;
                    """, (lab_codes, checkup_id))
                else:
                    # Skip updating the lab_code column if lab_codes is empty
                    cursor.execute("""
                        UPDATE checkup_lab_tests
                        SET lab_code = lab_code  -- No change
                        WHERE chck_id = %s;
                    """, (checkup_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Database error while updating lab codes: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_test_names_by_chckid(chck_id):
        conn = DBConnection.get_db_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT lab_code, lab_attachment
                    FROM checkup_lab_tests
                    WHERE chck_id = %s;
                """, (chck_id,))
                result = cursor.fetchall()
                return [
                    {'lab_code': row[0], 'lab_attachment': row[1]}
                    for row in result
                ]
        except Exception as e:
            print(f"Error fetching laboratory test details: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_lab_attachment(chck_id, lab_code, file_path):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cursor:
                # Ensure file_path is a string
                if not isinstance(file_path, str):
                    raise ValueError("File path must be a string.")

                cursor.execute("""
                    UPDATE checkup_lab_tests
                    SET lab_attachment = %s
                    WHERE lab_code = %s AND chck_id = %s;
                """, (file_path, lab_code, chck_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating lab attachment: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_lab_attachment(chck_id, lab_code):
        """Retrieve the file path (lab_attachment) for a specific check-up ID and lab code."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT lab_attachment
                    FROM checkup_lab_tests
                    WHERE chck_id = %s AND lab_code = %s;
                """, (chck_id, lab_code))
                result = cursor.fetchone()

                if result:
                    # Convert memoryview to string if necessary
                    lab_attachment = result[0]
                    if isinstance(lab_attachment, memoryview):
                        lab_attachment = lab_attachment.tobytes().decode('utf-8')
                    return lab_attachment
                return None
        except Exception as e:
            print(f"Error fetching lab attachment: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def add_diagnosis_notes(chck_id, chck_diagnoses, chck_notes=None):
        conn = None
        try:
            # Establish a database connection
            conn = DBConnection.get_db_connection()
            if not conn:
                raise ConnectionError("Failed to establish a database connection.")

            # Capitalize the first letter of each word in the diagnosis text
            chck_diagnoses = chck_diagnoses.strip().title()

            # SQL query to update diagnosis notes
            query = """
                    UPDATE checkup
                    SET chck_diagnoses = %s, chck_notes = %s
                    WHERE chck_id = %s
                """
            cursor = conn.cursor()
            cursor.execute(query, (chck_diagnoses, chck_notes, chck_id))
            conn.commit()

            print(f"Diagnosis notes added successfully for chck_id: {chck_id}")
            return True

        except Exception as e:
            print(f"Error adding diagnosis notes: {e}")
            if conn:
                conn.rollback()  # Roll back in case of failure
            return False

        finally:
            if conn:
                conn.close()
                print("Database connection closed.")

    @staticmethod
    def change_status_completed(chck_id):
        conn = None
        try:
            # Establish a database connection
            conn = DBConnection.get_db_connection()
            if not conn:
                raise ConnectionError("Failed to establish a database connection.")

            # SQL query to update the status
            query = """
                    UPDATE checkup
                    SET chck_status = 'Completed'
                    WHERE chck_id = %s
                """
            cursor = conn.cursor()
            cursor.execute(query, (chck_id,))
            conn.commit()

            print(f"Check-up status updated to 'Completed' for chck_id: {chck_id}")
            return True

        except Exception as e:
            print(f"Error changing check-up status to Completed: {e}")
            if conn:
                conn.rollback()  # Roll back in case of failure
            return False

        finally:
            if conn:
                conn.close()
                print("Database connection closed.")