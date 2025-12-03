import tkinter as tk
from tkinter import ttk, messagebox
import requests

class BookPage:
    def __init__(self, root, session, url):
        self.root = root
        self.url = url
        self.session = session
        self.cart = []

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

        # -------------------------
        # Manager Controls (Create / Update)
        # -------------------------
        if self.session.role == "manager":
            manager_frame = ttk.Frame(root, padding=5)
            manager_frame.pack(fill="x")

            ttk.Button(manager_frame, text="Create Book", command=self.open_create_window).pack(side="left", padx=5)

            ttk.Button(manager_frame, text="Update Selected Book", command=self.open_update_window).pack(side="left", padx=5)

        # -------------------------
        # Customer Controls (Add to Order)
        # -------------------------
        if self.session.role == "customer":
            cust_frame = ttk.Frame(root, padding=5)
            cust_frame.pack(fill="x")

            ttk.Button(cust_frame, text="Add Book to Order", command=self.open_order_window).pack(side="left", padx=5)
            ttk.Button(cust_frame, text="Checkout", command=self.checkout).pack(side="left", padx=5)
            ttk.Button(cust_frame, text="View Cart", command=self.open_cart_window).pack(side="left", padx=5)
                

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

    def open_create_window(self):
        win = tk.Toplevel(self.root)
        win.title("Create Book")
        win.geometry("300x300")

        fields = ["Title", "Author", "Rental Price", "Buy Price", "Quantity"]
        entries = {}

        for f in fields:
            label = ttk.Label(win, text=f)
            label.pack()
            entry = ttk.Entry(win)
            entry.pack()
            entries[f] = entry

        def submit():
            data = {
                "title": entries["Title"].get(),
                "author": entries["Author"].get(),
                "rental_price": entries["Rental Price"].get(),
                "buy_price": entries["Buy Price"].get(),
                "quantity": entries["Quantity"].get(),
            }

            headers = {"Authorization": f"Bearer {self.session.token}"}
            resp = requests.post(self.url + "/books/", json=data, headers=headers)

            if resp.status_code == 201:
                messagebox.showinfo("Success", "Book created successfully.")
                win.destroy()
                self.load_books()
            else:
                messagebox.showerror("Error", resp.json().get("error", "Failed to create"))

        ttk.Button(win, text="Create", command=submit).pack(pady=10)

    def open_update_window(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a book first.")
            return

        values = self.tree.item(selected)["values"]
        book_id = values[0]

        win = tk.Toplevel(self.root)
        win.title("Update Book")
        win.geometry("300x300")

        fields = ["Title", "Author", "Rental Price", "Buy Price", "Quantity"]
        entries = {}

        for i, f in enumerate(fields, start=1):
            ttk.Label(win, text=f).pack()
            entry = ttk.Entry(win)
            entry.insert(0, values[i])   # populate existing values
            entry.pack()
            entries[f] = entry

        def submit():
            data = {
                "title": entries["Title"].get(),
                "author": entries["Author"].get(),
                "rental_price": entries["Rental Price"].get(),
                "buy_price": entries["Buy Price"].get(),
                "quantity": entries["Quantity"].get(),
            }

            headers = {"Authorization": f"Bearer {self.session.token}"}
            resp = requests.put(self.url + f"/books/{book_id}", json=data, headers=headers)

            if resp.status_code == 200:
                messagebox.showinfo("Updated", "Book updated successfully.")
                win.destroy()
                self.load_books()
            else:
                messagebox.showerror("Error", resp.json().get("error", "Failed to update"))

        ttk.Button(win, text="Update", command=submit).pack(pady=10)

    def open_order_window(self):
        """Opens a popup where customer can add items to an order."""
        
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a book first.")
            return

        values = self.tree.item(selected)["values"]
        book_id = values[0]
        rental_price = values[3]
        buy_price = values[4]

        win = tk.Toplevel(self.root)
        win.title("Add Book to Order")
        win.geometry("300x250")

        ttk.Label(win, text=f"Book ID: {book_id}").pack(pady=5)

        order_type_var = tk.StringVar()
        order_type_var.set("rent")  # default

        ttk.Label(win, text="Order Type:").pack(pady=5)
        ttk.Radiobutton(win, text="Rent", variable=order_type_var, value="rent").pack()
        ttk.Radiobutton(win, text="Buy", variable=order_type_var, value="buy").pack()

        def submit_order():
            order_type = order_type_var.get()
            price = float(rental_price) if order_type == "rent" else float(buy_price)

            self.cart.append({
                "bookID": book_id,
                "order_type": order_type,
                "price": price
            })

            messagebox.showinfo("Added", "Book added to cart!")
            win.destroy()

        ttk.Button(win, text="Add to Order", command=submit_order).pack(pady=15)

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "You have no items in your cart.")
            return

        headers = {"Authorization": f"Bearer {self.session.token}"}

        # 1. Calculate total cost for Billing
        total_cost = sum(float(item["price"]) for item in self.cart)

        billing_payload = {"total_cost": total_cost}
        billing_resp = requests.post(self.url + "/billings/", json=billing_payload, headers=headers)

        if billing_resp.status_code != 201:
            messagebox.showerror("Error", "Could not create billing.")
            return

        billing_id = billing_resp.json()["billingID"]

        # 2. Create each OrderItem under the same billing
        for item in self.cart:
            payload = {
                "bookID": item["bookID"],
                "billingID": billing_id,
                "price": item["price"],
                "order_type": item["order_type"]
            }
            order_resp = requests.post(self.url + "/orderitems/", json=payload, headers=headers)

            if order_resp.status_code != 201:
                messagebox.showerror("Error", "Failed to create order item.")
                return

        # Clear the cart on successful purchase
        self.cart = []

        messagebox.showinfo("Success", f"Checkout complete!\nBilling ID: {billing_id}")

    def open_cart_window(self):
        if hasattr(self, "cart_win") and self.cart_win.winfo_exists():
            self.cart_win.lift()
            return

        self.cart_win = tk.Toplevel(self.root)
        self.cart_win.title("Your Cart")
        self.cart_win.geometry("450x350")

        # -------------------------
        # Cart Tree Table
        # -------------------------
        columns = ("BookID", "Type", "Price")
        self.cart_tree = ttk.Treeview(self.cart_win, columns=columns, show="headings", height=10)
        self.cart_tree.pack(fill="both", expand=True, pady=10)

        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=120)

        # Load items into the tree
        self.refresh_cart_tree()

        # -------------------------
        # Remove Button
        # -------------------------
        ttk.Button(self.cart_win, text="Remove Selected", command=self.remove_cart_item)\
            .pack(pady=5)

        # -------------------------
        # Total Label
        # -------------------------
        self.total_label = ttk.Label(self.cart_win, text=f"Total: ${self.calculate_cart_total():.2f}")
        self.total_label.pack(pady=5)

    def refresh_cart_tree(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        for item in self.cart:
            self.cart_tree.insert("", "end", values=(item["bookID"], item["order_type"], item["price"]))

    def remove_cart_item(self):
        selected = self.cart_tree.focus()
        print("trying to remove cart item")
        if not selected:
            messagebox.showwarning("Warning", "Select an item to remove.")
            return

        values = self.cart_tree.item(selected)["values"]
        print(values)

        # Convert types coming from the treeview (treeview values are strings)
        try:
            book_id = int(values[0])
            order_type = str(values[1])
            price = float(values[2])
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid item selected.")
            return

        # Find and remove one matching item
        for i, item in enumerate(self.cart):
            # ensure item values are same type before comparing
            if (
                int(item.get("bookID")) == book_id and
                str(item.get("order_type")) == order_type and
                float(item.get("price")) == price
            ):
                del self.cart[i]
                break
        else:
            # optional: inform if not found
            print("Item not found in cart list to remove.")

        self.refresh_cart_tree()
        if hasattr(self, "total_label"):
            self.total_label.config(text=f"Total: ${self.calculate_cart_total():.2f}")

    def calculate_cart_total(self):
        return sum(float(item["price"]) for item in self.cart)

