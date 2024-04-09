import json
import os
import pytest
import requests

from dotenv import load_dotenv
from lorem_text import lorem


load_dotenv()
BASE_URL = os.getenv("BASE_URL")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session")
def authorized_user() -> tuple:
    body = {
        "clientName": lorem.words(3),
        "clientEmail": f"{lorem.words(1)}@gmail.com"
    }
    response = requests.post(url=f"{BASE_URL}/api-clients", json=body)
    assert response.status_code == 201
    response_content = json.loads(response.content)
    yield body["clientName"], response_content["accessToken"]
