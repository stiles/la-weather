#!/usr/bin/env python
# coding: utf-8

# NWS seven-day, hourly forcast for the LA area
# This notebook captures the value heavy version of the forecast
# converting XML to JSON and uploading it to S3

# Import Python tools and Jupyter config

import os
import json
import boto3
import requests
import pandas as pd
from pathlib import Path
from xml.etree import ElementTree as ET

# Determine the absolute paths for input and output files
BASE = Path.cwd()
JSON_OUT = BASE / "../data/processed/seven_day_forecast_hourly.json"
CSV_OUT = BASE / "../data/processed/seven_day_forecast_hourly.csv"


# Load locations from the config file
with open("../data/reference/socal_stations_daily.json", "r") as f:
    locations = json.load(f)

base_url = (
    "https://forecast.weather.gov/MapClick.php?lat={}&lon={}&FcstType=digitalDWML"
)


def fetch_weather_data(latitude, longitude):
    url = base_url.format(latitude, longitude)
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch data for {latitude}, {longitude}")
        return None


def parse_weather_data(xml_data, station_name):
    root = ET.fromstring(xml_data)
    data = []
    location_name = root.find(".//location/description")
    if location_name is not None and location_name.text.strip():
        location_name = station_name.title()
    else:
        location_name = station_name.title()

    time_layout = {}
    for layout in root.findall(".//time-layout"):
        layout_key = layout.find("layout-key").text
        start_times = layout.findall("start-valid-time")
        time_layout[layout_key] = [start_time.text for start_time in start_times]

    parameters = root.find(".//parameters")
    temp_values = [
        int(temp.text) if temp.text is not None else None
        for temp in parameters.findall(".//temperature[@type='hourly']/value")
    ]
    humidity_values = [
        int(hum.text) if hum.text is not None else None
        for hum in parameters.findall(".//humidity[@type='relative']/value")
    ]
    wind_speed_values = [
        int(ws.text) if ws.text is not None else None
        for ws in parameters.findall(".//wind-speed[@type='sustained']/value")
    ]
    wind_direction_values = [
        int(wd.text) if wd.text is not None else None
        for wd in parameters.findall(".//direction[@type='wind']/value")
    ]
    cloud_cover_values = [
        int(cc.text) if cc.text is not None else None
        for cc in parameters.findall(".//cloud-amount[@type='total']/value")
    ]
    hourly_qpf_values = [
        float(qpf.text) if qpf.text is not None else None
        for qpf in parameters.findall(".//hourly-qpf/value")
    ]
    pop_values = [
        int(pop.text) if pop.text is not None else None
        for pop in parameters.findall(".//probability-of-precipitation/value")
    ]

    for i, time in enumerate(time_layout["k-p1h-n1-0"]):
        data.append(
            {
                "location": location_name,
                "time": time,
                "temperature": temp_values[i] if i < len(temp_values) else None,
                "humidity": humidity_values[i] if i < len(humidity_values) else None,
                "wind_speed": (
                    wind_speed_values[i] if i < len(wind_speed_values) else None
                ),
                "wind_direction": (
                    wind_direction_values[i] if i < len(wind_direction_values) else None
                ),
                "cloud_cover": (
                    cloud_cover_values[i] if i < len(cloud_cover_values) else None
                ),
                "hourly_qpf": (
                    hourly_qpf_values[i] if i < len(hourly_qpf_values) else None
                ),
                "probability_of_precipitation": (
                    pop_values[i] if i < len(pop_values) else None
                ),
            }
        )

    return data


all_data = []

for station_id, info in locations.items():
    xml_data = fetch_weather_data(info["latitude"], info["longitude"])
    if xml_data:
        weather_data = parse_weather_data(
            xml_data,
            info["station"].title().replace("Ucla", "UCLA").replace("Lax", "LAX"),
        )
        all_data.extend(weather_data)


# Convert to DataFrame
df = pd.DataFrame(all_data)


df.to_csv(CSV_OUT, index=False)
df.to_json(JSON_OUT, indent=4, orient="records")


# S3
# Paths for S3 storage
S3_BUCKET = "stilesdata.com"
S3_CSV_KEY = f"weather/seven_day_forecast_hourly.csv"
S3_JSON_KEY = f"weather/seven_day_forecast_hourly.json"

# Initialize boto3 client with environment variables
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("MY_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("MY_AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("MY_AWS_SESSION_TOKEN"),
)

# Upload the CSV file to S3
s3_client.upload_file(str(CSV_OUT), S3_BUCKET, S3_CSV_KEY)
print(f"CSV file uploaded to s3://{S3_BUCKET}/{S3_CSV_KEY}")

# Upload the JSON file
s3_client.upload_file(str(JSON_OUT), S3_BUCKET, S3_JSON_KEY)
print(f"JSON file uploaded to s3://{S3_BUCKET}/{S3_JSON_KEY}")