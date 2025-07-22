from gui import home_page
from database import initialize_admin

initialize_admin()

if __name__ == "__main__":
    home_page()
