import tkinter as tk
from tkinter import messagebox
import requests
from helper import create_json, Session
from views.login import LoginPage


BASE_URL = "http://127.0.0.1:5000"

session = Session()

root = tk.Tk()
LoginPage(root)

root.mainloop()