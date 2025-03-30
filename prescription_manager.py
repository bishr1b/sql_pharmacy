import tkinter as tk
from tkinter import ttk, messagebox
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
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Customer", "Doctor", "Issued", "Expires", "Items"), show="headings")
        
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
        # Clear current entries
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
        
        # Debugging: Check if prescriptions are returned
        print("Prescriptions:", prescriptions)

        if not prescriptions:
            messagebox.showinfo("No Data", "No prescriptions found.")
            return

        # Insert data into the treeview
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
                    # Check medicine availability
                    med = Medicine.get_by_id(item['medicine_id'])
                    if not med or med['quantity'] < item['quantity']:
                        raise ValueError(f"Not enough stock for {med['name'] if med else 'selected medicine'}")
                    
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
        try:
            # Get existing prescription data
            prescription = Prescription.get_by_id(prescription_id)
            if not prescription:
                raise Exception("Prescription not found")
            
            # Get existing items
            items = Database.execute_query(
                """SELECT medicine_id, quantity, dosage, instructions 
                   FROM prescription_items 
                   WHERE prescription_id = %s""",
                (prescription_id,), fetch=True
            )
            
            dialog = PrescriptionDialog(
                self.frame,
                title="Edit Prescription",
                data={
                    'prescription': {
                        'customer_id': prescription['customer_id'],
                        'doctor_name': prescription['doctor_name'],
                        'doctor_license': prescription['doctor_license'],
                        'issue_date': prescription['issue_date'].strftime("%Y-%m-%d"),
                        'expiry_date': prescription['expiry_date'].strftime("%Y-%m-%d") if prescription['expiry_date'] else None,
                        'notes': prescription['notes']
                    },
                    'items': items
                }
            )
            
            if dialog.result:
                # Update prescription
                Prescription.update(prescription_id, dialog.result['prescription'])
                
                # Delete existing items
                Database.execute_query(
                    "DELETE FROM prescription_items WHERE prescription_id = %s",
                    (prescription_id,)
                )
                
                # Add new items
                for item in dialog.result['items']:
                    Database.execute_query(
                        """INSERT INTO prescription_items 
                          (prescription_id, medicine_id, quantity, dosage, instructions) 
                          VALUES (%s, %s, %s, %s, %s)""",
                        (prescription_id, item['medicine_id'], item['quantity'], 
                         item['dosage'], item['instructions'])
                    )
                
                self.load_prescriptions()
                messagebox.showinfo("Success", "Prescription updated successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit prescription: {str(e)}")

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
