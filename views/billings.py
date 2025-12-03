import tkinter as tk
from tkinter import ttk, messagebox
import requests


class BillingPage:
    def __init__(self, root, session, url):
        self.root = root
        self.url = url
        self.session = session
        root.title("Library System - Billings")
        root.geometry("420x260")

        if not self.session.token:
            warning_label = tk.Label(root, text="Unauthorized\nYou need to sign in first.", fg="red", font=("Arial", 14), justify="center")
            warning_label.pack(expand=True)  # centers it vertically & horizontally
            return

        elif self.session.role != "manager":
            warning_label = tk.Label(root, text="Unauthorized\nMust be a manager to view.", fg="red", font=("Arial", 14), justify="center")
            warning_label.pack(expand=True)  # centers it vertically & horizontally
            return
