import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Database

class CustomerManager:
    def __init__(self, parent_frame, connection):
        self.frame = ttk.Frame(parent_frame)
        self.connection = connection
        self.setup_ui()

    def setup_ui(self):
        """Initialize the customer management UI"""
        # Search Frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_customers)
        
        # Customer table
        self.tree = ttk.Treeview(self.frame, 
                               columns=("ID", "Name", "Phone", "Email", "Address", "Age", "Points"),
                               show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Address", text="Address")
        self.tree.heading("Age", text="Age")
        self.tree.heading("Points", text="Loyalty Points")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add Customer", command=self.add_customer).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edit Customer", command=self.edit_customer).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Customer", command=self.delete_customer).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_customers).pack(side="right", padx=5)

        self.load_customers()

    def load_customers(self, search_term=None):
        """Load customers from database with optional search filter"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        cursor = self.connection.cursor()
        try:
            if search_term:
                query = """SELECT customer_id, name, phone, email, address, age, loyalty_points 
                          FROM customers 
                          WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s"""
                cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("""SELECT customer_id, name, phone, email, address, age, loyalty_points 
                                 FROM customers ORDER BY name""")
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {e}")
        finally:
            cursor.close()

    def search_customers(self, event=None):
        """Search customers based on entered text"""
        search_term = self.search_entry.get()
        self.load_customers(search_term)

    def add_customer(self):
        """Open dialog to add a new customer"""
        add_window = tk.Toplevel(self.frame)
        add_window.title("Add Customer")
        add_window.resizable(False, False)
        
        fields = [
            ("Name*", "name"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("Address", "address"),
            ("Age", "age")
        ]
        
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(add_window, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(add_window, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[field] = entry
    
        def save_customer():
            """Save the new customer to database"""
            if not entries["name"].get():
                messagebox.showwarning("Warning", "Name is required!")
                return
                
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """INSERT INTO customers 
                    (name, phone, email, address, age) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (entries["name"].get(), 
                     entries["phone"].get(),
                     entries["email"].get(),
                     entries["address"].get(),
                     int(entries["age"].get()) if entries["age"].get() else None)
                )
                self.connection.commit()
                messagebox.showinfo("Success", "Customer added successfully!")
                self.load_customers()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {e}")
            finally:
                cursor.close()

        ttk.Button(add_window, text="Save", command=save_customer).grid(row=len(fields), column=1, pady=10)

    def edit_customer(self):
        """Edit selected customer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to edit")
            return
            
        customer_id = self.tree.item(selected[0], "values")[0]
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT customer_id, name, phone, email, address, age, loyalty_points 
                            FROM customers WHERE customer_id = %s""", (customer_id,))
            customer = cursor.fetchone()
            
            edit_window = tk.Toplevel(self.frame)
            edit_window.title("Edit Customer")
            edit_window.resizable(False, False)
            
            fields = [
                ("Name*", "name"),
                ("Phone", "phone"),
                ("Email", "email"),
                ("Address", "address"),
                ("Age", "age"),
                ("Loyalty Points", "points")
            ]
            
            entries = {}
            for i, (label, field) in enumerate(fields):
                ttk.Label(edit_window, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
                entry = ttk.Entry(edit_window, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entry.insert(0, customer[i+1] if customer[i+1] else "")
                entries[field] = entry
        
            def update_customer():
                """Update customer in database"""
                if not entries["name"].get():
                    messagebox.showwarning("Warning", "Name is required!")
                    return
                    
                try:
                    cursor.execute(
                        """UPDATE customers SET 
                            name = %s, phone = %s, email = %s, 
                            address = %s, age = %s, loyalty_points = %s
                            WHERE customer_id = %s""",
                        (entries["name"].get(),
                         entries["phone"].get(),
                         entries["email"].get(),
                         entries["address"].get(),
                         int(entries["age"].get()) if entries["age"].get() else None,
                         int(entries["points"].get()) if entries["points"].get() else 0,
                         customer_id)
                    )
                    self.connection.commit()
                    messagebox.showinfo("Success", "Customer updated successfully!")
                    self.load_customers()
                    edit_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update customer: {e}")

            ttk.Button(edit_window, text="Update", command=update_customer).grid(row=len(fields), column=1, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer data: {e}")
        finally:
            cursor.close()

    def delete_customer(self):
        """Delete selected customer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
            
        customer_id = self.tree.item(selected[0], "values")[0]
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?"):
            return
            
        cursor = self.connection.cursor()
        try:
            # Check if customer has sales or prescriptions
            cursor.execute("SELECT COUNT(*) FROM sales WHERE customer_id = %s", (customer_id,))
            sales_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE customer_id = %s", (customer_id,))
            prescriptions_count = cursor.fetchone()[0]
            
            if sales_count > 0 or prescriptions_count > 0:
                messagebox.showwarning("Warning", 
                    f"Cannot delete customer. There are {sales_count} sales and {prescriptions_count} prescriptions associated.")
                return
                
            cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Customer deleted successfully!")
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {e}")
        finally:
            cursor.close()