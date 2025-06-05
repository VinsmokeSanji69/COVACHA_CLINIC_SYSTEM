from datetime import date
from Models.DB_Connection import DBConnection

class Patient:
    @staticmethod
    def get_patient_by_name(fname, lname):
        """Get patient details by first and last name (case-insensitive)"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                fname_lower = fname.strip().lower()
                lname_lower = lname.strip().lower()

                query = """
                    SELECT pat_id, pat_lname, pat_fname, pat_mname, pat_gender, 
                           pat_dob, pat_address, pat_contact 
                    FROM patient 
                    WHERE LOWER(pat_fname) = %s AND LOWER(pat_lname) = %s;
                """
                cursor.execute(query, (fname_lower, lname_lower))
                result = cursor.fetchone()

                if result:
                    return {
                        "id": result[0],
                        "last_name": result[1],
                        "first_name": result[2],
                        "middle_name": result[3],
                        "gender": result[4],
                        "dob": result[5],
                        "address": result[6],
                        "contact": result[7]
                    }
                return None

        except Exception as e:
            print(f"Error fetching patient by name: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_patients():
        """Get all patients with formatted information"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT pat_id, pat_lname, pat_fname, pat_mname,
                           pat_address, pat_contact, pat_dob, pat_gender
                    FROM patient;
                """
                cursor.execute(query)
                rows = cursor.fetchall()

                patients = []
                for row in rows:
                    (pat_id, pat_lname, pat_fname, pat_mname,
                     pat_address, pat_contact, pat_dob, pat_gender) = row

                    last_name = pat_lname.title() if pat_lname else ""
                    first_name = pat_fname.title() if pat_fname else ""
                    middle_initial = f"{pat_mname[0].upper()}." if pat_mname else ""
                    full_name = f"{last_name}, {first_name} {middle_initial}".strip()

                    patients.append({
                        "id": pat_id,
                        "name": full_name,
                        "gender": pat_gender or "N/A",
                        "dob": pat_dob.strftime('%Y-%m-%d') if pat_dob else "N/A",
                        "age": Patient._calculate_age(pat_dob) if pat_dob else "N/A",
                        "address": pat_address or "N/A",
                        "contact": pat_contact or "N/A"
                    })

                return patients

        except Exception as e:
            print(f"Error fetching all patients: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_patient_by_id(pat_id):
        """Get patient details by patient ID"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT pat_id, pat_lname, pat_fname, pat_mname,
                           pat_address, pat_contact, pat_dob, pat_gender
                    FROM patient 
                    WHERE pat_id = %s;
                """
                cursor.execute(query, (pat_id,))
                result = cursor.fetchone()

                if not result:
                    return None

                (id, last_name, first_name, middle_name,
                 address, contact, dob, gender) = result

                last_name = last_name.title() if last_name else ""
                first_name = first_name.title() if first_name else ""
                middle_name = middle_name.title() if middle_name else ""

                return {
                    "id": pat_id,
                    "last_name": last_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "gender": gender or "N/A",
                    "dob": dob.strftime('%Y-%m-%d') if dob else "N/A",
                    "age": Patient._calculate_age(dob) if dob else "N/A",
                    "address": address or "N/A",
                    "contact": contact or "N/A"
                }

        except Exception as e:
            print(f"Error fetching patient by ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def create_new_patient(data):
        """Create a new patient record"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nextval('patient_id_seq');")
                new_pat_id = cursor.fetchone()[0]

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
                return new_pat_id

        except Exception as e:
            print(f"Error creating new patient: {e}")
            conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_or_create_patient(data):
        """Update existing patient or create new if ID not provided"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                pat_id = data.get("id")

                if pat_id:
                    query = """
                        UPDATE patient 
                        SET pat_mname = %s, pat_gender = %s, pat_dob = %s, 
                            pat_address = %s, pat_contact = %s
                        WHERE pat_id = %s
                    """
                    params = (
                        data["middle_name"], data["gender"], data["dob"],
                        data["address"], data["contact"], pat_id
                    )
                else:
                    query = """
                        INSERT INTO patient (
                            pat_lname, pat_fname, pat_mname, pat_gender, 
                            pat_dob, pat_address, pat_contact
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
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

                cursor.execute(query, params)

                if not pat_id:
                    pat_id = cursor.fetchone()[0]

                conn.commit()
                return pat_id

        except Exception as e:
            print(f"Error updating/creating patient: {e}")
            if conn:
                conn.rollback()
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
                        SELECT pat_lname, pat_fname, pat_mname, pat_dob, pat_gender, pat_contact
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
                        'pat_gender': result[4],
                        'pat_contact': result[5]
                    }
                return None
        except Exception as e:
            print(f"Error fetching patient details: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _calculate_age(dob):
        """Internal method to calculate age from date of birth"""
        if not dob:
            return None
        today = date.today()
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1
        return age