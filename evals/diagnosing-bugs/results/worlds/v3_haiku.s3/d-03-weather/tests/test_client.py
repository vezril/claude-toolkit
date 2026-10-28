import os
import unittest

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

    def test_error_status_raises(self):
        with self.assertRaises(client.ForecastError):
            client.forecast("Montreal", StubTransport(500, {"error": "boom"}))

    def test_authorization_header_is_bearer_with_space(self):
        os.environ["WEATHER_API_KEY"] = "wk_test_key"
        self.assertEqual(client.headers()["Authorization"], "Bearer wk_test_key")

    def test_forecast_authenticates_against_fake_api(self):
        os.environ["WEATHER_API_KEY"] = "wk_test_key"
        self.assertEqual(client.forecast("Montreal")["high_c"], 4)


if __name__ == "__main__":
    unittest.main()
