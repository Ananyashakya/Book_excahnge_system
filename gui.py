import mysql.connector
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, PhotoImage
from database import get_connection

def set_background(window, image_path="background.png"):
    window.configure(bg="#DDDDDA")
    bg_image = PhotoImage(file=image_path)
    bg_label = ttk.Label(window, image=bg_image, background="#F3DBCF")
    bg_label.place(relx=0.5, rely=0.5, anchor="center")
    window.bg_image = bg_image  

def create_footer(root, active_page):
    footer = ttk.Frame(root, padding=10)
    footer.pack(side="bottom", fill="x")
    
    def switch_page(page):
        root.destroy()
        if page == "Home":
            home_page()
        elif page == "Login":
            login_window()
        elif page == "Register":
            register_window()
    
    ttk.Button(footer, text="🏠 Home", bootstyle="outline-info", command=lambda: switch_page("Home"), width=25).pack(side="left", padx=15)
    ttk.Button(footer, text="🔐 Login", bootstyle="outline-success", command=lambda: switch_page("Login"), width=25).pack(side="left", padx=15)
    ttk.Button(footer, text="📝 Register", bootstyle="outline-primary", command=lambda: switch_page("Register"), width=25).pack(side="left", padx=15)

def home_page():
    root = ttk.Window(themename="flatly")
    root.title("Book Exchange System")
    root.geometry("900x600")
    root.configure(bg="#F3DBCF")
    
    set_background(root)
    heading_label = ttk.Label(
        root, 
        text="📚 Welcome to the Book Exchange System", 
        font=("Merriweather", 30, "bold"), 
        foreground="black"
    )
    heading_label.pack(pady=50)

    ttk.Button(root, text="Login", bootstyle="success-outline", command=lambda: [root.destroy(), login_window()], width=40).pack(pady=15)
    ttk.Button(root, text="Register", bootstyle="primary-outline", command=lambda: [root.destroy(), register_window()], width=40).pack(pady=15)

    create_footer(root, "Home")
    root.mainloop()

def register_window():
    reg_win = ttk.Window(themename="cosmo")
    reg_win.title("Register")
    reg_win.geometry("900x600")
    reg_win.configure(bg="#F3DBCF")

    set_background(reg_win)
    ttk.Label(reg_win, text="Register", font=("Merriweather", 28, "bold"), bootstyle="inverse-primary").pack(pady=30)

    frame = ttk.Frame(reg_win, padding=30)
    frame.pack(pady=10)

    ttk.Label(frame, text="Name:", font=("Merriweather", 14)).grid(row=0, column=0, padx=15, pady=15, sticky="w")
    name_entry = ttk.Entry(frame, width=45)
    name_entry.grid(row=0, column=1)

    ttk.Label(frame, text="Email:", font=("Merriweather", 14)).grid(row=1, column=0, padx=15, pady=15, sticky="w")
    email_entry = ttk.Entry(frame, width=45)
    email_entry.grid(row=1, column=1)

    ttk.Label(frame, text="Password:", font=("Merriweather", 14)).grid(row=2, column=0, padx=15, pady=15, sticky="w")
    password_entry = ttk.Entry(frame, width=45, show="*")
    password_entry.grid(row=2, column=1)

    def register():
        name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()

        if not (name and email and password):
            messagebox.showerror("Error", "All fields are required!")
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            reg_win.destroy()
            login_window()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        conn.close()

    ttk.Button(reg_win, text="Register", bootstyle="success", command=register, width=40).pack(pady=15)
    create_footer(reg_win, "Register")
    reg_win.mainloop()

def login_window():
    login_win = ttk.Window(themename="cyborg")
    login_win.title("Login")
    login_win.geometry("900x600")
    login_win.configure(bg="#F3DBCF")

    set_background(login_win)
    ttk.Label(login_win, text="Login", font=("Merriweather", 28, "bold"), bootstyle="inverse-primary").pack(pady=30)

    frame = ttk.Frame(login_win, padding=30)
    frame.pack(pady=10)

    ttk.Label(frame, text="Email:", font=("Merriweather", 14)).grid(row=0, column=0, padx=15, pady=15, sticky="w")
    email_entry = ttk.Entry(frame, width=40)
    email_entry.grid(row=0, column=1)

    ttk.Label(frame, text="Password:", font=("Merriweather", 14)).grid(row=1, column=0, padx=15, pady=15, sticky="w")
    password_entry = ttk.Entry(frame, width=40, show="*")
    password_entry.grid(row=1, column=1)

    def authenticate():
        email = email_entry.get()
        password = password_entry.get()

        if email and password:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users WHERE email=%s AND password=%s", (email, password))
            result = cursor.fetchone()
            if result:
                login_win.destroy()
                user_dashboard(result[0])
            else:
                messagebox.showerror("Error", "Invalid credentials!")
            conn.close()
        else:
            messagebox.showerror("Error", "Please fill in both fields!")

    ttk.Button(login_win, text="Login", bootstyle="success", command=authenticate, width=40).pack(pady=15)
    create_footer(login_win, "Login")
    login_win.mainloop()

