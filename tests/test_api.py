from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_items():
    """Test getting all items"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 2


def test_get_item():
    """Test getting a specific item"""
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert "name" in item
    assert "description" in item
    assert "price" in item


def test_create_item():
    """Test creating a new item"""
    new_item = {
        "name": "Test Item",
        "description": "Test Description",
        "price": 15.99
    }
    response = client.post("/api/v1/items/", json=new_item)
    assert response.status_code == 201
    created_item = response.json()
    assert created_item["name"] == new_item["name"]
    assert created_item["description"] == new_item["description"]
    assert created_item["price"] == new_item["price"]
    assert "id" in created_item


def test_update_item():
    """Test updating an item"""
    update_data = {
        "name": "Updated Item"
    }
    response = client.put("/api/v1/items/1", json=update_data)
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["id"] == 1
    assert updated_item["name"] == update_data["name"]


def test_delete_item():
    """Test deleting an item"""
    # First create an item to delete
    new_item = {
        "name": "Item to Delete",
        "description": "This item will be deleted",
        "price": 9.99
    }
    create_response = client.post("/api/v1/items/", json=new_item)
    created_item = create_response.json()
    
    # Then delete it
    delete_response = client.delete(f"/api/v1/items/{created_item['id']}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/items/{created_item['id']}")
    assert get_response.status_code == 404
