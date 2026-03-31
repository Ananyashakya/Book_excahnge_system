"""
gui.py - BookSwap — Book Exchange System
Redesigned UI: warm literary aesthetic, animated home, rich cards,
hover effects, stat dashboard, review popup, profile page.
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import time
import threading

from database import (
    authenticate_user, register_user, is_valid_email,
    get_available_books, get_user_books, add_book, delete_book,
    request_exchange, get_user_transactions,
    get_all_users, get_all_transactions, update_transaction_status,
    add_review, get_book_reviews, get_all_reviews,
    get_user_profile, user_already_reviewed,
    get_books_reviewed_by_user,
)

#  DESIGN TOKENS 
C = {
    "bg":        "#F0F4FA",   # light blue-white
    "bg2":       "#E2EAF4",   # slightly deeper blue-white
    "card":      "#FFFFFF",
    "card2":     "#F7FAFF",
    "border":    "#B8CCDF",
    "ink":       "#0D1B2A",   # deep navy black
    "ink2":      "#2E4A6A",   # medium navy
    "muted":     "#6B84A0",   # muted steel blue
    "accent":    "#1A56A0",   # strong blue
    "accent2":   "#2E7DD1",   # lighter blue
    "gold":      "#1E6FBF",   # deep blue (replaces gold)
    "gold2":     "#5BA3E0",   # sky blue (replaces star gold)
    "success":   "#1A7A4A",   # green
    "danger":    "#C0392B",   # red
    "sidebar":   "#0D1B2A",   # deep navy sidebar
    "sidebar2":  "#1A2E45",
}

F = {
    "display":  ("Georgia", 38, "bold"),
    "h1":       ("Georgia", 26, "bold"),
    "h2":       ("Georgia", 18, "bold"),
    "h3":       ("Georgia", 13, "bold"),
    "body":     ("Helvetica", 11),
    "small":    ("Helvetica", 9),
    "mono":     ("Courier New", 10),
    "tag":      ("Helvetica", 9, "bold"),
}

#  ROOT WINDOW 
root = tk.Tk()
root.title("BookSwap")
root.geometry("1100x720")
root.configure(bg=C["bg"])
root.resizable(True, True)
root.update_idletasks()
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"1100x720+{(sw-1100)//2}+{(sh-720)//2}")
root.minsize(900, 600)

_frame = None

def show_frame(f):
    global _frame
    if _frame:
        _frame.destroy()
    _frame = f
    f.pack(fill="both", expand=True)


#  HELPERS 
def _btn(parent, text, cmd, style="accent", **kw):
    palettes = {
        "accent":   (C["accent"],  "#FFFFFF", C["accent2"]),
        "gold":     (C["gold"],    "#FFFFFF", C["gold2"]),
        "ghost":    (C["card"],    C["accent"], C["bg2"]),
        "danger":   (C["danger"],  "#FFFFFF", "#8B2020"),
        "success":  (C["success"], "#FFFFFF", "#2D5C3A"),
        "dark":     (C["sidebar"], "#FFFFFF", C["sidebar2"]),
        "outline":  (C["bg"],      C["accent"], C["bg2"]),
    }
    bg, fg, hover = palettes.get(style, palettes["accent"])
    b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                  font=F["h3"], relief="flat", cursor="hand2",
                  padx=18, pady=8, **kw)
    b.bind("<Enter>", lambda e: b.configure(bg=hover))
    b.bind("<Leave>", lambda e: b.configure(bg=bg))
    return b


def _entry(parent, width=34, show=None):
    e = tk.Entry(parent, width=width, bg=C["card"], fg=C["ink"],
                 insertbackground=C["ink"], relief="flat", font=F["body"],
                 highlightthickness=1, highlightbackground=C["border"],
                 highlightcolor=C["accent"], show=show or "")
    return e


def _label(parent, text, style="body", fg=None, bg=None, **kw):
    colors = {"display": C["ink"], "h1": C["ink"], "h2": C["ink"],
              "h3": C["ink"], "body": C["ink2"], "small": C["muted"],
              "accent": C["accent"], "gold": C["gold"]}
    return tk.Label(parent, text=text, font=F.get(style, F["body"]),
                    fg=fg or colors.get(style, C["ink2"]),
                    bg=bg or C["bg"], **kw)


def _divider(parent, color=None, thickness=1, pady=0):
    tk.Frame(parent, bg=color or C["border"],
             height=thickness).pack(fill="x", pady=pady)


def _card_frame(parent, bg=None, pad=20, border=True):
    f = tk.Frame(parent, bg=bg or C["card"],
                 highlightbackground=C["border"] if border else (bg or C["card"]),
                 highlightthickness=1 if border else 0,
                 padx=pad, pady=pad)
    return f


def _stars(rating, count=0):
    if not rating:
        return "  No ratings"
    r = round(float(rating))
    return "" * r + "" * (5 - r) + f"  {rating}/5" + (f" ({count})" if count else "")


def _treeview(parent, columns, height=13, bg=None):
    s = ttk.Style()
    bg = bg or C["card"]
    s.configure("Bk.Treeview", background=bg, foreground=C["ink"],
                fieldbackground=bg, rowheight=30, font=F["body"])
    s.configure("Bk.Treeview.Heading", background=C["bg2"],
                foreground=C["accent"], font=F["tag"])
    s.map("Bk.Treeview", background=[("selected", C["accent"])],
          foreground=[("selected", "#FFFFFF")])
    cols = [c[0] for c in columns]
    tv = ttk.Treeview(parent, columns=cols, show="headings",
                      height=height, style="Bk.Treeview")
    for col, w in columns:
        tv.heading(col, text=col)
        tv.column(col, width=w, anchor="center")
    sb = tk.Scrollbar(parent, orient="vertical", command=tv.yview,
                      bg=C["bg2"], troughcolor=C["bg"])
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return tv


#  SIDEBAR NAV 
def _sidebar(parent, user, tabs_def, default_tab, content_frame):
    """Left sidebar with navigation."""
    side = tk.Frame(parent, bg=C["sidebar"], width=200)
    side.pack(side="left", fill="y")
    side.pack_propagate(False)

    # Logo area
    logo_f = tk.Frame(side, bg=C["sidebar"], pady=24)
    logo_f.pack(fill="x")
    tk.Label(logo_f, text="", font=("Helvetica", 28),
             bg=C["sidebar"], fg=C["gold"]).pack()
    tk.Label(logo_f, text="BookSwap", font=F["h2"],
             bg=C["sidebar"], fg="#FFFFFF").pack()
    tk.Frame(side, bg=C["sidebar2"], height=1).pack(fill="x")

    # User chip
    user_f = tk.Frame(side, bg=C["sidebar2"], pady=12, padx=16)
    user_f.pack(fill="x")
    role = " Admin" if user.get("is_admin") else " Member"
    tk.Label(user_f, text=user["name"], font=F["h3"],
             bg=C["sidebar2"], fg="#FFFFFF").pack(anchor="w")
    tk.Label(user_f, text=role, font=F["small"],
             bg=C["sidebar2"], fg=C["gold"]).pack(anchor="w")

    tk.Frame(side, bg=C["sidebar2"], height=1).pack(fill="x", pady=(8, 0))

    # Tab buttons
    tabs = {}
    btn_refs = {}

    def switch(name):
        for t in tabs.values():
            t.pack_forget()
        tabs[name].pack(fill="both", expand=True)
        for n, b in btn_refs.items():
            b.configure(bg=C["sidebar2"] if n == name else C["sidebar"],
                        fg=C["gold"] if n == name else C["muted"])

    for icon, label, name in tabs_def:
        f = tk.Frame(content_frame, bg=C["bg"])
        tabs[name] = f

        b = tk.Button(side, text=f"  {icon}  {label}",
                      bg=C["sidebar"], fg=C["muted"],
                      font=F["body"], relief="flat", cursor="hand2",
                      anchor="w", padx=16, pady=12,
                      command=lambda n=name: switch(n))
        b.bind("<Enter>", lambda e, btn=b, n=name:
               btn.configure(bg=C["sidebar2"]) if n not in [k for k, v in btn_refs.items() if v.cget("bg") == C["sidebar2"]] else None)
        b.bind("<Leave>", lambda e, btn=b, n=name:
               btn.configure(bg=C["sidebar2"] if btn.cget("fg") == C["gold"] else C["sidebar"]))
        b.pack(fill="x")
        btn_refs[name] = b

    # Spacer + logout
    tk.Frame(side, bg=C["sidebar"]).pack(fill="both", expand=True)
    tk.Frame(side, bg=C["sidebar2"], height=1).pack(fill="x")

    logout_b = tk.Button(side, text="  ⎋  Logout",
                         bg=C["sidebar"], fg="#CC6666",
                         font=F["body"], relief="flat", cursor="hand2",
                         anchor="w", padx=16, pady=12,
                         command=home_page)
    logout_b.bind("<Enter>", lambda e: logout_b.configure(bg=C["danger"], fg="#FFFFFF"))
    logout_b.bind("<Leave>", lambda e: logout_b.configure(bg=C["sidebar"], fg="#CC6666"))
    logout_b.pack(fill="x")

    switch(default_tab)
    return tabs, switch


# 
#  HOME PAGE  — animated typewriter tagline
# 
def home_page():
    root.title("BookSwap")
    frame = tk.Frame(root, bg=C["bg"])

    # Split layout: decorative left, actions right
    left = tk.Frame(frame, bg=C["sidebar"], width=480)
    left.pack(side="left", fill="both")
    left.pack_propagate(False)

    right = tk.Frame(frame, bg=C["bg"])
    right.pack(side="right", fill="both", expand=True)

    #  Left decorative panel 
    tk.Label(left, text="", bg=C["sidebar"]).pack(pady=40)
    tk.Label(left, text="", font=("Helvetica", 56),
             bg=C["sidebar"], fg=C["gold"]).pack()
    tk.Label(left, text="BookSwap", font=("Georgia", 42, "bold"),
             bg=C["sidebar"], fg="#FFFFFF").pack(pady=(12, 4))

    tagline_var = tk.StringVar(value="")
    tk.Label(left, textvariable=tagline_var, font=("Georgia", 13, "italic"),
             bg=C["sidebar"], fg=C["gold"], wraplength=360,
             justify="center").pack(pady=8)

    # Animated typewriter
    full_text = "Exchange books. Share stories.\nBuild a reading community."
    def typewrite(i=0):
        if i <= len(full_text):
            tagline_var.set(full_text[:i] + ("" if i < len(full_text) else ""))
            root.after(45, typewrite, i + 1)
    root.after(400, typewrite)

    # Stats strip
    stats_f = tk.Frame(left, bg=C["sidebar2"], pady=20)
    stats_f.pack(fill="x", pady=40)
    for val, lbl in [("50+", "Books"), ("8", "Genres"), ("Free", "Always")]:
        sf = tk.Frame(stats_f, bg=C["sidebar2"])
        sf.pack(side="left", expand=True)
        tk.Label(sf, text=val, font=("Georgia", 22, "bold"),
                 bg=C["sidebar2"], fg=C["gold"]).pack()
        tk.Label(sf, text=lbl, font=F["small"],
                 bg=C["sidebar2"], fg=C["muted"]).pack()

    tk.Label(left, text="© 2025 BookSwap", font=F["small"],
             bg=C["sidebar"], fg=C["muted"]).pack(side="bottom", pady=16)

    #  Right action panel 
    center_r = tk.Frame(right, bg=C["bg"])
    center_r.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(center_r, text="Get Started", font=F["h1"],
             bg=C["bg"], fg=C["ink"]).pack(pady=(0, 6))
    _divider(center_r, C["gold"], 2, 4)
    tk.Label(center_r, text="Join thousands of book lovers\nexchanging stories.",
             font=F["body"], bg=C["bg"], fg=C["muted"],
             justify="center").pack(pady=12)

    btn_f = tk.Frame(center_r, bg=C["bg"])
    btn_f.pack(pady=20)
    _btn(btn_f, "  Login  ", login_page, "accent",
         width=16).pack(pady=6, fill="x")
    _btn(btn_f, "  Create Account  ", register_page, "ghost",
         width=16).pack(pady=6, fill="x")

    # Feature chips
    chips_f = tk.Frame(center_r, bg=C["bg"])
    chips_f.pack(pady=16)
    for chip in ["Secure Auth", "Book Reviews", "Profiles"]:
        tk.Label(chips_f, text=chip, font=F["small"],
                 bg=C["bg2"], fg=C["accent"],
                 padx=10, pady=4,
                 relief="flat").pack(side="left", padx=5)

    show_frame(frame)


# 
#  REGISTER
# 
def register_page():
    root.title("BookSwap — Register")
    frame = tk.Frame(root, bg=C["bg"])

    # Header strip
    hdr = tk.Frame(frame, bg=C["sidebar"], pady=20)
    hdr.pack(fill="x")
    tk.Label(hdr, text=" BookSwap", font=F["h2"],
             bg=C["sidebar"], fg=C["gold"]).pack(side="left", padx=24)
    _btn(hdr, "← Back", home_page, "ghost").pack(side="right", padx=24)

    body = tk.Frame(frame, bg=C["bg"])
    body.pack(expand=True, fill="both", padx=60, pady=30)

    # Left benefits
    left = tk.Frame(body, bg=C["bg"])
    left.pack(side="left", fill="both", expand=True, padx=(0, 30))

    tk.Label(left, text="Join BookSwap", font=F["h1"],
             bg=C["bg"], fg=C["ink"]).pack(anchor="w")
    tk.Label(left, text="Start exchanging books today.",
             font=F["body"], bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=4)
    _divider(left, C["gold"], 2, 8)

    for icon, text in [
        ("1.", "Browse 50+ books across 8 genres"),
        ("2.", "Secured with bcrypt encryption"),
        ("3.", "Full exchange tracking workflow"),
        ("4.", "Rate and review books"),
        ("5.", "Personal profile with stats"),
    ]:
        row = tk.Frame(left, bg=C["bg"], pady=6)
        row.pack(fill="x")
        tk.Label(row, text=icon, font=("Helvetica", 16),
                 bg=C["bg"], fg=C["accent"]).pack(side="left", padx=(0, 10))
        tk.Label(row, text=text, font=F["body"],
                 bg=C["bg"], fg=C["ink2"]).pack(side="left")

    # Right form
    right = _card_frame(body, pad=30)
    right.pack(side="right", fill="both", expand=True)

    tk.Label(right, text="Create Account", font=F["h2"],
             bg=C["card"], fg=C["ink"]).pack(anchor="w", pady=(0, 16))

    fields = {}
    for lbl, key, pw in [("Full Name", "name", False),
                          ("Email Address", "email", False),
                          ("Password", "pass", True),
                          ("Confirm Password", "confirm", True)]:
        tk.Label(right, text=lbl, font=F["small"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        e = _entry(right, show="*" if pw else None)
        e.pack(fill="x", ipady=6)
        fields[key] = e

    msg_var = tk.StringVar()
    tk.Label(right, textvariable=msg_var, font=F["small"],
             bg=C["card"], fg=C["danger"]).pack(pady=4)

    def do_register():
        name = fields["name"].get().strip()
        email = fields["email"].get().strip()
        pwd = fields["pass"].get()
        conf = fields["confirm"].get()
        if not all([name, email, pwd, conf]):
            msg_var.set("All fields are required.")
            return
        if not is_valid_email(email):
            msg_var.set("Invalid email format.")
            return
        if pwd != conf:
            msg_var.set("Passwords do not match.")
            return
        if len(pwd) < 6:
            msg_var.set("Password must be at least 6 characters.")
            return
        if not any(c.isupper() for c in pwd):
            msg_var.set("Password must contain an uppercase letter.")
            return

        if not any(c.isdigit() for c in pwd):
            msg_var.set("Password must contain a number.")
            return        
        ok, result = register_user(name, email, pwd)
        if ok:
            messagebox.showinfo("Welcome!", "Account created! Please log in.")
            login_page()
        else:
            msg_var.set(result)

    _btn(right, "Create Account →", do_register, "accent").pack(
        fill="x", pady=14)

    link_f = tk.Frame(right, bg=C["card"])
    link_f.pack()
    tk.Label(link_f, text="Already have an account?",
             font=F["small"], bg=C["card"], fg=C["muted"]).pack(side="left")
    tk.Button(link_f, text=" Sign in", font=F["small"],
              bg=C["card"], fg=C["accent"], relief="flat",
              cursor="hand2", command=login_page).pack(side="left")

    show_frame(frame)


# 
#  LOGIN
# 
def login_page():
    root.title("BookSwap — Login")
    frame = tk.Frame(root, bg=C["bg"])

    hdr = tk.Frame(frame, bg=C["sidebar"], pady=20)
    hdr.pack(fill="x")
    tk.Label(hdr, text=" BookSwap", font=F["h2"],
             bg=C["sidebar"], fg=C["gold"]).pack(side="left", padx=24)
    _btn(hdr, "← Back", home_page, "ghost").pack(side="right", padx=24)

    center = tk.Frame(frame, bg=C["bg"])
    center.place(relx=0.5, rely=0.5, anchor="center")

    card = _card_frame(center, pad=40)
    card.pack()

    tk.Label(card, text="", font=("Helvetica", 36),
             bg=C["card"], fg=C["accent"]).pack()
    tk.Label(card, text="Welcome Back", font=F["h1"],
             bg=C["card"], fg=C["ink"]).pack(pady=(4, 2))
    tk.Label(card, text="Sign in to your BookSwap account",
             font=F["small"], bg=C["card"], fg=C["muted"]).pack()
    _divider(card, C["border"], 1, 12)

    tk.Label(card, text="Email", font=F["small"],
             bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(6, 2))
    email_e = _entry(card)
    email_e.pack(fill="x", ipady=6)

    tk.Label(card, text="Password", font=F["small"],
             bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(10, 2))
    pass_e = _entry(card, show="*")
    pass_e.pack(fill="x", ipady=6)

    msg_var = tk.StringVar()
    tk.Label(card, textvariable=msg_var, font=F["small"],
             bg=C["card"], fg=C["danger"]).pack(pady=4)

    def do_login(event=None):
        email = email_e.get().strip()
        pwd = pass_e.get()
        if not email or not pwd:
            msg_var.set("Both fields are required.")
            return
        user = authenticate_user(email, pwd)
        if user:
            admin_dashboard(user) if user["is_admin"] else user_dashboard(user)
        else:
            msg_var.set("Incorrect email or password.")

    email_e.bind("<Return>", do_login)
    pass_e.bind("<Return>", do_login)

    _btn(card, "Sign In →", do_login, "accent").pack(fill="x", pady=14)

    hint = tk.Frame(card, bg=C["card"])
    hint.pack()
    tk.Label(hint, text="No account?", font=F["small"],
             bg=C["card"], fg=C["muted"]).pack(side="left")
    tk.Button(hint, text=" Register free", font=F["small"],
              bg=C["card"], fg=C["accent"], relief="flat",
              cursor="hand2", command=register_page).pack(side="left")

    # Admin hint
    hint2 = _card_frame(center, bg=C["bg2"], pad=10, border=True)
    hint2.pack(fill="x", pady=(12, 0))
    tk.Label(hint2, text="Admin:  admin@bookexchange.com  /  Admin@2025!",
             font=F["small"], bg=C["bg2"], fg=C["muted"]).pack()

    show_frame(frame)


# 
#  PROFILE PAGE
# 
def profile_page(user):
    root.title("BookSwap — My Profile")
    frame = tk.Frame(root, bg=C["bg"])

    hdr = tk.Frame(frame, bg=C["sidebar"], pady=20)
    hdr.pack(fill="x")
    tk.Label(hdr, text=" BookSwap — My Profile", font=F["h2"],
             bg=C["sidebar"], fg=C["gold"]).pack(side="left", padx=24)
    _btn(hdr, "← Dashboard", lambda: user_dashboard(user),
         "ghost").pack(side="right", padx=24)

    body = tk.Frame(frame, bg=C["bg"])
    body.pack(fill="both", expand=True, padx=40, pady=24)

    profile = get_user_profile(user["id"])

    #  Identity card 
    id_card = _card_frame(body, pad=28)
    id_card.pack(fill="x", pady=(0, 20))

    top_row = tk.Frame(id_card, bg=C["card"])
    top_row.pack(fill="x")

    # Avatar circle (drawn on canvas)
    av = tk.Canvas(top_row, width=72, height=72, bg=C["card"],
                   highlightthickness=0)
    av.pack(side="left", padx=(0, 20))
    av.create_oval(4, 4, 68, 68, fill=C["accent"], outline="")
    initials = "".join(w[0].upper() for w in profile["name"].split()[:2])
    av.create_text(36, 36, text=initials, font=("Georgia", 22, "bold"),
                   fill="#FFFFFF")

    info = tk.Frame(top_row, bg=C["card"])
    info.pack(side="left")
    tk.Label(info, text=profile["name"], font=F["h1"],
             bg=C["card"], fg=C["ink"]).pack(anchor="w")
    tk.Label(info, text=profile["email"], font=F["body"],
             bg=C["card"], fg=C["muted"]).pack(anchor="w")
    tk.Label(info, text=f"Member since {profile['member_since']}",
             font=F["small"], bg=C["card"], fg=C["accent"]).pack(anchor="w")

    #  Stats grid 
    _divider(body, C["border"], 1, 4)
    tk.Label(body, text="Your Activity", font=F["h2"],
             bg=C["bg"], fg=C["ink"]).pack(anchor="w", pady=(8, 12))

    stats_grid = tk.Frame(body, bg=C["bg"])
    stats_grid.pack(fill="x")

    stat_items = [
        ("Bk", profile["books_listed"],     "Books Listed",     C["accent"]),
        ("Ok", profile["books_available"],   "Available Now",    C["success"]),
        ("Ex", profile["exchanges_done"],    "Exchanges Done",   C["gold"]),
        ("-", profile["pending_requests"],  "Pending",          C["ink2"]),
        ("Rv", profile["reviews_given"],     "Reviews Given",    C["accent2"]),
    ]

    for i, (icon, val, lbl, color) in enumerate(stat_items):
        sc = tk.Frame(stats_grid, bg=C["card"],
                      highlightbackground=C["border"], highlightthickness=1,
                      padx=20, pady=20)
        sc.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")
        stats_grid.columnconfigure(i, weight=1)

        # Colored top bar
        tk.Frame(sc, bg=color, height=3).pack(fill="x", pady=(0, 10))
        tk.Label(sc, text=icon, font=("Helvetica", 24),
                 bg=C["card"], fg=color).pack()
        tk.Label(sc, text=str(val), font=("Georgia", 30, "bold"),
                 bg=C["card"], fg=C["ink"]).pack()
        tk.Label(sc, text=lbl, font=F["small"],
                 bg=C["card"], fg=C["muted"]).pack()

    show_frame(frame)


# 
#  REVIEW POPUP
# 
def review_popup(book_id, book_title, user_id):
    win = tk.Toplevel(root)
    win.title(f"Reviews — {book_title}")
    win.geometry("640x580")
    win.configure(bg=C["bg"])
    win.grab_set()

    # Header
    hdr = tk.Frame(win, bg=C["sidebar"], pady=14, padx=20)
    hdr.pack(fill="x")
    tk.Label(hdr, text=f"{book_title}", font=F["h3"],
             bg=C["sidebar"], fg=C["gold"]).pack(side="left")
    tk.Button(hdr, text="X", bg=C["sidebar"], fg=C["muted"],
              relief="flat", cursor="hand2",
              command=win.destroy).pack(side="right")

    # Scrollable reviews
    rv_outer = tk.Frame(win, bg=C["bg"])
    rv_outer.pack(fill="both", expand=True, padx=16, pady=12)

    rv_canvas = tk.Canvas(rv_outer, bg=C["bg"], highlightthickness=0)
    rv_scroll = tk.Scrollbar(rv_outer, orient="vertical",
                            command=rv_canvas.yview)
    rv_canvas.configure(yscrollcommand=rv_scroll.set)

    rv_scroll.pack(side="right", fill="y")
    rv_canvas.pack(side="left", fill="both", expand=True)

    rv_inner = tk.Frame(rv_canvas, bg=C["bg"])
    rv_canvas.create_window((0, 0), window=rv_inner, anchor="nw")

    rv_inner.bind("<Configure>",
                  lambda e: rv_canvas.configure(
                      scrollregion=rv_canvas.bbox("all")))

    def load_reviews():
        for w in rv_inner.winfo_children():
            w.destroy()

        reviews = get_book_reviews(book_id)

        # ✅ Average rating
        if reviews:
            avg = sum(r["rating"] for r in reviews) / len(reviews)
            tk.Label(rv_inner,
                     text=f"Average Rating: {round(avg,1)} / 5",
                     font=F["h3"],
                     bg=C["bg"],
                     fg=C["accent"]).pack(pady=8)

        # ✅ Empty state
        if not reviews:
            tk.Label(rv_inner, text="No reviews yet",
                     font=("Georgia", 16, "bold"),
                     bg=C["bg"], fg=C["muted"]).pack(pady=(30, 5))
            tk.Label(rv_inner,
                     text="Be the first to share your thoughts",
                     font=F["body"],
                     bg=C["bg"], fg=C["muted"]).pack()
            return

        # ✅ Review cards
        for rv in reviews:
            rc = tk.Frame(rv_inner, bg=C["card"],
                          highlightbackground=C["border"],
                          highlightthickness=1,
                          padx=12, pady=10)
            rc.pack(fill="x", pady=6)

            top = tk.Frame(rc, bg=C["card"])
            top.pack(fill="x")

            tk.Label(top, text=rv["reviewer"], font=F["h3"],
                     bg=C["card"], fg=C["accent"]).pack(side="left")

            tk.Label(top,
                     text="★" * rv["rating"] + "☆" * (5 - rv["rating"]),
                     font=("Helvetica", 12),
                     bg=C["card"],
                     fg=C["gold2"]).pack(side="right")

            if rv["review"]:
                tk.Label(rc, text=rv["review"], font=F["body"],
                         bg=C["card"], fg=C["ink2"],
                         wraplength=560, justify="left").pack(
                    anchor="w", pady=(6, 2))

            tk.Label(rc, text=str(rv["created_at"])[:10],
                     font=F["small"], bg=C["card"],
                     fg=C["muted"]).pack(anchor="w")

    load_reviews()

    # Divider
    _divider(win, C["border"], 1, 0)

    # Submit section
    submit_f = tk.Frame(win, bg=C["bg2"], padx=16, pady=12)
    submit_f.pack(fill="x")

    tk.Label(submit_f, text="Your Rating",
             font=F["body"], bg=C["bg2"],
             fg=C["muted"]).pack(anchor="w")

    # ✅ Star rating UI
    rating_var = tk.IntVar(value=5)
    star_frame = tk.Frame(submit_f, bg=C["bg2"])
    star_frame.pack(anchor="w", pady=5)

    stars = []

    def set_rating(val):
        rating_var.set(val)
        for i, s in enumerate(stars):
            s.config(text="★" if i < val else "☆")

    for i in range(5):
        lbl = tk.Label(star_frame, text="☆",
                       font=("Helvetica", 20),
                       bg=C["bg2"],
                       fg=C["gold2"],
                       cursor="hand2")
        lbl.bind("<Button-1>", lambda e, v=i+1: set_rating(v))
        lbl.pack(side="left", padx=2)
        stars.append(lbl)

    set_rating(5)

    tk.Label(submit_f, text="Comment (optional)",
             font=F["small"], bg=C["bg2"],
             fg=C["muted"]).pack(anchor="w")

    review_txt = tk.Text(submit_f, height=3,
                         bg=C["card"], fg=C["ink"],
                         insertbackground=C["ink"],
                         relief="flat", font=F["body"],
                         highlightthickness=1,
                         highlightbackground=C["border"])
    review_txt.pack(fill="x", pady=4)

    def submit():
        submit_btn.config(state="disabled")

        ok, msg = add_review(
            book_id,
            user_id,
            rating_var.get(),
            review_txt.get("1.0", "end").strip()
        )

        if ok:
            messagebox.showinfo("Success", "Review submitted successfully")
            review_txt.delete("1.0", "end")
            load_reviews()
        else:
            messagebox.showerror("Error", msg)

        submit_btn.config(state="normal")

    btn_row = tk.Frame(submit_f, bg=C["bg2"])
    btn_row.pack(pady=6)

    submit_btn = _btn(btn_row, "Submit Review", submit,
                     "accent", width=22)
    submit_btn.pack()
#  USER DASHBOARD
# 
def user_dashboard(user):
    root.title(f"BookSwap — {user['name']}")
    frame = tk.Frame(root, bg=C["bg"])

    # Sidebar + content area
    content_area = tk.Frame(frame, bg=C["bg"])
    content_area.pack(side="right", fill="both", expand=True)

    tabs_def = [
    ("-", "Browse Books",  "browse"),
    ("-", "List a Book",   "list"),
    ("-", "My Books",      "mybooks"),
    ("-", "Transactions",  "trans"),
    ("-", "My Reviews",    "reviews"),  
    ("-", "My Profile",    "profile"),
]

    tabs, switch = _sidebar(frame, user, tabs_def, "browse", content_area)

    #  PROFILE TAB 
    prof_t = tabs["profile"]
    prof_t.configure(bg=C["bg"])

    def build_profile():
        for w in prof_t.winfo_children():
            w.destroy()
        profile = get_user_profile(user["id"])

        # Header
        ph = tk.Frame(prof_t, bg=C["bg"], padx=20, pady=14)
        ph.pack(fill="x")
        tk.Label(ph, text="My Profile", font=F["h1"],
                 bg=C["bg"], fg=C["ink"]).pack(side="left")
        _btn(ph, "Refresh", build_profile, "ghost").pack(side="right")
        _divider(prof_t, C["border"], 1, 0)

        # Identity card
        id_card = _card_frame(prof_t, pad=24)
        id_card.pack(fill="x", padx=20, pady=12)
        top_row = tk.Frame(id_card, bg=C["card"])
        top_row.pack(fill="x")

        av = tk.Canvas(top_row, width=72, height=72,
                       bg=C["card"], highlightthickness=0)
        av.pack(side="left", padx=(0, 18))
        av.create_oval(4, 4, 68, 68, fill=C["accent"], outline="")
        initials = "".join(ww[0].upper() for ww in profile["name"].split()[:2])
        av.create_text(36, 36, text=initials,
                       font=("Georgia", 22, "bold"), fill="#FFFFFF")

        info = tk.Frame(top_row, bg=C["card"])
        info.pack(side="left")
        tk.Label(info, text=profile["name"], font=F["h1"],
                 bg=C["card"], fg=C["ink"]).pack(anchor="w")
        tk.Label(info, text=profile["email"], font=F["body"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w")
        tk.Label(info, text=f"Member since {profile['member_since']}",
                 font=F["small"], bg=C["card"], fg=C["accent"]).pack(anchor="w")

        # Activity heading
        tk.Label(prof_t, text="Your Activity  —  click any card to view details",
                 font=F["body"], bg=C["bg"], fg=C["muted"],
                 padx=20).pack(anchor="w", pady=(12, 4))

        sg = tk.Frame(prof_t, bg=C["bg"], padx=20)
        sg.pack(fill="x")

        # Each stat card with a clickable "View" button
        stat_items = [
            ("Books Listed",   profile["books_listed"],
             C["accent"],  lambda: switch("mybooks")),
            ("Available Now",  profile["books_available"],
             C["success"], lambda: switch("mybooks")),
            ("Exchanges Done", profile["exchanges_done"],
             C["gold"],    lambda: switch("trans")),
            ("Pending",        profile["pending_requests"],
             C["danger"],  lambda: [switch("trans"), load_trans_tab()]),
            ("Reviews Given",  profile["reviews_given"],
             C["accent2"], lambda: switch("reviews")),
        ]

        for i, (lbl, val, color, action) in enumerate(stat_items):
            sc = tk.Frame(sg, bg=C["card"],
                          highlightbackground=C["border"],
                          highlightthickness=1,
                          padx=14, pady=14,
                          cursor="hand2")
            sc.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
            sg.columnconfigure(i, weight=1)

            # Colored top accent bar
            tk.Frame(sc, bg=color, height=4).pack(fill="x", pady=(0, 10))
            tk.Label(sc, text=str(val),
                     font=("Georgia", 28, "bold"),
                     bg=C["card"], fg=C["ink"]).pack()
            tk.Label(sc, text=lbl, font=F["small"],
                     bg=C["card"], fg=C["muted"]).pack()

            # Clickable "View" button inside card
            view_btn = tk.Button(sc, text="View",
                                 font=F["small"], bg=C["bg2"],
                                 fg=color, relief="flat",
                                 cursor="hand2", padx=8, pady=3,
                                 command=action)
            view_btn.bind("<Enter>", lambda e, b=view_btn, c=color:
                          b.configure(bg=c, fg="#FFFFFF"))
            view_btn.bind("<Leave>", lambda e, b=view_btn, c=color:
                          b.configure(bg=C["bg2"], fg=c))
            view_btn.pack(pady=(8, 0))

            # Make whole card clickable too
            for widget in (sc,):
                widget.bind("<Button-1>", lambda e, a=action: a())

    def load_trans_tab():
        # reload transactions so pending ones show immediately
        for tab_name, tab_frame in tabs.items():
            if tab_name == "trans":
                for child in tab_frame.winfo_children():
                    if hasattr(child, '_load_trans'):
                        child._load_trans()
                break

    build_profile()

    #  BROWSE TAB 
    bt = tabs["browse"]
    bt.configure(bg=C["bg"])

    top_bar = tk.Frame(bt, bg=C["bg"], pady=10, padx=20)
    top_bar.pack(fill="x")
    tk.Label(top_bar, text="Available Books", font=F["h2"],
             bg=C["bg"], fg=C["ink"]).pack(side="left")

    search_f = tk.Frame(bt, bg=C["bg"], padx=20, pady=6)
    search_f.pack(fill="x")
    sv = tk.StringVar()
    se = _entry(search_f, width=44)
    se.configure(textvariable=sv)
    se.pack(side="left", ipady=6, padx=(0, 8))
    _btn(search_f, "Search", lambda: load_books(), "accent").pack(side="left", padx=4)
    _btn(search_f, "All", lambda: [sv.set(""), load_books()],
         "ghost").pack(side="left", padx=4)

    tree_f = tk.Frame(bt, bg=C["bg"], padx=20)
    tree_f.pack(fill="both", expand=True)
    browse_tree = _treeview(tree_f, [
        ("Title", 185), ("Author", 135), ("Genre", 100),
        ("Condition", 78), ("Owner", 105), ("Rating", 130), ("Reviews", 65)
    ])

    def load_books():
        browse_tree.delete(*browse_tree.get_children())
        for b in get_available_books(sv.get()):
            rating = _stars(b["avg_rating"], b["review_count"]) \
                     if b["avg_rating"] else "—"
            browse_tree.insert("", "end", iid=b["id"],
                               values=(b["title"], b["author"],
                                       b["genre"] or "—", b["condition_"],
                                       b["owner"], rating,
                                       b["review_count"]))

    act_f = tk.Frame(bt, bg=C["bg"], padx=20, pady=8)
    act_f.pack(fill="x")

    def request_sel():
        sel = browse_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a book first.")
            return
        ok, msg = request_exchange(int(sel[0]), user["id"])
        messagebox.showinfo("Done", msg) if ok else messagebox.showerror("Error", msg)
        load_books()

    def open_review():
        sel = browse_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a book to review.")
            return
        vals = browse_tree.item(sel[0])["values"]
        review_popup(int(sel[0]), vals[0], user["id"])

    _btn(act_f, "  Request Exchange", request_sel, "accent").pack(
        side="left", padx=(0, 8))
    _btn(act_f, "  Rate & Review", open_review, "ghost").pack(side="left")

    load_books()

    #  LIST A BOOK TAB 
    lt = tabs["list"]
    lt.configure(bg=C["bg"])

    lform_outer = tk.Frame(lt, bg=C["bg"])
    lform_outer.place(relx=0.5, rely=0.5, anchor="center")

    lcard = _card_frame(lform_outer, pad=36)
    lcard.pack()

    tk.Label(lcard, text="List a Book", font=F["h1"],
             bg=C["card"], fg=C["ink"]).pack(anchor="w")
    tk.Label(lcard, text="Make your book available for the community",
             font=F["small"], bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=4)
    _divider(lcard, C["gold"], 2, 8)

    fields_l = {}
    for lbl, key in [("Book Title", "title"), ("Author", "author"),
                     ("Genre", "genre")]:
        tk.Label(lcard, text=lbl, font=F["small"],
                 bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
        e = _entry(lcard)
        e.pack(fill="x", ipady=6)
        fields_l[key] = e

    tk.Label(lcard, text="Condition", font=F["small"],
             bg=C["card"], fg=C["muted"]).pack(anchor="w", pady=(8, 2))
    cond_v = tk.StringVar(value="Good")
    cond_row = tk.Frame(lcard, bg=C["card"])
    cond_row.pack(fill="x")
    for cond in ["Like New", "Good", "Fair", "Worn"]:
        tk.Radiobutton(cond_row, text=cond, variable=cond_v, value=cond,
                       bg=C["card"], fg=C["ink2"],
                       selectcolor=C["bg2"], font=F["body"],
                       activebackground=C["card"]).pack(side="left", padx=6)

    list_msg = tk.StringVar()
    tk.Label(lcard, textvariable=list_msg, font=F["small"],
             bg=C["card"], fg=C["success"]).pack(pady=4)

    def do_add():
        ok, msg = add_book(fields_l["title"].get(),
                           fields_l["author"].get(),
                           fields_l["genre"].get(),
                           cond_v.get(), user["id"])
        if ok:
            list_msg.set(" Book listed successfully!")
            for e in fields_l.values():
                e.delete(0, "end")
            refresh_mybooks()
        else:
            list_msg.set(f" {msg}")

    _btn(lcard, "List Book →", do_add, "accent").pack(fill="x", pady=14)

    #  MY BOOKS TAB 
    mt = tabs["mybooks"]
    mt.configure(bg=C["bg"])

    tk.Label(mt, text="My Listed Books", font=F["h2"],
             bg=C["bg"], fg=C["ink"], padx=20).pack(anchor="w", pady=(14, 6))

    mb_f = tk.Frame(mt, bg=C["bg"], padx=20)
    mb_f.pack(fill="both", expand=True)
    mb_tree = _treeview(mb_f, [
        ("Title", 200), ("Author", 140), ("Genre", 110),
        ("Condition", 82), ("Status", 78), ("Listed", 148)
    ])

    def refresh_mybooks():
        mb_tree.delete(*mb_tree.get_children())
        for b in get_user_books(user["id"]):
            mb_tree.insert("", "end", iid=b["id"],
                           values=(b["title"], b["author"],
                                   b["genre"] or "—", b["condition_"],
                                   "Available" if b["is_available"] else "Pending",
                                   str(b["listed_at"])[:16]))

    def remove_book():
        sel = mb_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a book to remove.")
            return
        if messagebox.askyesno("Confirm", "Remove this book from the exchange?"):
            if delete_book(int(sel[0]), user["id"]):
                refresh_mybooks()
            else:
                messagebox.showerror("Error", "Could not remove book.")

    mb_act = tk.Frame(mt, bg=C["bg"], padx=20, pady=8)
    mb_act.pack(fill="x")
    _btn(mb_act, "  Remove", remove_book, "danger").pack(side="left", padx=(0, 8))
    _btn(mb_act, "↺  Refresh", refresh_mybooks, "ghost").pack(side="left")
    refresh_mybooks()

    #  TRANSACTIONS TAB 
    tt = tabs["trans"]
    tt.configure(bg=C["bg"])

    tk.Label(tt, text="My Transactions", font=F["h2"],
             bg=C["bg"], fg=C["ink"], padx=20).pack(anchor="w", pady=(14, 6))

    tr_f = tk.Frame(tt, bg=C["bg"], padx=20)
    tr_f.pack(fill="both", expand=True)
    tr_tree = _treeview(tr_f, [
    ("ID", 40), ("BookID", 80), ("Book", 180), ("Author", 120),
    ("Requester", 110), ("Owner", 110), ("Status", 88), ("Date", 132)
])

    def load_trans():
        tr_tree.delete(*tr_tree.get_children())
        for t in get_user_transactions(user["id"]):
             tr_tree.insert("", "end", iid=t["id"],
                values=(
            t["id"],
            t["book_id"],   # NEW (important)
            t["title"],
            t["author"],
            t["requester"],
            t["owner"],
            t["status"],
            str(t["created_at"])[:16]
        )
    )

    tr_act = tk.Frame(tt, bg=C["bg"], padx=20, pady=8)
    tr_act.pack(fill="x")
        
    _btn(tr_act, "↺  Refresh", load_trans, "ghost").pack(side="left")
    load_trans()

    show_frame(frame)


    #  MY REVIEWS TAB 
    rt = tabs["reviews"]
    rt.configure(bg=C["bg"])

    tk.Label(rt, text="My Reviewed Books", font=F["h2"],
            bg=C["bg"], fg=C["ink"], padx=20).pack(anchor="w", pady=(14, 6))

    rf = tk.Frame(rt, bg=C["bg"], padx=20)
    rf.pack(fill="both", expand=True)

    reviews_tree = _treeview(rf, [
        ("Title", 200), ("Author", 140),
        ("Rating", 80), ("Review", 300), ("Date", 120)
    ])

    def load_my_reviews():
        reviews_tree.delete(*reviews_tree.get_children())

        data = get_books_reviewed_by_user(user["id"])

        if not data:
            messagebox.showinfo("Info", "No reviews yet.")
            return

        avg = sum(r["rating"] for r in data) / len(data)

        # Remove old label if exists
        for widget in rt.winfo_children():
            if isinstance(widget, tk.Label) and "Average Rating" in widget.cget("text"):
                widget.destroy()

        tk.Label(rt, text=f"Average Rating: {round(avg,1)} / 5",
                font=F["h3"], bg=C["bg"], fg=C["accent"]).pack(pady=5)

        for r in data:
            reviews_tree.insert("", "end", values=(
                r["title"],
                r["author"],
                r["rating"],
                r["review"] or "—",
                str(r["created_at"])[:16]
            ))

    load_my_reviews()

# 
#  ADMIN DASHBOARD
# 
def admin_dashboard(user):
    root.title("BookSwap — Admin Panel")
    frame = tk.Frame(root, bg=C["bg"])

    content_area = tk.Frame(frame, bg=C["bg"])
    content_area.pack(side="right", fill="both", expand=True)

    tabs_def = [
        ("U ", "Users",        "users"),
        ("B ", "All Books",    "books"),
        ("~ ", "Transactions", "trans"),
        ("R ", "Reviews",      "reviews"),
    ]

    tabs, switch = _sidebar(frame, user, tabs_def, "users", content_area)

    #  USERS 
    ut = tabs["users"]
    ut.configure(bg=C["bg"])
    tk.Label(ut, text="Registered Users", font=F["h2"],
             bg=C["bg"], fg=C["ink"], padx=20).pack(anchor="w", pady=(14, 6))
    uf = tk.Frame(ut, bg=C["bg"], padx=20)
    uf.pack(fill="both", expand=True)
    users_tree = _treeview(uf, [
        ("ID", 50), ("Name", 180), ("Email", 230),
        ("Role", 70), ("Joined", 148)
    ])

    def load_users():
        users_tree.delete(*users_tree.get_children())
        for u in get_all_users():
            users_tree.insert("", "end", values=(
                u["id"], u["name"], u["email"],
                "Admin" if u["is_admin"] else "Member",
                str(u["created_at"])[:16]))

    u_act = tk.Frame(ut, bg=C["bg"], padx=20, pady=8)
    u_act.pack(fill="x")
    _btn(u_act, "↺  Refresh", load_users, "ghost").pack(side="left")
    load_users()

    #  ALL BOOKS 
    bkt = tabs["books"]
    bkt.configure(bg=C["bg"])
    tk.Label(bkt, text="All Listed Books", font=F["h2"],
             bg=C["bg"], fg=C["ink"], padx=20).pack(anchor="w", pady=(14, 6))
    bkf = tk.Frame(bkt, bg=C["bg"], padx=20)
    bkf.pack(fill="both", expand=True)
    bk_tree = _treeview(bkf, [
        ("Title", 185), ("Author", 135), ("Genre", 100),
        ("Condition", 80), ("Owner", 118), ("Rating", 128)
    ])

    def load_all_books():
        bk_tree.delete(*bk_tree.get_children())
        for b in get_available_books():
            bk_tree.insert("", "end", iid=b["id"],
                           values=(b["title"], b["author"],
                                   b["genre"] or "—", b["condition_"],
                                   b["owner"],
                                   _stars(b["avg_rating"]) if b["avg_rating"] else "—"))

    def admin_del():
        sel = bk_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a book.")
            return
        if messagebox.askyesno("Confirm", "Permanently delete this book?"):
            delete_book(int(sel[0]), user["id"], is_admin=True)
            load_all_books()

    bk_act = tk.Frame(bkt, bg=C["bg"], padx=20, pady=8)
    bk_act.pack(fill="x")
    _btn(bk_act, "  Delete", admin_del, "danger").pack(side="left", padx=(0, 8))
    _btn(bk_act, "↺  Refresh", load_all_books, "ghost").pack(side="left")
    load_all_books()

    #  TRANSACTIONS 
    trt = tabs["trans"]
    trt.configure(bg=C["bg"])
    tk.Label(trt, text="All Transactions", font=F["h2"],
             bg=C["bg"], fg=C["ink"], padx=20).pack(anchor="w", pady=(14, 6))
    trf = tk.Frame(trt, bg=C["bg"], padx=20)
    trf.pack(fill="both", expand=True)
    tr_tree = _treeview(trf, [
        ("ID", 42), ("Book", 168), ("Author", 120),
        ("Requester", 110), ("Owner", 110), ("Status", 90), ("Date", 130)
    ])

    cache = []

    def load_all_trans():
        nonlocal cache
        tr_tree.delete(*tr_tree.get_children())
        cache = get_all_transactions()
        for t in cache:
            tr_tree.insert("", "end", iid=t["id"],
                           values=(t["id"], t["title"], t["author"],
                                   t["requester"], t["owner"],
                                   t["status"], str(t["created_at"])[:16]))

    def change_status(status):
        sel = tr_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a transaction.")
            return
        t_id = int(sel[0])
        row = next((r for r in cache if r["id"] == t_id), None)
        book_id = row.get("book_id", 0) if row else 0
        update_transaction_status(t_id, status, book_id)
        load_all_trans()

    tr_act = tk.Frame(trt, bg=C["bg"], padx=20, pady=8)
    tr_act.pack(fill="x")
    _btn(tr_act, "  Approve",  lambda: change_status("Approved"),
         "success").pack(side="left", padx=(0, 6))
    _btn(tr_act, "  Reject",   lambda: change_status("Rejected"),
         "danger").pack(side="left", padx=(0, 6))
    _btn(tr_act, "  Complete", lambda: change_status("Completed"),
         "gold").pack(side="left", padx=(0, 6))
    _btn(tr_act, "↺  Refresh",  load_all_trans,
         "ghost").pack(side="left")
    load_all_trans()

    #  REVIEWS 
    rvt = tabs["reviews"]
    rvt.configure(bg=C["bg"])
    tk.Label(rvt, text="All Reviews", font=F["h2"],
             bg=C["bg"], fg=C["ink"], padx=20).pack(anchor="w", pady=(14, 6))
    rvf = tk.Frame(rvt, bg=C["bg"], padx=20)
    rvf.pack(fill="both", expand=True)
    rv_tree = _treeview(rvf, [
        ("Book", 195), ("Reviewer", 135), ("Rating", 70),
        ("Review", 295), ("Date", 115)
    ])

    def load_reviews():
        rv_tree.delete(*rv_tree.get_children())
        for r in get_all_reviews():
            rv_tree.insert("", "end",
                           values=(r["title"], r["reviewer"],
                                   _stars(r["rating"]),
                                   r["review"] or "—",
                                   str(r["created_at"])[:16]))

    rv_act = tk.Frame(rvt, bg=C["bg"], padx=20, pady=8)
    rv_act.pack(fill="x")
    _btn(rv_act, "↺  Refresh", load_reviews, "ghost").pack(side="left")
    load_reviews()

    show_frame(frame)


#  Entry 
def start():
    home_page()
    root.mainloop()