def user_dashboard(username):
    user_win = ttk.Window(themename="flatly")
    user_win.title(f"Welcome, {username}")
    user_win.geometry("900x600")
    user_win.configure(bg="#F3DBCF")

    set_background(user_win, image_path="back_ground.png")
    
    ttk.Label(user_win, text=f"Welcome, {username}!", font=("Merriweather", 28, "bold"), bootstyle="inverse-primary").pack(pady=50)

    frame = ttk.Frame(user_win, padding=10)
    frame.pack(pady=30)

    ttk.Button(frame, text="📖 Available Books", bootstyle="outline-info", width=30, command=available_books).grid(row=0, column=0, padx=20, pady=20)
    ttk.Button(frame, text="🔍 Search Books", bootstyle="outline-warning", width=30, command=search_books).grid(row=1, column=0, padx=20, pady=20)
    ttk.Button(frame, text="💳 Transactions", bootstyle="outline-danger", width=30, command=transaction_history).grid(row=2, column=0, padx=20, pady=20)
    ttk.Button(frame, text="Logout", bootstyle="outline-danger", width=20, command=user_win.destroy).grid(row=3, column=0, padx=20, pady=20)

    user_win.mainloop()

def available_books():
    books_win = ttk.Window(themename="superhero")
    books_win.title("Available Books")
    books_win.geometry("900x600")
    books_win.configure(bg="#F3DBCF")

    ttk.Label(books_win, text="Available Books", font=("Arial", 28, "bold")).pack(pady=20)

    books_data = [
        ("The Catcher in the Rye", "J.D. Salinger"),
        ("To Kill a Mockingbird", "Harper Lee"),
        ("1984", "George Orwell"),
        ("Pride and Prejudice", "Jane Austen"),
        ("The Great Gatsby", "F. Scott Fitzgerald"),
    ]

    treeview = ttk.Treeview(books_win, columns=("Book", "Author"), show='headings')
    treeview.heading("Book", text="Book Title")
    treeview.heading("Author", text="Author")
    for book in books_data:
        treeview.insert("", "end", values=book)

    treeview.pack(fill="both", expand=True)
    books_win.mainloop()

def search_books():
    search_win = ttk.Window(themename="cosmo")
    search_win.title("Search Books")
    search_win.geometry("900x600")
    search_win.configure(bg="#F3DBCF")

    ttk.Label(search_win, text="Search Books", font=("Arial", 28, "bold")).pack(pady=20)
    
    search_entry = ttk.Entry(search_win, width=50)
    search_entry.pack(pady=10)
    
    def search_action():
        search_term = search_entry.get().lower()
        search_results = [
            ("1984", "George Orwell"),
            ("Pride and Prejudice", "Jane Austen"),
            ("The Catcher in the Rye", "J.D. Salinger"),
            ("To Kill a Mockingbird", "Harper Lee"),
            ("The Great Gatsby", "F. Scott Fitzgerald"),
        ]
        filtered_books = [book for book in search_results if search_term in book[0].lower()]
        if filtered_books:
            for item in filtered_books:
                print(item)

    ttk.Button(search_win, text="Search", command=search_action).pack(pady=10)
    search_win.mainloop()

def transaction_history():
    trans_win = ttk.Window(themename="cosmo")
    trans_win.title("Transaction History")
    trans_win.geometry("900x600")
    trans_win.configure(bg="#ADD8E6")

    ttk.Label(trans_win, text="Transaction History", font=("Arial", 28, "bold")).pack(pady=20)

    treeview = ttk.Treeview(trans_win, columns=("ID", "Book", "User", "Date"), show='headings')
    treeview.heading("ID", text="Transaction ID")
    treeview.heading("Book", text="Book Title")
    treeview.heading("User", text="User")
    treeview.heading("Date", text="Date")
    treeview.pack(fill="both", expand=True)

    trans_win.mainloop()

home_page()