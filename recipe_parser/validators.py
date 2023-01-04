from recipe_parser.custom_types import JSON

_RECIPE_FIELDS = (
    (
        'name',
        str,
    ),
    (
        'recipeYield',
        str,
    ),
    (
        'recipeInstructions',
        list,
    ),
    (
        'recipeIngredient',
        list,
    ),
    (
        'nutrition',
        dict,
    ),
)
_NUTRITION_FIELDS = (
    'calories',
    'proteinContent',
    'fatContent',
    'carbohydrateContent',
)


def check_recipe_layout(
    element: JSON,
) -> bool:
    for field, expected_type in _RECIPE_FIELDS:
        if not element.get(field) or not isinstance(element[field], expected_type):
            return False

    return True


def check_nutrition_layout(
    element: JSON,
) -> bool:
    for field in _NUTRITION_FIELDS:
        if not element['nutrition'].get(field):
            return False

    return True
