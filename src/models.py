import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Dict

class ExpenseBase(BaseModel):
    title: str = Field(..., max_length=100, description="Title of the expense")
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    category: str = Field(..., max_length=50, description="Expense category")
    date: datetime.date = Field(..., description="Date of the expense in YYYY-MM-DD format")

    @field_validator('title', 'category')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty or only whitespace")
        return cleaned

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: str = Field(..., description="Unique UUID identifier for the expense")

class TotalSummary(BaseModel):
    total: float
    by_category: Dict[str, float]


