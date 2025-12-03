import tkinter as tk
from tkinter import ttk
import requests

class LogoutPage:
    def __init__(self, root, session, url, login):
        self.root = root
        self.url = url
        self.login_root = login
        self.session = session

        root.title("Library System - Logout")
        root.geometry("300x200")

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Logged in as: {session.role}", font=("Arial", 12)).pack(pady=10)

        logout_btn = ttk.Button(frame, text="Log Out", command=self.logout)
        logout_btn.pack(pady=10)

    def logout(self):
        # reset session
        try:
            response = requests.post(
                self.url + "/auth/logout",
                headers={"Authorization": f"Bearer {self.session.token}"}
            )

            if response.status_code != 200:
                print("Warning: backend logout failed:", response.json())

        except requests.exceptions.ConnectionError:
            print("Server offline — logout locally only.")

        self.session.token = None
        self.session.role = None
        self.session.user_id = None

        

        # close this window
        self.root.destroy()

        self.login_root.deiconify()