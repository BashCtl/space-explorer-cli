from datetime import date
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, TypeAdapter

from space.utils import html_to_string

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


class ResponseLinks(BaseModel):
    next: str
    previous: str
    self: str


class MissDistance(BaseModel):
    astronomical: float
    kilometers: float
    lunar: float
    miles: float


class RelativeVelocity(BaseModel):
    kilometers_per_hour: float
    kilometers_per_second: float
    miles_per_hour: float


class CloseApproachData(BaseModel):
    close_approach_date: str
    close_approach_date_full: str
    epoch_date_close_approach: int
    miss_distance: MissDistance
    orbiting_body: str
    relative_velocity: RelativeVelocity


class EstimatedDiameterMeasurement(BaseModel):
    estimated_diameter_max: float
    estimated_diameter_min: float


class EstimatedDiameter(BaseModel):
    feet: EstimatedDiameterMeasurement
    kilometers: EstimatedDiameterMeasurement
    meters: EstimatedDiameterMeasurement
    miles: EstimatedDiameterMeasurement


class NEOLinks(BaseModel):
    self: str


class Asteroid(BaseModel):
    absolute_magnitude_h: float
    close_approach_data: list[CloseApproachData]
    estimated_diameter: EstimatedDiameter
    id: str
    is_potentially_hazardous_asteroid: bool
    is_sentry_object: bool
    links: NEOLinks
    name: str
    nasa_jpl_url: str
    neo_reference_id: str


class NEOResponse(BaseModel):
    element_count: int
    links: ResponseLinks
    near_earth_objects: dict[date, list[Asteroid]]

    @classmethod
    def parse_json(cls, data):
        return TypeAdapter(NEOResponse).validate_python(data)
