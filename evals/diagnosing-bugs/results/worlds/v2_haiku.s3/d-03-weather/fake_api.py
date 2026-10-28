"""Local stand-in for the forecast API: same auth rule as production."""
import os


def get(path, headers):
    expected = "Bearer " + os.environ.get("WEATHER_API_KEY", "")
    if headers.get("Authorization") != expected:
        return 401, {"error": "Unauthorized"}
    city = path.rsplit("/", 1)[-1]
    return 200, {"city": city, "high_c": 4, "low_c": -3}
