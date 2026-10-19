from pathlib import Path

import requests
from bs4 import BeautifulSoup

from space.errors import ApiTimeoutError

IMAGE_STORAGE_PATH = Path("images")


def download_image(url, image_name):

    IMAGE_STORAGE_PATH.mkdir(exist_ok=True)
    image_path = IMAGE_STORAGE_PATH / image_name
    try:
        data = requests.get(url).content
        with open(image_path, "wb") as file:
            file.write(data)
    except requests.Timeout as exc:
        raise ApiTimeoutError("Timeout occures, the server was too slow.") from exc


def html_to_string(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ", strip=True)
