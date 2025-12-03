import tkinter as tk
from tkinter import ttk, messagebox
import requests

class BookPage:
    def __init__(self, root, session, url):
        self.root = root
        self.url = url
        self.session = session
        root.title("Library System - Books")
        root.geometry("420x260")

        if not self.session.token:
            warning_label = tk.Label(root, text="Unauthorized\nYou need to sign in first.", fg="red", font=("Arial", 14), justify="center")
            warning_label.pack(expand=True)  # centers it vertically & horizontally
            return

        else:
            pass
