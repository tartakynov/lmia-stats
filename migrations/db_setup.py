#!/usr/bin/env python3
"""
Database setup script for LMIA Stats project.
This script creates the necessary database tables if they don't exist and
tracks which migrations have already been applied.
"""

import os
import mysql.connector
from mysql.connector import Error
import time
import glob
import re

# Database connection parameters
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'lmia_user'),
    'password': os.environ.get('DB_PASSWORD', 'lmia_password'),
    'database': os.environ.get('DB_NAME', 'lmia_stats')
}

def wait_for_db(max_attempts=30, delay=2):
    """Wait for the database to become available."""
    print("Waiting for database to become available...")
    attempts = 0

    while attempts < max_attempts:
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            conn.close()
            print("Database is available!")
            return True
        except Error:
            attempts += 1
            print(f"Database not available yet. Attempt {attempts}/{max_attempts}")
            time.sleep(delay)

    print("Failed to connect to the database after multiple attempts.")
    return False

def execute_sql_file(cursor, file_path):
    """Execute SQL statements from a file."""
    with open(file_path, 'r') as f:
        sql_script = f.read()

    # Split the script by semicolons to execute each statement separately
    statements = sql_script.split(';')

    for statement in statements:
        # Skip empty statements
        if statement.strip():
            cursor.execute(statement)

def ensure_migrations_table(cursor):
    """Ensure the migrations tracking table exists."""
    # First, create the migrations tracking table if it doesn't exist
    migrations_table_sql = """
    CREATE TABLE IF NOT EXISTS applied_migrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        migration_name VARCHAR(255) NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_migration (migration_name)
    );
    """
    cursor.execute(migrations_table_sql)

def get_applied_migrations(cursor):
    """Get a list of migrations that have already been applied."""
    cursor.execute("SELECT migration_name FROM applied_migrations")
    return [row[0] for row in cursor.fetchall()]

def record_migration(cursor, migration_name):
    """Record that a migration has been applied."""
    cursor.execute(
        "INSERT INTO applied_migrations (migration_name) VALUES (%s)",
        (migration_name,)
    )

def get_migration_files():
    """Get a sorted list of migration files."""
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    migration_files = glob.glob(os.path.join(migrations_dir, "*.sql"))

    # Sort files by their numeric prefix
    def get_migration_number(filename):
        match = re.match(r'(\d+)_', os.path.basename(filename))
        return int(match.group(1)) if match else float('inf')

    return sorted(migration_files, key=get_migration_number)

def setup_database():
    """Set up the database tables by running migrations that haven't been applied yet."""
    try:
        # Wait for the database to be available
        if not wait_for_db():
            return False

        # Connect to the database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Ensure migrations table exists
        ensure_migrations_table(cursor)

        # Get list of applied migrations
        applied_migrations = get_applied_migrations(cursor)

        # Get sorted list of migration files
        migration_files = get_migration_files()

        # Apply migrations that haven't been applied yet
        for migration_file in migration_files:
            migration_name = os.path.basename(migration_file)

            if migration_name not in applied_migrations:
                print(f"Applying migration: {migration_name}")
                execute_sql_file(cursor, migration_file)
                record_migration(cursor, migration_name)
                print(f"Migration applied: {migration_name}")
            else:
                print(f"Skipping already applied migration: {migration_name}")

        # Commit the changes
        conn.commit()

        print("Database setup completed successfully!")
        return True

    except Error as e:
        print(f"Error setting up database: {e}")
        return False

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()
