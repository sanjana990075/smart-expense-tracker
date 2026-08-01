import json
import threading
from pathlib import Path
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from src.models import Expense, ExpenseCreate

class JSONExpenseStorage:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.lock = threading.Lock()
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Ensure the directory and file exist."""
        with self.lock:
            if not self.file_path.parent.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)

    def _read(self) -> List[dict]:
        """Read expenses directly from the file."""
        with self.lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []

    def _write(self, data: List[dict]) -> None:
        """Write the raw list of dictionaries to the JSON file."""
        with self.lock:
            # Write to a temporary file first, then rename, to prevent file corruption
            temp_file = self.file_path.with_suffix(".tmp")
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                temp_file.replace(self.file_path)
            except Exception as e:
                if temp_file.exists():
                    temp_file.unlink()
                raise e

    def get_all(self) -> List[Expense]:
        """Get all expenses parsed into Expense models."""
        raw_expenses = self._read()
        return [Expense(**item) for item in raw_expenses]

    def get_by_id(self, expense_id: str) -> Optional[Expense]:
        """Get a single expense by its ID."""
        for expense in self.get_all():
            if expense.id == expense_id:
                return expense
        return None

    def add(self, new_expense: Expense) -> Expense:
        """Add a new expense and persist to disk."""
        expenses = self._read()
        # Serialize the Expense model to JSON-compatible dict (handling dates and UUIDs)
        serialized_expense = jsonable_encoder(new_expense)
        expenses.append(serialized_expense)
        self._write(expenses)
        return new_expense

    def delete(self, expense_id: str) -> bool:
        """Delete an expense by ID. Returns True if deleted, False if not found."""
        expenses = self._read()
        initial_count = len(expenses)
        filtered_expenses = [item for item in expenses if item.get("id") != expense_id]
        
        if len(filtered_expenses) == initial_count:
            return False
            
        self._write(filtered_expenses)
        return True
