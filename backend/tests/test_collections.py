import pytest


@pytest.fixture
def collection(client):
    response = client.post(
        "/api/collections", json={"name": "Weeknight Dinners", "description": "Quick meals"}
    )
    return response.json()


@pytest.fixture
def recipe(client):
    ing = client.post("/api/ingredients", json={"name": "Chicken"}).json()
    response = client.post(
        "/api/recipes",
        json={"title": "Grilled Chicken", "ingredients": [{"ingredient_id": ing["id"]}]},
    )
    return response.json()


class TestListCollections:
    def test_empty_list(self, client):
        response = client.get("/api/collections")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_collections(self, client, collection):
        response = client.get("/api/collections")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Weeknight Dinners"
        assert data[0]["recipe_count"] == 0


class TestCreateCollection:
    def test_create_success(self, client):
        response = client.post(
            "/api/collections",
            json={"name": "Breakfast", "description": "Morning meals"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Breakfast"
        assert data["description"] == "Morning meals"
        assert data["recipe_count"] == 0

    def test_create_minimal(self, client):
        response = client.post("/api/collections", json={"name": "Quick Bites"})
        assert response.status_code == 201
        assert response.json()["name"] == "Quick Bites"


class TestGetCollection:
    def test_get_existing(self, client, collection):
        response = client.get(f"/api/collections/{collection['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Weeknight Dinners"
        assert data["recipes"] == []

    def test_get_not_found(self, client):
        response = client.get("/api/collections/999")
        assert response.status_code == 404

    def test_get_with_recipes(self, client, collection, recipe):
        client.post(f"/api/collections/{collection['id']}/recipes/{recipe['id']}")
        response = client.get(f"/api/collections/{collection['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["title"] == "Grilled Chicken"


class TestUpdateCollection:
    def test_update_name(self, client, collection):
        response = client.put(
            f"/api/collections/{collection['id']}", json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_description(self, client, collection):
        response = client.put(
            f"/api/collections/{collection['id']}", json={"description": "New description"}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "New description"

    def test_update_not_found(self, client):
        response = client.put("/api/collections/999", json={"name": "Test"})
        assert response.status_code == 404


class TestDeleteCollection:
    def test_delete_success(self, client, collection):
        response = client.delete(f"/api/collections/{collection['id']}")
        assert response.status_code == 204

        list_response = client.get("/api/collections")
        assert len(list_response.json()) == 0

    def test_delete_not_found(self, client):
        response = client.delete("/api/collections/999")
        assert response.status_code == 404


class TestAddRecipeToCollection:
    def test_add_recipe_success(self, client, collection, recipe):
        response = client.post(
            f"/api/collections/{collection['id']}/recipes/{recipe['id']}"
        )
        assert response.status_code == 201

        detail = client.get(f"/api/collections/{collection['id']}").json()
        assert detail["recipe_count"] == 1

    def test_add_recipe_collection_not_found(self, client, recipe):
        response = client.post(f"/api/collections/999/recipes/{recipe['id']}")
        assert response.status_code == 404
        assert "Collection" in response.json()["detail"]

    def test_add_recipe_recipe_not_found(self, client, collection):
        response = client.post(f"/api/collections/{collection['id']}/recipes/999")
        assert response.status_code == 404
        assert "Recipe" in response.json()["detail"]

    def test_add_recipe_duplicate(self, client, collection, recipe):
        client.post(f"/api/collections/{collection['id']}/recipes/{recipe['id']}")
        response = client.post(
            f"/api/collections/{collection['id']}/recipes/{recipe['id']}"
        )
        assert response.status_code == 400
        assert "already in collection" in response.json()["detail"]


class TestRemoveRecipeFromCollection:
    def test_remove_recipe_success(self, client, collection, recipe):
        client.post(f"/api/collections/{collection['id']}/recipes/{recipe['id']}")
        response = client.delete(
            f"/api/collections/{collection['id']}/recipes/{recipe['id']}"
        )
        assert response.status_code == 204

        detail = client.get(f"/api/collections/{collection['id']}").json()
        assert detail["recipe_count"] == 0

    def test_remove_recipe_not_in_collection(self, client, collection, recipe):
        response = client.delete(
            f"/api/collections/{collection['id']}/recipes/{recipe['id']}"
        )
        assert response.status_code == 404
