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