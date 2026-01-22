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


class TestGetPantryItem:
    def test_get_existing(self, client, ingredient):
        create = client.post(
            "/api/pantry",
            json={"ingredient_id": ingredient["id"], "quantity": 500, "unit": "g"},
        )
        item_id = create.json()["id"]

        response = client.get(f"/api/pantry/{item_id}")
        assert response.status_code == 200
        assert response.json()["ingredient_name"] == "Test Ingredient"

    def test_get_not_found(self, client):
        response = client.get("/api/pantry/9999")
        assert response.status_code == 404


class TestSearchPantryItems:
    def test_search_by_ingredient_name(self, client):
        ing1 = client.post(
            "/api/ingredients",
            json={"name": "Tomato", "category": "produce"},
        ).json()
        ing2 = client.post(
            "/api/ingredients",
            json={"name": "Onion", "category": "produce"},
        ).json()

        client.post("/api/pantry", json={"ingredient_id": ing1["id"], "quantity": 100})
        client.post("/api/pantry", json={"ingredient_id": ing2["id"], "quantity": 200})

        response = client.get("/api/pantry?search=tomato")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["ingredient_name"] == "Tomato"


class TestAddIngredientToPantry:
    def test_add_new_ingredient(self, client, ingredient):
        response = client.post(
            f"/api/pantry/add-ingredient/{ingredient['id']}?quantity=100&unit=g"
        )
        assert response.status_code == 201
        assert float(response.json()["quantity"]) == 100

    def test_add_existing_increments_quantity(self, client, ingredient):
        client.post(f"/api/pantry/add-ingredient/{ingredient['id']}?quantity=100")
        response = client.post(
            f"/api/pantry/add-ingredient/{ingredient['id']}?quantity=50"
        )
        assert response.status_code == 201
        assert float(response.json()["quantity"]) == 150

    def test_add_invalid_ingredient(self, client):
        response = client.post("/api/pantry/add-ingredient/9999?quantity=100")
        assert response.status_code == 400
