import requests
import urllib
import json
import subprocess
import datetime
import logging
logger = logging.getLogger()

# api-endpoint
token = subprocess.run(["gcloud", "auth", "print-identity-token"],
                            stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")

headers = {
    "Authorization": f"Bearer {token}",
    'Content-Type': 'application/json',
}

payload = {
    'features': 
        {
        'area_name': 'Tōkyō-to Nerima-ku Toyotamakita',
        'date': '2016-01-01 00:00:00',
        'genre_name': 'Izakaya',
        'is_holiday': True,
        'latitude': 35.7356234,
        'longitude': 139.6516577,
        'store_id': 'air_04341b588bde96cd'
        }
    }


def test_health_check():
    print(f"==========================")
    print("Testing health_check route")
    print(f"==========================\n")

    url = "https://river-online-ml-api-axswvbmypa-ew.a.run.app/api/health_check"
    #url = "http://127.0.0.1:5000/api/health_check"
    r = requests.get(url=url, headers=headers)
    print(f"{r.json()}\n")

def test_predict():
    print(f"==========================")
    print(f"Testing predict route")
    print(f"==========================\n")

    print(f"Payload {payload}")

    endpoint="https://river-online-ml-api-axswvbmypa-ew.a.run.app/predict"
    audience="https://river-online-ml-api-axswvbmypa-ew.a.run.app"

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(endpoint, data=data)

    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"application/json")
    response = urllib.request.urlopen(req).read().decode('UTF-8')
    response = json.loads(response)
    print(response)

def test_learn():
    print(f"==========================")
    print(f"Testing learn route")
    print(f"==========================\n")

    payload["target"] = 37.7
    print(f"Payload {payload}")

    endpoint="https://river-online-ml-api-axswvbmypa-ew.a.run.app/learn"
    audience="https://river-online-ml-api-axswvbmypa-ew.a.run.app"

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(endpoint, data=data)

    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"application/json")
    response = urllib.request.urlopen(req).read().decode('UTF-8')
    response = json.loads(response)
    print(response)

test_health_check()
test_predict()
test_learn()