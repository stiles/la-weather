# How's the weather in LA?

## About this project 
This project a non-commercial exercise in data automation, analysis and presentation that collects [National Weather Service](https://www.weather.gov/lox) forecast information for various locations in the Los Angeles area.

*It will grow over time, adding more documentation, additional forecast details, historic [climate normals](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc:C00824) and, ultimately, a regularly updating static web application.*

## Scope

The project collects data from several sources, some live and some historical. 

- **Hourly and daily climate normals:** Normal conditions by month/day and month/day/hour at numerous stations. Derived from 2006-2020 data. 
    - Data source: [National Centers for Environmental Information](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals)
- **Airports:** Current temperature, wind speed, clouds and other conditions at 11 LA-area airports, including LAX, Burbank, Santa Monica and Long Beach. 
    - Source: National Weather Service [Aviation Weather Center](https://aviationweather.gov/gfa/#obs)
- **Seven-day hourly forecast:** Forecast conditions (numeric values for temperature, humidity, wind speed, etc.) for 32 weather stations the Los Angeles metro area. The forecast covers each hour for 168 hours following when it's fetched. 
    - Source: [National Weather Service, Los Angeles/Oxnard office](https://forecast.weather.gov/MapClick.php?x=272&y=146&site=lox&zmx=&zmy=&map_x=271&map_y=146)
- **Seven-day narrative forecast:** Forecast conditions (text statements describing the weather, i.e. "partly cloudy with a chance of rain) for 32 weather stations the Los Angeles metro area. The forecast covers each hour for 168 hours following when it's fetched.

*More to come.*

## Collection and locations

The data are fetched using Python scripts that read data from a variety of sources. The daily and hourly seven-day forecasts are captured from XML files served dynamically by the weather service based on longitude and latitude parameters passed for each place. 

These comes from `data/reference/socal_stations_daily.json` file: 

```json
 {
    "USW00023129": {
        "station": "LONG BEACH",
        "state": "CA",
        "country": "US",
        "latitude": 33.8117,
        "longitude": -118.1464,
        "elevation": 9.4
    },
    "USW00093134": {
        "station": "DOWNTOWN LOS ANGELES",
        "state": "CA",
        "country": "US",
        "latitude": 34.0511,
        "longitude": -118.2353,
        "elevation": 70.1
    },
    "USW00023174": {
        "station": "LAX",
        "state": "CA",
        "country": "US",
        "latitude": 33.9381,
        "longitude": -118.3889,
        "elevation": 29.6
    },
}
```

The XML files for each location are fetched from these URLs: 

**Hourly:**

[`https://forecast.weather.gov/MapClick.php?lat=33.9159&lon=-118.4097&FcstType=digitalDWML`](https://forecast.weather.gov/MapClick.php?lat=33.9159&lon=-118.4097&FcstType=digitalDWML)

**Daily**

[`https://forecast.weather.gov/MapClick.php?lat=33.9159&lon=-118.4097&unit=0&lg=english&FcstType=dwml`](https://forecast.weather.gov/MapClick.php?lat=33.9159&lon=-118.4097&unit=0&lg=english&FcstType=dwml)

## Outputs

### Airports

```json
{
    "station": "Station Name",
    "time": "ISO 8601 Timestamp",
    "temp": "Temperature in Fahrenheit",
    "wind": "Wind speed and direction",
    "clouds": "Cloud coverage",
    "weather": "General weather conditions"
}
```

### Daily normals example

| Key              | Description                                     | Example          |
|------------------|-------------------------------------------------|------------------|
| station          | Station identifier                              | "USC00040192"    |
| name             | Name and location of the station                | "ANAHEIM, CA US" |
| date             | Date in MM-DD format                            | "01-14"          |
| month            | Month as a number                               | 1                |
| day              | Day of the month                                | 14               |
| avg_temp_normal  | Average temperature normal in Fahrenheit        | 60.6             |
| max_temp_normal  | Maximum temperature normal in Fahrenheit        | 71.9             |
| min_temp_normal  | Minimum temperature normal in Fahrenheit        | 49.3             |
| latitude         | Latitude of the station                         | 33.8647          |
| longitude        | Longitude of the station                        | -117.8425        |

### Hourly normals example

| Key              | Description                                     | Example                          |
|------------------|-------------------------------------------------|----------------------------------|
| station          | Station identifier                              | "USW00023174"                    |
| name             | Name and location of the station                | "LOS ANGELES INTL AP, CA US"     |
| date             | Date and time in MM-DDTHH:MM format             | "01-01T00:00:00"                 |
| month            | Month as a number                               | 1                                |
| day              | Day of the month                                | 1                                |
| hour             | Hour of the day                                 | 0                                |
| temp_normal      | Normal temperature in Fahrenheit                | 54.5                             |
| dewpoint_normal  | Normal dew point temperature in Fahrenheit      | 39.3                             |
| precip_normal    | Normal precipitation in inches                  | 1018.7                           |
| pct_overcast     | Percentage of overcast sky                      | 6.5                              |
| avg_windspeed    | Average wind speed in mph                       | 5.0                              |
| wind_direction   | Average wind direction in degrees               | 47.0                             |
| latitude         | Latitude of the station                         | 33.9381                          |
| longitude        | Longitude of the station                        | -118.3889                        |
| elevation        | Elevation of the station in meters              | 29.6                             |

### Seven-day daily forecast

```json
[
    {
        "location": "Location Name",
        "current_as_of": "ISO 8601 Timestamp",
        "forecast": {
            "timestamp": {
                "daily_maximum_temperature": "Temperature in Fahrenheit",
                "daily_minimum_temperature": "Temperature in Fahrenheit",
                "word_forecast": "Textual forecast description",
                "probability_of_precipitation": "Percentage",
                "weather": "Short weather description"
            }
        }
    }
]
```

### Seven-day hourly forecast

```json
[
    {
        "location": "Location Name",
        "current_as_of": "ISO 8601 Timestamp",
        "forecast": {
            "timestamp": {
                "temperature": "Temperature in Fahrenheit",
                "dewpoint": "Dewpoint in Fahrenheit",
                "wind_speed": "Wind speed in mph",
                "wind_direction": "Wind direction in degrees",
                "clouds": "Cloud coverage",
                "weather": "Short weather description",
                "probability_of_precipitation": "Percentage"
            }
        }
    }
]
```

*More details to come.*

Questions? Thoughts? [Please let me know](mailto:mattstiles@gmail.com).

