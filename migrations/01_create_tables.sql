-- Create table to track imported files
CREATE TABLE IF NOT EXISTS imported_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_name VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_file (dataset_name, file_name)
);

-- Create table for employers dataset
CREATE TABLE IF NOT EXISTS employers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT,
    quarter INT,
    province VARCHAR(255),
    program_stream VARCHAR(255),
    employer VARCHAR(255),
    address TEXT,
    occupation VARCHAR(255),
    incorporate_status VARCHAR(255),
    approved_lmias INT,
    approved_positions INT,
    import_file_id INT,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (import_file_id) REFERENCES imported_files(id)
);

-- Create indexes for common queries
CREATE INDEX idx_employers_province ON employers(province);
CREATE INDEX idx_employers_program_stream ON employers(program_stream);
CREATE INDEX idx_employers_employer ON employers(employer);
CREATE INDEX idx_employers_occupation ON employers(occupation);
