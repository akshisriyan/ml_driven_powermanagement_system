import requests

BASE = 'http://127.0.0.1:5000'

def try_get(path):
    url = BASE + path
    try:
        r = requests.get(url, timeout=5)
        print(path, '->', r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text[:400])
    except Exception as e:
        print(path, 'error', e)


def try_post(path, data):
    url = BASE + path
    try:
        r = requests.post(url, json=data, timeout=10)
        print(path, '->', r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text[:400])
    except Exception as e:
        print(path, 'error', e)

if __name__ == '__main__':
    try_get('/')
    try_get('/grid-status')
    try_get('/forecast?steps=5')
    try_get('/historical-data?limit=5')
    try_get('/system-health')
    try_get('/zones')
    try_post('/simulate', {'temperature': 28, 'humidity': 55, 'lighting': 600})
