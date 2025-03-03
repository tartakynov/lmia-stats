#!/usr/bin/env python3
"""
Database utility functions for LMIA Stats project.
"""

import os
import mysql.connector
from mysql.connector import Error

# Database connection parameters
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'lmia_user'),
    'password': os.environ.get('DB_PASSWORD', 'lmia_password'),
    'database': os.environ.get('DB_NAME', 'lmia_stats')
}

def get_db_connection():
    """
    Create and return a database connection.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def close_connection(conn, cursor=None):
    """
    Close database connection and cursor.

    Args:
        conn: Database connection object
        cursor: Database cursor object
    """
    if cursor:
        cursor.close()
    if conn and conn.is_connected():
        conn.close()

def is_file_imported(dataset_name, file_name):
    """
    Check if a file has already been imported into the database.

    Args:
        dataset_name (str): Name of the dataset
        file_name (str): Name of the file

    Returns:
        bool: True if the file has been imported, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        query = """
        SELECT COUNT(*) FROM imported_files
        WHERE dataset_name = %s AND file_name = %s
        """
        cursor.execute(query, (dataset_name, file_name))
        result = cursor.fetchone()
        return result[0] > 0
    except Error as e:
        print(f"Error checking if file is imported: {e}")
        return False
    finally:
        close_connection(conn, cursor)

def record_imported_file(dataset_name, file_name):
    """
    Record that a file has been imported into the database.

    Args:
        dataset_name (str): Name of the dataset
        file_name (str): Name of the file

    Returns:
        int: ID of the inserted record, or None if the operation failed
    """
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO imported_files (dataset_name, file_name)
        VALUES (%s, %s)
        """
        cursor.execute(query, (dataset_name, file_name))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error recording imported file: {e}")
        conn.rollback()
        return None
    finally:
        close_connection(conn, cursor)

def insert_employer_data(data_rows, import_file_id):
    """
    Insert employer data into the database.

    Args:
        data_rows (list): List of dictionaries containing employer data
        import_file_id (int): ID of the imported file record

    Returns:
        bool: True if the operation was successful, False otherwise
    """
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO employers (
            province, program_stream, employer, address,
            occupation, incorporate_status, approved_lmias,
            approved_positions, import_file_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for row in data_rows:
            cursor.execute(query, (
                row.get('province'),
                row.get('program_stream'),
                row.get('employer'),
                row.get('address'),
                row.get('occupation'),
                row.get('incorporate_status'),
                row.get('approved_lmias'),
                row.get('approved_positions'),
                import_file_id
            ))

        conn.commit()
        return True
    except Error as e:
        print(f"Error inserting employer data: {e}")
        conn.rollback()
        return False
    finally:
        close_connection(conn, cursor)
