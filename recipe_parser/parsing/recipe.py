import requests
from bs4 import BeautifulSoup

from recipe_parser.custom_types import JSON
from recipe_parser.parsing.utils import make_headers


def parse_recipe(
    url: str,
) -> JSON:
    page_content = requests.get(
        url,
        headers=make_headers(),
    )
    soup = BeautifulSoup(page_content.content)
    ingredients = _get_ingredients(soup)

    return {
        'name': _get_name(soup).replace('\xa0', ' '),
        'serves_amount': _get_serves_amount(soup),
        'steps': _get_steps(soup),
        'ingredients': ingredients,
        'energy_value_per_serving': _get_energy_value(soup),
        'unique_ingredients': list({ing['ingredient'] for ing in ingredients}),
    }


def _get_name(
    soup: BeautifulSoup,
) -> str:
    return soup.find('h1').get_text()


def _get_serves_amount(
    soup: BeautifulSoup,
) -> int:
    return int(soup.find('span', itemprop='recipeYield').get_text())


def _get_steps(
    soup: BeautifulSoup,
) -> list[str]:
    steps = []

    for elem in soup.find_all('span', itemprop='text'):
        steps.append(elem.get_text().replace('\xa0', ' '))

    return steps


def _get_energy_value(
    soup: BeautifulSoup,
) -> dict[str, int]:
    return {
        'calories': int(soup.find('span', itemprop='calories').get_text()),
        'protein': int(soup.find('span', itemprop='proteinContent').get_text()),
        'fat': int(soup.find('span', itemprop='fatContent').get_text()),
        'carbohydrates': int(soup.find('span', itemprop='carbohydrateContent').get_text()),
    }


def _get_ingredients(
    soup: BeautifulSoup,
) -> list[dict[str, str]]:
    ingredients = []

    for ingredient in soup.find_all('span', itemprop='recipeIngredient'):
        amount = None

        for candidate in list(ingredient.parents)[2].find_all('span', title=True):
            span = candidate.get_text()

            if span != ingredient.get_text():
                amount = span

        ingredients.append({
            'ingredient': ingredient.get_text().replace('\xa0', ' '),
            'amount': amount,
        })

    return ingredients
