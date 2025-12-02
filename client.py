import tkinter as tk
from helper import create_json

BASE_URL = "http://127.0.0.1:5000"

root = tk.Tk()
root.title("Online Bookstore")
root.geometry("400x300")

label = tk.Label(root, text="Hello, Tkinter!")
label.pack()

button = tk.Button(root, text="Click Me")
button.pack()

keys = ["name", "email", "password"]

values = ["Sean", "seano1641@tamu.edu", "password1234"]

print(create_json(keys, values))

root.mainloop()