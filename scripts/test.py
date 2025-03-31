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
ROUTE = "{}/api/measurements/bulk-create/".format(URL)
TOKEN = f"JWT {os.getenv('TOKEN')}"
STATION_ID = os.getenv('STATION_ID') or 1

HEADERS = {
    'Content-type': 'application/json',
    'Authorization': TOKEN
}

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            local_time = o.astimezone()
            return local_time.isoformat()
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


    r = requests.post(ROUTE, headers=HEADERS, data=json.dumps(temps, cls=DateTimeEncoder))
    print(r.text)

if __name__ == "__main__":
    main()
