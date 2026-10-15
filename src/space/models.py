from typing import Annotated

from pydantic import BaseModel, BeforeValidator, TypeAdapter

from space.parser import html_to_string

HtmlText = Annotated[str, BeforeValidator(html_to_string)]


class Apod(BaseModel):
    date: str
    post_id: int
    title: str
    permalink: str
    media_type: str
    explanation: HtmlText
    credit: str
    copyright: str
    alt: str
    url: str
    hdurl: str
    basic_html: str
    basic_html_url: str

    @classmethod
    def parse_json(cls, data):
        return TypeAdapter(list[Apod]).validate_python(data)
