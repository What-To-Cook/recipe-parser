import json
from pathlib import Path
from typing import Optional

import requests
from loguru import logger

from recipe_parser.custom_types import JSON
from recipe_parser.db import MongoDatabase
from recipe_parser.parsing.page import get_urls_from_page  # type: ignore
from recipe_parser.parsing.recipe import parse_recipe


def _process_url_with_retries(  # type: ignore
    url: str,
    max_retries: int,
) -> Optional[JSON]:
    for _ in range(max_retries):
        try:
            recipe = parse_recipe(url)
        except requests.RequestException:
            logger.error(f'unable to process url {url}')

            return None

        return recipe


def _process_urls(
    urls: list[str],
    max_retries: int,
) -> list[JSON]:
    recipes = []

    for url in urls:
        recipe = _process_url_with_retries(
            url,
            max_retries,
        )

        if recipe is not None:
            recipes.append(recipe)

    return recipes


def parse_recipes(
    num_pages: int,
    max_retries: int,
    out_path: Path,
    db: Optional[MongoDatabase] = None,
) -> None:
    recipes = []

    for page in range(1, num_pages + 1):
        recipes.extend(
            _process_urls(
                get_urls_from_page(page),
                max_retries,
            ),
        )

    out_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    for idx, recipe in enumerate(recipes):
        with open(out_path / f'{idx}.json', 'w', encoding='utf-8') as out:
            json.dump(
                recipe,
                out,
                indent=4,
                ensure_ascii=False,
            )

        if db is not None:
            db.insert_recipes(recipe)
