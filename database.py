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
        query = f"SELECT * FROM {cls.TABLE}"
        if search_term:
            query += " WHERE name LIKE %s"
            return Database.execute_query(query, (f"%{search_term}%",), fetch=True)
        return Database.execute_query(query, fetch=True)
    
    @classmethod
    def get_by_id(cls, id: int) -> Optional[Dict]:
        query = f"SELECT * FROM {cls.TABLE} WHERE {cls.TABLE}_id = %s"
        result = Database.execute_query(query, (id,), fetch=True)
        return result[0] if result else None
    
    @classmethod
    def create(cls, data: Dict) -> int:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {cls.TABLE} ({columns}) VALUES ({placeholders})"
        Database.execute_query(query, tuple(data.values()))
        return Database.execute_query("SELECT LAST_INSERT_ID()", fetch=True)[0]['LAST_INSERT_ID()']
    
    @classmethod
    def update(cls, id: int, data: Dict) -> bool:
        set_clause = ', '.join([f"{key}=%s" for key in data.keys()])
        query = f"UPDATE {cls.TABLE} SET {set_clause} WHERE {cls.TABLE}_id = %s"
        try:
            Database.execute_query(query, tuple(data.values()) + (id,))
            return True
        except:
            return False
    
    @classmethod
    def delete(cls, id: int) -> bool:
        query = f"DELETE FROM {cls.TABLE} WHERE {cls.TABLE}_id = %s"
        try:
            Database.execute_query(query, (id,))
            return True
        except:
            return False

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

class Customer(BaseModel):
    TABLE = "customers"
    
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
                       (customer_id, employee_id, order_date, total_amount, order_type) 
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                order_data.get('customer_id'),
                order_data.get('employee_id'),
                order_data.get('order_date', datetime.now()),
                order_data['total_amount'],
                order_data.get('order_type', 'retail')
            ))
            order_id = cursor.lastrowid
            
            # Add order items - Fixed table name to match SQL schema
            for item in items:
                query = """INSERT INTO order_items 
                          (order_id, medicine_id, quantity, unit_price, subtotal) 
                          VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (
                    order_id,
                    item['medicine_id'],
                    item['quantity'],
                    item['price'],
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