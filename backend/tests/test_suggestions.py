import pytest


@pytest.fixture
def ingredients(client):
    ing1 = client.post(
        "/api/ingredients",
        json={"name": "Tomato", "category": "produce"},
    ).json()
    ing2 = client.post(
        "/api/ingredients",
        json={"name": "Onion", "category": "produce"},
    ).json()
    ing3 = client.post(
        "/api/ingredients",
        json={"name": "Garlic", "category": "produce"},
    ).json()
    return [ing1, ing2, ing3]


@pytest.fixture
def recipe(client, ingredients):
    return client.post(
        "/api/recipes",
        json={
            "title": "Test Recipe",
            "ingredients": [
                {"ingredient_id": ingredients[0]["id"], "quantity": "100", "unit": "g"},
                {"ingredient_id": ingredients[1]["id"], "quantity": "50", "unit": "g"},
                {"ingredient_id": ingredients[2]["id"], "quantity": "10", "unit": "g"},
            ],
        },
    ).json()


class TestGetSuggestions:
    def test_empty_pantry_no_suggestions(self, client, recipe):
        response = client.get("/api/suggestions?min_match_percentage=0.5")
        assert response.status_code == 200
        assert response.json()["suggestions"] == []

    def test_suggestions_with_partial_match(self, client, recipe, ingredients):
        client.post(
            "/api/pantry",
            json={"ingredient_id": ingredients[0]["id"], "quantity": 200},
        )
        client.post(
            "/api/pantry",
            json={"ingredient_id": ingredients[1]["id"], "quantity": 100},
        )

        response = client.get("/api/suggestions?min_match_percentage=0.5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) == 1
        suggestion = data["suggestions"][0]
        assert suggestion["recipe_id"] == recipe["id"]
        assert suggestion["available_ingredients"] == 2
        assert suggestion["total_ingredients"] == 3
        assert 60 <= suggestion["match_percentage"] <= 70

    def test_suggestions_sorted_by_match(self, client, ingredients):
        recipe1 = client.post(
            "/api/recipes",
            json={
                "title": "Recipe 1",
                "ingredients": [
                    {"ingredient_id": ingredients[0]["id"], "quantity": "100"},
                ],
            },
        ).json()
        recipe2 = client.post(
            "/api/recipes",
            json={
                "title": "Recipe 2",
                "ingredients": [
                    {"ingredient_id": ingredients[0]["id"], "quantity": "100"},
                    {"ingredient_id": ingredients[1]["id"], "quantity": "50"},
                ],
            },
        ).json()

        client.post(
            "/api/pantry",
            json={"ingredient_id": ingredients[0]["id"], "quantity": 200},
        )

        response = client.get("/api/suggestions?min_match_percentage=0")
        data = response.json()

        assert len(data["suggestions"]) == 2
        assert data["suggestions"][0]["recipe_id"] == recipe1["id"]
        assert data["suggestions"][0]["match_percentage"] == 100.0
        assert data["suggestions"][1]["recipe_id"] == recipe2["id"]
        assert data["suggestions"][1]["match_percentage"] == 50.0

    def test_min_match_filter(self, client, ingredients):
        client.post(
            "/api/recipes",
            json={
                "title": "Recipe with many ingredients",
                "ingredients": [
                    {"ingredient_id": ingredients[0]["id"], "quantity": "100"},
                    {"ingredient_id": ingredients[1]["id"], "quantity": "50"},
                    {"ingredient_id": ingredients[2]["id"], "quantity": "10"},
                ],
            },
        )
        client.post(
            "/api/pantry",
            json={"ingredient_id": ingredients[0]["id"], "quantity": 200},
        )

        response_high = client.get("/api/suggestions?min_match_percentage=0.5")
        assert len(response_high.json()["suggestions"]) == 0

        response_low = client.get("/api/suggestions?min_match_percentage=0.3")
        assert len(response_low.json()["suggestions"]) == 1
