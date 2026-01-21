import pytest


@pytest.fixture
def ingredient(client):
    response = client.post("/api/ingredients", json={"name": "Flour"})
    return response.json()


@pytest.fixture
def tag(client):
    response = client.post("/api/tags", json={"name": "Baking"})
    return response.json()


class TestListRecipes:
    def test_empty_list(self, client):
        response = client.get("/api/recipes")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_active_recipes(self, client, ingredient):
        client.post(
            "/api/recipes",
            json={
                "title": "Bread",
                "servings": 4,
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "2 cups"}],
            },
        )
        response = client.get("/api/recipes")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_search_filter(self, client, ingredient):
        client.post(
            "/api/recipes",
            json={
                "title": "Chocolate Cake",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1 cup"}],
            },
        )
        client.post(
            "/api/recipes",
            json={
                "title": "Vanilla Cake",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1 cup"}],
            },
        )

        response = client.get("/api/recipes?search=chocolate")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Chocolate Cake"

    def test_difficulty_filter(self, client, ingredient):
        client.post(
            "/api/recipes",
            json={
                "title": "Easy Recipe",
                "difficulty": "easy",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )
        client.post(
            "/api/recipes",
            json={
                "title": "Hard Recipe",
                "difficulty": "hard",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )

        response = client.get("/api/recipes?difficulty=easy")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Easy Recipe"

    def test_tag_filter(self, client, ingredient, tag):
        create = client.post(
            "/api/recipes",
            json={
                "title": "Tagged Recipe",
                "tag_ids": [tag["id"]],
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )
        client.post(
            "/api/recipes",
            json={
                "title": "Untagged Recipe",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )

        response = client.get(f"/api/recipes?tag_ids={tag['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Tagged Recipe"


class TestCreateRecipe:
    def test_create_success(self, client, ingredient, tag):
        response = client.post(
            "/api/recipes",
            json={
                "title": "Test Recipe",
                "description": "A test recipe",
                "instructions": "Mix and bake",
                "prep_time_minutes": 15,
                "cook_time_minutes": 30,
                "servings": 4,
                "difficulty": "easy",
                "tag_ids": [tag["id"]],
                "ingredients": [
                    {
                        "ingredient_id": ingredient["id"],
                        "quantity": "2 cups",
                        "unit": "cups",
                        "notes": "sifted",
                    }
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Recipe"
        assert data["servings"] == 4
        assert len(data["ingredients"]) == 1
        assert len(data["tags"]) == 1

    def test_create_minimal(self, client, ingredient):
        response = client.post(
            "/api/recipes",
            json={
                "title": "Minimal Recipe",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )
        assert response.status_code == 201

    def test_create_invalid_ingredient_fails(self, client):
        response = client.post(
            "/api/recipes",
            json={
                "title": "Invalid Recipe",
                "ingredients": [{"ingredient_id": 999, "quantity": "1"}],
            },
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]


class TestGetRecipe:
    def test_get_existing(self, client, ingredient):
        create = client.post(
            "/api/recipes",
            json={
                "title": "Get Test",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )
        recipe_id = create.json()["id"]

        response = client.get(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Get Test"

    def test_get_not_found(self, client):
        response = client.get("/api/recipes/999")
        assert response.status_code == 404


class TestUpdateRecipe:
    def test_update_title(self, client, ingredient):
        create = client.post(
            "/api/recipes",
            json={
                "title": "Original Title",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )
        recipe_id = create.json()["id"]

        response = client.put(
            f"/api/recipes/{recipe_id}", json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_update_ingredients(self, client, ingredient):
        ing2 = client.post("/api/ingredients", json={"name": "Sugar"}).json()
        create = client.post(
            "/api/recipes",
            json={
                "title": "Test",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )
        recipe_id = create.json()["id"]

        response = client.put(
            f"/api/recipes/{recipe_id}",
            json={"ingredients": [{"ingredient_id": ing2["id"], "quantity": "2 cups"}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["ingredients"]) == 1
        assert data["ingredients"][0]["ingredient_name"] == "Sugar"

    def test_update_not_found(self, client):
        response = client.put("/api/recipes/999", json={"title": "Test"})
        assert response.status_code == 404


class TestDeleteRecipe:
    def test_soft_delete(self, client, ingredient):
        create = client.post(
            "/api/recipes",
            json={
                "title": "Delete Me",
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "1"}],
            },
        )
        recipe_id = create.json()["id"]

        response = client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 204

        list_response = client.get("/api/recipes")
        assert len(list_response.json()) == 0

    def test_delete_not_found(self, client):
        response = client.delete("/api/recipes/999")
        assert response.status_code == 404


class TestScaleRecipe:
    def test_scale_up(self, client, ingredient):
        create = client.post(
            "/api/recipes",
            json={
                "title": "Scalable",
                "servings": 4,
                "ingredients": [{"ingredient_id": ingredient["id"], "quantity": "2"}],
            },
        )
        recipe_id = create.json()["id"]

        response = client.get(f"/api/recipes/{recipe_id}/scale/8")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["scaled_quantity"] == "4"

    def test_scale_not_found(self, client):
        response = client.get("/api/recipes/999/scale/8")
        assert response.status_code == 404
