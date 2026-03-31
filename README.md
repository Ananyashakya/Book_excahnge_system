# BookSwap — Book Exchange System

BookSwap is a desktop-based application that allows users to exchange books through a structured request and approval system. The project is built using Python and MySQL, with a focus on clean design, secure authentication, and a smooth user experience.

---

## Overview

The application provides a simple and organized way for users to share books within a community. Users can list books, browse available titles, and request exchanges. Each exchange follows a proper workflow, ensuring that actions like approvals and completions are handled in a controlled manner.

The system is designed to reflect real-world logic rather than just basic CRUD operations.

---

## Features

### User Functionality

- Create an account and log in securely  
- Browse and search books by title, author, or genre  
- List books with condition details  
- Send exchange requests to other users  
- Track the status of all transactions  
- Submit ratings and reviews after completing an exchange  

---

### Admin Functionality

- View all registered users  
- Manage book listings  
- Approve, reject, or complete exchange requests  
- Monitor the complete transaction history  

---

## Security and Data Handling

- Passwords are securely stored using bcrypt hashing  
- Parameterized queries are used to prevent SQL injection  
- Role-based access ensures separation between admin and users  
- Input validation is applied across forms and operations  
- Sensitive information such as passwords is never exposed  

---

## Tech Stack

- Python (core logic)  
- Tkinter with ttkbootstrap (GUI)  
- MySQL (database)  
- mysql-connector-python (database connectivity)  
- bcrypt (authentication security)  

---


---

## Database Structure

The application uses the following core tables:

- users — stores user details and roles  
- books — stores book listings and availability  
- transactions — manages exchange requests and their status  
- reviews — stores user ratings and feedback  

---

## Project Structure
    ```
    Book_excahnge_system/
    ├── main.py
    ├── database.py
    ├── gui.py
    ├── seed_books.sql
    └── README.md

---

## Default Admin Access

Email: admin@bookexchange.com  
Password: Admin@2025!  

---

## Conclusion

BookSwap is designed to go beyond a simple academic project. It demonstrates how a real system can manage users, data, and workflows in a structured and secure way. The project helped strengthen my understanding of database design, authentication, and building user-friendly interfaces.
