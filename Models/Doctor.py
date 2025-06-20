from datetime import date
from Models.DB_Connection import DBConnection

class Doctor:
    @staticmethod
    def get_next_doctor_id():
        Conn = None
        try:
            Conn = DBConnection.get_db_connection()
            if not Conn:
                return None
            with Conn.cursor() as cursor:
                cursor.execute("SELECT MAX(doc_id) FROM doctor;")
                max_id = cursor.fetchone()[0]

                if max_id is None or max_id < 10000:
                    next_id = 10000
                else:
                    next_id = max_id + 1

                return next_id
        except Exception as e:
            return None
        finally:
            if Conn:
                Conn.close()

    @staticmethod
    def delete(doc_id):
        Conn = None
        try:
            Conn = DBConnection.get_db_connection()
            if not Conn:
                return False

            with Conn.cursor() as cursor:
                cursor.execute("UPDATE doctor SET is_active = False WHERE doc_id = %s", (doc_id,))
                Conn.commit()
                return cursor.rowcount == 1

        except Exception as e:
            if Conn:
                Conn.rollback()
            return False
        finally:
            if Conn:
                Conn.close()

    @staticmethod
    def count_total_patients_by_doctor(doc_id):
        conn = DBConnection.get_db_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(DISTINCT pat_id)
                    FROM checkup
                    WHERE doc_id = %s;
                """, (doc_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            return 0
        finally:
            if conn:
                conn.close()

    @staticmethod
    def save_doctor (doctor_data):
        Conn = DBConnection.get_db_connection()
        if not Conn:
            return False
        try:
            with Conn.cursor() as cursor:
                query = """
                    INSERT INTO doctor (
                    doc_id, doc_password, doc_license, doc_specialty, doc_gender, doc_dob,
                               doc_address, doc_contact, doc_joined_date, doc_lname, doc_fname,
                               doc_mname, doc_email
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(query,(
                    doctor_data["id"],
                    doctor_data["password"],
                    doctor_data["license"],
                    doctor_data["specialty"],
                    doctor_data["gender"],
                    doctor_data["dob"],
                    doctor_data["address"],
                    doctor_data["contact"],
                    doctor_data["date_joined"],
                    doctor_data["last_name"],
                    doctor_data["first_name"],
                    doctor_data["middle_name"],
                    doctor_data["email"]
                ))
            Conn.commit()
            return True
        except  Exception as e:
            return None

        finally:
            if Conn:
                Conn.close()

    @staticmethod
    def update_doctor_rate(doctor_data):
        Conn = DBConnection.get_db_connection()
        if not Conn:
            return False

        try:
            with Conn.cursor() as cursor:
                query = """
                    UPDATE doctor 
                    SET doc_rate = %s
                    WHERE doc_id = %s
                """
                rate = int(doctor_data["new_rate"])
                doc_id = int(doctor_data["doctor_id"])
                cursor.execute(query, (rate, doc_id))

            Conn.commit()
            return True

        except Exception as e:
            return False

        finally:
            if Conn:
                Conn.close()

    @staticmethod
    def update(doctor_data):
        Conn = None
        try:
            Conn = DBConnection.get_db_connection()
            if not Conn:
                raise False

            with Conn.cursor() as cursor:
                query = """
                    UPDATE doctor 
                    SET doc_license = %s, doc_specialty = %s, doc_gender = %s, 
                        doc_dob = %s, doc_address = %s, doc_contact = %s, doc_joined_date = %s, 
                        doc_lname = %s, doc_fname = %s, doc_mname = %s, doc_email = %s
                    WHERE doc_id = %s
                """
                doc_id = int(doctor_data["id"])

                cursor.execute(query, (
                    doctor_data["license"],
                    doctor_data["specialty"],
                    doctor_data["gender"],
                    doctor_data["dob"],
                    doctor_data["address"],
                    doctor_data["contact"],
                    doctor_data["date_joined"],
                    doctor_data["last_name"],
                    doctor_data["first_name"],
                    doctor_data["middle_name"],
                    doctor_data["email"],
                    doc_id
                ))

                affected_rows = cursor.rowcount
                Conn.commit()

                if affected_rows == 1:
                    return True
                return False

        except ValueError as ve:
            return False
        except Exception as e:
            if Conn:
                Conn.rollback()
            return False
        finally:
            if Conn:
                Conn.close()

    @staticmethod
    def get_doctor(doctor_id):
        conn = None
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                raise ConnectionError("Failed to establish database connection")

            with conn.cursor() as cursor:
                query = """
                    SELECT doc_id, doc_lname, doc_fname, doc_mname, doc_specialty, 
                           doc_license, doc_gender, doc_dob, doc_address, 
                           doc_contact, doc_joined_date, doc_email, doc_rate
                    FROM doctor 
                    WHERE doc_id = %s
                """
                cursor.execute(query, (doctor_id,))
                result = cursor.fetchone()

                if not result:
                    return None

                # Unpack the result tuple
                (doc_id, last_name, first_name, middle_name, specialty,
                 license, gender, dob, address, contact,
                 joined_date, email, rate) = result

                # Format names
                last_name = last_name.title() if last_name else ""
                first_name = first_name.title() if first_name else ""
                middle_name = middle_name.title() if middle_name else ""
                # Calculate age if DOB exists
                age = calculate_age(dob)

                return {
                    "id": doc_id,
                    "last_name": last_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "specialty": specialty or "N/A",
                    "license": license or "N/A",
                    "gender": gender or "N/A",
                    "dob": dob if dob else "N/A",
                    "age": age or "N/A",
                    "address": address or "N/A",
                    "contact": contact or "N/A",
                    "email": email or "N/A",
                    "joined_date": joined_date if joined_date else "N/A",
                    "rate": float(rate) if rate is not None else 0.0
                }

        except Exception as e:
            return None

        finally:
            if conn:
                conn.close()


    @staticmethod
    def get_all_doctors():
        conn = None
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                raise ConnectionError("Failed to establish database connection")

            with conn.cursor() as cursor:
                query = """
                    SELECT doc_id, doc_lname, doc_fname, doc_mname, doc_specialty, 
                           doc_license, doc_gender, doc_dob, doc_address, 
                           doc_contact, doc_joined_date, doc_email, doc_rate
                    FROM doctor WHERE is_active = True
                """
                cursor.execute(query)
                rows = cursor.fetchall()

                doctors = []
                for row in rows:
                    (doc_id, last_name, first_name, middle_name, specialty,
                     license, gender, dob, address, contact, joined_date, email, rate) = row

                    # Format names
                    last_name = last_name.title() if last_name else ""
                    first_name = first_name.title() if first_name else ""
                    middle_initial = f"{middle_name[0].upper()}." if middle_name else ""
                    full_name = f"{last_name}, {first_name} {middle_initial}".strip()

                    doctors.append({
                        "id": doc_id,
                        "name": full_name,
                        "specialty": specialty,
                        "license": license or "N/A",
                        "gender": gender or "N/A",
                        "dob": dob.strftime('%Y-%m-%d') if dob else "N/A",
                        "age": calculate_age(dob) if dob else "N/A",
                        "address": address or "N/A",
                        "contact": contact or "N/A",
                        "email": email or "N/A",
                        "joined_date": joined_date.strftime('%B %d, %Y') if joined_date else "N/A",
                        "rate": rate or 0
                    })

                return doctors

        except Exception as e:
            return []

        finally:
            if conn:
                conn.close()


def calculate_age(dob):
    """Calculate age from date of birth"""
    if not dob:
        return None
    today = date.today()
    age = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age