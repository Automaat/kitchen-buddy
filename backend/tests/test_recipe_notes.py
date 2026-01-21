import pytest


@pytest.fixture
def recipe(client):
    ing = client.post("/api/ingredients", json={"name": "Salt"}).json()
    response = client.post(
        "/api/recipes",
        json={"title": "Test Recipe", "ingredients": [{"ingredient_id": ing["id"]}]},
    )
    return response.json()


class TestAddRecipeNote:
    def test_add_note_success(self, client, recipe):
        response = client.post(
            f"/api/recipes/{recipe['id']}/notes",
            json={"content": "This was delicious!"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "This was delicious!"
        assert "id" in data
        assert "created_at" in data

    def test_add_note_recipe_not_found(self, client):
        response = client.post("/api/recipes/999/notes", json={"content": "Test"})
        assert response.status_code == 404


class TestUpdateRecipeNote:
    def test_update_note_success(self, client, recipe):
        note = client.post(
            f"/api/recipes/{recipe['id']}/notes", json={"content": "Original"}
        ).json()

        response = client.put(
            f"/api/recipes/{recipe['id']}/notes/{note['id']}",
            json={"content": "Updated content"},
        )
        assert response.status_code == 200
        assert response.json()["content"] == "Updated content"

    def test_update_note_not_found(self, client, recipe):
        response = client.put(
            f"/api/recipes/{recipe['id']}/notes/999", json={"content": "Test"}
        )
        assert response.status_code == 404


class TestDeleteRecipeNote:
    def test_delete_note_success(self, client, recipe):
        note = client.post(
            f"/api/recipes/{recipe['id']}/notes", json={"content": "To delete"}
        ).json()

        response = client.delete(f"/api/recipes/{recipe['id']}/notes/{note['id']}")
        assert response.status_code == 204

    def test_delete_note_not_found(self, client, recipe):
        response = client.delete(f"/api/recipes/{recipe['id']}/notes/999")
        assert response.status_code == 404


class TestRecipeWithNotes:
    def test_get_recipe_includes_notes(self, client, recipe):
        client.post(
            f"/api/recipes/{recipe['id']}/notes", json={"content": "First note"}
        )
        client.post(
            f"/api/recipes/{recipe['id']}/notes", json={"content": "Second note"}
        )

        response = client.get(f"/api/recipes/{recipe['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["notes"]) == 2
