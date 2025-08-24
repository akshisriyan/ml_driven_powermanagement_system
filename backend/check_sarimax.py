import sys
import os
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from fastapi.testclient import TestClient
import app.main as main
import json

client = TestClient(main.app)
resp = client.get('/forecast')
print('STATUS', resp.status_code)
try:
    data = resp.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print('Failed to decode JSON:', e)
    print(resp.text)
