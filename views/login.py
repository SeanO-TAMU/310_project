import tkinter as tk
from tkinter import ttk, messagebox
import requests
from views.logout import LogoutPage
from views.books import BookPage
from views.billings import BillingPage


class LoginPage:
    def __init__(self, root, session, url):
        self.root = root
        self.url = url
        self.session = session
        root.title("Library System - Login")
        root.geometry("420x260")  # adjust as needed

        # --- Main Frame ---
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        # -------------------------
        # Input Fields
        # -------------------------

        # Name
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=0, column=1, pady=5)

        # Email
        ttk.Label(frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        email_entry = ttk.Entry(frame, width=30)
        email_entry.grid(row=1, column=1, pady=5)

        # Password
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        password_entry = ttk.Entry(frame, show="*", width=30)
        password_entry.grid(row=2, column=1, pady=5)

        # Error Label
        self.error_label = ttk.Label(frame, text="", foreground="red")
        self.error_label.grid(row=4, columnspan=2, pady=5)

        # -------------------------
        # Action Buttons (Row)
        # -------------------------

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, columnspan=2, pady=20)

        # Spacing config
        for i in range(3):
            button_frame.columnconfigure(i, pad=10)

        login_btn = ttk.Button(button_frame, text="Login",command=lambda: self.login_user(email_entry.get(), password_entry.get()))
        signup_customer_btn = ttk.Button(button_frame, text="Sign Up (Customer)", command=lambda: self.sign_up_cust(name_entry.get(), email_entry.get(), password_entry.get()))
        signup_manager_btn = ttk.Button(button_frame, text="Sign Up (Manager)", command=lambda: self.sign_up_man(name_entry.get(), email_entry.get(), password_entry.get()))

        login_btn.grid(row=0, column=0, padx=5)
        signup_customer_btn.grid(row=0, column=1, padx=5)
        signup_manager_btn.grid(row=0, column=2, padx=5)

    def login_user(self, email, password):

        if not email.strip() or not password.strip():
            messagebox.showerror("Error", "Email and password are required.")
            return
        
        email = email.strip()
        password =password.strip()

        print("Login: ", email, password)

        # payload for the server
        data = {
            "email": email,
            "password": password
        }

        try:
            response = requests.post(self.url + "/auth/login", json=data)

            if response.status_code == 200:
                result = response.json()
                print("Login successful:", result)
                self.session.user_id = result["userID"]
                self.session.role = result["role"]
                self.session.token = result["token"]

                # TODO: open next screen
                # close login window
                self.root.withdraw()

                # open LogoutPage window
                logout_win = tk.Toplevel()
                LogoutPage(logout_win, self.session, self.url, self.root)

                books_win = tk.Toplevel(self.root)
                BookPage(books_win, self.session, self.url)

                billings_win = tk.Toplevel(self.root)
                BillingPage(billings_win, self.session, self.url)

            else:
                self.error_label.config(text="Invalid email or password.")

        except requests.exceptions.ConnectionError:
            self.error_label.config(text="Server unavailable.")

    def sign_up_cust(self, name, email, password):

        if not name.strip() or not email.strip() or not password.strip():
            messagebox.showerror("Error", "Name, email and password are required.")

        email = email.strip()
        password =password.strip()
        name = name.strip()

        print("Sign up as customer: ", name, email, password)
        
        data = {
            "name": name,
            "email": email,
            "password": password
        }

        try:
            response = requests.post(self.url + "/users/", json=data)
            
            if response.status_code == 201:
                print("User created successfully")
                self.login_user(email, password)
        
        except requests.exceptions.ConnectionError:
            self.error_label.config(text="Server unavailable.")

        # need to call sign up route and then after call the log in route
    
       
    def sign_up_man(self, name, email, password):

        if not name.strip() or not email.strip() or not password.strip():
            messagebox.showerror("Error", "Name, email and password are required.")

        # need to call sign up route and then after call the log in route

        email = email.strip()
        password =password.strip()
        name = name.strip()
        
        print("Sign up as manager: ", name, email, password)
        
        data = {
            "name": name,
            "email": email,
            "password": password
        }

        try:
            response = requests.post(self.url + "/users/manager", json=data)
            
            if response.status_code == 201:
                print("User created successfully")
                self.login_user(email, password)
        
        except requests.exceptions.ConnectionError:
            self.error_label.config(text="Server unavailable.")