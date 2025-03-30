import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from database import Prescription, Customer, Medicine, Database

class PrescriptionManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.current_prescription = None
        self.setup_ui()

    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_frame, text="Customer:").pack(side="left")
        self.customer_combo = ttk.Combobox(search_frame, state="readonly")
        self.customer_combo.pack(side="left", padx=5)
        
        ttk.Button(search_frame, text="Search", 
                  command=self.search_prescriptions).pack(side="left", padx=5)
        
        # Prescription treeview
        self.tree = ttk.Treeview(self.frame, columns=(
            "ID", "Customer", "Doctor", "Issued", "Expires", "Items"
        ), show="headings")
        
        columns = [
            ("ID", "Prescription ID", 80),
            ("Customer", "Customer", 150),
            ("Doctor", "Doctor", 150),
            ("Issued", "Issued Date", 100),
            ("Expires", "Expiry Date", 100),
            ("Items", "Items", 50)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_prescription_select)
        
        # Button frame
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_btn = ttk.Button(btn_frame, text="Add", command=self.show_add_dialog)
        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.show_edit_dialog, state="disabled")
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_prescription, state="disabled")
        self.view_btn = ttk.Button(btn_frame, text="View Items", command=self.view_items, state="disabled")
        
        self.add_btn.pack(side="left", padx=5)
        self.edit_btn.pack(side="left", padx=5)
        self.delete_btn.pack(side="left", padx=5)
        self.view_btn.pack(side="right", padx=5)
        
        # Load initial data
        self.load_customers()
        self.load_prescriptions()

    def load_customers(self):
        customers = Customer.get_all()
        self.customer_combo['values'] = [f"{c['customer_id']} - {c['name']}" for c in customers]

    def load_prescriptions(self, customer_id=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        query = """SELECT p.*, c.name as customer_name, 
                  (SELECT COUNT(*) FROM prescription_items WHERE prescription_id = p.prescription_id) as item_count
                  FROM prescriptions p JOIN customers c ON p.customer_id = c.customer_id"""
        
        params = []
        if customer_id:
            query += " WHERE p.customer_id = %s"
            params.append(customer_id)
        
        prescriptions = Database.execute_query(query, tuple(params) if params else None, fetch=True)
        
        for pres in prescriptions:
            self.tree.insert("", "end", values=(
                pres['prescription_id'],
                pres['customer_name'],
                pres['doctor_name'] or "N/A",
                pres['issue_date'].strftime("%Y-%m-%d"),
                pres['expiry_date'].strftime("%Y-%m-%d") if pres['expiry_date'] else "N/A",
                pres['item_count']
            ))

    def search_prescriptions(self):
        customer = self.customer_combo.get()
        if customer:
            customer_id = int(customer.split(" - ")[0])
            self.load_prescriptions(customer_id)
        else:
            self.load_prescriptions()

    def on_prescription_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_prescription = self.tree.item(selected[0])['values']
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
            self.view_btn.config(state="normal")
        else:
            self.current_prescription = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            self.view_btn.config(state="disabled")

    def show_add_dialog(self):
        dialog = PrescriptionDialog(self.frame, title="Add New Prescription")
        if dialog.result:
            try:
                # Create prescription
                prescription_id = Prescription.create(dialog.result['prescription'])
                
                # Add prescription items
                for item in dialog.result['items']:
                    Database.execute_query(
                        """INSERT INTO prescription_items 
                          (prescription_id, medicine_id, quantity, dosage, instructions) 
                          VALUES (%s, %s, %s, %s, %s)""",
                        (prescription_id, item['medicine_id'], item['quantity'], 
                         item['dosage'], item['instructions'])
                    )
                
                self.load_prescriptions()
                messagebox.showinfo("Success", "Prescription added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add prescription: {str(e)}")

    def show_edit_dialog(self):
        if not self.current_prescription:
            return
        
        prescription_id = self.current_prescription[0]
        # Similar to add but with existing data
        pass

    def delete_prescription(self):
        if not self.current_prescription:
            return
        
        if messagebox.askyesno("Confirm", "Delete this prescription?"):
            try:
                Prescription.delete(self.current_prescription[0])
                self.load_prescriptions()
                messagebox.showinfo("Success", "Prescription deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete prescription: {str(e)}")

    def view_items(self):
        if not self.current_prescription:
            return
        
        prescription_id = self.current_prescription[0]
        items = Database.execute_query(
            """SELECT m.name, pi.quantity, pi.dosage, pi.instructions 
              FROM prescription_items pi JOIN medicines m 
              ON pi.medicine_id = m.medicine_id 
              WHERE pi.prescription_id = %s""",
            (prescription_id,), fetch=True)
        
        detail_window = tk.Toplevel(self.frame)
        detail_window.title(f"Prescription #{prescription_id} Items")
        
        tree = ttk.Treeview(detail_window, columns=("Medicine", "Quantity", "Dosage", "Instructions"), show="headings")
        tree.heading("Medicine", text="Medicine")
        tree.heading("Quantity", text="Quantity")
        tree.heading("Dosage", text="Dosage")
        tree.heading("Instructions", text="Instructions")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        for item in items:
            tree.insert("", "end", values=(
                item['name'],
                item['quantity'],
                item['dosage'] or "N/A",
                item['instructions'] or "N/A"
            ))

class PrescriptionDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x500")
        self.resizable(False, False)
        self.result = None
        
        self.data = data or {
            'prescription': {
                'customer_id': None,
                'doctor_name': '',
                'doctor_license': '',
                'issue_date': datetime.now().strftime("%Y-%m-%d"),
                'expiry_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                'notes': ''
            },
            'items': []
        }
        
        self.create_widgets()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        
        # Prescription tab
        pres_frame = ttk.Frame(notebook)
        notebook.add(pres_frame, text="Prescription")
        
        ttk.Label(pres_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.customer_combo = ttk.Combobox(pres_frame, state="readonly")
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(pres_frame, text="Doctor Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.doctor_entry = ttk.Entry(pres_frame)
        self.doctor_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(pres_frame, text="License:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.license_entry = ttk.Entry(pres_frame)
        self.license_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(pres_frame, text="Issue Date:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.issue_entry = ttk.Entry(pres_frame)
        self.issue_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.issue_entry.insert(0, self.data['prescription']['issue_date'])
        
        ttk.Label(pres_frame, text="Expiry Date:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.expiry_entry = ttk.Entry(pres_frame)
        self.expiry_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.expiry_entry.insert(0, self.data['prescription']['expiry_date'])
        
        ttk.Label(pres_frame, text="Notes:").grid(row=5, column=0, padx=5, pady=5, sticky="ne")
        self.notes_text = tk.Text(pres_frame, height=5, width=40)
        self.notes_text.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.notes_text.insert("1.0", self.data['prescription']['notes'] or "")
        
        # Items tab
        items_frame = ttk.Frame(notebook)
        notebook.add(items_frame, text="Items")
        
        # Items treeview
        self.items_tree = ttk.Treeview(items_frame, columns=("Medicine", "Quantity", "Dosage"), show="headings")
        self.items_tree.heading("Medicine", text="Medicine")
        self.items_tree.heading("Quantity", text="Quantity")
        self.items_tree.heading("Dosage", text="Dosage")
        self.items_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add item frame
        add_frame = ttk.Frame(items_frame)
        add_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(add_frame, text="Medicine:").pack(side="left")
        self.medicine_combo = ttk.Combobox(add_frame, state="readonly")
        self.medicine_combo.pack(side="left", padx=5)
        
        ttk.Label(add_frame, text="Qty:").pack(side="left")
        self.quantity_entry = ttk.Entry(add_frame, width=5)
        self.quantity_entry.pack(side="left", padx=5)
        
        ttk.Label(add_frame, text="Dosage:").pack(side="left")
        self.dosage_entry = ttk.Entry(add_frame, width=15)
        self.dosage_entry.pack(side="left", padx=5)
        
        ttk.Button(add_frame, text="Add", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(add_frame, text="Remove", command=self.remove_item).pack(side="right", padx=5)
        
        # Load data
        self.load_customers()
        self.load_medicines()
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
    
    def load_customers(self):
        customers = Customer.get_all()
        self.customer_combo['values'] = [f"{c['customer_id']} - {c['name']}" for c in customers]

    def load_medicines(self):
        medicines = Medicine.get_all()
        self.medicine_combo['values'] = [f"{m['medicine_id']} - {m['name']}" for m in medicines]

    def add_item(self):
        medicine = self.medicine_combo.get()
        quantity = self.quantity_entry.get()
        dosage = self.dosage_entry.get()
        
        if not medicine or not quantity:
            messagebox.showwarning("Warning", "Please select medicine and enter quantity")
            return
        
        try:
            medicine_id = int(medicine.split(" - ")[0])
            quantity = int(quantity)
            
            # Get medicine name
            med = next((m for m in Medicine.get_all() if m['medicine_id'] == medicine_id), None)
            if not med:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            self.items_tree.insert("", "end", values=(
                med['name'],
                quantity,
                dosage or "As directed"
            ), tags=(medicine_id,))
            
            self.medicine_combo.set('')
            self.quantity_entry.delete(0, tk.END)
            self.dosage_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid quantity")

    def remove_item(self):
        selected = self.items_tree.selection()
        if selected:
            self.items_tree.delete(selected[0])

    def on_save(self):
        customer = self.customer_combo.get()
        if not customer:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        if not self.items_tree.get_children():
            messagebox.showwarning("Warning", "Please add at least one item")
            return
        
        try:
            customer_id = int(customer.split(" - ")[0])
            
            self.result = {
                'prescription': {
                    'customer_id': customer_id,
                    'doctor_name': self.doctor_entry.get() or None,
                    'doctor_license': self.license_entry.get() or None,
                    'issue_date': self.issue_entry.get(),
                    'expiry_date': self.expiry_entry.get() or None,
                    'notes': self.notes_text.get("1.0", "end-1c") or None
                },
                'items': []
            }
            
            for item in self.items_tree.get_children():
                values = self.items_tree.item(item)['values']
                self.result['items'].append({
                    'medicine_id': self.items_tree.item(item)['tags'][0],
                    'quantity': values[1],
                    'dosage': values[2],
                    'instructions': "Take as directed"
                })
            
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid customer selection")