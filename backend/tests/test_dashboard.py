import pytest


class TestDashboard:
    def test_empty_dashboard(self, client):
        response = client.get("/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_recipes"] == 0
        assert data["total_ingredients"] == 0
        assert data["total_favorites"] == 0
        assert data["todays_meals"] == []

    def test_counts_active_items(self, client):
        ing1 = client.post("/api/ingredients", json={"name": "Salt"}).json()
        ing2 = client.post("/api/ingredients", json={"name": "Pepper"}).json()

        client.post(
            "/api/recipes",
            json={
                "title": "Recipe 1",
                "ingredients": [{"ingredient_id": ing1["id"], "quantity": "1"}],
            },
        )
        recipe2 = client.post(
            "/api/recipes",
            json={
                "title": "Recipe 2",
                "ingredients": [{"ingredient_id": ing2["id"], "quantity": "1"}],
            },
        ).json()

        client.post(f"/api/favorites/{recipe2['id']}")

        response = client.get("/api/dashboard")
        data = response.json()
        assert data["total_recipes"] == 2
        assert data["total_ingredients"] == 2
        assert data["total_favorites"] == 1

    def test_excludes_deleted_items(self, client):
        ing = client.post("/api/ingredients", json={"name": "Butter"}).json()
        recipe = client.post(
            "/api/recipes",
            json={
                "title": "To Delete",
                "ingredients": [{"ingredient_id": ing["id"], "quantity": "1"}],
            },
        ).json()

        client.delete(f"/api/recipes/{recipe['id']}")
        client.delete(f"/api/ingredients/{ing['id']}")

        response = client.get("/api/dashboard")
        data = response.json()
        assert data["total_recipes"] == 0
        assert data["total_ingredients"] == 0
