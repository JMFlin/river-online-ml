import requests
import json
import subprocess

# api-endpoint
token = subprocess.run(["gcloud", "auth", "print-identity-token"],
                            stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")

headers = {
    "Authorization": f"Bearer {token}",
    'Content-Type': 'application/json',
}

# sending get request and saving the response as response object
print("Testing health_check route")
url = "https://river-online-ml-api-axswvbmypa-ew.a.run.app/api/health_check"
r = requests.get(url=url, headers=headers)
print(r.json())


payload = {
    "area_name": "1", 
    "date": "2022-01-01",
    "genre_name": "1",
    "is_holiday": True,
    "latitude": 1.0,
    "longitude": 1.0,
    "store_id": "1"
}

print(f"Testing predict route with {payload}")
#url = "https://river-online-ml-api-axswvbmypa-ew.a.run.app/predict"
url = "http://127.0.0.1:5000/predict"
r = requests.get(url=url, params=payload, headers=headers)
print(r.json())

payload["y"] = 1
print(f"Testing learn route with {payload}")
#url = "https://river-online-ml-api-axswvbmypa-ew.a.run.app/learn"
url = "http://127.0.0.1:5000/learn"
r = requests.post(url=url, json=payload, headers=headers)
print(r.json())