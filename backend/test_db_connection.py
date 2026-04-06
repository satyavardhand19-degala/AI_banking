import sys
import os
sys.path.append(os.getcwd())

from database.connection import db_pool
import logging

logging.basicConfig(level=logging.INFO)

def test():
    print("Testing database connection...")
    success = db_pool.test_connection()
    if success:
        print("SUCCESS: Database connection established!")
    else:
        print("FAILURE: Could not connect to the database.")

if __name__ == "__main__":
    test()
