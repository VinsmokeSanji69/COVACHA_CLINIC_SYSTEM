from Models.DB_Connection import DBConnection

class Admin:
    @staticmethod
    def count_doctor():
        """Count the number of doctors in the database"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Database connection failed!")
            return 0

        try:
            with conn.cursor() as cursor:
                query = "SELECT COUNT(*) FROM doctor;"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"Number of doctors: {count}")
                return count

        except Exception as e:
            print(f"Error counting doctors: {e}")
            return 0

        finally:
            if conn:
                conn.close()

    @staticmethod
    def count_staff():
        """Count the number of staff members in the database"""
        conn = DBConnection.get_db_connection()
        if not conn:
            print("Database connection failed!")
            return 0

        try:
            with conn.cursor() as cursor:
                query = "SELECT COUNT(*) FROM staff;"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"Number of staff members: {count}")
                return count

        except Exception as e:
            print(f"Error counting staff: {e}")
            return 0

        finally:
            if conn:
                conn.close()