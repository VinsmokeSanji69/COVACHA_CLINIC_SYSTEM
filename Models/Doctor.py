from Models.DB_Connection import DBConnection
class Doctor:
    @staticmethod
    def get_next_doctor_id():
        Conn = DBConnection.get_db_connection()
        try:
            if not Conn:
                return None
            with Conn.cursor() as cursor:
                cursor.execute("SELECT last_value FROM doctor_id_seq;")
                last_value = cursor.fetchone()[0]

                if last_value == 0:
                    cursor.execute("ALTER SEQUENCE doctor_id_seq RESTART WITH 10000;")
                else:
                    next_id = last_value + 1

                Conn.commit()
                return next_id
        except  Exception as e:
            print(f"Error fetching next ID: {e}")
            return None

        finally:
            if Conn:
                Conn.close()

    @staticmethod
    def save_doctor (doctor_data):
        Conn = DBConnection.get_db_connection()
        if not Conn:
            return False
        try:
            with Conn.cursor() as cursor:
                query = """
                    INSERT INTO doctor (
                    doc_password, doc_license, doc_doc_specialty, doc_gender, doc_dob,
                               doc_address, doc_contact, doc_joined_date, doc_lname, doc_fname,
                               doc_mname, doc_email
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(query,(
                    doctor_data["password"],
                    doctor_data["license"],
                    doctor_data["specailty"],
                    doctor_data["gender"],
                    doctor_data["dob"],
                    doctor_data["address"],
                    doctor_data["contact"],
                    doctor_data["joined_date"],
                    doctor_data["lname"],
                    doctor_data["fname"],
                    doctor_data["mname"],
                    doctor_data["email"]
                ))
            Conn.commit()
            return True
        except  Exception as e:
            print(f"Error fetching next ID: {e}")
            return None

        finally:
            if Conn:
                Conn.close()

    @staticmethod
    def get_doctor_by_id(doc_id):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                            SELECT doc_lname, doc_fname, doc_mname
                            FROM doctor
                            WHERE doc_id = %s;
                        """, (doc_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'doc_lname': result[0],
                        'doc_fname': result[1],
                        'doc_mname': result[2],
                    }
                return None
        except Exception as e:
            print(f"Error fetching doctor details: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_doctors():
        """Fetch all doctor records from the database"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Database connection failed!")
            return []

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT doc_id, doc_lname, doc_fname, doctor_mname, doc_specialty 
                    FROM doctor;
                """
                cursor.execute(query)
                rows = cursor.fetchall()

                # Format the results
                doctors = []
                for row in rows:
                    doc_id, last_name, first_name, middle_name, specialty = row

                    # Capitalize the first letter of each word in the name
                    last_name = last_name.title() if last_name else ""
                    first_name = first_name.title() if first_name else ""
                    middle_initial = f"{middle_name[0].upper()}." if middle_name else ""

                    full_name = f"{last_name}, {first_name} {middle_initial}".strip()
                    doctors.append({
                        "id": doc_id,
                        "name": full_name,
                        "specialty": specialty.title() if specialty else ""  # Capitalize specialty
                    })

                print(f"Fetched doctors: {doctors}")
                return doctors

        except Exception as e:
            print(f"Error fetching doctors: {e}")
            return []

        finally:
            if conn:
                conn.close()