import os
import requests
from pprint import pprint


GET = requests.get
POST = requests.post


SERVER_URL = "https://collective-minds-ddd728d51f4d.herokuapp.com/room/fullexperiment_np_reinvited_1"

# Prefer environment variable, fallback to hardcoded value
OTREE_REST_KEY = os.getenv("OTREE_REST_KEY", "Complex2025!")


def call_api(method, *path_parts, **params) -> dict:
    path_parts = '/'.join(path_parts)
    url = f'{SERVER_URL}/api/{path_parts}/'
    resp = method(url, json=params, headers={'otree-rest-key': OTREE_REST_KEY})
    if not resp.ok:
        msg = (
            f'Request to "{url}" failed '
            f'with status code {resp.status_code}: {resp.text}'
        )
        raise Exception(msg)
    return resp.json()