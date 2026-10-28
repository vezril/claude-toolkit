# weather

Forecast client. `fake_api.py` is a local stand-in for the forecast API that checks the API key the
way the real one does, so you can run the client offline: `python3 -c "import client; print(client.forecast('Montreal'))"`.
The key lives in `.env`. Run the tests with `python3 -m unittest`.
