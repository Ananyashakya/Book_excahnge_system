"""
Book Exchange System - GUI
A clean interface for swapping books with your community
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import math
import random

from database import (
    authenticate_user, register_user, is_valid_email,
    get_available_books, get_user_books, add_book, delete_book,
    request_exchange, get_user_transactions,
    get_all_users, get_all_transactions, update_transaction_status,
)

# Colors that work well together
COLORS = {
    "bg_dark": "#0A0E17",
    "bg_card": "#121725", 
    "bg_hover": "#1A2133",
    "bg_input": "#0F1420",
    "accent": "#5B7DB1",
    "accent_light": "#7B9BC9",
    "accent_dark": "#3D5A80",
    "text_light": "#E8EDF2",
    "text_muted": "#8A99B0",
    "success": "#4C9A6F",
    "danger": "#D9534F",
    "warning": "#F0AD4E",
}

# Font settings
FONTS = {
    "h1": ("Segoe UI", 34, "bold"),
    "h2": ("Segoe UI", 22, "bold"),
    "h3": ("Segoe UI", 15, "bold"),
    "body": ("Segoe UI", 11),
    "body_small": ("Segoe UI", 9),
    "button": ("Segoe UI", 11, "bold"),
}

# Main window setup - full screen
root = tk.Tk()
root.title("BookSwap")
root.attributes('-fullscreen', True)
root.configure(bg=COLORS["bg_dark"])

_current_frame = None

# Press F11 for fullscreen, Esc to exit
def toggle_fullscreen(event=None):
    root.attributes('-fullscreen', not root.attributes('-fullscreen'))

root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

def show_frame(frame):
    """Switch between different pages"""
    global _current_frame
    if _current_frame:
        _current_frame.destroy()
    _current_frame = frame
    frame.pack(fill="both", expand=True)

# Reusable UI elements
def create_card(parent, padding=25):
    """A card container with a subtle border"""
    card = tk.Frame(parent, bg=COLORS["bg_card"], relief="flat")
    card.configure(highlightbackground=COLORS["accent"], highlightthickness=1)
    return card

def create_button(parent, text, command, style="primary", width=None):
    """Button with hover effect - primary, secondary, or danger style"""
    color_map = {
        "primary": (COLORS["accent"], COLORS["accent_light"]),
        "secondary": (COLORS["bg_hover"], COLORS["accent_dark"]),
        "danger": (COLORS["danger"], "#B93A37"),
    }
    bg_color, hover_color = color_map.get(style, color_map["primary"])
    
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg_color, fg=COLORS["text_light"],
        font=FONTS["button"], relief="flat", cursor="hand2",
        padx=25 if not width else 0, pady=10, width=width
    )
    
    def on_enter(e): btn.configure(bg=hover_color)
    def on_leave(e): btn.configure(bg=bg_color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def create_entry(parent, placeholder="", is_password=False):
    """Input field with placeholder text"""
    frame = tk.Frame(parent, bg=COLORS["bg_card"])
    entry = tk.Entry(
        frame, width=38,
        bg=COLORS["bg_input"], fg=COLORS["text_light"],
        insertbackground=COLORS["text_light"], relief="flat",
        font=FONTS["body"], show="*" if is_password else ""
    )
    entry.pack(fill="x", padx=8, pady=8, ipady=8)
    
    # Add placeholder text that disappears when clicked
    if placeholder:
        entry.insert(0, placeholder)
        entry.configure(fg=COLORS["text_muted"])
        
        def on_focus(e):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.configure(fg=COLORS["text_light"])
        
        def on_blur(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(fg=COLORS["text_muted"])
        
        entry.bind("<FocusIn>", on_focus)
        entry.bind("<FocusOut>", on_blur)
    
    return frame, entry

def create_treeview(parent, columns, height=14):
    """Styled table for displaying data"""
    style = ttk.Style()
    style.theme_use("flatly")
    style.configure(
        "Custom.Treeview",
        background=COLORS["bg_card"],
        foreground=COLORS["text_light"],
        fieldbackground=COLORS["bg_card"],
        rowheight=36,
        font=FONTS["body"],
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=COLORS["bg_dark"],
        foreground=COLORS["accent"],
        font=FONTS["h3"],
    )
    
    col_names = [c[0] for c in columns]
    tree = ttk.Treeview(parent, columns=col_names, show="headings", height=height, style="Custom.Treeview")
    
    for col, width in columns:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")
    
    scroll = tk.Scrollbar(parent, orient="vertical", command=tree.yview, bg=COLORS["bg_dark"])
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    
    return tree

def create_header(parent, title, subtitle=""):
    """Page header with decorative accent line"""
    header = tk.Frame(parent, bg=COLORS["bg_dark"], pady=30)
    header.pack(fill="x")
    
    tk.Frame(header, bg=COLORS["accent"], height=3, width=70).pack(pady=(0, 12))
    tk.Label(header, text=title, font=FONTS["h1"], bg=COLORS["bg_dark"], fg=COLORS["text_light"]).pack()
    
    if subtitle:
        tk.Label(header, text=subtitle, font=FONTS["body"], bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(pady=(5, 0))
    
    tk.Frame(header, bg=COLORS["accent"], height=2, width=50).pack(pady=(12, 0))

def create_bottom_bar(parent, user):
    """Footer with user info and system status"""
    bar = tk.Frame(parent, bg="#080A0E", pady=12, padx=25)
    bar.pack(fill="x", side="bottom")
    
    tk.Label(bar, text="Book Exchange System", font=FONTS["body_small"], bg="#080A0E", fg=COLORS["text_muted"]).pack(side="left")
    
    role = "Admin" if user.get("is_admin") else "Member"
    role_color = COLORS["accent"] if user.get("is_admin") else COLORS["text_muted"]
    
    user_info = tk.Frame(bar, bg="#080A0E")
    user_info.pack(side="right")
    
    tk.Label(user_info, text=f"{user['name']} ({role})", font=FONTS["body_small"], bg="#080A0E", fg=role_color).pack()

# Home page with animated background
def home_page():
    root.title("BookSwap - Home")
    frame = tk.Frame(root, bg=COLORS["bg_dark"])
    
    canvas = tk.Canvas(frame, bg=COLORS["bg_dark"], highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    def draw_background(event=None):
        canvas.delete("all")
        w = canvas.winfo_width() or root.winfo_width()
        h = canvas.winfo_height() or root.winfo_height()
        
        # Floating circles for visual interest
        circles = [
            (w - 200, h - 200, 280, "#121725"),
            (-100, -100, 220, "#121725"),
            (w // 2, h // 3, 150, "#1A2133"),
            (w // 4, h - 100, 100, "#0F1420"),
            (w - 150, 100, 120, "#0F1420"),
        ]
        for x, y, r, color in circles:
            canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
        
        # Main title
        canvas.create_text(w // 2, h // 2 - 120, text="BookSwap", font=("Segoe UI", 64, "bold"), fill=COLORS["text_light"])
        
        # Decorative line under title
        canvas.create_line(w // 2 - 60, h // 2 - 60, w // 2 + 60, h // 2 - 60, fill=COLORS["accent"], width=3)
        
        # Tagline
        canvas.create_text(w // 2, h // 2 - 10, text="Exchange books. Share stories. Build community.", font=("Segoe UI", 14), fill=COLORS["text_muted"])
        
        # Buttons container
        btn_container = tk.Frame(canvas, bg=COLORS["bg_dark"])
        canvas.create_window(w // 2, h // 2 + 60, window=btn_container)
        
        login_btn = create_button(btn_container, "Login", login_page, style="primary")
        login_btn.pack(side="left", padx=15)
        
        register_btn = create_button(btn_container, "Register", register_page, style="secondary")
        register_btn.pack(side="left", padx=15)
        
        # Footer
        canvas.create_text(w // 2, h - 40, text="© 2025 BookSwap — Connect through literature", font=FONTS["body_small"], fill=COLORS["text_muted"])
    
    canvas.bind("<Configure>", draw_background)
    show_frame(frame)

# Register page
def register_page():
    root.title("BookSwap - Create Account")
    frame = tk.Frame(root, bg=COLORS["bg_dark"])
    create_header(frame, "Join BookSwap", "Start your reading journey")
    
    # Two column layout - info on left, form on right
    main_container = tk.Frame(frame, bg=COLORS["bg_dark"])
    main_container.pack(expand=True, fill="both", padx=50, pady=20)
    
    # Left side - benefits list
    info_card = create_card(main_container, padding=35)
    info_card.pack(side="left", fill="both", expand=True, padx=(0, 25))
    
    tk.Label(info_card, text="Why join?", font=FONTS["h2"], bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(0, 25))
    
    benefits = [
        "Access to hundreds of shared books",
        "Connect with fellow readers",
        "Sustainable book swapping",
        "Track your reading journey",
        "Completely free",
    ]
    
    for benefit in benefits:
        row = tk.Frame(info_card, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=8)
        tk.Label(row, text="→", font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(side="left", padx=(0, 12))
        tk.Label(row, text=benefit, font=FONTS["body"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).pack(side="left")
    
    # Right side - registration form
    form_card = create_card(main_container, padding=35)
    form_card.pack(side="right", fill="both", expand=True)
    
    tk.Label(form_card, text="Create Account", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).pack(pady=(0, 20))
    
    # Form fields
    name_frame, name_entry = create_entry(form_card, "Full name")
    name_frame.pack(fill="x", pady=5)
    
    email_frame, email_entry = create_entry(form_card, "Email address")
    email_frame.pack(fill="x", pady=5)
    
    pass_frame, pass_entry = create_entry(form_card, "Password", is_password=True)
    pass_frame.pack(fill="x", pady=5)
    
    confirm_frame, confirm_entry = create_entry(form_card, "Confirm password", is_password=True)
    confirm_frame.pack(fill="x", pady=5)
    
    error_var = tk.StringVar()
    tk.Label(form_card, textvariable=error_var, bg=COLORS["bg_card"], fg=COLORS["danger"], font=FONTS["body_small"]).pack(pady=5)
    
    def do_register():
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        password = pass_entry.get()
        confirm = confirm_entry.get()
        
        if not all([name, email, password, confirm]):
            error_var.set("All fields are required")
            return
        if not is_valid_email(email):
            error_var.set("Invalid email format")
            return
        if password != confirm:
            error_var.set("Passwords don't match")
            return
        if len(password) < 6:
            error_var.set("Password must be at least 6 characters")
            return
        
        success, result = register_user(name, email, password)
        if success:
            messagebox.showinfo("Success", "Account created! Please log in.")
            login_page()
        else:
            error_var.set(result)
    
    register_btn = create_button(form_card, "Create Account", do_register, style="primary")
    register_btn.pack(pady=20, fill="x")
    
    tk.Label(form_card, text="Already have an account?", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack()
    
    login_link = tk.Button(form_card, text="Sign in here", bg=COLORS["bg_card"], fg=COLORS["accent"], relief="flat", cursor="hand2", font=FONTS["body_small"], command=login_page)
    login_link.pack()
    
    show_frame(frame)

# Login page
def login_page():
    root.title("BookSwap - Login")
    frame = tk.Frame(root, bg=COLORS["bg_dark"])
    create_header(frame, "Welcome Back", "Sign in to continue")
    
    # Center the form
    center = tk.Frame(frame, bg=COLORS["bg_dark"])
    center.pack(expand=True)
    
    form_card = create_card(center, padding=50)
    form_card.pack()
    
    # Decorative element
    tk.Label(form_card, text="◈", font=("Segoe UI", 48), bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(0, 15))
    tk.Label(form_card, text="Sign In", font=FONTS["h2"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).pack(pady=(0, 25))
    
    # Email field
    email_frame, email_entry = create_entry(form_card, "Email address")
    email_frame.pack(fill="x", pady=8)
    
    # Password field
    pass_frame, pass_entry = create_entry(form_card, "Password", is_password=True)
    pass_frame.pack(fill="x", pady=8)
    
    error_var = tk.StringVar()
    tk.Label(form_card, textvariable=error_var, bg=COLORS["bg_card"], fg=COLORS["danger"], font=FONTS["body_small"]).pack(pady=5)
    
    def do_login(event=None):
        email = email_entry.get().strip()
        password = pass_entry.get()
        
        if not email or not password:
            error_var.set("Both fields are required")
            return
        
        user = authenticate_user(email, password)
        if user:
            if user["is_admin"]:
                admin_dashboard(user)
            else:
                user_dashboard(user)
        else:
            error_var.set("Invalid email or password")
    
    email_entry.bind("<Return>", do_login)
    pass_entry.bind("<Return>", do_login)
    
    login_btn = create_button(form_card, "Login", do_login, style="primary")
    login_btn.pack(pady=20, fill="x")
    
    tk.Label(form_card, text="Don't have an account?", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack()
    
    register_link = tk.Button(form_card, text="Create one here", bg=COLORS["bg_card"], fg=COLORS["accent"], relief="flat", cursor="hand2", font=FONTS["body_small"], command=register_page)
    register_link.pack()
    
    show_frame(frame)

# User dashboard
def user_dashboard(user):
    root.title(f"BookSwap - {user['name']}")
    frame = tk.Frame(root, bg=COLORS["bg_dark"])
    create_header(frame, "BookSwap", f"Welcome, {user['name']}")
    
    # Tab bar
    tab_bar = tk.Frame(frame, bg="#080A0E", pady=10, padx=25)
    tab_bar.pack(fill="x")
    
    content = tk.Frame(frame, bg=COLORS["bg_dark"])
    content.pack(fill="both", expand=True, padx=20, pady=15)
    
    tabs = {}
    
    def switch_tab(name):
        for t in tabs.values():
            t.pack_forget()
        tabs[name].pack(fill="both", expand=True)
    
    def create_tab_btn(label, tab_name):
        btn = tk.Button(tab_bar, text=label, bg="#080A0E", fg=COLORS["text_muted"], font=FONTS["button"], relief="flat", cursor="hand2", padx=25, pady=8, command=lambda: switch_tab(tab_name))
        btn.pack(side="left", padx=4)
        
        def on_enter(e): btn.configure(fg=COLORS["accent"])
        def on_leave(e): btn.configure(fg=COLORS["text_muted"])
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    create_tab_btn("Browse Books", "browse")
    create_tab_btn("List a Book", "list")
    create_tab_btn("My Books", "mybooks")
    create_tab_btn("Transactions", "transactions")
    
    logout_btn = tk.Button(tab_bar, text="Logout", bg="#080A0E", fg=COLORS["danger"], font=FONTS["button"], relief="flat", cursor="hand2", padx=20, pady=8, command=home_page)
    logout_btn.pack(side="right")
    
    # Browse tab
    browse_tab = tk.Frame(content, bg=COLORS["bg_dark"])
    tabs["browse"] = browse_tab
    
    search_frame = tk.Frame(browse_tab, bg=COLORS["bg_dark"], pady=10)
    search_frame.pack(fill="x")
    
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=50, bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground=COLORS["text_light"], relief="flat", font=FONTS["body"])
    search_entry.pack(side="left", padx=5, ipady=8)
    
    def load_books():
        for item in browse_tree.get_children():
            browse_tree.delete(item)
        for book in get_available_books(search_var.get()):
            browse_tree.insert("", "end", iid=book["id"], values=(book["title"], book["author"], book["genre"] or "-", book["condition_"], book["owner"]))
    
    search_btn = create_button(search_frame, "Search", load_books, style="secondary")
    search_btn.pack(side="left", padx=5)
    
    reset_btn = create_button(search_frame, "Show All", lambda: [search_var.set(""), load_books()], style="secondary")
    reset_btn.pack(side="left", padx=5)
    
    tree_container = tk.Frame(browse_tab, bg=COLORS["bg_dark"])
    tree_container.pack(fill="both", expand=True, pady=10)
    
    browse_tree = create_treeview(tree_container, [("Title", 220), ("Author", 160), ("Genre", 120), ("Condition", 100), ("Owner", 130)], height=14)
    
    def request_selected():
        selected = browse_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book first")
            return
        success, msg = request_exchange(int(selected[0]), user["id"])
        if success:
            messagebox.showinfo("Request Sent", msg)
            load_books()
        else:
            messagebox.showerror("Failed", msg)
    
    request_btn = create_button(browse_tab, "Request Exchange", request_selected, style="primary")
    request_btn.pack(pady=10)
    
    load_books()
    
    # List a book tab
    list_tab = tk.Frame(content, bg=COLORS["bg_dark"])
    tabs["list"] = list_tab
    
    list_form = create_card(list_tab, padding=40)
    list_form.pack(expand=True, padx=100, pady=30)
    
    tk.Label(list_form, text="Add a New Book", font=FONTS["h2"], bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=(0, 20))
    
    title_frame, title_entry = create_entry(list_form, "Book title")
    title_frame.pack(fill="x", pady=5)
    
    author_frame, author_entry = create_entry(list_form, "Author name")
    author_frame.pack(fill="x", pady=5)
    
    genre_frame, genre_entry = create_entry(list_form, "Genre")
    genre_frame.pack(fill="x", pady=5)
    
    # Condition dropdown
    cond_frame = tk.Frame(list_form, bg=COLORS["bg_card"])
    cond_frame.pack(fill="x", pady=10)
    tk.Label(cond_frame, text="Condition:", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body"]).pack(anchor="w", padx=8)
    condition_var = tk.StringVar(value="Good")
    cond_menu = ttk.Combobox(cond_frame, textvariable=condition_var, values=["Like New", "Good", "Fair", "Worn"], state="readonly", width=35)
    cond_menu.pack(pady=5, padx=8, fill="x")
    
    status_var = tk.StringVar()
    tk.Label(list_form, textvariable=status_var, bg=COLORS["bg_card"], fg=COLORS["success"], font=FONTS["body_small"]).pack(pady=5)
    
    def add_new_book():
        success, msg = add_book(title_entry.get(), author_entry.get(), genre_entry.get(), condition_var.get(), user["id"])
        if success:
            status_var.set("Book listed successfully!")
            title_entry.delete(0, "end")
            author_entry.delete(0, "end")
            genre_entry.delete(0, "end")
            refresh_my_books()
        else:
            status_var.set(f"Error: {msg}")
    
    submit_btn = create_button(list_form, "List Book", add_new_book, style="primary")
    submit_btn.pack(pady=20, fill="x")
    
    # My books tab
    mybooks_tab = tk.Frame(content, bg=COLORS["bg_dark"])
    tabs["mybooks"] = mybooks_tab
    
    mybooks_container = tk.Frame(mybooks_tab, bg=COLORS["bg_dark"])
    mybooks_container.pack(fill="both", expand=True)
    
    mybooks_tree = create_treeview(mybooks_container, [("Title", 210), ("Author", 150), ("Genre", 120), ("Condition", 90), ("Status", 90), ("Listed Date", 160)], height=12)
    
    def refresh_my_books():
        for item in mybooks_tree.get_children():
            mybooks_tree.delete(item)
        for book in get_user_books(user["id"]):
            status = "Available" if book["is_available"] else "Pending"
            mybooks_tree.insert("", "end", iid=book["id"], values=(book["title"], book["author"], book["genre"] or "-", book["condition_"], status, str(book["listed_at"])[:16]))
    
    def delete_selected():
        selected = mybooks_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a book to remove")
            return
        if messagebox.askyesno("Confirm", "Remove this book?"):
            if delete_book(int(selected[0]), user["id"]):
                refresh_my_books()
            else:
                messagebox.showerror("Error", "Could not remove book")
    
    btn_frame = tk.Frame(mybooks_tab, bg=COLORS["bg_dark"], pady=10)
    btn_frame.pack()
    
    remove_btn = create_button(btn_frame, "Remove Book", delete_selected, style="danger")
    remove_btn.pack(side="left", padx=10)
    
    refresh_btn = create_button(btn_frame, "Refresh", refresh_my_books, style="secondary")
    refresh_btn.pack(side="left", padx=10)
    
    refresh_my_books()
    
    # Transactions tab
    trans_tab = tk.Frame(content, bg=COLORS["bg_dark"])
    tabs["transactions"] = trans_tab
    
    trans_container = tk.Frame(trans_tab, bg=COLORS["bg_dark"])
    trans_container.pack(fill="both", expand=True)
    
    trans_tree = create_treeview(trans_container, [("ID", 50), ("Book", 190), ("Author", 140), ("Requester", 120), ("Owner", 120), ("Status", 100), ("Date", 150)], height=12)
    
    def load_transactions():
        for item in trans_tree.get_children():
            trans_tree.delete(item)
        for trans in get_user_transactions(user["id"]):
            trans_tree.insert("", "end", iid=trans["id"], values=(trans["id"], trans["title"], trans["author"], trans["requester"], trans["owner"], trans["status"], str(trans["created_at"])[:16]))
    
    refresh_trans_btn = create_button(trans_tab, "Refresh", load_transactions, style="secondary")
    refresh_trans_btn.pack(pady=10)
    
    load_transactions()
    
    create_bottom_bar(frame, user)
    show_frame(frame)
    switch_tab("browse")

# Admin dashboard
def admin_dashboard(user):
    root.title("BookSwap - Admin Panel")
    frame = tk.Frame(root, bg=COLORS["bg_dark"])
    create_header(frame, "Administration", "Manage users, books, and transactions")
    
    tab_bar = tk.Frame(frame, bg="#080A0E", pady=10, padx=25)
    tab_bar.pack(fill="x")
    
    content = tk.Frame(frame, bg=COLORS["bg_dark"])
    content.pack(fill="both", expand=True, padx=20, pady=15)
    
    tabs = {}
    
    def switch_tab(name):
        for t in tabs.values():
            t.pack_forget()
        tabs[name].pack(fill="both", expand=True)
    
    def create_tab_btn(label, tab_name):
        btn = tk.Button(tab_bar, text=label, bg="#080A0E", fg=COLORS["text_muted"], font=FONTS["button"], relief="flat", cursor="hand2", padx=25, pady=8, command=lambda: switch_tab(tab_name))
        btn.pack(side="left", padx=4)
        
        def on_enter(e): btn.configure(fg=COLORS["accent"])
        def on_leave(e): btn.configure(fg=COLORS["text_muted"])
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    create_tab_btn("Users", "users")
    create_tab_btn("All Books", "books")
    create_tab_btn("Transactions", "transactions")
    
    logout_btn = tk.Button(tab_bar, text="Logout", bg="#080A0E", fg=COLORS["danger"], font=FONTS["button"], relief="flat", cursor="hand2", padx=20, pady=8, command=home_page)
    logout_btn.pack(side="right")
    
    # Users tab
    users_tab = tk.Frame(content, bg=COLORS["bg_dark"])
    tabs["users"] = users_tab
    
    users_container = tk.Frame(users_tab, bg=COLORS["bg_dark"])
    users_container.pack(fill="both", expand=True)
    
    users_tree = create_treeview(users_container, [("ID", 60), ("Name", 180), ("Email", 260), ("Role", 90), ("Joined", 180)], height=14)
    
    def load_users():
        for item in users_tree.get_children():
            users_tree.delete(item)
        for u in get_all_users():
            role = "Admin" if u["is_admin"] else "Member"
            users_tree.insert("", "end", values=(u["id"], u["name"], u["email"], role, str(u["created_at"])[:16]))
    
    refresh_users_btn = create_button(users_tab, "Refresh", load_users, style="secondary")
    refresh_users_btn.pack(pady=10)
    
    load_users()
    
    # Books tab
    books_tab = tk.Frame(content, bg=COLORS["bg_dark"])
    tabs["books"] = books_tab
    
    books_container = tk.Frame(books_tab, bg=COLORS["bg_dark"])
    books_container.pack(fill="both", expand=True)
    
    all_books_tree = create_treeview(books_container, [("Title", 220), ("Author", 160), ("Genre", 120), ("Condition", 90), ("Owner", 140), ("Status", 90)], height=13)
    
    def load_all_books():
        for item in all_books_tree.get_children():
            all_books_tree.delete(item)
        for book in get_available_books():
            all_books_tree.insert("", "end", iid=book["id"], values=(book["title"], book["author"], book["genre"] or "-", book["condition_"], book["owner"], "Available"))
    
    def admin_delete_book():
        selected = all_books_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a book to delete")
            return
        if messagebox.askyesno("Confirm", "Permanently delete this book?"):
            if delete_book(int(selected[0]), user["id"], is_admin=True):
                load_all_books()
                messagebox.showinfo("Success", "Book deleted")
            else:
                messagebox.showerror("Error", "Could not delete")
    
    admin_btn_frame = tk.Frame(books_tab, bg=COLORS["bg_dark"], pady=10)
    admin_btn_frame.pack()
    
    delete_btn = create_button(admin_btn_frame, "Delete Book", admin_delete_book, style="danger")
    delete_btn.pack(side="left", padx=10)
    
    refresh_books_btn = create_button(admin_btn_frame, "Refresh", load_all_books, style="secondary")
    refresh_books_btn.pack(side="left", padx=10)
    
    load_all_books()
    
    # Transactions tab
    admin_trans_tab = tk.Frame(content, bg=COLORS["bg_dark"])
    tabs["transactions"] = admin_trans_tab
    
    trans_container = tk.Frame(admin_trans_tab, bg=COLORS["bg_dark"])
    trans_container.pack(fill="both", expand=True)
    
    admin_trans_tree = create_treeview(trans_container, [("ID", 50), ("Book", 190), ("Author", 140), ("Requester", 120), ("Owner", 120), ("Status", 100), ("Date", 150)], height=12)
    
    all_transactions = []
    
    def load_all_transactions():
        nonlocal all_transactions
        for item in admin_trans_tree.get_children():
            admin_trans_tree.delete(item)
        all_transactions = get_all_transactions()
        for trans in all_transactions:
            admin_trans_tree.insert("", "end", iid=trans["id"], values=(trans["id"], trans["title"], trans["author"], trans["requester"], trans["owner"], trans["status"], str(trans["created_at"])[:16]))
    
    def update_status(status):
        selected = admin_trans_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a transaction")
            return
        trans_id = int(selected[0])
        trans = next((t for t in all_transactions if t["id"] == trans_id), None)
        book_id = trans.get("book_id", 0) if trans else 0
        update_transaction_status(trans_id, status, book_id)
        load_all_transactions()
        messagebox.showinfo("Success", f"Transaction {status.lower()}")
    
    admin_btn_frame = tk.Frame(admin_trans_tab, bg=COLORS["bg_dark"], pady=10)
    admin_btn_frame.pack()
    
    approve_btn = create_button(admin_btn_frame, "Approve", lambda: update_status("Approved"), style="primary")
    approve_btn.pack(side="left", padx=5)
    
    reject_btn = create_button(admin_btn_frame, "Reject", lambda: update_status("Rejected"), style="danger")
    reject_btn.pack(side="left", padx=5)
    
    complete_btn = create_button(admin_btn_frame, "Complete", lambda: update_status("Completed"), style="secondary")
    complete_btn.pack(side="left", padx=5)
    
    refresh_admin_btn = create_button(admin_btn_frame, "Refresh", load_all_transactions, style="secondary")
    refresh_admin_btn.pack(side="left", padx=5)
    
    load_all_transactions()
    
    create_bottom_bar(frame, user)
    show_frame(frame)
    switch_tab("users")

# Start the app
def start():
    home_page()
    root.mainloop()