#!/usr/bin/env python
# coding: utf-8

# Download and validate hourly and daily normals data from NCEI.
# Exclude stations that don't have data we need.
# Export data and a list of validated stations for later use.

# Import Python tools and Jupyter config
import os
import json
import boto3
import pandas as pd
from pathlib import Path

# Determine the absolute paths for input and output files
# BASE = Path.cwd()
BASE = Path(__file__).resolve().parent
STATIONS_HOURLY = BASE / "../data/reference/socal_stations_hourly.json"
STATIONS_DAILY = BASE / "../data/reference/socal_stations_daily.json"
DAILY_JSON_OUT = BASE / "../data/processed/daily_normals.json"
HOURLY_JSON_OUT = BASE / "../data/processed/hourly_normals.json"
DAILY_CSV_OUT = BASE / "../data/processed/daily_normals.csv"
HOURLY_CSV_OUT = BASE / "../data/processed/hourly_normals.csv"

# Base URLs for hourly and daily data
base_urls = {
    "hourly": "https://www.ncei.noaa.gov/data/normals-hourly/2006-2020/access/{}.csv",
    "daily": "https://www.ncei.noaa.gov/data/normals-daily/2006-2020/access/{}.csv",
}

# Columns to retain
hourly_columns = [
    "STATION", "NAME", "LATITUDE", "LONGITUDE", "ELEVATION", "DATE", "month", "day", "hour",
    "HLY-TEMP-NORMAL", "HLY-DEWP-NORMAL", "HLY-PRES-NORMAL", "HLY-CLOD-PCTOVC",
    "HLY-WIND-AVGSPD", "HLY-WIND-VCTDIR"
]

daily_columns = [
    "STATION", "DATE", "LATITUDE", "LONGITUDE", "ELEVATION", "NAME", "month", "day",
    "DLY-TAVG-NORMAL", "DLY-TMAX-NORMAL", "DLY-TMIN-NORMAL"
]

def load_data(stations_file, frequency, columns):
    with open(stations_file, "r") as f:
        stations = json.load(f)

    data_frames = []
    valid_stations = []
    for station_id in stations.keys():
        url = base_urls[frequency].format(station_id)
        data = None
        # Try different delimiters and quote settings
        for delimiter in [',', '\t']:
            for quoting in [0, 1, 2, 3]:
                try:
                    data = pd.read_csv(url, delimiter=delimiter, quoting=quoting)
                    if all(column in data.columns for column in columns):
                        break
                except Exception:
                    data = None
            if data is not None and all(column in data.columns for column in columns):
                break

        if data is not None and all(column in data.columns for column in columns):
            data = data[columns]
            data_frames.append(data)
            valid_stations.append(station_id)
        else:
            print(f"Station {station_id} ({frequency}) doesn't have enough data. Excluded.")

    if data_frames:
        return pd.concat(data_frames, ignore_index=True), valid_stations
    else:
        return pd.DataFrame(columns=columns), valid_stations

# Load hourly data
hourly_data, valid_hourly_stations = load_data(STATIONS_HOURLY, "hourly", hourly_columns)

# Load daily data
daily_data, valid_daily_stations = load_data(STATIONS_DAILY, "daily", daily_columns)

# Clean up columns
hourly_data.columns = hourly_data.columns.str.lower().str.replace('hly-', '').str.replace('-', '_')
daily_data.columns = daily_data.columns.str.lower().str.replace('dly-', '').str.replace('-', '_')

hourly_df = hourly_data[['station', 'name', 'date', 'month', 'day', 'hour', 'temp_normal', 'dewp_normal', 'pres_normal', 'clod_pctovc', 'wind_avgspd', 'wind_vctdir', 'latitude', 'longitude', 'elevation']].rename(columns={'clod_pctovc': 'pct_overcast', 'wind_avgspd': 'avg_windspeed', 'wind_vctdir': 'wind_direction', 'dewp_normal': 'dewpoint_normal', 'pres_normal': 'precip_normal'})

daily_df = daily_data[['station', 'name', 'date', 'month', 'day', 'tavg_normal', 'tmax_normal', 'tmin_normal', 'latitude', 'longitude']].rename(columns={'tavg_normal': 'avg_temp_normal', 'tmax_normal': 'max_temp_normal', 'tmin_normal': 'min_temp_normal'})

# Export the data to JSON for further processing if needed
hourly_df.to_json(HOURLY_JSON_OUT, orient='records', indent=4)
daily_df.to_json(DAILY_JSON_OUT, orient='records', indent=4)
hourly_df.to_csv(HOURLY_CSV_OUT, index=False)
daily_df.to_csv(DAILY_CSV_OUT, index=False)

# Print the number of valid stations for debugging purposes
print(f"\nTotal valid hourly stations: {len(valid_hourly_stations)}")
print(f"Total valid daily stations: {len(valid_daily_stations)}")

# Export the list of valid stations to new JSON files for reference
valid_hourly_stations_file = BASE / "../data/reference/valid_hourly_stations.json"
valid_daily_stations_file = BASE / "../data/reference/valid_daily_stations.json"

with open(valid_hourly_stations_file, "w") as f:
    json.dump(valid_hourly_stations, f, indent=4)

with open(valid_daily_stations_file, "w") as f:
    json.dump(valid_daily_stations, f, indent=4)

# Paths for S3 storage
S3_BUCKET = "stilesdata.com"
S3_DAILY_JSON_KEY = "weather/normals/daily_normals_socal.json"
S3_HOURLY_JSON_KEY = "weather/normals/hourly_normals_socal.json"
S3_DAILY_CSV_KEY = "weather/normals/daily_normals_socal.csv"
S3_HOURLY_CSV_KEY = "weather/normals/hourly_normals_socal.csv"

# Initialize boto3 client with environment variables
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("MY_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("MY_AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("MY_AWS_SESSION_TOKEN"),
)

# Upload the daily JSON file
s3_client.upload_file(str(DAILY_JSON_OUT), S3_BUCKET, S3_DAILY_JSON_KEY)
print(f"JSON file uploaded to s3://{S3_BUCKET}/{S3_DAILY_JSON_KEY}")

# Upload the hourly JSON file
s3_client.upload_file(str(HOURLY_JSON_OUT), S3_BUCKET, S3_HOURLY_JSON_KEY)
print(f"JSON file uploaded to s3://{S3_BUCKET}/{S3_HOURLY_JSON_KEY}")

# Upload the daily CSV file
s3_client.upload_file(str(DAILY_CSV_OUT), S3_BUCKET, S3_DAILY_CSV_KEY)
print(f"CSV file uploaded to s3://{S3_BUCKET}/{S3_DAILY_CSV_KEY}")

# Upload the hourly CSV file
s3_client.upload_file(str(HOURLY_CSV_OUT), S3_BUCKET, S3_HOURLY_CSV_KEY)
print(f"CSV file uploaded to s3://{S3_BUCKET}/{S3_HOURLY_CSV_KEY}")