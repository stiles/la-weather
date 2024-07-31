# How's the weather in LA?

### About this project 
This project a non-commercial exercise in data automation, analysis and presentation that collects [National Weather Service](https://www.weather.gov/lox) forecast data for various locations in the Los Angeles area. 

*It will grow over time, adding more documentation, additional forecast details, historic [climate normals](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc:C00824) and, ultimately, a regularly updating static web application.*

### Collection

The data are fetched using a Python script that reads and parses XML files served dynamically based on longitude and latitude parameters passed for each place: 

#### Location parameters

```python
locations = {
    "Santa Monica": {"latitude": 34.0195, "longitude": -118.4912},
    "Culver City": {"latitude": 34.0219, "longitude": -118.3965},
    "Pasadena": {"latitude": 34.1478, "longitude": -118.1445},
    "Irvine": {"latitude": 33.6846, "longitude": -117.8265},
    "Manhattan Beach": {"latitude": 33.8847, "longitude": -118.4109},
    "Downtown Los Angeles": {"latitude": 34.0407, "longitude": -118.2468},
    "Arcadia": {"latitude": 34.1397, "longitude": -118.0353},
    "Burbank": {"latitude": 34.1808, "longitude": -118.3089},
    "Torrance": {"latitude": 33.8358, "longitude": -118.3406},
    "Newport Beach": {"latitude": 33.6189, "longitude": -117.9298},
    "Malibu": {"latitude": 34.0259, "longitude": -118.7798},
}
```

#### XML structure

The XML files for each location are fetched from URLs such as this one: 

[`https://forecast.weather.gov/MapClick.php?lat=33.9159&lon=-118.4097&FcstType=digitalDWML`](https://forecast.weather.gov/MapClick.php?lat=33.9159&lon=-118.4097&FcstType=digitalDWML)

They are structured like this: 

```xml
<parameters applicable-location="point1">
    <temperature type="hourly" time-layout="k-p1h-n1-0">
        <!-- Temperature values here -->
    </temperature>
    <dew point" time-layout="k-p1h-n1-0">
        <!-- Dew point values here -->
    </dew>
    <probability-of-precipitation type="floating" units="percent" time-layout="k-p1h-n1-0">
        <!-- Probability of precipitation values here -->
    </probability-of-precipitation>
    <wind-speed type="sustained" time-layout="k-p1h-n1-0">
        <!-- Wind speed values here -->
    </wind-speed>
    <direction type="wind" units="degrees true" time-layout="k-p1h-n1-0">
        <!-- Wind direction values here -->
    </direction>
    <cloud-amount type="total" units="percent" time-layout="k-p1h-n1-0">
        <!-- Cloud amount values here -->
    </cloud-amount>
    <humidity type="relative" units="percent" time-layout="k-p1h-n1-0">
        <!-- Humidity values here -->
    </humidity>
    <hourly-qpf type="floating" units="inches" time-layout="k-p1h-n1-0">
        <!-- Hourly QPF values here -->
    </hourly-qpf>
    <weather time-layout="k-p1h-n1-0">
        <!-- Weather conditions here -->
    </weather>
</parameters>
```

### Data scope and format

The forecast data provides hourly predictions for a period of several days. Each hourly forecast includes multiple weather measures, offering a surface-level view of the expected weather conditions.

#### Schema

The collected data is structured in a long format to help with presentation based on the user's location and current date/time. The table below outlines the measures included in the forecast data, along with example values, data types, detailed descriptions, and units:

| Measure                       | Example | Type | Description                                        | Unit       |
|-------------------------------|---------------|-----------|----------------------------------------------------|------------|
| `location`                    | Santa Monica  | str       | Name of the location                               | N/A        |
| `time`                        | 2024-07-30T11:00:00-07:00 | str  | Forecast time in ISO 8601 format                   | N/A        |
| `temperature`                 | 75            | int       | Hourly temperature                                 | Fahrenheit |
| `humidity`                    | 60            | int       | Relative humidity                                  | Percent    |
| `wind_speed`                  | 10            | int       | Sustained wind speed                               | MPH        |
| `wind_direction`              | 240           | int       | Wind direction in degrees                          | Degrees    |
| `cloud_cover`                 | 20            | int       | Cloud cover                                        | Percent    |
| `hourly_qpf`                  | 0.01          | float     | Hourly Quantitative Precipitation Forecast (QPF)   | Inches     |
| `probability_of_precipitation`| 10            | int       | Probability of precipitation                       | Percent    |

#### Examples

The following is a snippet of the data for a location:

| location      | time                        | temperature | humidity | wind_speed | wind_direction | cloud_cover | hourly_qpf | probability_of_precipitation |
|---------------|-----------------------------|-------------|----------|------------|----------------|-------------|------------|-----------------------------|
| Santa Monica  | 2024-07-30T11:00:00-07:00   | 75          | 60       | 10         | 240            | 20          | 0.01       | 10                          |
| Santa Monica  | 2024-07-30T12:00:00-07:00   | 76          | 61       | 12         | 230            | 15          | 0.00       | 5                           |

This data will ultimately be collected and updated hourly to ensure the most accurate and timely forecasts for users. 

For more details on the specific weather measures and their significance, refer to the [National Weather Service](https://www.weather.gov/lox). 

Questions? Thoughts? [Please let me know](mailto:mattstiles@gmail.com).

