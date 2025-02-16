import tkinter as tk
import os
import time
from tkinter import messagebox
import subprocess as sp
from PIL import Image, ImageTk
import webbrowser as wb
import dashboard as db
import ttkbootstrap as ttkb

def on_closing():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def open_login_dialog():
    # Create the login window
    login_window = tk.Toplevel()
    login_window.iconbitmap('image/Untitled_design-removebg-preview.ico')
    login_window.title("Login Portal")
    # Center the login window on the screen
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width // 2) - (350 // 2)  # Center horizontally
    y = (screen_height // 2) - (300 // 2)  # Center vertically
    login_window.geometry(f"{350}x{300}+{x}+{y}")  # Adjusted size for a more compact layout
    login_window.configure(bg="#1E1E2F")

    # Make the login window transient (keeps it on top of the root window)
    login_window.transient(root)

    # Create a frame for padding and structure
    frame = tk.Frame(login_window, bg="#1E1E2F", padx=10, pady=10)
    frame.pack(fill='both', expand=True)

    # Style configurations
    title_font = ("Helvetica", 16, "bold")
    entry_font = ("Helvetica", 10)
    button_font = ("Helvetica", 10, "bold")
    message_font = ("Helvetica", 9, "italic")

    # Placeholder functionality for Entry widgets
    def set_placeholder(entry, placeholder_text):
        entry.insert(0, placeholder_text)
        entry.config(fg='#5A5A89')

        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, tk.END)
                entry.config(fg='black')

        def on_focus_out(event):
            if entry.get() == "":
                entry.insert(0, placeholder_text)
                entry.config(fg='#5A5A89')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # Title label
    tk.Label(frame, text="Login/Sign up", font=title_font, fg='white', bg="#1E1E2F").pack(pady=10)

    # Username entry with placeholder
    username_entry = tk.Entry(frame, font=entry_font, highlightbackground="#5A5A89", highlightthickness=2)
    username_entry.pack(pady=5, padx=10, fill=tk.X)
    set_placeholder(username_entry, "Enter your User ID")

    # Password entry with placeholder
    password_entry = tk.Entry(frame, font=entry_font, highlightbackground="#5A5A89", highlightthickness=2)
    password_entry.pack(pady=5, padx=10, fill=tk.X)
    set_placeholder(password_entry, "Enter your password")

    # Validate login locally
    def validate_login(event=None):
        global root
        username = username_entry.get()
        password = password_entry.get()

        if username == "admin" and password == "password":  # Example credentials
            messagebox.showinfo("Login", "Login Successful")
            login_window.destroy()
            root.destroy()
            time.sleep(2)
            root =tk.Tk()
            root.after(3,db.main(base=root))
        else:
            messagebox.showerror("Login", "Invalid credentials. Try again.")

    # Cancel login and close windows
    def cancel_login():
        login_window.destroy()
        root.destroy()

    # Function to open register window
    def open_register_dialog():
        register_url = "http://protech.byethost9.com"  # Replace this with the actual register link
        wb.open(register_url)

    # Bind Enter key to login
    login_window.bind("<Return>", validate_login)

    # Buttons for login and cancel
    button_frame = tk.Frame(frame, bg="#1E1E2F")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Login", font=button_font, command=validate_login, bg="#007BFF", fg="white", activebackground="#0056b3").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", font=button_font, command=cancel_login, bg="#DC3545", fg="white", activebackground="#a71d2a").pack(side=tk.RIGHT, padx=5)

    # Register Button and message
    tk.Button(frame, text="Register", font=button_font, command=open_register_dialog, bg="#28A745", fg="white", activebackground="#1e7e34").pack(pady=5)
    tk.Label(frame, text="Click to Register or Forgot Password", font=message_font, fg="#BBBBBB", bg="#1E1E2F").pack(pady=5)

    # Handle window closing event
    login_window.protocol('WM_DELETE_WINDOW', cancel_login)

root = tk.Tk()

root.geometry('800x600')  # Adjusted size for a more compact and organized layout
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (800 // 2)  # Calculate x position
y = (screen_height // 2) - (600 // 2)  # Calculate y position
root.geometry(f"+{x}+{y}")  # Set the position
bg_image = Image.open("image/Untitled_design-removebg-preview.png")  # Replace with your image path
bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)  # Resize to fit the window
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

root.overrideredirect(True)
root.attributes('-transparentcolor', root['bg'])
root.title("Protech")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.after(3000, open_login_dialog)

root.mainloop()
