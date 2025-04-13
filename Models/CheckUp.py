from Models.DB_Connection import DBConnection

class CheckUp:
    @staticmethod
    def get_next_sequence_number(checkup_date):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                sequence_name = f"checkup_seq_{checkup_date.replace('-', '')}"
                cursor.execute(f"""
                    CREATE SEQUENCE IF NOT EXISTS {sequence_name}
                    START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 999 CYCLE;
                """)
                cursor.execute(f"SELECT nextval('{sequence_name}');")
                next_val = cursor.fetchone()[0]
                return f"{next_val:03d}"

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

                chck_id = f"{checkup_date}-{sequence_number}"


                query = """
                    INSERT INTO checkup (
                        chck_id, chck_date, chck_status, pat_id,
                        chck_bp, chck_height, chck_weight, chck_temp, staff_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    int(data["staff_id"])
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