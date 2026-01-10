# Cryptostory

Cryptostory is a self-hosted Python platform for collecting and storing OHLCV (Open, High, Low, Close, Volume) data from the Binance cryptocurrency exchange. It features a Terminal User Interface (TUI) for configuration, a robust backend built with Domain-Driven Design principles, and automation capabilities through systemd.

## Features

- **Data Collection**: Fetches historical and real-time OHLCV data from Binance.
- **TUI**: A simple, terminal-based interface for configuring data collection tasks.
- **Database**: Uses PostgreSQL with the TimescaleDB extension for efficient time-series data storage.
- **Automation**: Can be configured to run automatically using systemd timers.
- **Resilient**: Includes rate limiting and exponential backoff to handle API limits gracefully.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cryptostory
    ```

2.  **Install dependencies:**
    This project uses Poetry for dependency management.
    ```bash
    poetry install
    ```

3.  **Set up the database:**
    -   Ensure you have PostgreSQL and TimescaleDB installed.
    -   Create a `.env` file from the `.env.example` template and configure your database connection details.
    -   Apply the database migrations:
        ```bash
        poetry run alembic upgrade head
        ```

## Usage

### Terminal User Interface (TUI)

To launch the TUI, run:
```bash
poetry run python -m cryptostory.ui.app
```
From the TUI, you can configure which symbols and intervals to fetch.

### Command-Line Interface (CLI)

The CLI can be used to manually trigger data fetching.

-   **Fetch data for a symbol:**
    ```bash
    poetry run python -m cryptostory.cli fetch --symbol BTCUSDT --interval 1h
    ```

## Running Tests

To run the test suite:
```bash
poetry run pytest
```
