# LMIA Stats Analysis

Analysis of Canada's Temporary Foreign Worker Program (TFWP) data from Open Government.

## Setup

1. Set up `.env` file in the project root. Copy the structure from `.env.example` file.

2. Create virtualenv environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Start the database:
   ```bash
   docker-compose up -d
   ```

4. Run migrations:
   ```bash
   python setup_db.py
   ```

## Data Import

Place data files in `data/(dataset_name)/` directory. Supported formats: Excel (*.xlsx) or CSV. Naming must be in the following format `tfwp_{year}q{quarter}_.*` since the data extraction script infers the year and quarter of the data from the file name.

Import data:
```bash
python3 extract-data.py <dataset_name>
```

Example:
```bash
python3 extract-data.py employers
```

## File Format

Each data file contains:
- Line 1: Description
- Line 2: Column headers
- Lines 3+: Data rows
- "Notes:" section (optional)

## Datasets

### Employers (dataset_name: "employers")

Database column mappings:
- Province/Territory → province (string)
- Program Stream → program_stream (string)
- Employer → employer (string)
- Address → address (string)
- Occupation → occupation (string)
- Incorporate Status → incorporate_status (string)
- Approved LMIAs → approved_lmias (integer)
- Approved Positions → approved_positions (integer)
- Year → year (integer, from filename)
- Quarter → quarter (integer, from filename)

## Database Migrations

Migrations in `migrations/` directory control database schema changes. Files follow `XX_description.sql` naming pattern, where `XX` is a sequence number.

See `migrations/README.md` for migration system details.
