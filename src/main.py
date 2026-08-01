from uuid import uuid4
from fastapi import FastAPI, HTTPException, status
from typing import List
from src.config import EXPENSES_FILE
from src.models import Expense, ExpenseCreate, TotalSummary
from src.storage import JSONExpenseStorage

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Smart Expense Tracker API",
    description=(
        "A REST API to manage personal expenses, supporting creating, listing, "
        "filtering by category, total calculations, retrieval by ID, and deletion."
    ),
    version="1.0.0",
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


storage = JSONExpenseStorage(EXPENSES_FILE)

@app.post(
    "/expenses", 
    response_model=Expense, 
    status_code=status.HTTP_201_CREATED,
    summary="Add a new expense",
    description="Validates and adds a new expense, returning the created expense with a unique UUID."
)
def create_expense(expense_in: ExpenseCreate):
    expense_id = str(uuid4())
    expense = Expense(id=expense_id, **expense_in.model_dump())
    storage.add(expense)
    return expense

@app.get(
    "/expenses", 
    response_model=List[Expense],
    summary="Retrieve all expenses",
    description="Retrieve all expenses. Sorted by date descending."
)
def list_expenses():
    expenses = storage.get_all()
    expenses.sort(key=lambda e: e.date, reverse=True)
    return expenses

@app.get(
    "/expenses/category/{category}", 
    response_model=List[Expense],
    summary="Filter expenses by category (dedicated endpoint)",
    description="Retrieve all expenses belonging to a specific category. Sorted by date descending."
)
def list_expenses_by_category(category: str):
    category_clean = category.strip().lower()
    expenses = storage.get_all()
    filtered = [e for e in expenses if e.category.lower() == category_clean]
    filtered.sort(key=lambda e: e.date, reverse=True)
    return filtered


@app.get(
    "/expenses/total", 
    response_model=TotalSummary,
    summary="Calculate total expenses",
    description="Returns the total expenses and breakdown by category."
)
def get_totals():
    expenses = storage.get_all()
    
    total = sum(e.amount for e in expenses)
    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0.0) + e.amount
        
    # Rounding to 2 decimal places to avoid float precision issues
    return TotalSummary(
        total=round(total, 2),
        by_category={k: round(v, 2) for k, v in by_category.items()}
    )


@app.get(
    "/expenses/{expense_id}",
    response_model=Expense,
    summary="Get expense by ID",
    description="Retrieves a single expense details by its unique ID. Returns 404 if not found."
)
def get_expense_by_id(expense_id: str):
    expense = storage.get_by_id(expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found"
        )
    return expense

@app.delete(
    "/expenses/{expense_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
    description="Deletes the expense with the specified ID. Returns 404 if not found."
)
def delete_expense(expense_id: str):
    deleted = storage.delete(expense_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Expense with ID {expense_id} not found"
        )
    return None

