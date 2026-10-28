"""Forecast client."""
import os

import env
import fake_api

env.load()


class ForecastError(Exception):
    pass


def headers():
    key = os.environ["WEATHER_API_KEY"]
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


def forecast(city, transport=fake_api):
    status, body = transport.get(f"/v1/forecast/{city}", headers())
    if status != 200:
        raise ForecastError(f"{status} {body.get('error')}")
    return body
