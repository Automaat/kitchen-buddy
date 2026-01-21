class TestListTags:
    def test_empty_list(self, client):
        response = client.get("/api/tags")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_all_tags_ordered(self, client):
        client.post("/api/tags", json={"name": "Dessert"})
        client.post("/api/tags", json={"name": "Asian"})
        client.post("/api/tags", json={"name": "Quick"})

        response = client.get("/api/tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Asian"
        assert data[1]["name"] == "Dessert"
        assert data[2]["name"] == "Quick"


class TestCreateTag:
    def test_create_success(self, client):
        response = client.post("/api/tags", json={"name": "Vegetarian"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Vegetarian"
        assert "id" in data

    def test_create_duplicate_fails(self, client):
        client.post("/api/tags", json={"name": "Vegan"})
        response = client.post("/api/tags", json={"name": "Vegan"})
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestDeleteTag:
    def test_delete_success(self, client):
        create = client.post("/api/tags", json={"name": "ToDelete"})
        tag_id = create.json()["id"]

        response = client.delete(f"/api/tags/{tag_id}")
        assert response.status_code == 204

        list_response = client.get("/api/tags")
        assert len(list_response.json()) == 0

    def test_delete_not_found(self, client):
        response = client.delete("/api/tags/999")
        assert response.status_code == 404
