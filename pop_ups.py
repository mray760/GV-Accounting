import tkinter as tk
from tkinter import messagebox

def confirm_run():
    # Create hidden root window
    root = tk.Tk()
    root.withdraw()  # Hide main window

    answer = messagebox.askyesno("Confirmation", "Are you sure you want to run monthly balances?")
    root.destroy()   # Clean up

    return answer
