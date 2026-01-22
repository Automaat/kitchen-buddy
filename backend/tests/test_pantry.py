import pytest


@pytest.fixture
def ingredient(client):
    response = client.post(
        "/api/ingredients",
        json={"name": "Test Ingredient", "category": "produce", "default_unit": "g"},
    )
    return response.json()


class TestListPantryItems:
    def test_empty_list(self, client):
        response = client.get("/api/pantry")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_items(self, client, ingredient):
        client.post(
            "/api/pantry",
            json={"ingredient_id": ingredient["id"], "quantity": 500, "unit": "g"},
        )
        response = client.get("/api/pantry")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["ingredient_name"] == "Test Ingredient"


class TestCreatePantryItem:
    def test_create_success(self, client, ingredient):
        response = client.post(
            "/api/pantry",
            json={
                "ingredient_id": ingredient["id"],
                "quantity": 500,
                "unit": "g",
                "notes": "Fresh",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["ingredient_id"] == ingredient["id"]
        assert float(data["quantity"]) == 500
        assert data["unit"] == "g"
        assert data["notes"] == "Fresh"

    def test_create_invalid_ingredient(self, client):
        response = client.post(
            "/api/pantry",
            json={"ingredient_id": 9999, "quantity": 500},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()


class TestUpdatePantryItem:
    def test_update_quantity(self, client, ingredient):
        create_response = client.post(
            "/api/pantry",
            json={"ingredient_id": ingredient["id"], "quantity": 500},
        )
        item_id = create_response.json()["id"]

        response = client.put(
            f"/api/pantry/{item_id}",
            json={"quantity": 250},
        )
        assert response.status_code == 200
        assert float(response.json()["quantity"]) == 250

    def test_update_not_found(self, client):
        response = client.put("/api/pantry/9999", json={"quantity": 100})
        assert response.status_code == 404


class TestDeletePantryItem:
    def test_delete_success(self, client, ingredient):
        create_response = client.post(
            "/api/pantry",
            json={"ingredient_id": ingredient["id"], "quantity": 500},
        )
        item_id = create_response.json()["id"]

        response = client.delete(f"/api/pantry/{item_id}")
        assert response.status_code == 204

        get_response = client.get("/api/pantry")
        assert len(get_response.json()) == 0

    def test_delete_not_found(self, client):
        response = client.delete("/api/pantry/9999")
        assert response.status_code == 404
