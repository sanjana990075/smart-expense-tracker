import pytest


def make_expense_payload(title: str, amount: float, category: str, date_str: str) -> dict:
    return {
        "title": title,
        "amount": amount,
        "category": category,
        "date": date_str,
    }


def create_expense(client, title: str, amount: float, category: str, date_str: str):
    return client.post("/expenses", json=make_expense_payload(title, amount, category, date_str))


def test_create_expense_success(client):
    payload = make_expense_payload("Groceries", 45.50, "Food", "2026-08-01")
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["title"] == "Groceries"
    assert data["amount"] == 45.50
    assert data["category"] == "Food"
    assert data["date"] == "2026-08-01"

@pytest.mark.parametrize("payload,expected_detail", [
    # Zero amount
    ({"title": "Free lunch", "amount": 0.0, "category": "Food", "date": "2026-08-01"}, "greater than 0"),
    # Negative amount
    ({"title": "Refund", "amount": -10.0, "category": "Food", "date": "2026-08-01"}, "greater than 0"),
    # Empty title
    ({"title": "  ", "amount": 10.0, "category": "Food", "date": "2026-08-01"}, "Value cannot be empty or only whitespace"),
    # Empty category
    ({"title": "Taxi", "amount": 10.0, "category": "", "date": "2026-08-01"}, "Value cannot be empty or only whitespace"),
    # Invalid date
    ({"title": "Taxi", "amount": 10.0, "category": "Transport", "date": "2026-13-45"}, "Input should be a valid date"),
])
def test_create_expense_validation(client, payload, expected_detail):
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422
    
    # Check that error detail mentions the correct validation message
    errors = response.json()["detail"]
    assert any(expected_detail in err["msg"] for err in errors)

def test_list_expenses_and_filtering(client):
    # Setup mock expenses
    create_expense(client, "Apple", 1.5, "Food", "2026-08-01")
    create_expense(client, "Bus Ticket", 2.5, "Transport", "2026-08-02")
    create_expense(client, "Banana", 0.8, "Food", "2026-08-03")
    
    # List all
    list_response = client.get("/expenses")
    assert list_response.status_code == 200
    all_expenses = list_response.json()
    assert len(all_expenses) == 3
    # Check descending order by date (2026-08-03, then 2026-08-02, then 2026-08-01)
    assert all_expenses[0]["title"] == "Banana"
    assert all_expenses[1]["title"] == "Bus Ticket"
    assert all_expenses[2]["title"] == "Apple"

    # Filter by category (case-insensitive) - path param (dedicated endpoint)
    category_response = client.get("/expenses/category/food")
    assert category_response.status_code == 200
    food_expenses = category_response.json()
    assert len(food_expenses) == 2
    assert all(expense["category"] == "Food" for expense in food_expenses)

    # Filter by category path with no match
    no_match_response = client.get("/expenses/category/Entertainment")
    assert no_match_response.status_code == 200
    assert len(no_match_response.json()) == 0

def test_get_totals(client):
    create_expense(client, "A", 10.0, "Food", "2026-08-01")
    create_expense(client, "B", 20.0, "Food", "2026-08-02")
    create_expense(client, "C", 15.5, "Transport", "2026-08-03")
    
    totals_response = client.get("/expenses/total")
    assert totals_response.status_code == 200
    totals = totals_response.json()
    assert totals["total"] == 45.5
    assert totals["by_category"] == {
        "Food": 30.0,
        "Transport": 15.5
    }


def test_get_totals_empty(client):
    totals_response = client.get("/expenses/total")
    assert totals_response.status_code == 200
    assert totals_response.json() == {
        "total": 0.0,
        "by_category": {}
    }


def test_delete_expense(client):
    # Setup
    resp = create_expense(client, "Delete Me", 100.0, "Bills", "2026-08-01")
    expense_id = resp.json()["id"]
    
    # Verify it exists
    assert len(client.get("/expenses").json()) == 1
    
    # Delete
    del_resp = client.delete(f"/expenses/{expense_id}")
    assert del_resp.status_code == 204
    
    # Verify deleted from list
    assert len(client.get("/expenses").json()) == 0
    
    # Delete again (404)
    del_resp_again = client.delete(f"/expenses/{expense_id}")
    assert del_resp_again.status_code == 404

def test_delete_invalid_id(client):
    response = client.delete("/expenses/non-existent-uuid")
    assert response.status_code == 404

def test_get_expense_by_id(client):
    resp = create_expense(client, "Get Me", 50.0, "Shopping", "2026-08-02")
    expense_id = resp.json()["id"]
    
    # Test success retrieve
    get_response = client.get(f"/expenses/{expense_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == expense_id
    assert data["title"] == "Get Me"
    assert data["amount"] == 50.0
    assert data["category"] == "Shopping"
    assert data["date"] == "2026-08-02"
    
    # Test 404 retrieve
    missing_response = client.get("/expenses/non-existent-uuid")
    assert missing_response.status_code == 404
