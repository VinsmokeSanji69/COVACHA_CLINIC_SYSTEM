from idlelib.pyparse import trans
from typing import final

from Models.DB_Connection import DBConnection

class Transaction():
    @staticmethod
    def add_transaction(chck_id, trans_data):
        conn = DBConnection.get_db_connection()

        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO transaction (
                        chck_id, tran_discount, tran_base_charge, tran_lab_charge, tran_status
                    ) VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    chck_id,
                    trans_data["discount"],
                    trans_data["base_charge"],
                    trans_data["lab_charge"],
                    trans_data.get("status", "Completed")
                ))

                conn.commit()
                print("Transaction data saved successfully")

        except Exception as e:
            # If duplicate key, update instead
            if "duplicate key value violates unique constraint" in str(e):
                print(f"Transaction already exists for chck_id={chck_id}. Updating instead.")
                return Transaction.update_transaction(chck_id, trans_data)
            else:
                print(f"Database error while creating new transaction: {e}")
                conn.rollback()
                return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_transaction(chck_id, trans_data):
        conn = DBConnection.get_db_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                # Only update values that changed, or at least status to Completed
                query = """
                    UPDATE transaction
                    SET tran_discount = %s,
                        tran_base_charge = %s,
                        tran_lab_charge = %s,
                        tran_status = %s
                    WHERE chck_id = %s
                """
                cursor.execute(query, (
                    trans_data["discount"],
                    trans_data["base_charge"],
                    trans_data["lab_charge"],
                    "Completed",  # Always set to Completed when updating from Partial
                    chck_id
                ))
                conn.commit()
                print("Transaction updated successfully")

        except Exception as e:
            print(f"Database error while updating transaction: {e}")
            conn.rollback()
            return None

        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_transaction_by_chckid(chck_id):
        """Fetch transaction discount for a given chck_id."""
        from Models.DB_Connection import DBConnection

        conn = DBConnection.get_db_connection()
        if not conn:
            print("Failed to establish database connection.")
            return None

        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT tran_discount 
                    FROM transaction 
                    WHERE chck_id = %s;
                """
                cursor.execute(query, (chck_id,))
                result = cursor.fetchone()

                if result:
                    # Return the transaction discount as a dictionary
                    return {'tran_discount': float(result[0]) if result[0] is not None else 0.0}
                else:
                    return None

        except Exception as e:
            print(f"Error fetching transaction for chck_id={chck_id}: {e}")
            return None

        finally:
            # Check if the connection is still open before closing it
            if conn and not conn.closed:
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
                    SELECT chck_id, tran_status
                    FROM transaction;
                """)

                results = cursor.fetchall()

                # Convert results to a list of dictionaries
                transactions = []
                for row in results:
                    transactions.append({
                        'chck_id': row[0],
                        'tran_status': row[1],
                    })

                # Debug: Log the fetched transactions
                #print(f"Fetched transactions: {transactions}")
                return transactions

        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []

        finally:
            if conn:
                conn.close()