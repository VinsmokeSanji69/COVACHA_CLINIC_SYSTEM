from idlelib.pyparse import trans
from typing import final

from Models.DB_Connection import DBConnection


class Transaction():
    @staticmethod
    def add_transaction(chck_id, trans_data):
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                # Check if transaction already exists
                check_query = "SELECT tran_status FROM transaction WHERE chck_id = %s"
                cursor.execute(check_query, (chck_id,))
                existing = cursor.fetchone()

                if existing:
                    existing_status = existing[0]
                    # If transaction exists and is Partial, allow update to Completed
                    if existing_status == "Partial" and trans_data.get("status") == "Completed":
                        return Transaction.update_transaction_status(chck_id, trans_data)
                    else:
                        return False

                # Insert new transaction
                insert_query = """
                    INSERT INTO transaction (
                        chck_id, tran_discount, tran_base_charge, 
                        tran_lab_charge, tran_status
                    ) VALUES (%s, %s, %s, %s, %s)
                """

                cursor.execute(insert_query, (
                    chck_id,
                    trans_data.get("discount", 0),
                    trans_data.get("base_charge", 0),
                    trans_data.get("lab_charge", 0),
                    trans_data.get("status", "Completed")
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
    def update_transaction(chck_id, trans_data):
        """Legacy method - use update_transaction_status instead"""
        return Transaction.update_transaction_status(chck_id, trans_data)

    @staticmethod
    def update_transaction_status(chck_id, trans_data):
        """Update an existing transaction's status and data"""
        conn = DBConnection.get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                # Update the transaction
                query = """
                    UPDATE transaction
                    SET tran_discount = %s,
                        tran_base_charge = %s,
                        tran_lab_charge = %s,
                        tran_status = %s
                    WHERE chck_id = %s
                """
                cursor.execute(query, (
                    trans_data.get("discount", 0),
                    trans_data.get("base_charge", 0),
                    trans_data.get("lab_charge", 0),
                    trans_data.get("status", "Completed"),
                    chck_id
                ))

                # Check if any row was updated
                if cursor.rowcount == 0:
                    return False

                conn.commit()
                return True

        except Exception as e:
            conn.rollback()
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_transaction_by_chckid1(chck_id):
        """Fetch complete transaction details for a given chck_id."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return {}  # Return empty dict instead of None

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT tran_discount, tran_base_charge, tran_lab_charge, tran_status
                    FROM transaction 
                    WHERE chck_id = %s;
                """
                cursor.execute(query, (chck_id,))
                result = cursor.fetchone()

                if result:
                    return {
                        'tran_discount': float(result[0]) if result[0] is not None else 0.0,
                        'tran_base_charge': float(result[1]) if result[1] is not None else 0.0,
                        'tran_lab_charge': float(result[2]) if result[2] is not None else 0.0,
                        'tran_status': result[3] if result[3] is not None else "Pending"
                    }
                else:
                    return {}

        except Exception as e:
            return {}

        finally:
            if conn and not conn.closed:
                conn.close()

    @staticmethod
    def get_transaction_by_chckid(chck_id):
        """Fetch complete transaction details for a given chck_id."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT chck_id, tran_discount, tran_base_charge, tran_lab_charge, tran_status
                    FROM transaction 
                    WHERE chck_id = %s;
                """
                cursor.execute(query, (chck_id,))
                result = cursor.fetchone()

                if result:
                    return {
                        'chck_id': result[0],
                        'tran_discount': float(result[1]) if result[1] is not None else 0.0,
                        'tran_base_charge': float(result[2]) if result[2] is not None else 0.0,
                        'tran_lab_charge': float(result[3]) if result[3] is not None else 0.0,
                        'tran_status': result[4] if result[4] is not None else "Pending"
                    }
                else:
                    return None

        except Exception as e:
            return None
        finally:
            if conn:
                conn.close()


    @staticmethod
    def get_all_transaction():
        """Fetch all transactions with their chck_id and tran_status."""
        conn = DBConnection.get_db_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                # Fetch all transactions
                cursor.execute("""
                    SELECT chck_id, tran_status, tran_discount, tran_base_charge, tran_lab_charge
                    FROM transaction
                    ORDER BY chck_id DESC;
                """)

                results = cursor.fetchall()

                # Convert results to a list of dictionaries
                transactions = []
                for row in results:
                    transactions.append({
                        'chck_id': row[0],
                        'tran_status': row[1],
                        'tran_discount': float(row[2]) if row[2] is not None else 0.0,
                        'tran_base_charge': float(row[3]) if row[3] is not None else 0.0,
                        'tran_lab_charge': float(row[4]) if row[4] is not None else 0.0,
                    })

                return transactions

        except Exception as e:
            return []

        finally:
            if conn:
                conn.close()
