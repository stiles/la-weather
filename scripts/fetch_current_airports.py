#!/usr/bin/env python
# coding: utf-8

# Current conditions at LA-area airports
# This notebook fetches and processes JSON for numerous airports, reads it as a Pandas dataframe and stores it locally and on S3. 

# Import Python tools and Jupyter config

import os
import json
import boto3
import requests
import pandas as pd
from pathlib import Path

# Determine the absolute paths for input and output files
# BASE = Path.cwd()
BASE = Path(__file__).resolve().parent
JSON_OUT = BASE / "../data/processed/latest_conditions_airports.json"
CSV_OUT = BASE / "../data/processed/latest_conditions_airports.csv"


# Load locations from the config file
with open("../data/reference/airports.json", "r") as f:
    airports = json.load(f)


base_url = "https://aviationweather.gov/api/data/metar?ids={}&format=json"


dfs = []

for airport, station in airports.items():
    response = requests.get(base_url.format(station))
    src = pd.DataFrame(response.json()).dropna(axis=1).assign(airport=airport)
    src["cloud_cover"] = src["clouds"].apply(lambda x: x[0]["cover"] if x else None)
    dfs.append(src)


cols = [
    "icaoId",
    "airport",
    "reportTime",
    "temp",
    "dewp",
    "wdir",
    "wspd",
    "visib",
    "cloud_cover",
    "lat",
    "lon",
]


src_df = pd.concat(dfs)[cols]


src_df["temperature"] = ((src_df["temp"] * 9 / 5) + 32).round().astype(int)
src_df["dewpoint"] = ((src_df["dewp"] * 9 / 5) + 32).round().astype(int)


# Compass dictionary for windspeed
compass = {
    range(349, 361): "N",  # 361 to include 360
    range(0, 11): "N",
    range(11, 34): "NNE",
    range(34, 56): "NE",
    range(56, 79): "ENE",
    range(79, 101): "E",
    range(101, 124): "ESE",
    range(124, 146): "SE",
    range(146, 169): "SSE",
    range(169, 191): "S",
    range(191, 214): "SSW",
    range(214, 236): "SW",
    range(236, 259): "WSW",
    range(259, 281): "W",
    range(281, 304): "WNW",
    range(304, 326): "NW",
    range(326, 349): "NNW",
}


# Function to map degrees to direction
def wind_direction_to_compass(degrees):
    for k, v in compass.items():
        if degrees in k:
            return v
    return None


# Apply the function to the DataFrame
src_df["wind_direction"] = src_df["wdir"].apply(wind_direction_to_compass)


df = (
    src_df[
        [
            "icaoId",
            "airport",
            "reportTime",
            "temperature",
            "dewpoint",
            "wind_direction",
            "wspd",
            "visib",
            "cloud_cover",
            "lat",
            "lon",
        ]
    ]
    .rename(
        columns={
            "icaoId": "icao_id",
            "reportTime": "reported",
            "wspd": "wind_speed",
            "visib": "visibility",
            "lat": "latitude",
            "lon": "longitude",
        }
    )
    .copy()
)


df.to_csv(CSV_OUT, index=False)
df.to_json(JSON_OUT, indent=4, orient="records")


# S3
# Paths for S3 storage
S3_BUCKET = "stilesdata.com"
S3_CSV_KEY = f"weather/latest_conditions_airports.csv"
S3_JSON_KEY = f"weather/latest_conditions_airports.json"

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
