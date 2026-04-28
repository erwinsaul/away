#!/usr/bin/env python3
"""
Debug script to check database schema
"""

import sys
import os
import sqlite3

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import DB_PATH

def check_database_schema():
    print("=== Checking Database Schema ===")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(estudiantes);")
    columns = cursor.fetchall()
    print("Columns in estudiantes table:")
    for col in columns:
        print(f"  {col}")
    
    print("\nChecking for indexes:")
    cursor.execute("PRAGMA index_list(estudiantes);")
    indexes = cursor.fetchall()
    for idx in indexes:
        print(f"  Index: {idx}")
        # Get index info
        cursor.execute(f"PRAGMA index_info('{idx[1]}');")
        index_cols = cursor.fetchall()
        print(f"    Columns: {index_cols}")
    
    print("\nChecking for unique constraints in the SQL:")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='estudiantes';")
    table_sql = cursor.fetchone()
    if table_sql:
        print(f"Table SQL: {table_sql[0]}")
    
    conn.close()

if __name__ == "__main__":
    check_database_schema()