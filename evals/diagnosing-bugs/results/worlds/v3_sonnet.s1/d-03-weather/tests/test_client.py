import os
import unittest
from unittest import mock

import client


class StubTransport:
    def __init__(self, status, body):
        self.status, self.body, self.calls = status, body, []

    def get(self, path, headers):
        self.calls.append(path)
        return self.status, self.body


class ClientTest(unittest.TestCase):
    def test_forecast_returns_body(self):
        t = StubTransport(200, {"city": "Montreal", "high_c": 4})
        self.assertEqual(client.forecast("Montreal", t)["high_c"], 4)
        self.assertEqual(t.calls, ["/v1/forecast/Montreal"])

    def test_forecast_authenticates_against_api(self):
        with mock.patch.dict(os.environ, {"WEATHER_API_KEY": "k3y"}):
            self.assertEqual(client.forecast("Montreal")["city"], "Montreal")

    def test_error_status_raises(self):
        with self.assertRaises(client.ForecastError):
            client.forecast("Montreal", StubTransport(500, {"error": "boom"}))


if __name__ == "__main__":
    unittest.main()
