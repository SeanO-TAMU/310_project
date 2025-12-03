import tkinter as tk
from tkinter import messagebox
import requests
from views.login import LoginPage

class Session:
    token = None
    role = None
    user_id = None

BASE_URL = "http://127.0.0.1:5000"

session = Session()

root = tk.Tk()
LoginPage(root, session, BASE_URL)



# books_win = tk.Toplevel(root)
# BookPage(books_win, session, BASE_URL)


# billings_win = tk.Toplevel(root)
# BillingPage(billings_win, session, BASE_URL)

root.mainloop()