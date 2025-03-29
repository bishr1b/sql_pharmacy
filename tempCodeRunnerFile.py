import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from ttkthemes import ThemedTk
import mysql.connector
from tkinter import font

# Database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Default XAMPP MySQL username
            password="",  # Default XAMPP MySQL password (empty)
            database="pharmacy_db"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# Main application class
class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1400x800")
        self.root.configure(bg="#c4a484")  # Bright pink background

        # Connect to the database
        self.connection = connect_to_database()
        if self.connection:
            print("Connected to the database!")

        # Modern Theme
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use a colorful theme

        # Pharmacy Name
        self.pharmacy_name_font = font.Font(family="Times", size=30, weight="bold")
        pharmacy_name = tk.Label(root, text="Pharmacy of Life", font=self.pharmacy_name_font, fg="#00FF00", bg="#FF00FF")
        pharmacy_name.place(relx=0.85, rely=0.02, anchor="ne")

        # Dashboard Frame (Left Side)
        self.dashboard_frame = tk.Frame(root, bg="#997950", width=200)  # Bright cyan
        self.dashboard_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Dashboard Buttons
        tk.Button(self.dashboard_frame, text="Medicine Management", command=self.show_medicine_management, bg="#F5F5DC", fg="#000000", bd=0, font=("Times", 12)).pack(pady=10, fill="x")
        tk.Button(self.dashboard_frame, text="Sales and Billing", command=self.show_sales_and_billing, bg="#F5F5DC", fg="#000000", bd=0, font=("Times", 12)).pack(pady=10, fill="x")

        # Main Content Frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Medicine Management Setup
        self.setup_medicine_management()

        # Sales and Billing Setup
        self.setup_sales_and_billing()

        # Show Medicine Management by Default
        self.show_medicine_management()

    # Medicine Management Setup
    def setup_medicine_management(self):
        self.medicine_frame = ttk.Frame(self.main_frame)
        self.medicine_frame.pack(fill="both", expand=True)

        # Search Bar Frame
        search_frame = ttk.Frame(self.medicine_frame)
        search_frame.pack(fill="x", padx=10, pady=10)

        # Search Criteria Dropdown
        self.search_criteria = tk.StringVar()
        self.search_criteria.set("Name")  # Default search criteria
        search_options = ["Name", "Category", "Manufacturer", "Batch Number"]
        ttk.Label(search_frame, text="Search By:").pack(side="left", padx=5)
        ttk.Combobox(search_frame, textvariable=self.search_criteria, values=search_options, width=15).pack(side="left", padx=5)

        # Search Entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_medicines)  # Real-time filtering

        # Clear Search Button
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left", padx=5)

        # Add Medicine Frame
        add_medicine_frame = ttk.LabelFrame(self.medicine_frame, text="Add Medicine", padding=10, style="Colorful.TLabelframe")
        add_medicine_frame.pack(fill="x", padx=10, pady=10)

        # Form Fields
        fields = [
            ("Name", "name"),
            ("Quantity", "quantity"),
            ("Price", "price"),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date"),
            ("Manufacturer", "manufacturer"),
            ("Batch Number", "batch_number"),
            ("Category", "category"),
            ("Description", "description")
        ]

        self.entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(add_medicine_frame, text=label, style="Colorful.TLabel").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(add_medicine_frame, width=40, style="Colorful.TEntry")
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[field] = entry

        # Submit Button
        ttk.Button(add_medicine_frame, text="Submit", command=self.add_medicine, style="Colorful.TButton").grid(row=len(fields), column=1, pady=10)

        # Table to Display Medicines
        self.tree = ttk.Treeview(self.medicine_frame, columns=("ID", "Name", "Quantity", "Price", "Expiry Date", "Manufacturer", "Batch Number", "Category"), show="headings", style="Colorful.Treeview")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Expiry Date", text="Expiry Date")
        self.tree.heading("Manufacturer", text="Manufacturer")
        self.tree.heading("Batch Number", text="Batch Number")
        self.tree.heading("Category", text="Category")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Update and Delete Buttons
        button_frame = ttk.Frame(self.medicine_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Update", command=self.update_medicine, style="Blue.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_medicine, style="Red.TButton").pack(side="left", padx=5)

        # Load existing medicines into the table
        self.load_medicines()

    # Filter Medicines Based on Search
    def filter_medicines(self, event=None):
        search_term = self.search_var.get().lower()
        criteria = self.search_criteria.get()

        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.connection.cursor()
        query = f"SELECT * FROM medicines WHERE LOWER({criteria}) LIKE %s"
        cursor.execute(query, (f"%{search_term}%",))
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    # Clear Search
    def clear_search(self):
        self.search_var.set("")
        self.load_medicines()

    # Sales and Billing Setup
    def setup_sales_and_billing(self):
        self.sales_frame = ttk.Frame(self.main_frame)
        self.sales_frame.pack(fill="both", expand=True)

        # Add to Bill Frame
        add_to_bill_frame = ttk.LabelFrame(self.sales_frame, text="Add to Bill", padding=10, style="Colorful.TLabelframe")
        add_to_bill_frame.pack(fill="x", padx=10, pady=10)

        # Medicine Selection
        ttk.Label(add_to_bill_frame, text="Select Medicine", style="Colorful.TLabel").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.medicine_var = tk.StringVar()
        self.medicine_dropdown = ttk.Combobox(add_to_bill_frame, textvariable=self.medicine_var, width=40, style="Colorful.TCombobox")
        self.medicine_dropdown.grid(row=0, column=1, padx=10, pady=5)
        self.load_medicine_names()

        # Quantity Input
        ttk.Label(add_to_bill_frame, text="Quantity", style="Colorful.TLabel").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(add_to_bill_frame, width=40, style="Colorful.TEntry")
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        # Add to Bill Button
        ttk.Button(add_to_bill_frame, text="Add to Bill", command=self.add_to_bill, style="Colorful.TButton").grid(row=2, column=1, pady=10)

        # Bill Table
        self.bill_tree = ttk.Treeview(self.sales_frame, columns=("Medicine", "Quantity", "Price", "Total"), show="headings", style="Colorful.Treeview")
        self.bill_tree.heading("Medicine", text="Medicine")
        self.bill_tree.heading("Quantity", text="Quantity")
        self.bill_tree.heading("Price", text="Price")
        self.bill_tree.heading("Total", text="Total")
        self.bill_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Total Label
        self.total_label = ttk.Label(self.sales_frame, text="Total: $0.00", font=("Times", 14), style="Colorful.TLabel")
        self.total_label.pack(pady=10)

        # Delete and Change Quantity Buttons
        button_frame = ttk.Frame(self.sales_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Delete Selected", command=self.delete_from_bill, style="Red.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Change Quantity", command=self.change_quantity, style="Blue.TButton").pack(side="left", padx=5)

        # Generate Bill Button
        ttk.Button(self.sales_frame, text="Generate Bill", command=self.generate_bill, style="Colorful.TButton").pack(pady=10)

    # Show Medicine Management
    def show_medicine_management(self):
        self.sales_frame.pack_forget()
        self.medicine_frame.pack(fill="both", expand=True)

    # Show Sales and Billing
    def show_sales_and_billing(self):
        self.medicine_frame.pack_forget()
        self.sales_frame.pack(fill="both", expand=True)

    # Load Medicine Names for Dropdown
    def load_medicine_names(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM medicines")
        medicines = [row[0] for row in cursor.fetchall()]
        self.medicine_dropdown["values"] = medicines

    # Add Medicine to Bill
    def add_to_bill(self):
        medicine_name = self.medicine_var.get()
        quantity = int(self.quantity_entry.get())

        cursor = self.connection.cursor()
        cursor.execute("SELECT id, price FROM medicines WHERE name = %s", (medicine_name,))
        medicine = cursor.fetchone()

        if medicine:
            medicine_id, price = medicine
            total = price * quantity
            self.bill_tree.insert("", "end", values=(medicine_name, quantity, price, total))
            self.update_total()

    # Update Total Amount
    def update_total(self):
        total = sum(float(self.bill_tree.item(item, "values")[3]) for item in self.bill_tree.get_children())
        self.total_label.config(text=f"Total: ${total:.2f}")

    # Delete from Bill
    def delete_from_bill(self):
        selected_item = self.bill_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return
        self.bill_tree.delete(selected_item)
        self.update_total()

    # Change Quantity in Bill
    def change_quantity(self):
        selected_item = self.bill_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to change quantity.")
            return

        # Get current values
        medicine_name, old_quantity, price, total = self.bill_tree.item(selected_item, "values")

        # Ask for new quantity
        new_quantity = simpledialog.askinteger("Change Quantity", f"Enter new quantity for {medicine_name}:", minvalue=1)
        if new_quantity:
            # Update the quantity and total
            total = float(price) * new_quantity
            self.bill_tree.item(selected_item, values=(medicine_name, new_quantity, price, total))
            self.update_total()

    # Generate Bill
    def generate_bill(self):
        for item in self.bill_tree.get_children():
            medicine_name, quantity, price, total = self.bill_tree.item(item, "values")
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO sales (medicine_id, quantity, total_price) VALUES ((SELECT id FROM medicines WHERE name = %s), %s, %s)", (medicine_name, quantity, total))
            self.connection.commit()
        messagebox.showinfo("Success", "Bill generated and saved to database!")
        self.bill_tree.delete(*self.bill_tree.get_children())
        self.total_label.config(text="Total: $0.00")

    # Add Medicine to Database
    def add_medicine(self):
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO medicines (name, quantity, price, expiry_date, manufacturer, batch_number, category, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                self.entries["name"].get(),
                int(self.entries["quantity"].get()),
                float(self.entries["price"].get()),
                self.entries["expiry_date"].get(),
                self.entries["manufacturer"].get(),
                self.entries["batch_number"].get(),
                self.entries["category"].get(),
                self.entries["description"].get()
            )
            cursor.execute(query, values)
            self.connection.commit()
            messagebox.showinfo("Success", "Medicine added successfully!")
            self.load_medicines()  # Refresh the table
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {e}")

    # Load Medicines into Table
    def load_medicines(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, quantity, price, expiry_date, manufacturer, batch_number, category FROM medicines")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    # Update Medicine
    def update_medicine(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a medicine to update.")
            return
        medicine_id = self.tree.item(selected_item, "values")[0]
        self.open_update_window(medicine_id)

    # Open Update Window
    def open_update_window(self, medicine_id):
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Medicine")
        update_window.geometry("400x400")

        # Fetch medicine details
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM medicines WHERE id = %s", (medicine_id,))
        medicine = cursor.fetchone()

        # Form Fields
        fields = [
            ("Name", "name"),
            ("Quantity", "quantity"),
            ("Price", "price"),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date"),
            ("Manufacturer", "manufacturer"),
            ("Batch Number", "batch_number"),
            ("Category", "category"),
            ("Description", "description")
        ]

        self.update_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(update_window, text=label, style="Colorful.TLabel").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(update_window, width=30, style="Colorful.TEntry")
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, medicine[i + 1])  # Fill with current values
            self.update_entries[field] = entry

        # Update Button
        ttk.Button(update_window, text="Update", command=lambda: self.save_updated_medicine(medicine_id), style="Colorful.TButton").grid(row=len(fields), column=1, pady=10)

    # Save Updated Medicine
    def save_updated_medicine(self, medicine_id):
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE medicines
                SET name = %s, quantity = %s, price = %s, expiry_date = %s, manufacturer = %s, batch_number = %s, category = %s, description = %s
                WHERE id = %s
            """
            values = (
                self.update_entries["name"].get(),
                int(self.update_entries["quantity"].get()),
                float(self.update_entries["price"].get()),
                self.update_entries["expiry_date"].get(),
                self.update_entries["manufacturer"].get(),
                self.update_entries["batch_number"].get(),
                self.update_entries["category"].get(),
                self.update_entries["description"].get(),
                medicine_id
            )
            cursor.execute(query, values)
            self.connection.commit()
            messagebox.showinfo("Success", "Medicine updated successfully!")
            self.load_medicines()  # Refresh the table
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update medicine: {e}")

    # Delete Medicine
    def delete_medicine(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a medicine to delete.")
            return
        medicine_id = self.tree.item(selected_item, "values")[0]
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM medicines WHERE id = %s", (medicine_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Medicine deleted successfully!")
            self.load_medicines()  # Refresh the table
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete medicine: {e}")

# Run the application
if __name__ == "__main__":
    root = ThemedTk(theme="clam")  # Use a colorful theme
    app = PharmacyApp(root)
    root.mainloop()