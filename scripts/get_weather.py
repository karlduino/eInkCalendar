#!cal_venv/bin/python

import datetime
from datetime import date, timedelta
import os.path
import json
import requests

def main():
    """Get weather info from OpenWeatherMap API.
    """

    # load openweather.json with appid, lat, and lon
    weather_file = "openweather.json"
    if os.path.exists(weather_file):
        with open(weather_file) as f:
            weather_json = json.load(f)

    # load weather icon codes
    icon_code_file = "WeatherIcons/icon_codes.json"
    if os.path.exists(icon_code_file):
        with open(icon_code_file) as f:
            icon_codes = json.load(f)
    icons = icon_codes['icon_list']

    # api call
    url = "https://api.openweathermap.org/data/2.5/weather"
    weather_json["units"] = "imperial"

    # get weather datas
    response = requests.post(url, params=weather_json)
    data = {}
    if response.status_code == 200:
        data = response.json()

        print("temp:       ", "%.0f" % data['main']['temp'] + u'\N{DEGREE SIGN}' + 'F')
        print("conditions: ", data['weather'][0]['description'])
        print("weather_id: ", data['weather'][0]['id'])
        print("icon:       ", data['weather'][0]['icon'])
        print("icon file:  ", icons[data['weather'][0]['icon']])
        print("sunrise:    ", convert_date(data['sys']['sunrise']))
        print("sunset:     ", convert_date(data['sys']['sunset']))

    else:
        print("weather error ", response.status_code)

    # api call for air pollution (seems to need GET rather than POST)
    aqi_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    del weather_json["units"]
    aqi_fullurl = f'{aqi_url}?appid={weather_json["appid"]}&lat={weather_json["lat"]}&lon={weather_json["lon"]}'

    air_quality = ["good",
                   "fair",
                   "moderate",
                   "poor",
                   "very poor"]

    # get air pollution data
    aqi_response = requests.get(aqi_fullurl)
    aqi_data = {}
    if aqi_response.status_code == 200:
        aqi_data = aqi_response.json()

        print("aqi:        ", air_quality[aqi_data['list'][0]['main']['aqi']-1])
        print("pm2.5:      ", "%.1f" % aqi_data['list'][0]['components']['pm2_5'] + " μg/m" + '\u00b3')
        print("o" + '\u00b3' + ":         ", "%.1f" % aqi_data['list'][0]['components']['o3'] + " μg/m" + '\u00b3')

    else:
        print("aqi error ", aqi_response.status_code)


    # api call for weather forecast
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    weather_json["cnt"] = 8 # just one day
    weather_json["units"] = "imperial"

    forecast_response = requests.post(forecast_url, params=weather_json)
    forecast_data = {}
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()

        forecasts = forecast_data["list"]
        for x in forecasts:
            print("%-7s %.0f %s" % (convert_date(x["dt"]), x["main"]["temp"], x["weather"][0]["description"]))

    else:
        print("forecast error ", forecast_response.status_code)



def convert_date(ts, format="%I:%M%p"):

    return datetime.datetime.fromtimestamp(ts).strftime(format).lower()



if __name__ == "__main__":
  main()
