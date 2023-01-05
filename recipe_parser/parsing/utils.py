import json
import random
from typing import Union

import requests
from bs4 import BeautifulSoup

from recipe_parser.const import USER_AGENTS
from recipe_parser.custom_types import JSON


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
