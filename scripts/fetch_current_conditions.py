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
JSON_OUT = BASE / "../data/processed/current_conditions.json"

# Load locations from the config file
with open("../data/reference/socal_stations_daily.json", "r") as f:
    locations = json.load(f)

base_url = "https://forecast.weather.gov/MapClick.php?lat={}&lon={}&unit=0&lg=english&FcstType=dwml"










    

# Paths for S3 storage
S3_BUCKET = "stilesdata.com"
S3_JSON_KEY = f"weather/current_conditions.json"

# Initialize boto3 client with environment variables
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("MY_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("MY_AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("MY_AWS_SESSION_TOKEN"),
)

# Upload the JSON file
s3_client.upload_file(str(JSON_OUT), S3_BUCKET, S3_JSON_KEY)
print(f"JSON file uploaded to s3://{S3_BUCKET}/{S3_JSON_KEY}")