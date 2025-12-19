import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="opticalclinic_db"
            )
            
            if self.conn.is_connected():
                print("Connection to database successful.")
        
        except Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

db = Database()
