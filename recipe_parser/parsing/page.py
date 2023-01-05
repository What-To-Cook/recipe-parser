# type: ignore

import requests

from recipe_parser.const import BASE_URL
from recipe_parser.parsing.utils import (
    make_headers,
    response_to_json,
)


def get_urls_from_page(
    page_idx: int,
) -> list[str]:
    page_content = requests.get(
        BASE_URL,
        {'page': page_idx},
        headers=make_headers(),
    )
    page_content = response_to_json(page_content)

    if page_content['@type'] == 'ItemList':
        return [entry['url'] for entry in page_content['itemListElement'] if entry['@type'] == 'ListItem']

    return []
