import json
from pathlib import Path
from typing import (
    Generator,
    Optional,
)

import requests
from loguru import logger

from recipe_parser import parsing_utils
from recipe_parser.const import BASE_URL
from recipe_parser.custom_types import JSON
from recipe_parser.proxy import (
    run_with_proxy,
    StepResult,
)
from recipe_parser.validators import (
    check_nutrition_layout,
    check_recipe_layout,
)


def _json_to_recipe(element: JSON) -> Optional[JSON]:
    from pprint import pprint
    pprint(element)

    if not isinstance(element, dict):
        return None

    if not check_recipe_layout(element):
        return None

    if not check_nutrition_layout(element):
        return None

    return {
        'name': element['name'],
        'serves_amount': int(element['recipeYield'].split()[0]),
        'text': parsing_utils.parse_instructions(element['recipeInstructions']),
        'ingredients': [parsing_utils.parse_ingredient(ingr) for ingr in element['recipeIngredient']],
        'energy_value_per_serving': {
            'calories': element['nutrition']['calories'],
            'protein': element['nutrition']['proteinContent'],
            'fat': element['nutrition']['fatContent'],
            'carbohydrates': element['nutrition']['carbohydrateContent'],
        },
    }


def _parse_page(
    page_idx: int,
) -> list[JSON]:
    page_content = requests.get(
        BASE_URL,
        {'page': page_idx},
        headers=parsing_utils.make_headers(),
        timeout=5,
    )
    recipes = []
    recipes_json = parsing_utils.response_to_json(page_content)

    from pprint import pprint
    pprint(recipes_json)

    if not isinstance(recipes_json, dict) or not isinstance(recipes_json['itemListElement'], list):
        return []

    for element in recipes_json['itemListElement']:
        if element.get('@type') != 'Recipe':
            continue

        recipe = _json_to_recipe(element)
        pprint(recipe)

        if recipe:
            recipes.append(recipe)

    return recipes


def _parse_wrapper(
    num_pages: int,
    max_retries: int,
) -> Generator[list[JSON], Optional[StepResult], None]:
    for page in range(1, num_pages + 1):
        parse_status = StepResult.OK

        for _ in range(max_retries):
            parse_status = yield _parse_page(page)  # type: ignore

            if parse_status == StepResult.OK:
                break

        if parse_status != StepResult.OK:
            logger.debug(f'Failed to load page {num_pages}')


def _flatten(nested: list[list]) -> list:
    return [item for sublist in nested for item in sublist]  # noqa: WPS110


def parse(
    num_pages: int,
    max_retries: int,
    out_path: Path,
) -> None:
    out_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    parser = _parse_wrapper(
        num_pages,
        max_retries,
    )
    result_entries = _flatten(parser)

    for idx, entry in enumerate(result_entries):
        with open(out_path / f'{idx}.json', 'w', encoding='utf-8') as out:
            json.dump(
                entry,
                out,
                indent=4,
                ensure_ascii=False,
            )
