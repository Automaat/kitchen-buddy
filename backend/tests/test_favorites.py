import pytest


@pytest.fixture
def recipe(client):
    ing = client.post("/api/ingredients", json={"name": "Flour"}).json()
    response = client.post(
        "/api/recipes",
        json={
            "title": "Favorite Test",
            "ingredients": [{"ingredient_id": ing["id"], "quantity": "1"}],
        },
    )
    return response.json()


class TestListFavorites:
    def test_empty_list(self, client):
        response = client.get("/api/favorites")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_favorites(self, client, recipe):
        client.post(f"/api/favorites/{recipe['id']}")

        response = client.get("/api/favorites")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Favorite Test"
        assert data[0]["is_favorite"] is True


class TestAddFavorite:
    def test_add_success(self, client, recipe):
        response = client.post(f"/api/favorites/{recipe['id']}")
        assert response.status_code == 201
        assert response.json()["recipe_id"] == recipe["id"]

    def test_add_idempotent(self, client, recipe):
        client.post(f"/api/favorites/{recipe['id']}")
        response = client.post(f"/api/favorites/{recipe['id']}")
        assert response.status_code == 201

        list_response = client.get("/api/favorites")
        assert len(list_response.json()) == 1

    def test_add_recipe_not_found(self, client):
        response = client.post("/api/favorites/999")
        assert response.status_code == 404


class TestRemoveFavorite:
    def test_remove_success(self, client, recipe):
        client.post(f"/api/favorites/{recipe['id']}")

        response = client.delete(f"/api/favorites/{recipe['id']}")
        assert response.status_code == 204

        list_response = client.get("/api/favorites")
        assert len(list_response.json()) == 0

    def test_remove_not_found(self, client, recipe):
        response = client.delete(f"/api/favorites/{recipe['id']}")
        assert response.status_code == 404
