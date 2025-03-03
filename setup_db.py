#!/usr/bin/env python3
"""
Script to set up the database for LMIA Stats project.
This script runs all pending database migrations.
"""

import os
import sys
from migrations.db_setup import setup_database

if __name__ == "__main__":
    print("Setting up the LMIA Stats database...")
    print("Running pending migrations...")

    # Run the database setup
    success = setup_database()

    if success:
        print("Database setup completed successfully!")
        sys.exit(0)
    else:
        print("Database setup failed!")
        sys.exit(1)
