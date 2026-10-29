"""Hidden check for d-03: the client authenticates against the fake API, with a key it never saw."""
import os, subprocess, sys
proj = sys.argv[1]
code = "import os, client, fake_api; os.environ['WEATHER_API_KEY']='hidden_key_123'; print(client.forecast('Quebec')['city'])"
r = subprocess.run([sys.executable, "-c", code], cwd=proj, capture_output=True, text=True)
ok = r.returncode == 0 and r.stdout.strip() == "Quebec"
if not ok: print("FAIL", (r.stderr or r.stdout).strip().splitlines()[-1:] )
sys.exit(0 if ok else 1)
