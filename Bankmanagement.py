import mysql.connector
from mysql.connector import Error
from decimal import Decimal, InvalidOperation

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="9347769926",
        database="bankmanager"
    )
class BankDetails:
    def __init__(self, account_no, customer_name):
        self.account_no = account_no
        self.customer_name = customer_name
        self._balance = Decimal("0.00")
    def create_account(self, initial_deposit):
        initial_deposit = Decimal(str(initial_deposit))
        if initial_deposit < 0:
            raise ValueError(
                "Initial deposit cannot be negative."
            )
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute( """ INSERT INTO bankaccount(account_no, customer_name, balance) VALUES (%s, %s, %s) """,
                (
                    self.account_no,
                    self.customer_name,
                    initial_deposit
                )
            )
            if initial_deposit > 0:
                cursor.execute("""  INSERT INTO transactions(account_no, transaction_type,amount, balance_after) VALUES (%s, %s, %s, %s)""",
                    (
                        self.account_no,
                        "INITIAL_DEPOSIT",
                        initial_deposit,
                        initial_deposit
                    )
                )
            conn.commit()
            self._balance = initial_deposit
            print("Account created successfully!")
        except Error:
            if conn is not None and conn.is_connected():
                conn.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()
    def get_balance(self):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT balance
                FROM accounts
                WHERE account_no = %s
                """,
                (self.account_no,)
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError("Account does not exist.")

            self._balance = Decimal(str(result[0]))

            return self._balance

        finally:
            if cursor is not None:
                cursor.close()

            if conn is not None and conn.is_connected():
                conn.close()
def main():

    print("===== BANK MANAGEMENT SYSTEM =====")

    account_no = int(input("Enter Account Number: "))
    customer_name = input("Enter Customer Name: ").strip()

    if account_no <= 0:
        raise ValueError("Account number must be positive.")

    if not customer_name:
        raise ValueError("Customer name cannot be empty.")

    initial_deposit = Decimal(
        input("Enter Initial Deposit: ").strip()
    )
    if not initial_deposit.is_finite():
        raise ValueError("Enter a valid deposit amount.")
        account = BankDetails(account_no , customer_name)
        account.create_account(initial_deposit)
        balance = account.get_balance()
        print("\n===== ACCOUNT DETAILS =====")
        print("Account Number:", account.account_no)
        print("Customer Name:", account.customer_name)
        print("Current Balance: ₹", f"{balance:.2f}")
if __name__ == "__main__":
    try:
        main()
    except Error as e:
        print("Database Error:", e)
    except (ValueError, InvalidOperation) as e:
        print("Invalid input:", e)
    except Exception as e:
        print("Unexpected error:", e)