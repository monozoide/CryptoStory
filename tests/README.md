# Testing

This directory contains all the tests for the Cryptostory application.

## How to Run Tests

To run the tests, first activate the virtual environment:

```bash
source venv/bin/activate
```

Then, run the following command:

```bash
pytest tests/
```

## Fixture Structure

The `tests/conftest.py` file contains the fixtures used in the tests. The `test_db` fixture sets up an in-memory SQLite database for testing, and the `sample_configured_symbol` and `sample_fetchjob` fixtures provide sample data for the tests.

## Column Naming Conventions

The database schema is defined in the `cryptostory/backend/dal/migrations/001_initial_schema.sql` file. The column names in the models and repositories should match the column names in the schema.
