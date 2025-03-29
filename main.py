from tkinter import font
from ttkthemes import ThemedTk
from logintoapp import LoginWindow
from pharmacy_app import PharmacyApp
if __name__ == "__main__":
    # Run login window first
    login = LoginWindow()
    if login.run():  # Only proceed if login is successful
        root = ThemedTk(theme="clam")
        app = PharmacyApp(root)
        root.mainloop()