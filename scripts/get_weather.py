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

    # api call
    url = "https://api.openweathermap.org/data/2.5/weather"
    weather_json["units"] = "imperial"

    response = requests.post(url, params=weather_json)
    if response.status_code == 200:
        data = response.json()

        print("temp:       ", data['main']['temp'])
        print("conditions: ", data['weather'][0]['description'])
        print("sunrise:    ", convert_date(data['sys']['sunrise']))
        print("sunset:     ", convert_date(data['sys']['sunset']))



def convert_date(ts, format="%I:%M %p"):

    return datetime.datetime.fromtimestamp(ts).strftime(format)



if __name__ == "__main__":
  main()
