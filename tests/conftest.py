import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.main import app
import src.main

@pytest.fixture
def temp_storage(tmp_path):
    """Fixture to isolate storage for each test using a temporary JSON file."""
    test_file = tmp_path / "test_expenses.json"
    
    # Instantiate temporary storage
    from src.storage import JSONExpenseStorage
    test_store = JSONExpenseStorage(test_file)
    
    # Dynamically patch the storage module in main
    orig_store = src.main.storage
    src.main.storage = test_store
    
    yield test_store
    
    # Restore original storage
    src.main.storage = orig_store

@pytest.fixture
def client(temp_storage):
    """Fixture to provide a TestClient configured with isolated storage."""
    with TestClient(app) as c:
        yield c
