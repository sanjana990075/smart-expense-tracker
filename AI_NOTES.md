# AI Collaboration & Engineering Notes

This document describes how AI assistance was utilized to build the Smart Expense Tracker API, including details on code generation, validations, refinements, and architectural decisions.

---

## 1. Code Attribution: AI-Generated vs. Written/Refined

### AI-Generated Skeleton

- The initial architecture (using **FastAPI** + **Pydantic**), standard router definitions, configuration files, and pytest template structure were generated using the AI.
- Boilerplate JSON read/write operations were drafted by the AI.

### Developer Refinements & Custom Code

- **Pydantic Namespace Conflict Resolution**: The initial model definition declared a field `date: date = Field(...)`. This led to a `PydanticUserError` during runtime since the field name `date` shadowed the type name `date` imported from `datetime`. We refactored this to use `import datetime` and annotated the field as `date: datetime.date` to solve the namespace collision.
- **Validation Message Unification**: Initially, `min_length=1` was defined in the Pydantic `Field` arguments for `title` and `category`, along with a custom `@field_validator` to catch whitespace-only inputs. Pytest revealed that empty strings `""` bypassed the custom validator and threw a generic Pydantic error, whereas `"   "` threw our custom error. We removed `min_length=1` from `Field` and moved all emptiness checks to the `@field_validator`, ensuring a consistent `"Value cannot be empty or only whitespace"` error message.
- **Thread-Safety & Atomic Writes**: The AI proposed a basic `json.dump` file writer. We refactored the persistence layer in `storage.py` to use a `threading.Lock()` to prevent race conditions from concurrent requests, and implemented an atomic write flow (writing to a `.tmp` file and then renaming it via `Path.replace()`) to prevent file corruption in case of unexpected crashes.
- **Float Rounding Precision**: Added explicit rounding to 2 decimal places in `/expenses/total` calculations to prevent floating-point precision issues (e.g., `15.5 + 30.0` outputting `45.50000000000001`).
- **CORS Middleware Integration**: Enabled FastAPI's `CORSMiddleware` configured to allow all origins (`*`), credentials, methods, and headers. This allows browser-based front-ends and Swagger UI instances to consume the API endpoints without cross-origin fetch failures.
- **Single Retrieval Endpoint (`GET /expenses/{expense_id}`)**: Implemented retrieval of individual expense details by ID, throwing HTTP `404 Not Found` if missing.
- **Totals Endpoint Alignment (`GET /expenses/total`)**: Implemented `GET /expenses/total` to calculate total expenses and provide a breakdown by category.

---

## 2. Validation & Testing

We ran the automated test suite using `pytest` to validate:

- Validation on negative or zero amounts.
- Rejection of empty/whitespace titles and categories.
- ISO date validation.
- Filtering by category (case-insensitive).
- Chronological ordering of list expenses (newest first).
- Correct aggregation for category totals.
- HTTP status codes (e.g., 201 for creation, 204 for deletion, 404 for missing IDs, 422 for bad requests).

---

## 3. Suggestions & Architecture Decisions Not Used

### Suggestions Rejected

1. **Using an ORM / SQLite DB**: The AI suggested using SQLite with SQLAlchemy or SQLModel. We decided against it to keep the project setup simple and lightweight as requested ("no database is required"). A well-designed thread-safe local JSON persistence layer fulfilled the assignment requirements while keeping the implementation lightweight.
2. **Third-Party File Lock Libraries**: The AI suggested installing `portalocker` or `pywin32` for platform-specific OS file locking. Instead, we used the standard library `threading.Lock` and atomic replacement (`Path.replace()`), which are cross-platform, require no additional dependencies, and are well-suited for this project's file-based persistence.
