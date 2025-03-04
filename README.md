# Globants_DE_Challenge
Globants' Data Engineering Coding Challenge
# DB Migration API

This project is a REST API for migrating data from CSV files to a SQL database. It supports batch inserts and uploading CSV files to the database.

## Endpoints

### Upload CSV
- **URL**: `/upload_csv`
- **Method**: `POST`
- **Parameters**:
  - `file`: CSV file to upload
  - `table`: Table name (`departments`, `jobs`, `employees`)

### Batch Insert
- **URL**: `/batch_insert`
- **Method**: `POST`
- **Parameters**:
  - `table`: Table name (`departments`, `jobs`, `employees`)
  - `rows`: List of rows to insert

### Metrics
- **URL**: `/metrics/hired_per_quarter`
- **Method**: `GET`
- **Description**: Number of employees hired for each job and department in 2021 divided by quarter.

- **URL**: `/metrics/departments_above_mean`
- **Method**: `GET`
- **Description**: List of departments that hired more employees than the mean in 2021.

## Setup
1. Install required libraries:
    ```bash
    pip install Flask SQLAlchemy pandas
    ```
2. Run the application:
    ```bash
    python app.py
    ```

## Development Process
Frequent updates will be made to this repository to allow analyzing the development process.
