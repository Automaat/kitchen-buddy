import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.utils.recipe_import import (
    parse_duration,
    extract_text,
    parse_instructions,
    parse_ingredients,
    parse_servings,
    extract_recipe_from_jsonld,
    extract_recipe_from_microdata,
    import_recipe_from_url,
)


class TestParseDuration:
    def test_none_input(self):
        assert parse_duration(None) is None

    def test_empty_string(self):
        assert parse_duration("") is None

    def test_hours_and_minutes(self):
        assert parse_duration("PT1H30M") == 90

    def test_hours_only(self):
        assert parse_duration("PT2H") == 120

    def test_minutes_only(self):
        assert parse_duration("PT45M") == 45

    def test_invalid_format(self):
        assert parse_duration("invalid") is None


class TestExtractText:
    def test_string_input(self):
        assert extract_text("  hello world  ") == "hello world"

    def test_list_input(self):
        assert extract_text(["line1", "line2"]) == "line1\nline2"

    def test_dict_with_text(self):
        assert extract_text({"text": "content"}) == "content"

    def test_dict_with_name(self):
        assert extract_text({"name": "title"}) == "title"

    def test_none_input(self):
        assert extract_text(None) is None

    def test_number_input(self):
        assert extract_text(123) is None


class TestParseInstructions:
    def test_none_input(self):
        assert parse_instructions(None) is None

    def test_string_input(self):
        assert parse_instructions("  Mix well  ") == "Mix well"

    def test_list_of_strings(self):
        result = parse_instructions(["Mix", "Bake", "Serve"])
        assert result == "1. Mix\n2. Bake\n3. Serve"

    def test_list_of_dicts_with_text(self):
        result = parse_instructions([{"text": "Step one"}, {"text": "Step two"}])
        assert result == "1. Step one\n2. Step two"

    def test_list_of_dicts_with_name(self):
        result = parse_instructions([{"name": "First"}, {"name": "Second"}])
        assert result == "1. First\n2. Second"

    def test_mixed_list(self):
        result = parse_instructions(["String step", {"text": "Dict step"}])
        assert "1. String step" in result
        assert "2. Dict step" in result


class TestParseIngredients:
    def test_none_input(self):
        assert parse_ingredients(None) == []

    def test_empty_list(self):
        assert parse_ingredients([]) == []

    def test_list_of_strings(self):
        result = parse_ingredients(["1 cup flour", "2 eggs"])
        assert result == ["1 cup flour", "2 eggs"]

    def test_strips_whitespace(self):
        result = parse_ingredients(["  flour  ", "  sugar  "])
        assert result == ["flour", "sugar"]


class TestParseServings:
    def test_none_input(self):
        assert parse_servings(None) is None

    def test_int_input(self):
        assert parse_servings(4) == 4

    def test_string_with_number(self):
        assert parse_servings("4 servings") == 4

    def test_string_number_only(self):
        assert parse_servings("6") == 6

    def test_list_input(self):
        assert parse_servings(["4 servings"]) == 4

    def test_invalid_string(self):
        assert parse_servings("many") is None


class TestExtractRecipeFromJsonld:
    def test_direct_recipe(self):
        data = [{"@type": "Recipe", "name": "Test"}]
        result = extract_recipe_from_jsonld(data)
        assert result["name"] == "Test"

    def test_recipe_in_graph(self):
        data = [{"@graph": [{"@type": "Recipe", "name": "Nested"}]}]
        result = extract_recipe_from_jsonld(data)
        assert result["name"] == "Nested"

    def test_no_recipe(self):
        data = [{"@type": "WebPage"}]
        result = extract_recipe_from_jsonld(data)
        assert result is None

    def test_empty_data(self):
        assert extract_recipe_from_jsonld([]) is None


class TestExtractRecipeFromMicrodata:
    def test_recipe_microdata(self):
        data = [{"type": ["Recipe"], "properties": {"name": "Test"}}]
        result = extract_recipe_from_microdata(data)
        assert result["name"] == "Test"

    def test_no_recipe(self):
        data = [{"type": ["WebPage"], "properties": {}}]
        result = extract_recipe_from_microdata(data)
        assert result is None


class TestImportRecipeFromUrl:
    @pytest.mark.asyncio
    async def test_import_with_jsonld(self):
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
        <script type="application/ld+json">
        {
            "@type": "Recipe",
            "name": "Chocolate Cake",
            "description": "Delicious cake",
            "prepTime": "PT15M",
            "cookTime": "PT30M",
            "recipeYield": "8 servings",
            "recipeIngredient": ["2 cups flour", "1 cup sugar"],
            "recipeInstructions": ["Mix dry ingredients", "Add wet ingredients", "Bake"],
            "image": "https://example.com/cake.jpg"
        }
        </script>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await import_recipe_from_url("https://example.com/recipe")

        assert result["title"] == "Chocolate Cake"
        assert result["description"] == "Delicious cake"
        assert result["prep_time_minutes"] == 15
        assert result["cook_time_minutes"] == 30
        assert result["servings"] == 8
        assert len(result["ingredients"]) == 2
        assert result["image_url"] == "https://example.com/cake.jpg"
        assert result["source_url"] == "https://example.com/recipe"

    @pytest.mark.asyncio
    async def test_import_fallback_to_title(self):
        html = """
        <html>
        <head><title>My Recipe Page</title></head>
        <body><p>No structured data</p></body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await import_recipe_from_url("https://example.com/recipe")

        assert result["title"] == "My Recipe Page"
        assert result["ingredients"] == []

    @pytest.mark.asyncio
    async def test_import_image_as_list(self):
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
        <script type="application/ld+json">
        {
            "@type": "Recipe",
            "name": "Test",
            "image": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
        }
        </script>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await import_recipe_from_url("https://example.com/recipe")

        assert result["image_url"] == "https://example.com/img1.jpg"

    @pytest.mark.asyncio
    async def test_import_image_as_dict(self):
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
        <script type="application/ld+json">
        {
            "@type": "Recipe",
            "name": "Test",
            "image": {"url": "https://example.com/photo.jpg"}
        }
        </script>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await import_recipe_from_url("https://example.com/recipe")

        assert result["image_url"] == "https://example.com/photo.jpg"
