import re
from typing import Any

import extruct
import httpx
from bs4 import BeautifulSoup


def parse_duration(duration: str | None) -> int | None:
    if not duration:
        return None
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return hours * 60 + minutes
    return None


def extract_text(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "\n".join(str(v) for v in value if v)
    if isinstance(value, dict):
        return value.get("text") or value.get("name")
    return None


def parse_instructions(instructions: Any) -> str | None:
    if not instructions:
        return None
    if isinstance(instructions, str):
        return instructions.strip()
    if isinstance(instructions, list):
        steps = []
        for i, item in enumerate(instructions, 1):
            if isinstance(item, str):
                steps.append(f"{i}. {item.strip()}")
            elif isinstance(item, dict):
                text = item.get("text") or item.get("name", "")
                if text:
                    steps.append(f"{i}. {text.strip()}")
        return "\n".join(steps)
    return None


def parse_ingredients(ingredients: Any) -> list[str]:
    if not ingredients:
        return []
    if isinstance(ingredients, list):
        return [str(i).strip() for i in ingredients if i]
    return []


def parse_servings(yield_value: Any) -> int | None:
    if not yield_value:
        return None
    if isinstance(yield_value, int):
        return yield_value
    if isinstance(yield_value, str):
        match = re.search(r"\d+", yield_value)
        if match:
            return int(match.group())
    if isinstance(yield_value, list) and yield_value:
        return parse_servings(yield_value[0])
    return None


def extract_recipe_from_jsonld(data: list[dict]) -> dict | None:
    for item in data:
        if item.get("@type") == "Recipe":
            return item
        if isinstance(item.get("@graph"), list):
            for graph_item in item["@graph"]:
                if graph_item.get("@type") == "Recipe":
                    return graph_item
    return None


def extract_recipe_from_microdata(data: list[dict]) -> dict | None:
    for item in data:
        if "Recipe" in str(item.get("type", [])):
            return item.get("properties", {})
    return None


async def import_recipe_from_url(url: str) -> dict:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; KitchenBuddy/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, "html.parser")
    metadata = extruct.extract(
        html,
        base_url=url,
        syntaxes=["json-ld", "microdata"],
        uniform=True,
    )

    recipe_data = extract_recipe_from_jsonld(
        metadata.get("json-ld", [])
    ) or extract_recipe_from_microdata(metadata.get("microdata", []))

    result = {
        "title": None,
        "description": None,
        "instructions": None,
        "prep_time_minutes": None,
        "cook_time_minutes": None,
        "servings": None,
        "ingredients": [],
        "image_url": None,
        "source_url": url,
    }

    if recipe_data:
        result["title"] = extract_text(recipe_data.get("name"))
        result["description"] = extract_text(recipe_data.get("description"))
        result["instructions"] = parse_instructions(
            recipe_data.get("recipeInstructions")
        )
        result["prep_time_minutes"] = parse_duration(recipe_data.get("prepTime"))
        result["cook_time_minutes"] = parse_duration(recipe_data.get("cookTime"))
        result["servings"] = parse_servings(recipe_data.get("recipeYield"))
        result["ingredients"] = parse_ingredients(
            recipe_data.get("recipeIngredient") or recipe_data.get("ingredients")
        )

        image = recipe_data.get("image")
        if isinstance(image, str):
            result["image_url"] = image
        elif isinstance(image, list) and image:
            result["image_url"] = image[0] if isinstance(image[0], str) else image[0].get("url")
        elif isinstance(image, dict):
            result["image_url"] = image.get("url")

    if not result["title"]:
        title_tag = soup.find("title")
        if title_tag:
            result["title"] = title_tag.get_text().strip()

    return result
