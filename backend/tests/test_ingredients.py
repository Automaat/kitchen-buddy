import pytest


class TestListIngredients:
    def test_empty_list(self, client):
        response = client.get("/api/ingredients")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_active_ingredients(self, client):
        client.post("/api/ingredients", json={"name": "Salt"})
        client.post("/api/ingredients", json={"name": "Pepper"})

        response = client.get("/api/ingredients")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_search_filter(self, client):
        client.post("/api/ingredients", json={"name": "Salt"})
        client.post("/api/ingredients", json={"name": "Pepper"})

        response = client.get("/api/ingredients?search=sal")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Salt"

    def test_pagination(self, client):
        for i in range(5):
            client.post("/api/ingredients", json={"name": f"Ingredient {i}"})

        response = client.get("/api/ingredients?skip=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestCreateIngredient:
    def test_create_success(self, client):
        response = client.post(
            "/api/ingredients",
            json={"name": "Tomato", "category": "produce", "default_unit": "pieces"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tomato"
        assert data["category"] == "produce"
        assert data["default_unit"] == "pieces"
        assert data["is_active"] is True

    def test_create_minimal(self, client):
        response = client.post("/api/ingredients", json={"name": "Garlic"})
        assert response.status_code == 201
        assert response.json()["name"] == "Garlic"

    def test_create_duplicate_fails(self, client):
        client.post("/api/ingredients", json={"name": "Salt"})
        response = client.post("/api/ingredients", json={"name": "Salt"})
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestGetIngredient:
    def test_get_existing(self, client):
        create = client.post("/api/ingredients", json={"name": "Onion"})
        ingredient_id = create.json()["id"]

        response = client.get(f"/api/ingredients/{ingredient_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Onion"

    def test_get_not_found(self, client):
        response = client.get("/api/ingredients/999")
        assert response.status_code == 404


class TestUpdateIngredient:
    def test_update_name(self, client):
        create = client.post("/api/ingredients", json={"name": "Tomato"})
        ingredient_id = create.json()["id"]

        response = client.put(
            f"/api/ingredients/{ingredient_id}", json={"name": "Cherry Tomato"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Cherry Tomato"

    def test_update_partial(self, client):
        create = client.post(
            "/api/ingredients", json={"name": "Salt", "category": "pantry"}
        )
        ingredient_id = create.json()["id"]

        response = client.put(
            f"/api/ingredients/{ingredient_id}", json={"category": "spices"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Salt"
        assert data["category"] == "spices"

    def test_update_not_found(self, client):
        response = client.put("/api/ingredients/999", json={"name": "Test"})
        assert response.status_code == 404


class TestDeleteIngredient:
    def test_soft_delete(self, client):
        create = client.post("/api/ingredients", json={"name": "Butter"})
        ingredient_id = create.json()["id"]

        response = client.delete(f"/api/ingredients/{ingredient_id}")
        assert response.status_code == 204

        get_response = client.get("/api/ingredients")
        assert len(get_response.json()) == 0

    def test_delete_not_found(self, client):
        response = client.delete("/api/ingredients/999")
        assert response.status_code == 404
