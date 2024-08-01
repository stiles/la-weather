#!/usr/bin/env python
# coding: utf-8

# NWS seven-day, daily forcast for the LA area
# This notebook captures the text heavy version of the forecast
# converting XML to JSON and uploading it to S3

# Import Python tools and Jupyter config

import os
import json
import requests
import pandas as pd
import boto3
from pathlib import Path
from xml.etree import ElementTree as ET

# Determine the absolute paths for input and output files
BASE = Path.cwd()
JSON_OUT = BASE / "../data/processed/seven_day_forecast_daily.json"
CSV_OUT = BASE / "../data/processed/seven_day_forecast_daily.csv"

# Load locations from the config file
with open("../data/reference/socal_stations_daily.json", "r") as f:
    locations = json.load(f)

base_url = "https://forecast.weather.gov/MapClick.php?lat={}&lon={}&unit=0&lg=english&FcstType=dwml"

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
    location_element = root.find(".//location/description")
    location_name = (
        location_element.text.replace(", CA", "").replace("East L.A.", "Downtown LA").strip()
        if location_element is not None and location_element.text.strip()
        else station_name
    )
    
    creation_date = root.find(".//creation-date").text
    
    time_layouts = {}
    for time_layout in root.findall(".//time-layout"):
        layout_key = time_layout.find("layout-key").text
        times = [time.text for time in time_layout.findall("start-valid-time")]
        time_layouts[layout_key] = times

    data = {}
    parameters = root.find(".//parameters")
    if parameters is not None:
        max_temps = parameters.findall(".//temperature[@type='maximum']")
        min_temps = parameters.findall(".//temperature[@type='minimum']")
        pop_values = parameters.findall(".//probability-of-precipitation")
        weather_conditions = parameters.findall(".//weather")
        word_forecasts = parameters.findall(".//wordedForecast")

        for temp in max_temps:
            layout_key = temp.attrib["time-layout"]
            for i, value in enumerate(temp.findall("value")):
                if value.text:
                    time = time_layouts[layout_key][i]
                    if time not in data:
                        data[time] = {}
                    data[time]["daily_maximum_temperature"] = int(value.text)

        for temp in min_temps:
            layout_key = temp.attrib["time-layout"]
            for i, value in enumerate(temp.findall("value")):
                if value.text:
                    time = time_layouts[layout_key][i]
                    if time not in data:
                        data[time] = {}
                    data[time]["daily_minimum_temperature"] = int(value.text)

        for word in word_forecasts:
            layout_key = word.attrib["time-layout"]
            for i, text in enumerate(word.findall("text")):
                if text.text:
                    time = time_layouts[layout_key][i]
                    if time not in data:
                        data[time] = {}
                    data[time]["word_forecast"] = text.text

        for pop in pop_values:
            layout_key = pop.attrib["time-layout"]
            for i, value in enumerate(pop.findall("value")):
                if value.text:
                    time = time_layouts[layout_key][i]
                    if time not in data:
                        data[time] = {}
                    data[time]["probability_of_precipitation"] = int(value.text)

        for weather in weather_conditions:
            layout_key = weather.attrib["time-layout"]
            for i, conditions in enumerate(weather.findall("weather-conditions")):
                summary = conditions.attrib.get("weather-summary", None)
                if summary:
                    time = time_layouts[layout_key][i]
                    if time not in data:
                        data[time] = {}
                    data[time]["weather"] = summary

    parsed_data = {"location": location_name, "current_as_of": creation_date, "forecast": data}
    return parsed_data

all_data = []

for station_id, info in locations.items():
    xml_data = fetch_weather_data(info["latitude"], info["longitude"])
    if xml_data:
        weather_data = parse_weather_data(xml_data, info["station"])
        all_data.append(weather_data)

# Convert to JSON
json_data = json.dumps(all_data, indent=2)

# Save to file
with open(JSON_OUT, "w") as f:
    f.write(json_data)

# Convert to DataFrame and save as CSV
all_data_flat = []
for location_data in all_data:
    location_name = location_data["location"]
    current_as_of = location_data["current_as_of"]
    for time, measures in location_data["forecast"].items():
        row = {"location": location_name, "time": time, "current_as_of": current_as_of}
        row.update(measures)
        all_data_flat.append(row)

df = pd.DataFrame(all_data_flat)
df.to_csv(CSV_OUT, index=False)

# Paths for S3 storage
S3_BUCKET = "stilesdata.com"
S3_CSV_KEY = f"weather/seven_day_forecast_daily.csv"
S3_JSON_KEY = f"weather/seven_day_forecast_daily.json"

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