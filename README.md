# BookSwap — Book Exchange System

BookSwap is a secure desktop application that enables users to exchange books through a structured request and approval system. It is built using Python and MySQL, with a focus on clean architecture, security, and usability.

## Overview

The application allows users to browse, search, and list books, while facilitating controlled exchanges through an admin-managed workflow. It implements secure authentication and maintains a complete transaction lifecycle from request to completion.

## Key Features

### User
- Secure registration and login
- Browse and search books by title, author, or genre
- List books with condition and category
- Request books for exchange
- Track exchange requests and transaction status

### Admin
- View and manage registered users
- Manage all book listings
- Approve, reject, or complete exchange requests
- Monitor complete transaction history

## Security

- Password hashing using **bcrypt** with salting
- Parameterized queries to prevent SQL injection
- Role-based access control (Admin/User separation)
- Input validation for authentication and data integrity
- Sensitive data (password hashes) never exposed to UI

## Tech Stack

- **Python** (Core Logic)
- **Tkinter** with **ttkbootstrap** (GUI)
- **MySQL** (Database)
- **mysql-connector-python** (Database Connectivity)
- **bcrypt** (Authentication Security)

## Installation

    ```bash
    git clone https://github.com/Ananyashakya/Book_excahnge_system.git
    cd Book_excahnge_system
    pip install mysql-connector-python ttkbootstrap bcrypt
    python main.py
## Database
The system uses three core tables:

users — stores user credentials and roles
books — stores book listings and availability
transactions — manages exchange requests and status

## Project Structure
    ```bash
    Book_excahnge_system/
    ├── main.py
    ├── database.py
    ├── gui.py
    ├── seed_books.sql
    └── README.md

## Default Admin Access

Email: admin@bookexchange.com
Password: Admin@2025!

## Summary
BookSwap demonstrates a complete desktop-based CRUD system with authentication, role-based access, and transactional workflows. The project highlights backend logic design, database integration, and secure application development practices.
