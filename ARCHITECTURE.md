# Architecture

This document provides a high-level overview of the Cryptostory application's architecture.

## Core Modules

The application is structured into several core modules, each with a distinct responsibility:

-   **`cryptostory.domain`**: Contains the core business logic and entities of the application, such as `Candle`, `ConfiguredSymbol`, and `FetchJob`. This layer is independent of any specific framework or infrastructure.

-   **`cryptostory.infrastructure`**: Provides concrete implementations of the interfaces defined in the domain. This includes:
    -   **`database`**: Contains the SQLAlchemy schema, Alembic migrations, and repositories for data persistence.
    -   **`systemd`**: Holds templates for generating systemd service and timer files.

-   **`cryptostory.services`**: Contains the application's services, which orchestrate the business logic. This includes the `FetchService` for retrieving data and the `SchedulerService` for managing automated tasks.

-   **`cryptostory.adapters`**: Holds the components responsible for interacting with external systems, such as the `BinanceClient`.

-   **`cryptostory.ui`**: The Terminal User Interface (TUI) built with Textual. It provides a user-friendly way to configure and monitor the application.

## Technology Stack

-   **Language**: Python 3.11+
-   **Database**: PostgreSQL 16 with TimescaleDB extension
-   **TUI**: Textual
-   **API Client**: httpx
-   **ORM**: SQLAlchemy 2.0
-   **Dependency Management**: Poetry
-   **Testing**: pytest

## Data Flow

The typical data flow is as follows:

1.  A user configures a new symbol to track via the **TUI**.
2.  The configuration is saved to the **PostgreSQL database**.
3.  The **`SchedulerService`** generates a **systemd timer** for the new symbol.
4.  At the scheduled time, the systemd timer triggers a **`systemd service`**.
5.  The service runs the **CLI**, which calls the **`FetchService`**.
6.  The `FetchService` uses the **`BinanceClient`** to fetch OHLCV data from the Binance API.
7.  The `FetchService` uses the **`CandleRepository`** to save the data to the TimescaleDB hypertable in the PostgreSQL database.
