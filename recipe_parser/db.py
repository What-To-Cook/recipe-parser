import os
from typing import Union
from urllib.parse import quote_plus

from pymongo import MongoClient

from recipe_parser.custom_types import JSON

_INGREDIENTS_KEY = 'ingredients'


class MongoDatabase:
    def __init__(  # noqa: WPS211
        self,
        host: str,
        port: int,
        *,
        db: str,
        recipes_collection: str,
        ingredients_collection: str,
    ) -> None:
        self._db = db
        self._recipes_collection = recipes_collection
        self._ingredients_collection = ingredients_collection

        self._client = MongoClient(
            self._get_connection_string(
                host,
                port,
            ),
        )

    def insert_recipes(
        self,
        recipe: Union[JSON, list[JSON]],
    ) -> None:
        if not isinstance(recipe, list):
            recipe = [recipe]

        self._client[self._db][self._recipes_collection].insert_many(recipe)
        self._client[self._db][self._ingredients_collection].update_one(
            {},
            {'$set': {_INGREDIENTS_KEY: self._gather_ingredients(recipe)}},
            upsert=True,
        )

    def _gather_ingredients(
        self,
        recipes: list[JSON],
    ) -> list[str]:
        ingredients = self._client[self._db][self._ingredients_collection].find_one()
        ingredients = set() if ingredients is None else set(ingredients[_INGREDIENTS_KEY])

        for recipe in recipes:
            ingredients.update(recipe['unique_ingredients'])

        return list(ingredients)

    @staticmethod
    def _get_connection_string(
        host: str,
        port: int,
    ) -> str:
        user = quote_plus(os.environ['MONGO_USER'])
        password = quote_plus(os.environ['MONGO_PASSWORD'])

        return f'mongodb://{user}:{password}@{host}:{port}/'  # noqa: WPS221
