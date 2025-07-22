# Book Exchange System

A desktop-based book exchange platform built using Python and MySQL. This application includes features like user registration, login, admin access, and book-related interactions via a graphical interface. The project focuses on building a functional desktop app with a real database backend and GUI design.

# Features

- User registration and login with email and password
- Admin login with ability to view all registered users
- GUI interface using ttkbootstrap (Tkinter-based themes)
- View available books and transaction history
- Search books from a predefined list
- Modular structure with separate files for GUI, database, and main execution

# Technologies Used

- Python
- Tkinter + ttkbootstrap
- MySQL (via `mysql-connector-python`)
- Structured query handling and modular Python scripts

# How to Run

1. Make sure MySQL is installed and running on your system
2. Create a database named `BookExchangeDB`
3. Use the following SQL to create the `users` table:
   ```sql
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(100),
       email VARCHAR(100) UNIQUE,
       password VARCHAR(100),
       is_admin BOOLEAN DEFAULT FALSE
   );
