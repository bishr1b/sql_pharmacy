import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from database import Database

class MedicineManager:
    def __init__(self, parent_frame, connection):
        self.frame = ttk.Frame(parent_frame)
        self.connection = connection
        self.entries = {}
        self.setup_ui()

    def setup_ui(self):
        """Initialize the medicine management UI"""
        # Search Bar Frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)

        # Search Criteria Dropdown
        self.search_criteria = tk.StringVar()
        self.search_criteria.set("name")  # Default search criteria
        search_options = ["name", "category", "manufacturer", "batch_number"]
        ttk.Label(search_frame, text="Search By:").pack(side="left", padx=5)
        ttk.Combobox(search_frame, textvariable=self.search_criteria, 
                    values=search_options, width=15).pack(side="left", padx=5)

        # Search Entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_medicines)

        # Clear Search Button
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left", padx=5)

        # Add Medicine Frame
        add_medicine_frame = ttk.LabelFrame(self.frame, text="Add Medicine", padding=10)
        add_medicine_frame.pack(fill="x", padx=10, pady=10)

        # Form Fields
        fields = [
            ("Name*", "name"),
            ("Quantity*", "quantity"),
            ("Price*", "price"),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date"),
            ("Manufacturer", "manufacturer"),
            ("Batch Number", "batch_number"),
            ("Category", "category"),
            ("Description", "description"),
            ("Supplier ID", "supplier_id")
        ]

        self.entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(add_medicine_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(add_medicine_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[field] = entry

        # Submit Button
        ttk.Button(add_medicine_frame, text="Submit", command=self.add_medicine).grid(row=len(fields), column=1, pady=10)

        # Table to Display Medicines
        self.tree = ttk.Treeview(self.frame, 
                               columns=("ID", "Name", "Quantity", "Price", "Expiry Date", 
                                       "Manufacturer", "Batch Number", "Category", "Supplier"),
                               show="headings")
        columns = [
            ("ID", "ID"),
            ("Name", "Name"),
            ("Quantity", "Quantity"),
            ("Price", "Price"),
            ("Expiry Date", "Expiry Date"),
            ("Manufacturer", "Manufacturer"),
            ("Batch Number", "Batch Number"),
            ("Category", "Category"),
            ("Supplier", "Supplier")
        ]
        
        for col_id, col_text in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=100 if col_id in ["ID", "Quantity", "Price"] else 120)
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Update and Delete Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Update", command=self.update_medicine).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_medicine).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Check Expiry", command=self.check_expiry).pack(side="right", padx=5)

        # Load existing medicines into the table
        self.load_medicines()

    def load_medicines(self):
        """Load all medicines from database"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT m.medicine_id, m.name, m.quantity, m.price, m.expiry_date, 
                            m.manufacturer, m.batch_number, m.category, 
                            COALESCE(s.name, 'No Supplier') as supplier_name
                            FROM medicines m
                            LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id""")
            for row in cursor.fetchall():
                # Format expiry date if exists
                formatted_row = list(row)
                if formatted_row[4]:  # expiry_date
                    formatted_row[4] = formatted_row[4].strftime("%Y-%m-%d")
                self.tree.insert("", "end", values=formatted_row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines: {e}")
        finally:
            cursor.close()

    def filter_medicines(self, event=None):
        """Filter medicines based on search criteria"""
        search_term = self.search_var.get().lower()
        criteria = self.search_criteria.get()

        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.connection.cursor()
        try:
            query = f"""SELECT m.medicine_id, m.name, m.quantity, m.price, m.expiry_date, 
                      m.manufacturer, m.batch_number, m.category, 
                      COALESCE(s.name, 'No Supplier') as supplier_name
                      FROM medicines m
                      LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
                      WHERE LOWER(m.{criteria}) LIKE %s"""
            cursor.execute(query, (f"%{search_term}%",))
            
            for row in cursor.fetchall():
                # Format expiry date if exists
                formatted_row = list(row)
                if formatted_row[4]:  # expiry_date
                    formatted_row[4] = formatted_row[4].strftime("%Y-%m-%d")
                self.tree.insert("", "end", values=formatted_row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter medicines: {e}")
        finally:
            cursor.close()

    def clear_search(self):
        """Clear search and reload all medicines"""
        self.search_var.set("")
        self.load_medicines()

    def add_medicine(self):
        """Add new medicine to database"""
        # Validate required fields
        if not all([self.entries["name"].get(), 
                   self.entries["quantity"].get(), 
                   self.entries["price"].get()]):
            messagebox.showwarning("Warning", "Name, Quantity and Price are required fields!")
            return
            
        try:
            # Validate numeric fields
            quantity = int(self.entries["quantity"].get())
            price = float(self.entries["price"].get())
            if quantity <= 0 or price <= 0:
                raise ValueError("Quantity and Price must be positive numbers")
                
            # Validate date format if provided
            expiry_date = self.entries["expiry_date"].get()
            if expiry_date:
                try:
                    datetime.strptime(expiry_date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Expiry date must be in YYYY-MM-DD format")
                    
            # Validate supplier ID if provided
            supplier_id = self.entries["supplier_id"].get()
            if supplier_id:
                try:
                    supplier_id = int(supplier_id)
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT COUNT(*) FROM suppliers WHERE supplier_id = %s", (supplier_id,))
                    if cursor.fetchone()[0] == 0:
                        raise ValueError("Supplier ID does not exist")
                except ValueError:
                    raise ValueError("Supplier ID must be a valid number")
                finally:
                    cursor.close()
                    
            # Insert the medicine
            cursor = self.connection.cursor()
            query = """
                INSERT INTO medicines 
                (name, quantity, price, expiry_date, manufacturer, batch_number, category, description, supplier_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                self.entries["name"].get(),
                quantity,
                price,
                expiry_date if expiry_date else None,
                self.entries["manufacturer"].get() or None,
                self.entries["batch_number"].get() or None,
                self.entries["category"].get() or None,
                self.entries["description"].get() or None,
                int(supplier_id) if supplier_id else None
            )
            cursor.execute(query, values)
            self.connection.commit()
            messagebox.showinfo("Success", "Medicine added successfully!")
            
            # Clear form and refresh table
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.load_medicines()
            
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {e}")
        finally:
            cursor.close()

    def update_medicine(self):
        """Open update dialog for selected medicine"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a medicine to update.")
            return
            
        medicine_id = self.tree.item(selected_item[0], "values")[0]
        self.open_update_window(medicine_id)

    def open_update_window(self, medicine_id):
        """Open window to update medicine details"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM medicines WHERE medicine_id = %s", (medicine_id,))
            medicine = cursor.fetchone()
            
            if not medicine:
                messagebox.showerror("Error", "Medicine not found!")
                return
                
            update_window = tk.Toplevel(self.frame)
            update_window.title("Update Medicine")
            update_window.geometry("500x500")
            
            fields = [
                ("Name*", "name"),
                ("Quantity*", "quantity"),
                ("Price*", "price"),
                ("Expiry Date (YYYY-MM-DD)", "expiry_date"),
                ("Manufacturer", "manufacturer"),
                ("Batch Number", "batch_number"),
                ("Category", "category"),
                ("Description", "description"),
                ("Supplier ID", "supplier_id")
            ]
            
            self.update_entries = {}
            for i, (label, field) in enumerate(fields):
                ttk.Label(update_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
                entry = ttk.Entry(update_window, width=40)
                entry.grid(row=i, column=1, padx=10, pady=5)
                
                # Fill with current values
                value = medicine[i+1]  # Skip id at index 0
                if value is not None:
                    if field == "expiry_date" and isinstance(value, datetime.date):
                        entry.insert(0, value.strftime("%Y-%m-%d"))
                    else:
                        entry.insert(0, str(value))
                        
                self.update_entries[field] = entry
            
            ttk.Button(update_window, text="Update", 
                      command=lambda: self.save_updated_medicine(medicine_id, update_window)
                      ).grid(row=len(fields), column=1, pady=10)
                      
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicine data: {e}")
        finally:
            cursor.close()

    def save_updated_medicine(self, medicine_id, update_window):
        """Save updated medicine details to database"""
        # Validate required fields
        if not all([self.update_entries["name"].get(), 
                   self.update_entries["quantity"].get(), 
                   self.update_entries["price"].get()]):
            messagebox.showwarning("Warning", "Name, Quantity and Price are required fields!")
            return
            
        try:
            # Validate numeric fields
            quantity = int(self.update_entries["quantity"].get())
            price = float(self.update_entries["price"].get())
            if quantity <= 0 or price <= 0:
                raise ValueError("Quantity and Price must be positive numbers")
                
            # Validate date format if provided
            expiry_date = self.update_entries["expiry_date"].get()
            if expiry_date:
                try:
                    datetime.strptime(expiry_date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Expiry date must be in YYYY-MM-DD format")
                    
            # Validate supplier ID if provided
            supplier_id = self.update_entries["supplier_id"].get()
            if supplier_id:
                try:
                    supplier_id = int(supplier_id)
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT COUNT(*) FROM suppliers WHERE supplier_id = %s", (supplier_id,))
                    if cursor.fetchone()[0] == 0:
                        raise ValueError("Supplier ID does not exist")
                except ValueError:
                    raise ValueError("Supplier ID must be a valid number")
                finally:
                    cursor.close()
                    
            # Update the medicine
            cursor = self.connection.cursor()
            query = """
                UPDATE medicines
                SET name = %s, quantity = %s, price = %s, expiry_date = %s, 
                    manufacturer = %s, batch_number = %s, category = %s, 
                    description = %s, supplier_id = %s
                WHERE medicine_id = %s
            """
            values = (
                self.update_entries["name"].get(),
                quantity,
                price,
                expiry_date if expiry_date else None,
                self.update_entries["manufacturer"].get() or None,
                self.update_entries["batch_number"].get() or None,
                self.update_entries["category"].get() or None,
                self.update_entries["description"].get() or None,
                int(supplier_id) if supplier_id else None,
                medicine_id
            )
            cursor.execute(query, values)
            self.connection.commit()
            messagebox.showinfo("Success", "Medicine updated successfully!")
            update_window.destroy()
            self.load_medicines()
            
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update medicine: {e}")
        finally:
            cursor.close()

    def delete_medicine(self):
        """Delete selected medicine from database"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a medicine to delete.")
            return
            
        medicine_id = self.tree.item(selected_item[0], "values")[0]
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this medicine?"):
            return
            
        cursor = self.connection.cursor()
        try:
            # Check if medicine has sales records
            cursor.execute("SELECT COUNT(*) FROM sales WHERE medicine_id = %s", (medicine_id,))
            sales_count = cursor.fetchone()[0]
            
            if sales_count > 0:
                messagebox.showwarning("Warning", 
                    f"Cannot delete medicine. There are {sales_count} sales records associated with this medicine.")
                return
                
            cursor.execute("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Medicine deleted successfully!")
            self.load_medicines()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete medicine: {e}")
        finally:
            cursor.close()

    def check_expiry(self):
        """Check for medicines expiring soon"""
        cursor = self.connection.cursor()
        try:
            today = datetime.now().date()
            alert_date = today + timedelta(days=30)

            cursor.execute("""
                SELECT name, expiry_date 
                FROM medicines 
                WHERE expiry_date IS NOT NULL AND expiry_date <= %s
                ORDER BY expiry_date
            """, (alert_date,))
            expiring_medicines = cursor.fetchall()
            
            if not expiring_medicines:
                messagebox.showinfo("Expiry Check", "No medicines are expiring in the next 30 days.")
                return
                
            alert_message = "Medicines expiring soon:\n\n"
            for medicine in expiring_medicines:
                days_left = (medicine[1] - today).days
                alert_message += f"{medicine[0]} - Expires on: {medicine[1]} ({days_left} days left)\n"
                
            messagebox.showwarning("Expiry Alert", alert_message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check expiry dates: {e}")
        finally:
            cursor.close()

    def reduce_medicine_quantity(self, medicine_id, quantity):
        """Reduce medicine quantity after sale"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE medicines 
                SET quantity = quantity - %s 
                WHERE medicine_id = %s AND quantity >= %s
            """, (quantity, medicine_id, quantity))
            
            if cursor.rowcount == 0:
                self.connection.rollback()
                return False
                
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Error", f"Failed to update medicine quantity: {e}")
            return False
        finally:
            cursor.close()