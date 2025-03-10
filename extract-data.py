#!/usr/bin/env python3
"""
Script to extract data from Excel files and import it into the database.
Usage: python extract-data.py <dataset_name>
Example: python extract-data.py employers
"""

import os
import sys
import glob
import re
import pandas as pd
from db_utils import is_file_imported, record_imported_file, insert_employer_data

def parse_year_quarter(filename):
    """
    Parse year and quarter from filename.
    Expected format: tfwp_YYYYqQ_pos_en.xlsx or tfwp_YYYYqQ_pos_en.csv
    Example: tfwp_2024q3_pos_en.xlsx

    Args:
        filename (str): Name of the file

    Returns:
        tuple: (year, quarter) or (None, None) if parsing fails
    """
    # Remove file extension
    base_name = os.path.splitext(filename)[0]

    # Pattern for tfwp_YYYYqQ_pos_en format
    pattern = r'tfwp_(\d{4})q(\d)_.+'

    match = re.search(pattern, base_name.lower())  # case insensitive match
    if match:
        try:
            year = int(match.group(1))
            quarter = int(match.group(2))
            if 2000 <= year <= 2100 and 1 <= quarter <= 4:
                return year, quarter
        except (ValueError, IndexError):
            pass

    return None, None

def read_data_file(file_path):
    """
    Read data from either Excel or CSV file.

    Args:
        file_path (str): Path to the data file

    Returns:
        pandas.DataFrame: DataFrame containing the file data, or None if reading fails
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.xlsx':
            return pd.read_excel(file_path, header=None)
        elif file_ext == '.csv':
            # Read CSV with Windows line endings and try different encodings
            encodings = ['utf-8', 'cp1252', 'latin1']
            for encoding in encodings:
                try:
                    return pd.read_csv(file_path, header=None, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            # If all encodings fail, try default encoding with error handling
            return pd.read_csv(file_path, header=None, encoding='utf-8', errors='replace')
        else:
            print(f"Unsupported file format: {file_ext}")
            return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def extract_employers_data(file_path, year, quarter):
    """
    Extract data from an employers dataset file.

    Args:
        file_path (str): Path to the data file
        year (int): Year parsed from filename
        quarter (int): Quarter parsed from filename

    Returns:
        list: List of dictionaries containing the extracted data
    """
    try:
        # Read the file
        df = read_data_file(file_path)
        if df is None:
            return []

        # Find the row index where the data starts (after the header)
        # First row is description, second row is column headers
        data_start_row = 2

        # Find the row index where the data ends (before "Notes:")
        notes_row_idx = None
        for idx, row in df.iterrows():
            if idx >= data_start_row:
                # Check if the first cell in this row contains "Notes:"
                if isinstance(row[0], str) and row[0].strip().startswith("Notes:"):
                    notes_row_idx = idx
                    break

        if notes_row_idx is None:
            # If "Notes:" not found, assume all rows after header are data
            data_end_row = len(df)
        else:
            data_end_row = notes_row_idx

        # Extract the column headers (second row)
        headers = df.iloc[1].tolist()

        # Clean up headers (remove NaN, strip whitespace)
        headers = [str(h).strip() if not pd.isna(h) else f"Column_{i}" for i, h in enumerate(headers)]

        # Extract the data rows
        data_df = df.iloc[data_start_row:data_end_row].copy()

        # Set the column names
        if len(data_df) > 0:
            data_df.columns = headers

        # Convert to list of dictionaries
        data_rows = []
        for _, row in data_df.iterrows():
            # Map Excel columns to database columns and strip whitespace from string values
            data_row = {
                'province': row.get('Province/Territory', '').strip() if isinstance(row.get('Province/Territory'), str) else None,
                'program_stream': row.get('Program Stream', '').strip() if isinstance(row.get('Program Stream'), str) else None,
                'employer': row.get('Employer', '').strip() if isinstance(row.get('Employer'), str) else None,
                'address': row.get('Address', '').strip() if isinstance(row.get('Address'), str) else None,
                'occupation': row.get('Occupation', '').strip() if isinstance(row.get('Occupation'), str) else None,
                'incorporate_status': row.get('Incorporate Status', '').strip() if isinstance(row.get('Incorporate Status'), str) else None,
                'approved_lmias': int(row.get('Approved LMIAs', 0)) if pd.notna(row.get('Approved LMIAs', 0)) else 0,
                'approved_positions': int(row.get('Approved Positions', 0)) if pd.notna(row.get('Approved Positions', 0)) else 0,
                'year': year,
                'quarter': quarter
            }
            data_rows.append(data_row)

        return data_rows

    except Exception as e:
        print(f"Error extracting data from {file_path}: {e}")
        return []

def process_dataset(dataset_name):
    """
    Process all Excel and CSV files for a given dataset.

    Args:
        dataset_name (str): Name of the dataset
    """
    # Get the data directory for this dataset
    data_dir = os.path.join('data', dataset_name)

    # Check if the directory exists
    if not os.path.isdir(data_dir):
        print(f"Error: Directory {data_dir} does not exist.")
        return

    # Get all Excel and CSV files in the directory
    data_files = glob.glob(os.path.join(data_dir, '*.xlsx'))
    data_files.extend(glob.glob(os.path.join(data_dir, '*.csv')))

    if not data_files:
        print(f"No Excel or CSV files found in {data_dir}.")
        return

    print(f"Found {len(data_files)} data files in {data_dir}.")

    # Process each file
    for file_path in data_files:
        file_name = os.path.basename(file_path)

        # Parse year and quarter from filename
        year, quarter = parse_year_quarter(file_name)
        if year is None or quarter is None:
            print(f"Warning: Could not parse year and quarter from {file_name}. Skipping file.")
            continue

        # Check if this file has already been imported
        if is_file_imported(dataset_name, file_name):
            print(f"Skipping {file_name} - already imported.")
            continue

        print(f"Processing {file_name} (Year: {year}, Quarter: {quarter})...")

        # Extract data based on the dataset type
        if dataset_name == 'employers':
            data_rows = extract_employers_data(file_path, year, quarter)
        else:
            print(f"Error: Unknown dataset type '{dataset_name}'.")
            continue

        if not data_rows:
            print(f"No data extracted from {file_name}.")
            continue

        print(f"Extracted {len(data_rows)} rows from {file_name}.")

        # Record the file import
        import_file_id = record_imported_file(dataset_name, file_name)

        if import_file_id is None:
            print(f"Error recording file import for {file_name}.")
            continue

        # Insert the data into the database
        if dataset_name == 'employers':
            success = insert_employer_data(data_rows, import_file_id)

            if success:
                print(f"Successfully imported {len(data_rows)} rows from {file_name}.")
            else:
                print(f"Error importing data from {file_name}.")

    print(f"Finished processing {dataset_name} dataset.")

def main():
    """Main function."""
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python extract-data.py <dataset_name>")
        print("Example: python extract-data.py employers")
        sys.exit(1)

    dataset_name = sys.argv[1]

    # Process the dataset
    process_dataset(dataset_name)

if __name__ == "__main__":
    main()
