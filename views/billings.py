import tkinter as tk
from tkinter import ttk, messagebox
import requests


class BillingPage:
    def __init__(self, root, session, url):
        self.root = root
        self.url = url
        self.session = session
        root.title("Library System - Billings")
        root.geometry("650x400")

        # --- UNAUTHORIZED STATES ---
        if not self.session.token:
            warning_label = tk.Label(
                root,
                text="Unauthorized\nYou need to sign in first.",
                fg="red",
                font=("Arial", 14),
                justify="center"
            )
            warning_label.pack(expand=True)
            return

        if self.session.role != "manager":
            warning_label = tk.Label(
                root,
                text="Unauthorized\nMust be a manager to view.",
                fg="red",
                font=("Arial", 14),
                justify="center"
            )
            warning_label.pack(expand=True)
            return

        # --- MAIN FRAME ---
        frame = tk.Frame(root)
        frame.pack(fill="both", expand=True)

        # TABLE (Treeview)
        columns = ("ID", "UserID", "Date", "Total", "Status")
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=110)

        self.table.pack(fill="both", expand=True)

        # BUTTONS
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="View Billing", command=self.view_billing).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Mark as Paid", command=self.update_status).grid(row=0, column=1, padx=10)

        self.load_billings()

    # ----------------------------------------------------
    # LOAD BILLINGS FROM API
    # ----------------------------------------------------
    def load_billings(self):
        headers = {"Authorization": f"Bearer {self.session.token}"}
        response = requests.get(f"{self.url}/billings/", headers=headers)

        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to load billings")
            return

        billings = response.json()["billings"]

        for row in billings:
            self.table.insert(
                "", "end",
                values=(
                    row["billingID"],
                    row["userID"],
                    row["order_date"],
                    row["total_cost"],
                    row["status"]
                )
            )

    # ----------------------------------------------------
    # VIEW BILLING — opens new window and shows orderitems
    # ----------------------------------------------------
    def view_billing(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("Select Billing", "You must select a billing to view.")
            return

        values = self.table.item(selected, "values")
        billing_id = values[0]

        ViewBillingWindow(self.root, self.session, self.url, billing_id)

    # ----------------------------------------------------
    # UPDATE BILLING FROM pending -> paid
    # ----------------------------------------------------
    def update_status(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("Select Billing", "You must select a billing to update.")
            return

        values = self.table.item(selected, "values")
        billing_id = values[0]
        status = values[4]

        if status == "paid":
            messagebox.showinfo("Already Paid", "This billing is already paid.")
            return

        headers = {"Authorization": f"Bearer {self.session.token}"}
        response = requests.put(f"{self.url}/billings/{billing_id}", headers=headers)

        if response.status_code == 200:
            messagebox.showinfo("Updated", "Billing status updated to PAID.")
            self.table.delete(*self.table.get_children())
            self.load_billings()
        else:
            messagebox.showerror("Error", response.json().get("error", "Unknown error"))

class ViewBillingWindow:
    def __init__(self, root, session, url, billing_id):
        self.session = session
        self.url = url
        self.billing_id = billing_id

        self.win = tk.Toplevel(root)
        self.win.title(f"Billing {billing_id} - Order Items")
        self.win.geometry("600x350")

        columns = ("ID", "BookID", "Title", "Price", "Type")
        self.table = ttk.Treeview(self.win, columns=columns, show="headings", height=12)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120)

        self.table.pack(fill="both", expand=True)

        self.load_items()

    def load_items(self):
        headers = {"Authorization": f"Bearer {self.session.token}"}
        resp = requests.get(f"{self.url}/orderitems/billing/{self.billing_id}", headers=headers)

        if resp.status_code != 200:
            messagebox.showerror("Error", "Could not load order items")
            return

        items = resp.json().get("orderitems", [])

        for row in items:
            # row is a dict with bookID, orderitemID, price, order_type
            book_id = row.get("bookID")

            # safe request for book details
            try:
                book_resp = requests.get(f"{self.url}/books/{book_id}", headers=headers)
            except requests.exceptions.RequestException:
                book_resp = None

            title = "<unknown>"
            if book_resp and book_resp.status_code == 200:
                # endpoint returns {"book": {...}}
                book_json = book_resp.json()
                book_obj = book_json.get("book") or {}
                title = book_obj.get("title", "<unknown>")

            # insert into treeview
            self.table.insert(
                "",
                "end",
                values=(
                    row.get("orderitemID"),
                    row.get("bookID"),
                    title,
                    row.get("price"),
                    row.get("order_type")
                )
            )
