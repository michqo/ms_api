import json
import os
import requests
from datetime import datetime
import random
import sys
import dataclasses
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('URL', 'http://localhost:8000')
ROUTE = "{}/api/measurements/".format(URL)
TOKEN = f"JWT {os.getenv('TOKEN')}"

HEADERS = {
    'Content-type': 'application/json',
    'Authorization': TOKEN
}

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat() + 'Z'
        return super().default(o)

@dataclass
class Temp:
    timestamp: datetime
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
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            data.timestamp = data.timestamp.replace(day=int(sys.argv[1]))
    
    for i in range (0, 24):
        lower = random.uniform(21, 22.5)
        upper = random.uniform(22.5, 24.5)
        temp = random.uniform(lower, upper)
        humidity = random.uniform(50, 70)
        data.temperature = round(temp, 1)
        data.humidity = round(humidity, 1)
        data.timestamp = data.timestamp.replace(hour=i)
        temps.append(dataclasses.asdict(data))


    for temp in temps:
        r = requests.post(ROUTE, headers=HEADERS, data=json.dumps(temp, cls=DateTimeEncoder))
        print(r.text)

if __name__ == "__main__":
    main()
