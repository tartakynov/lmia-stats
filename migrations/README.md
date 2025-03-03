# Database Migrations

This directory contains database migration scripts for the LMIA Stats project.

## How Migrations Work

The migration system tracks which migrations have been applied to the database and only runs new migrations. This ensures that migrations are only applied once.

## Migration File Naming Convention

Migration files should follow this naming convention:

```
XX_description.sql
```

Where:
- `XX` is a numeric prefix (e.g., 00, 01, 02) that determines the order in which migrations are applied
- `description` is a brief description of what the migration does

For example:
- `00_create_migrations_table.sql`
- `01_create_tables.sql`
- `02_add_new_column.sql`

## Creating a New Migration

To create a new migration:

1. Create a new SQL file in this directory following the naming convention
2. Write your SQL statements in the file
3. Run the migration using the setup script

## Running Migrations

To run all pending migrations:

```bash
python setup_db.py
```

This will:
1. Check which migrations have already been applied
2. Run any new migrations in the correct order
3. Record which migrations have been applied

## Migration Tracking

The system uses a table called `applied_migrations` to track which migrations have been applied. This table is automatically created when you run the first migration.
