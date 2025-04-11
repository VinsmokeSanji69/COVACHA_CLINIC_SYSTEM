from Models.DB_Connection import DBConnection


class StaffAccount:
    @staticmethod
    def get_next_id(staff_type):
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                return None

            with conn.cursor() as cursor:
                if staff_type == "Doctor":
                    # Query the next value from the doctor_id_seq sequence
                    cursor.execute("SELECT last_value FROM doctor_id_seq;")
                elif staff_type == "Staff":
                    # Query the next value from the staff_staff_id_seq sequence
                    cursor.execute("SELECT last_value FROM staff_staff_id_seq;")
                else:
                    return None

                last_value = cursor.fetchone()[0]
                print(f"Last value for {staff_type}_id_seq: {last_value}")

                # Handle uninitialized sequence
                if last_value == 0:
                    if staff_type == "Doctor":
                        cursor.execute("ALTER SEQUENCE doctor_id_seq RESTART WITH 1;")
                    elif staff_type == "Staff":
                        cursor.execute("ALTER SEQUENCE staff_staff_id_seq RESTART WITH 1;")
                    next_id = 1
                else:
                    next_id = last_value + 1

                conn.commit()
                return next_id

        except Exception as e:
            print(f"Error fetching next ID: {e}")
            return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def save_to_database(staff_data):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                if staff_data["staff_type"] == "Doctor":
                    # Insert into doctor table (exclude doc_id since it's SERIAL)
                    query = """
                           INSERT INTO doctor (
                               doc_password, doc_license, doc_specialty, doc_gender, doc_dob,
                               doc_address, doc_contact, doc_joined_date, doc_lname, doc_fname,
                               doctor_mname, doctor_email
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       """
                    cursor.execute(query, (
                        staff_data["password"],
                        staff_data["license"],
                        staff_data["specialty"],
                        staff_data["gender"],
                        staff_data["dob"],
                        staff_data["address"],
                        staff_data["contact"],
                        staff_data["date_joined"],
                        staff_data["last_name"],
                        staff_data["first_name"],
                        staff_data["middle_name"],
                        staff_data["email"]
                    ))
                elif staff_data["staff_type"] == "Staff":
                    # Insert into staff table (exclude staff_id since it's SERIAL)
                    query = """
                           INSERT INTO staff (
                               staff_password, staff_lname, staff_fname, staff_joined_date,
                               staff_gender, staff_dob, staff_address, staff_contact, staff_mname, staff_email
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       """
                    cursor.execute(query, (
                        staff_data["password"],
                        staff_data["last_name"],
                        staff_data["first_name"],
                        staff_data["date_joined"],
                        staff_data["gender"],
                        staff_data["dob"],
                        staff_data["address"],
                        staff_data["contact"],
                        staff_data["middle_name"],
                        staff_data["email"]
                    ))

                conn.commit()
                return True

        except Exception as e:
            print(f"Database error: {e}")
            return False

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

    @staticmethod
    def get_all_staff():
        """Fetch all staff records from the database"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Database connection failed!")
            return []

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT staff_id, staff_lname, staff_fname, staff_mname 
                    FROM staff
                    WHERE staff_id != 100000;
                """
                cursor.execute(query)
                rows = cursor.fetchall()

                # Format the results
                staff_list = []
                for row in rows:
                    staff_id, last_name, first_name, middle_name = row

                    # Capitalize the first letter of each word in the name
                    last_name = last_name.title() if last_name else ""
                    first_name = first_name.title() if first_name else ""
                    middle_initial = f"{middle_name[0].upper()}." if middle_name else ""

                    full_name = f"{last_name}, {first_name} {middle_initial}".strip()
                    staff_list.append({
                        "id": staff_id,
                        "name": full_name
                    })

                print(f"Fetched staff: {staff_list}")
                return staff_list

        except Exception as e:
            print(f"Error fetching staff: {e}")
            return []

        finally:
            if conn:
                conn.close()