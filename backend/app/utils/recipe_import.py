import ipaddress
import logging
import re
from typing import Any
from urllib.parse import urlparse

import extruct
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254"}


def is_private_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https URLs are allowed")
    host = parsed.hostname or ""
    if host.lower() in BLOCKED_HOSTS:
        raise ValueError("URL host is not allowed")
    if is_private_ip(host):
        raise ValueError("Private IP addresses are not allowed")


def parse_duration(duration: str | None) -> int | None:
    if not duration:
        return None
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", duration)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_minutes = hours * 60 + minutes
        if seconds > 0:
            total_minutes += 1
        return total_minutes
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
    validate_url(url)
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
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
