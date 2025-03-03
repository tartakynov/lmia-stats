This is set of Python tools for downloading, extracting and analysing data for Temporary Foreign Worker Program (TFWP) from Canada's Open Government website.

Scripts
- `download-data.py` downloads the specified dataset for the specified period
- `extract-data.py` extracts data from the downloaded files into the database
- `setup_db.py` sets up the database and runs pending migrations

## extract-data.py

Data files are going to be downloaded to `data/(dataset_name)` folder in Excel format (*.xlsx). The script iterates over the files, confirms if their data was already extracted into the database and if the file was not yet extracted, then it extracts its data into the database.

Data in each Excel file will be given in a single spreadsheet in the following format:
```
First line - description of the data
Second line - columns
Next N lines until "Notes:" - data cells
Notes:
Next N lines - each line contains notes
```

To extract datasets, run `python3 extract-data.py (dataset_name)`, for example

```bash
python3 extract-data.py employers
```

This will make the sccript to look for data in `./data/employers/` and extract their content into the database.

The script also maintains the list of imported data files in the database.

# Datasets

## Positive Labour Market Impact Assessment (LMIA) Employers List (dataset_name "employers")

Columns mappings
- Province/Territory - db column "province", string
- Program Stream - db column "program_stream", string
- Employer - db column "employer, string
- Address - db column "address", string
- Occupation - db column "occupation", string
- Incorporate Status - db column "incorporate_status", string
- Approved LMIAs - db column "approved_lmias", integer
- Approved Positions - db column "approved_positions", integer

# Database

The database uses mariadb:11 docker image. To set up the database:

1. Start the database container:
   ```bash
   docker-compose up -d
   ```

2. Run the database migrations:
   ```bash
   python setup_db.py
   ```

## Database Migrations

The project uses a migration system to manage database schema changes. Migrations are stored in the `migrations/` directory and are applied in order based on their numeric prefix.

To create a new migration, add a new SQL file to the `migrations/` directory following the naming convention `XX_description.sql` where `XX` is a numeric prefix.

See `migrations/README.md` for more details on the migration system.
