import mysql.connector
from mysql.connector import pooling
from datetime import date, datetime
from typing import List, Dict, Optional

class Database:
    __connection_pool = None

    @classmethod
    def initialize_pool(cls):
        try:
            cls.__connection_pool = pooling.MySQLConnectionPool(
                pool_name="pharmacy_pool",
                pool_size=5,
                host="localhost",
                user="root",
                password="",
                database="pharmacy_db",
                autocommit=False
            )
        except mysql.connector.Error as err:
            raise Exception(f"Database connection error: {err}")

    @classmethod
    def get_connection(cls):
        if cls.__connection_pool is None:
            cls.initialize_pool()
        return cls.__connection_pool.get_connection()

    @classmethod
    def close_connection(cls, connection, cursor=None):
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    @classmethod
    def execute_query(cls, query: str, params: tuple = None, fetch: bool = False):
        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cls.close_connection(conn, cursor)

class BaseModel:
    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        pass
    
    @classmethod
    def get_by_id(cls, id: int) -> Optional[Dict]:
        pass
    
    @classmethod
    def create(cls, data: Dict) -> int:
        pass
    
    @classmethod
    def update(cls, id: int, data: Dict) -> bool:
        pass
    
    @classmethod
    def delete(cls, id: int) -> bool:
        pass

class Medicine(BaseModel):
    TABLE = "medicines"
    
    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        query = f"""SELECT m.*, s.name as supplier_name 
                   FROM {cls.TABLE} m LEFT JOIN suppliers s 
                   ON m.supplier_id = s.supplier_id"""
        if search_term:
            query += " WHERE m.name LIKE %s OR m.category LIKE %s"
            return Database.execute_query(query, (f"%{search_term}%", f"%{search_term}%"), fetch=True)
        return Database.execute_query(query, fetch=True)
    
    @classmethod
    def reduce_stock(cls, medicine_id: int, quantity: int) -> bool:
        query = f"UPDATE {cls.TABLE} SET quantity = quantity - %s WHERE medicine_id = %s AND quantity >= %s"
        try:
            Database.execute_query(query, (quantity, medicine_id, quantity))
            return True
        except:
            return False

class Supplier(BaseModel):
    TABLE = "suppliers"
    
    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        query = f"SELECT * FROM {cls.TABLE}"
        if search_term:
            query += " WHERE name LIKE %s OR contact_person LIKE %s"
            return Database.execute_query(query, (f"%{search_term}%", f"%{search_term}%"), fetch=True)
        return Database.execute_query(query, fetch=True)

class Customer(BaseModel):
    TABLE = "customers"
    
    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        query = f"SELECT * FROM {cls.TABLE}"
        if search_term:
            query += " WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s"
            return Database.execute_query(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"), fetch=True)
        return Database.execute_query(query, fetch=True)
    
    @classmethod
    def add_loyalty_points(cls, customer_id: int, points: int) -> bool:
        query = f"UPDATE {cls.TABLE} SET loyalty_points = loyalty_points + %s WHERE customer_id = %s"
        try:
            Database.execute_query(query, (points, customer_id))
            return True
        except:
            return False

class Employee(BaseModel):
    TABLE = "employees"
    
    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        query = f"SELECT * FROM {cls.TABLE}"
        if search_term:
            query += " WHERE name LIKE %s OR role LIKE %s OR email LIKE %s"
            return Database.execute_query(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"), fetch=True)
        return Database.execute_query(query, fetch=True)

class Prescription(BaseModel):
    TABLE = "prescriptions"
    
    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        query = f"""SELECT p.*, c.name as customer_name 
                   FROM {cls.TABLE} p JOIN customers c ON p.customer_id = c.customer_id"""
        if search_term:
            query += " WHERE c.name LIKE %s OR p.doctor_name LIKE %s"
            return Database.execute_query(query, (f"%{search_term}%", f"%{search_term}%"), fetch=True)
        return Database.execute_query(query, fetch=True)

class Order(BaseModel):
    TABLE = "orders"
    
    @classmethod
    def create_with_details(cls, order_data: Dict, items: List[Dict]) -> int:
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            # Create order
            query = f"""INSERT INTO {cls.TABLE} 
                       (customer_id, employee_id, order_date, total_amount, status, order_type) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                order_data['customer_id'],
                order_data['employee_id'],
                order_data.get('order_date', datetime.now()),
                order_data['total_amount'],
                order_data.get('status', 'pending'),
                order_data.get('order_type', 'retail')
            ))
            order_id = cursor.lastrowid
            
            # Add order items
            for item in items:
                query = """INSERT INTO order_details 
                          (order_id, medicine_id, quantity, subtotal) 
                          VALUES (%s, %s, %s, %s)"""
                cursor.execute(query, (
                    order_id,
                    item['medicine_id'],
                    item['quantity'],
                    item['subtotal']
                ))
            
            conn.commit()
            return order_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            Database.close_connection(conn, cursor)

class Sale(BaseModel):
    TABLE = "sales"
    
    @classmethod
    def create_from_order(cls, order_id: int) -> int:
        query = """INSERT INTO sales 
                  (order_id, sale_date) 
                  SELECT %s, order_date FROM orders WHERE order_id = %s"""
        try:
            Database.execute_query(query, (order_id, order_id))
            return True
        except:
            return False

class Payment(BaseModel):
    TABLE = "payments"

class Stock(BaseModel):
    TABLE = "stock"
    
    @classmethod
    def check_low_stock(cls, threshold: int = 10) -> List[Dict]:
        query = f"""SELECT m.name, s.quantity_in_stock, s.reorder_level 
                   FROM {cls.TABLE} s JOIN medicines m 
                   ON s.medicine_id = m.medicine_id 
                   WHERE s.quantity_in_stock <= s.reorder_level"""
        return Database.execute_query(query, fetch=True)