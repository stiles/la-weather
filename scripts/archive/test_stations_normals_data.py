import json
import requests
from pathlib import Path

"""
Not all SoCal weather stations have hourly or daily normals data
Test those that do and output clean stations jsons for collection
"""

# Determine the absolute paths for input and output files
BASE = Path(__file__).resolve().parent
STATIONS_ALL = BASE / "../data/reference/socal_stations.json"
STATIONS_HOURLY = BASE / "../data/reference/socal_stations_hourly.json"
STATIONS_DAILY = BASE / "../data/reference/socal_stations_daily.json"

# Base URLs for hourly and daily data
base_urls = {
    "hourly": "https://www.ncei.noaa.gov/data/normals-hourly/2006-2020/access/{}.csv",
    "daily": "https://www.ncei.noaa.gov/data/normals-daily/2006-2020/access/{}.csv",
}

# Function to test whether stations have data
def test_station_url(station_id, url_template):
    url = url_template.format(station_id)
    response = requests.head(url)
    return response.status_code == 200

# Load station data from the JSON file
with open(STATIONS_ALL, "r") as f:
    stations = json.load(f)

working_stations = {
    "hourly": {},
    "daily": {}
}

# Test stations for hourly and daily data
for station_id, details in stations.items():
    for frequency, base_url in base_urls.items():
        if test_station_url(station_id, base_url):
            working_stations[frequency][station_id] = details
            print(f"Station number {station_id} has {frequency} normals data!")
        else:
            print(f"Station number {station_id} doesn't have {frequency} normals data!")

# Export the working stations to new JSON files
with open(STATIONS_HOURLY, "w") as f:
    json.dump(working_stations["hourly"], f, indent=4)

with open(STATIONS_DAILY, "w") as f:
    json.dump(working_stations["daily"], f, indent=4)

print(f"\nTotal working hourly stations: {len(working_stations['hourly'])}")
print(f"Total working daily stations: {len(working_stations['daily'])}")