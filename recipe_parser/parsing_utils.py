import json
import random
from fractions import Fraction
from typing import Union

import requests
from bs4 import BeautifulSoup

from recipe_parser.const import (
    TO_TASTE,
    USER_AGENTS,
)
from recipe_parser.custom_types import JSON


def parse_ingredient(
    ingredients: str,
) -> dict[str, dict[str, float]]:
    if TO_TASTE in ingredients:
        return {ingredients.split(TO_TASTE)[0]: {TO_TASTE: 1.0}}

    ingredients = ingredients.split()
    measure_name = ''
    measure_idx = 0

    for idx, word in reversed(list(enumerate(ingredients))):
        if word[0].isdigit():
            measure_idx = idx
            break

        measure_name = ' '.join([word, measure_name]).lower().strip()

    return {_parse_ingredient_name(ingredients, measure_idx): {measure_name: _parse_amount(ingredients, measure_idx)}}


def parse_instructions(
    instructions: list[str],
) -> str:
    steps = []

    for idx, step in enumerate(instructions, 1):
        steps.append(f'{idx}. {step.rstrip()}')

    return '\n'.join(steps)


def make_headers() -> dict[str, str]:
    return {
        'User-Agent': random.choice(USER_AGENTS),  # noqa: S311
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }


def response_to_json(
    response: requests.Response,
) -> Union[JSON, list]:
    soup = BeautifulSoup(response.content)

    return json.loads(soup.find('script', {'type': 'application/ld+json'}).text)


def _parse_amount(
    ingredients: list[str],
    measure_idx: int,
) -> float:
    return float(Fraction(ingredients[measure_idx].replace(',', '.')))


def _parse_ingredient_name(
    ingredients: list[str],
    measure_idx: int,
) -> str:
    return ' '.join(ingredients[:measure_idx]).lower().strip()
