from datetime import date

from Models.DB_Connection import DBConnection

class Staff:
    @staticmethod
    def get_next_staff_id():
        try:
            Conn = DBConnection.get_db_connection()
            if not Conn:
                return None
            with Conn.cursor() as cursor:
                cursor.execute("SELECT last_value FROM staff_staff_id_seq;")
                last_value = cursor.fetchone()[0]

                if last_value == 0:
                    cursor.execute("ALTER SEQUENCE staff_staff_id_seq RESTART WITH 100001;")
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
    def save_staff (staff_data):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cursor:
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
    def get_staff(staff_id):
        conn = None
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                raise ConnectionError("Failed to establish database connection")

            with conn.cursor() as cursor:
                query = """
                        SELECT staff_id, staff_lname, staff_fname, staff_mname, 
                               staff_gender, staff_dob, staff_address, 
                               staff_contact, staff_joined_date, staff_email
                        FROM staff 
                        WHERE staff_id = %s
                    """
                cursor.execute(query, (staff_id,))
                result = cursor.fetchone()

                if not result:
                    return None

                # Unpack the result tuple
                (staff_id, last_name, first_name, middle_name, gender,
                 dob, address, contact, joined_date, email) = result

                # Format names
                last_name = last_name.title() if last_name else ""
                first_name = first_name.title() if first_name else ""
                middle_name = middle_name.title() if middle_name else ""

                # Calculate age if DOB exists
                age = calculate_age(dob)

                return {
                    "id": staff_id,
                    "last_name": last_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "gender": gender or "N/A",
                    "dob": dob if dob else "N/A",
                    "age": age or "N/A",
                    "address": address or "N/A",
                    "contact": contact or "N/A",
                    "email": email or "N/A",
                    "joined_date": joined_date if joined_date else "N/A"
                }

        except Exception as e:
            print(f"Error fetching staff: {str(e)}")
            return None

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



def calculate_age(dob):
    """Calculate age from date of birth"""
    if not dob:
        return None
    today = date.today()
    age = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age