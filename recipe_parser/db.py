from typing import Union, Optional

from pymongo import MongoClient

from recipe_parser.custom_types import JSON


class MongoDatabase:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        default_db_name: str,
        default_collection: str,
    ) -> None:
        self._default_db_name = default_db_name
        self._default_collection = default_collection

        self._client = MongoClient(
            host=host,
            port=port,
        )

    def insert_recipes(
        self,
        recipe: Union[JSON, list[JSON]],
        *,
        db_name: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> None:
        if db_name is None and collection is not None:
            raise ValueError('collection is None when db_name is specified')

        if db_name is not None and collection is None:
            raise ValueError('db_name is None when collection is specified')

        if db_name is None and collection is None:
            db_name = self._default_db_name
            collection = self._default_collection

        if not isinstance(recipe, list):
            recipe = [recipe]

        self._client[db_name][collection].insert_many(recipe)
