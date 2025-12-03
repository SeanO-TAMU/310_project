import tkinter as tk
from tkinter import ttk, messagebox
import requests

class BookPage:
    def __init__(self, root, session, url):
        self.root = root
        self.url = url
        self.session = session

        root.title("Library System - Books")
        root.geometry("700x400")

        # --- AUTH CHECK ---
        if not self.session.token:
            warning = tk.Label(root, text="Unauthorized\nYou need to sign in first.", fg="red", font=("Arial", 14))
            warning.pack(expand=True)
            return
        
        # -------------------------
        # Search Bar Frame
        # -------------------------
        search_frame = ttk.Frame(root, padding=5)
        search_frame.pack(fill="x")

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)

        search_btn = ttk.Button(search_frame, text="Go", command=self.search_books)
        search_btn.pack(side="left", padx=5)

        reset_btn = ttk.Button(search_frame, text="Reset", command=self.load_books)
        reset_btn.pack(side="left", padx=5)
        

        # --- Table for Books ---
        self.tree = ttk.Treeview(root, columns=("ID", "Title", "Author", "Rent", "Buy", "Qty"), show="headings", height=15)
        self.tree.pack(fill="both", expand=True, pady=10)

        for col in ("ID", "Title", "Author", "Rent", "Buy", "Qty"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # Load books
        self.load_books()

    def load_books(self):
        """Fetch all books from backend and display them."""

        headers = {"Authorization": f"Bearer {self.session.token}"}

        try:
            response = requests.get(self.url + "/books/", headers=headers)

            if response.status_code != 200:
                messagebox.showerror("Error", "Unable to load books.")
                return

            books = response.json()["books"]

            # Clear old rows
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Insert books
            for b in books:
                self.tree.insert(
                    "", "end",
                    values=(b["bookID"], b["title"], b["author"], b["rental_price"], b["buy_price"], b["quantity"])
                )

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Server is unavailable.")

    def search_books(self):
        """Fetch all books from backend that match the search and display them."""
        
        query = self.search_entry.get().strip()

        if not query:
            messagebox.showwarning("Warning", "Enter text to search.")
            return

        headers = {"Authorization": f"Bearer {self.session.token}"}
        params = {"query": query}

        try:
            response = requests.get(self.url + "/books/search", headers=headers, params=params)

            if response.status_code != 200:
                messagebox.showerror("Error", "Unable to load books.")
                return

            books = response.json()["books"]

            # Clear old rows
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Insert books
            for b in books:
                self.tree.insert(
                    "", "end",
                    values=(b["bookID"], b["title"], b["author"], b["rental_price"], b["buy_price"], b["quantity"])
                )

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Server is unavailable.")
