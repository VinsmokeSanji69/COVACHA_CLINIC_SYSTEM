from Models.DB_Connection import DBConnection

class Laboratory:
    @staticmethod
    def get_last_lab_id():
        """Fetch the last lab ID from the database."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                query = "SELECT lab_code FROM laboratory_test ORDER BY lab_code DESC LIMIT 1;"
                cursor.execute(query)
                result = cursor.fetchone()

                if result:
                    return result[0]
                return None

        except Exception as e:
            return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_next_lab_id():
        """Generate the next lab ID in the format Lab-XXX."""
        last_lab_id = Laboratory.get_last_lab_id()
        if last_lab_id:
            # Extract the numeric part and increment it
            numeric_part = int(last_lab_id.split("-")[1])
            next_numeric = numeric_part + 1
        else:
            next_numeric = 1

        return f"Lab-{next_numeric:03d}"

    @staticmethod
    def lab_name_exists(lab_name):
        """Check if a lab name already exists (case-insensitive)."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                query = "SELECT COUNT(*) FROM laboratory_test WHERE LOWER(lab_test_name) = %s;"
                cursor.execute(query, (lab_name.lower(),))
                count = cursor.fetchone()[0]
                return count > 0

        except Exception as e:
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def save_lab_test(data):
        """Save the lab test data to the database."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO laboratory_test (lab_code, lab_test_name, lab_price)
                    VALUES (%s, %s, %s);
                """
                cursor.execute(query, (
                    data["lab_code"],
                    data["lab_test_name"],
                    data["lab_price"],
                ))

                conn.commit()
                return True

        except Exception as e:
            conn.rollback()
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_test():
        conn = DBConnection.get_db_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT lab_code, lab_test_name, lab_price
                    FROM laboratory_test;
                """
                cursor.execute(query)
                results = cursor.fetchall()

                # Convert results to a list of dictionaries
                tests = []
                for row in results:
                    lab_code, lab_test_name, lab_price = row
                    tests.append({
                        "lab_code": lab_code,
                        "lab_test_name": lab_test_name.capitalize(),
                        "lab_price": lab_price
                    })

                return tests

        except Exception as e:
            return []

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_test_by_labcode(lab_code):
        conn = DBConnection.get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT lab_test_name, lab_price
                    FROM laboratory_test
                    WHERE lab_code = %s;
                """, (lab_code,))
                result = cursor.fetchone()
                if result:
                    return {'lab_test_name': result[0]}, {'lab_price':result[1]}
                return None
        except Exception as e:
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_lab_code_by_name(lab_test_name):
        """Retrieve the lab_code based on the lab_test_name."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return None
        try:
            # Normalize the input lab_test_name: strip whitespace and convert to lowercase
            lab_test_name = lab_test_name.strip().lower()

            with conn.cursor() as cursor:

                # Use LOWER(TRIM(...)) for case-insensitive and whitespace-insensitive comparison
                cursor.execute("""
                    SELECT lab_code
                    FROM laboratory_test
                    WHERE LOWER(TRIM(lab_test_name)) = %s;
                """, (lab_test_name,))
                result = cursor.fetchone()

                if result:
                    return result[0]
                else:
                    return None
        except Exception as e:
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def count_all_test():
        """Count the total number of lab tests in the database."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cursor:
                query = "SELECT COUNT(*) FROM laboratory_test;"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                return count

        except Exception as e:
            return 0

        finally:
            if conn:
                conn.close()

    @staticmethod
    def lab_code_exists(lab_code):
        """Check if a lab code exists in the laboratory_test table."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                query = "SELECT COUNT(*) FROM laboratory_test WHERE lab_code = %s;"
                cursor.execute(query, (lab_code,))
                count = cursor.fetchone()[0]
                return count > 0

        except Exception as e:
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_lab_test(lab_id):
        conn = None
        try:
            conn = DBConnection.get_db_connection()
            if not conn:
                raise ConnectionError("Database connection failed")

            with conn.cursor() as cursor:
                query = """
                        SELECT lab_code, lab_test_name, lab_price
                        FROM laboratory_test 
                        WHERE lab_code = %s
                    """
                cursor.execute(query, (lab_id,))
                row = cursor.fetchone()

                if row:
                    lab_code, lab_test_name, lab_price = row
                    return {
                        "lab_code": lab_code,
                        "lab_test_name": lab_test_name.capitalize(),
                        "lab_price": float(lab_price) if lab_price is not None else 0.0
                    }
                return None

        except Exception as e:
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_lab_test(lab_test):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                query = """
                                UPDATE laboratory_test 
                                SET lab_test_name = %s , lab_price = %s
                                WHERE lab_code = %s;
                            """
                cursor.execute(query, (
                    lab_test["lab_test_name"],
                    lab_test["lab_price"],
                    lab_test["lab_code"]
                ))

                conn.commit()
                return True

        except Exception as e:
            conn.rollback()
            return False

        finally:
            if conn:
                conn.close()