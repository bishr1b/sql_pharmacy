import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from ttkthemes import ThemedTk
import mysql.connector
from tkinter import font
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import os
from customer_manager import CustomerManager
from supplier_manager import SupplierManager
from medicine_manager import MedicineManager
from sales_manager import SalesManager

# Database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pharmacy_db",
            autocommit=False  # Explicitly set autocommit to False
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Admin Login")
        self.root.geometry("400x300")
        self.root.configure(bg="#f0f0f0")
        
        # Center the window
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")

        # Title
        title_label = ttk.Label(main_frame, text="Pharmacy Management System", 
                             font=("Helvetica", 16, "bold"))
        title_label.pack(pady=20)

        # Login frame
        login_frame = ttk.LabelFrame(main_frame, text="Admin Login", padding="20")
        login_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Username
        ttk.Label(login_frame, text="Username:").pack(fill="x", pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.pack(fill="x", pady=5)

        # Password
        ttk.Label(login_frame, text="Password:").pack(fill="x", pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(fill="x", pady=5)

        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.pack(pady=20)

        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())

        # Store the login status
        self.login_successful = False

    def login(self):
        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "admin123"

        if (self.username_entry.get() == ADMIN_USERNAME and 
            self.password_entry.get() == ADMIN_PASSWORD):
            self.login_successful = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)

    def run(self):
        self.root.mainloop()
        return self.login_successful

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f0f0")

        # Connect to the database
        self.connection = connect_to_database()
        if not self.connection:
            messagebox.showerror("Error", "Failed to connect to database")
            self.root.destroy()
            return

        # Modern Theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Pharmacy Name
        self.pharmacy_name_font = font.Font(family="Helvetica", size=24, weight="bold")
        pharmacy_name = tk.Label(root, text="Pharmacy Management System", 
                               font=self.pharmacy_name_font, fg="#333333", bg="#f0f0f0")
        pharmacy_name.place(relx=0.5, rely=0.02, anchor="center")

        # Dashboard Frame
        self.dashboard_frame = tk.Frame(root, bg="#333333", width=200)
        self.dashboard_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Dashboard Buttons
        buttons = [
            ("Medicine Management", self.show_medicine_management),
            ("Sales and Billing", self.show_sales_and_billing),
            ("Customer Management", self.show_customer_management),
            ("Supplier Management", self.show_supplier_management)
        ]
        
        for text, command in buttons:
            btn = tk.Button(self.dashboard_frame, text=text, command=command,
                         bg="#444444", fg="white", bd=0, 
                         font=("Helvetica", 12), padx=10, pady=10)
            btn.pack(pady=5, fill="x")

        # Main Content Frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Initialize all managers
        self.medicine_manager = MedicineManager(self.main_frame, self.connection)
        self.sales_manager = SalesManager(self.main_frame, self.connection, self.medicine_manager)
        self.customer_manager = CustomerManager(self.main_frame, self.connection)
        self.supplier_manager = SupplierManager(self.main_frame, self.connection)

        # Show default view
        self.show_medicine_management()
        self.check_expiration_alerts()

    def check_expiration_alerts(self):
        """Check for medicines nearing expiration"""
        cursor = self.connection.cursor()
        today = datetime.now().date()
        alert_date = today + timedelta(days=30)

        cursor.execute("SELECT name, expiry_date FROM medicines WHERE expiry_date <= %s", (alert_date,))
        expiring_medicines = cursor.fetchall()

        if expiring_medicines:
            alert_message = "The following medicines are nearing expiration:\n\n"
            for medicine in expiring_medicines:
                days_left = (medicine[1] - today).days
                alert_message += f"{medicine[0]} (Expires on: {medicine[1]}, {days_left} days left)\n"
            messagebox.showwarning("Expiration Alert", alert_message)

    def show_medicine_management(self):
        """Show medicine management interface"""
        self.hide_all_frames()
        self.medicine_manager.frame.pack(fill="both", expand=True)

    def show_sales_and_billing(self):
        """Show sales and billing interface"""
        self.hide_all_frames()
        self.sales_manager.frame.pack(fill="both", expand=True)
        self.sales_manager.load_medicine_names()
        self.sales_manager.load_customer_names()

    def show_customer_management(self):
        """Show customer management interface"""
        self.hide_all_frames()
        self.customer_manager.frame.pack(fill="both", expand=True)
        self.customer_manager.load_customers()

    def show_supplier_management(self):
        """Show supplier management interface"""
        self.hide_all_frames()
        self.supplier_manager.frame.pack(fill="both", expand=True)
        self.supplier_manager.load_suppliers()

    def hide_all_frames(self):
        """Hide all content frames"""
        self.medicine_manager.frame.pack_forget()
        self.sales_manager.frame.pack_forget()
        self.customer_manager.frame.pack_forget()
        self.supplier_manager.frame.pack_forget()

if __name__ == "__main__":
    login_window = LoginWindow()
    if login_window.run():
        root = ThemedTk(theme="clam")
        app = PharmacyApp(root)
        root.mainloop()