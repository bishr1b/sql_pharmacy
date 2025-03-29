import mysql.connector
from tkinter import messagebox
from mysql.connector import pooling

class Database:
    __connection_pool = None

    @classmethod
    def initialize_pool(cls):
        """Initialize the database connection pool"""
        try:
            cls.__connection_pool = pooling.MySQLConnectionPool(
                pool_name="pharmacy_pool",
                pool_size=5,
                host="localhost",
                user="root",
                password="",
                database="pharmacy_db"
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Connection Pool Error: {err}")

    @staticmethod
    def get_connection():
        """Get a database connection from the pool"""
        if Database.__connection_pool is None:
            Database.initialize_pool()
        try:
            return Database.__connection_pool.get_connection()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error getting connection: {err}")
            return None

    @staticmethod
    def close_connection(connection, cursor=None):
        """Close database connection and cursor"""
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error closing connection: {err}")