import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Database

class SupplierManager:
    def __init__(self, parent_frame, connection):
        self.frame = ttk.Frame(parent_frame)
        self.connection = connection
        self.setup_ui()

    def setup_ui(self):
        """Initialize the supplier management UI"""
        # Search Frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_suppliers)
        
        # Supplier table
        self.tree = ttk.Treeview(self.frame, 
                               columns=("ID", "Name", "Contact", "Phone", "Email", "Country", "Terms"),
                               show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Contact", text="Contact Person")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Country", text="Country")
        self.tree.heading("Terms", text="Payment Terms")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons frame
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add Supplier", command=self.add_supplier).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edit Supplier", command=self.edit_supplier).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Supplier", command=self.delete_supplier).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_suppliers).pack(side="right", padx=5)

        self.load_suppliers()

    def load_suppliers(self, search_term=None):
        """Load suppliers from database with optional search filter"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        cursor = self.connection.cursor()
        try:
            if search_term:
                query = """SELECT supplier_id, name, contact_person, phone, email, country, payment_terms 
                          FROM suppliers WHERE name LIKE %s OR contact_person LIKE %s"""
                cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("""SELECT supplier_id, name, contact_person, phone, email, country, payment_terms 
                                 FROM suppliers ORDER BY name""")
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {e}")
        finally:
            cursor.close()

    def search_suppliers(self, event=None):
        """Search suppliers based on entered text"""
        search_term = self.search_entry.get()
        self.load_suppliers(search_term)

    def add_supplier(self):
        """Open dialog to add a new supplier"""
        add_window = tk.Toplevel(self.frame)
        add_window.title("Add Supplier")
        add_window.resizable(False, False)
        
        fields = [
            ("Name*", "name"),
            ("Contact Person", "contact"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("Country", "country"),
            ("Payment Terms", "terms")
        ]
        
        entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(add_window, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(add_window, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[field] = entry
    
        def save_supplier():
            """Save the new supplier to database"""
            if not entries["name"].get():
                messagebox.showwarning("Warning", "Name is required!")
                return
                
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """INSERT INTO suppliers 
                    (name, contact_person, phone, email, country, payment_terms) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (entries["name"].get(), 
                     entries["contact"].get(),
                     entries["phone"].get(),
                     entries["email"].get(),
                     entries["country"].get(),
                     entries["terms"].get())
                )
                self.connection.commit()
                messagebox.showinfo("Success", "Supplier added successfully!")
                self.load_suppliers()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add supplier: {e}")
            finally:
                cursor.close()

        ttk.Button(add_window, text="Save", command=save_supplier).grid(row=len(fields), column=1, pady=10)

    def edit_supplier(self):
        """Edit selected supplier"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier to edit")
            return
            
        supplier_id = self.tree.item(selected[0], "values")[0]
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""SELECT supplier_id, name, contact_person, phone, email, country, payment_terms 
                            FROM suppliers WHERE supplier_id = %s""", (supplier_id,))
            supplier = cursor.fetchone()
            
            edit_window = tk.Toplevel(self.frame)
            edit_window.title("Edit Supplier")
            edit_window.resizable(False, False)
            
            fields = [
                ("Name*", "name"),
                ("Contact Person", "contact"),
                ("Phone", "phone"),
                ("Email", "email"),
                ("Country", "country"),
                ("Payment Terms", "terms")
            ]
            
            entries = {}
            for i, (label, field) in enumerate(fields):
                ttk.Label(edit_window, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
                entry = ttk.Entry(edit_window, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entry.insert(0, supplier[i+1] if supplier[i+1] else "")
                entries[field] = entry
        
            def update_supplier():
                """Update supplier in database"""
                if not entries["name"].get():
                    messagebox.showwarning("Warning", "Name is required!")
                    return
                    
                try:
                    cursor.execute(
                        """UPDATE suppliers SET 
                            name = %s, contact_person = %s, phone = %s, 
                            email = %s, country = %s, payment_terms = %s
                            WHERE supplier_id = %s""",
                        (entries["name"].get(),
                         entries["contact"].get(),
                         entries["phone"].get(),
                         entries["email"].get(),
                         entries["country"].get(),
                         entries["terms"].get(),
                         supplier_id)
                    )
                    self.connection.commit()
                    messagebox.showinfo("Success", "Supplier updated successfully!")
                    self.load_suppliers()
                    edit_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update supplier: {e}")

            ttk.Button(edit_window, text="Update", command=update_supplier).grid(row=len(fields), column=1, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load supplier data: {e}")
        finally:
            cursor.close()

    def delete_supplier(self):
        """Delete selected supplier"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier to delete")
            return
            
        supplier_id = self.tree.item(selected[0], "values")[0]
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this supplier?"):
            return
            
        cursor = self.connection.cursor()
        try:
            # Check if supplier has medicines associated
            cursor.execute("SELECT COUNT(*) FROM medicines WHERE supplier_id = %s", (supplier_id,))
            medicine_count = cursor.fetchone()[0]
            
            if medicine_count > 0:
                messagebox.showwarning("Warning", 
                    f"Cannot delete supplier. There are {medicine_count} medicines associated with this supplier.")
                return
                
            cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Supplier deleted successfully!")
            self.load_suppliers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete supplier: {e}")
        finally:
            cursor.close()