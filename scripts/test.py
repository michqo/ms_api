import json
import os
import requests
from datetime import datetime
import random
import sys
import dataclasses
from dataclasses import dataclass
from dotenv import load_dotenv, set_key

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

URL = os.getenv('URL', 'http://localhost:8000')
USERNAME = os.getenv('SCRIPT_USERNAME')
PASSWORD = os.getenv('SCRIPT_PASSWORD')
STATION_ID = os.getenv('STATION_ID') or 1
TOKEN = os.getenv("TOKEN")

CREATE_ROUTE = f"{URL}/api/measurements/bulk-create/"
AUTH_URL = f"{URL}/auth/jwt/create/"

def login(relogin: bool = False):
    if TOKEN and not relogin:
        return f"JWT {TOKEN}"

    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(AUTH_URL, json=payload)
    response.raise_for_status()
    token = response.json()["access"]
    set_key(dotenv_path, "TOKEN", token)
    return f"JWT {token}"

# Initialize TOKEN and HEADERS later after login
HEADERS = {
    'Content-type': 'application/json',
}

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

@dataclass
class Temp:
    timestamp: datetime
    station: int = int(STATION_ID)
    temperature: float = 0.0
    humidity: float = 0.0
    pressure: float = 0.0
    rain: float = 0.0
    wind_speed: float = 0.0
    wind_direction: float = 0.0

now = datetime.now()
data = Temp(now)
temps: list[dict] = []

def main():
    token = login()
    HEADERS["Authorization"] = token

    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        data.timestamp = data.timestamp.replace(day=int(sys.argv[1]))
    
    for i in range(24):
        lower = random.uniform(21, 22.5)
        upper = random.uniform(22.5, 24.5)
        temp = random.uniform(lower, upper)
        humidity = random.uniform(50, 70)
        data.temperature = round(temp, 1)
        data.humidity = round(humidity, 1)
        data.timestamp = data.timestamp.replace(hour=i)
        temps.append(dataclasses.asdict(data))

    send_request = lambda: requests.post(CREATE_ROUTE, headers=HEADERS, data=json.dumps(temps, cls=DateTimeEncoder))

    response = send_request()
    if response.status_code == 401:
        print("Unauthorized error: token is invalid. Re-logging in...")
        token = login(relogin=True)
        HEADERS["Authorization"] = token
        response = send_request()
    print(response.text)

if __name__ == "__main__":
    main()
