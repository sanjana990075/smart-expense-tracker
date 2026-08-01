# Smart Expense Tracker API

A REST API built with Python 3 and FastAPI to manage personal expenses. It supports adding, listing, filtering, retrieving, deleting expenses, and calculating expense totals. Data is persisted to a local JSON file store with thread-safe atomic writes to prevent corruption.

## Features

- **Add an Expense**: Validates parameters (amount must be positive, title/category cannot be empty) and assigns a unique UUID.
- **View All Expenses**: Retrieve all expenses. Results are returned in reverse chronological order (newest first).
- **View a Single Expense**: Retrieve detailed fields of a specific expense by ID (`GET /expenses/{expense_id}`), returning HTTP `404 Not Found` if it does not exist.
- **Filter Expenses by Category**: Retrieve all expenses belonging to a specific category (`GET /expenses/category/{category}`).
- **Calculate Total Expenses**: Calculates the total expenses and breaks it down by category (available via `GET /expenses/total`).
- **Delete an Expense**: Deletes an expense by its unique identifier (returns HTTP `204 No Content`, or HTTP `404 Not Found` if the expense doesn't exist).
- **Interactive Documentation**: Interactive API documentation automatically generated via Swagger UI/OpenAPI.
- **Robust Persistence**: Persists data to `data/expenses.json` using atomic file writes to ensure storage integrity.

---

## Installation & Setup

Ensure you have Python 3.8+ installed on your system.

### 1. Install Dependencies

Run the following command from the project root to install the required packages:

```bash
python -m pip install -r requirements.txt
```

> Optional: you can use a `.env` file for local configuration values. The project already ignores `.env` so sensitive or environment-specific contents will not be committed.

---

## Running the Server

Start the development server using Uvicorn:

```bash
python -m uvicorn src.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### Interactive API Documentation

Once the server is running, you can explore and test the endpoints interactively using the built-in OpenAPI/Swagger UI at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

| Method | Endpoint                        | Description                 |
| ------ | ------------------------------- | --------------------------- |
| POST   | `/expenses`                     | Create a new expense        |
| GET    | `/expenses`                     | List all expenses           |
| GET    | `/expenses/{expense_id}`        | Retrieve an expense by ID   |
| GET    | `/expenses/category/{category}` | Filter expenses by category |
| GET    | `/expenses/total`               | Calculate total expenses    |
| DELETE | `/expenses/{expense_id}`        | Delete an expense           |

---

## Running the Tests

To run the full suite of unit tests, use:

```bash
python -m pytest
```

or simply:

```bash
pytest
```

---

## Project Structure

```
smart-expense-tracker/
  ├── README.md               # Setup and execution instructions (this file)
  ├── AI_NOTES.md             # Documentation on AI collaboration and engineering decisions
  ├── requirements.txt        # Python package dependencies
  ├── data/
  │   └── expenses.json       # Local database (generated automatically on first run)
  ├── src/
  │   ├── __init__.py
  │   ├── main.py             # FastAPI App instance and route definitions
  │   ├── models.py           # Pydantic validation schemas
  │   ├── storage.py          # Data persistence layer with atomic write locks
  │   └── config.py           # Configuration values (file paths, settings)
  └── tests/
      ├── __init__.py
      ├── conftest.py         # Pytest fixtures and mocks (isolating storage)
      └── test_api.py         # Complete API unit tests
```
