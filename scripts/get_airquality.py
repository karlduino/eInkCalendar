#!cal_venv/bin/python

import datetime
from datetime import date, timedelta
import os.path
import json
import requests

def main():
    """Get air quality info from
    """

    # load airquality.json with token and location
    airquality_file = "airquality.json"
    if os.path.exists(airquality_file):
        with open(airquality_file) as f:
            airquality_json = json.load(f)

    # api call
    url = "http://api.waqi.info/feed/"
    aqi_url = url + airquality_json["location"] + "/?token=" + airquality_json["token"]

    # get air pollution data
    aqi_response = requests.get(aqi_url)
    aqi_data = {}
    if aqi_response.status_code == 200:
        aqi_data = aqi_response.json()

#        print(aqi_data)
        print("aqi:        ", aqi_data['data']['aqi']);
        print("pm2.5:      ", "%.1f" % aqi_data['data']['iaqi']['pm25']['v'])
        print("o" + '\u2083' + ":         ", "%.1f" % aqi_data['data']['iaqi']['o3']['v'])

    else:
        print("aqi error ", aqi_response.status_code)


if __name__ == "__main__":
  main()
