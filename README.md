# recipe-parser
Parser for eda.ru, which allows storing data in MongoDB.

## Usage
Clone the repository:
```
git clone https://github.com/What-To-Cook/recipe-parser.git
cd recipe-parser
```

Install dependencies. You will need Python (used **3.9.15**, but newer versions might also work) with Poetry **1.1.***:
```
poetry install
```

Write an example script:

```python
from pathlib import Path

from recipe_parser import (
    MongoDatabase,
    parse_recipes,
)

# this step is optional
# note that user and password must be stored in "MONGO_USER" and "MONGO_PASSWORD" env variables respectively
db = MongoDatabase(
    'localhost',
    27017,
    db='recipes-db',
    recipes_collection='recipes',
    ingredients_collection='ingredients',
)

parse_recipes(
    num_pages=1,
    max_retries=10,
    out_path=Path('./output'),
    db=db,
)
```

After the execution, you will find parsed recipes in the **output** folder (each recipe is presented as a single JSON) and in your database.

**Note:** if you're using a database, the collection with unique ingredients from all recipes will also be created:
```json
{
    "_id": {
        "$oid": "some_id"
    },
    "ingredients": [
        "ingredient1",
        "ingredient2",
        "ingredient3"
    ]
}
```

## Recipes structure
Every recipe has the following structure:
```json
{
    "name": "My Cool Dish",
    "serves_amount": 6,
    "steps": [
        "first step",
        "second step",
        "third step"
    ],
    "ingredients": [
        {
            "ingredient": "ingredient1",
            "amount": "250 г"
        },
        {
            "ingredient": "ingredient2",
            "amount": "500 г"
        }
    ],
    "energy_value_per_serving": {
        "calories": 676,
        "protein": 10,
        "fat": 46,
        "carbohydrates": 55
    },
    "unique_ingredients": [
        "ingredient1",
        "ingredient2"
    ]
}
```