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

    def test_authorization_header_has_space_after_bearer(self):
        import os
        os.environ["WEATHER_API_KEY"] = "k"
        self.assertEqual(client.headers()["Authorization"], "Bearer k")

    def test_forecast_accepted_by_fake_api(self):
        import os
        os.environ["WEATHER_API_KEY"] = "k"
        self.assertEqual(client.forecast("Montreal")["city"], "Montreal")

    def test_error_status_raises(self):
        with self.assertRaises(client.ForecastError):
            client.forecast("Montreal", StubTransport(500, {"error": "boom"}))


if __name__ == "__main__":
    unittest.main()
