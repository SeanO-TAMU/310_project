import tkinter as tk

root = tk.Tk()
root.title("Online Bookstore")
root.geometry("400x300")

label = tk.Label(root, text="Hello, Tkinter!")
label.pack()

button = tk.Button(root, text="Click Me")
button.pack()

root.mainloop()