"""
main.py - Book Exchange System entry point.
"""
from database import initialize_db
from gui import start

if __name__ == "__main__":
    initialize_db()
    start()