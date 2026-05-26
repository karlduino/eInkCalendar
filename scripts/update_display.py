#!cal_venv/bin/python

import datetime
from datetime import date, timedelta
import os.path
import json
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():

  today = date.today()
  weekday = today.strftime("%a")   # or %A spelled out
  month = today.strftime("%b")     # or %B spelled out
  day = today.strftime("%-d")

  events = get_calendar()
  weather = get_weather()

  print("\n")
  print("%s %s %s" % (weekday, month, day))

  for event in events:
    to_print = "%-17s %-9s %-10s %-s" % (event["when"], event["day"], event["time"], event["summary"])
    print(to_print)

  print("\n")

  print("temp:       ", "%.0f" % weather['temp'] + u'\N{DEGREE SIGN}' + 'F')
  print("conditions: ", weather['conditions'])
  print("weather_id: ", weather['weather_id'])
  print("icon:       ", weather['icon'])
  print("icon file:  ", weather['icon_file'])
  print("sunrise:    ", weather['sunrise'])
  print("sunset:     ", weather['sunset'])
  print("aqi:        ", weather['aqi'])
  print("pm2.5:      ", "%.1f" % weather['pm2.5'] + " μg/m" + '\u00b3')
  print("o" + '\u00b3' + ":          " + "%.1f" % weather['o3'] + " μg/m" + '\u00b3')


def get_calendar():
  """Get events from Google Calendar API.
  """

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # calendar ids are in file calendar_ids.json
    calendarid_file = "calendar_ids.json"
    if os.path.exists(calendarid_file):
      with open(calendarid_file) as f:
        calendar_ids = json.load(f)

    # Call the Calendar API
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Getting the upcoming events in each calendar")

    events = []

    for (calendar,id) in calendar_ids.items():

      events_result = (
        service.events()
        .list(
            calendarId=id,
            timeMin=now,
            maxResults=30,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
      )
      this_events = events_result.get("items", [])
      events += this_events

    curweek = ''  #variable for week of event
    curday = ''   #variable for day of event

    # sort events by date/time
    events = sorted(events, key=lambda e: e["start"].get("dateTime", e["start"].get("date")))

    thisweek = date.today().strftime("%V")
    nextweek = (date.today() + timedelta(days=7)).strftime("%V")

    # if sat or sunday, add 1 to thisweek and nextweek
    this_day = date.today().strftime("%a")
    if this_day == "Sat" or this_day == "Sun":
        thisweek = nextweek
        nextweek = (date.today() + timedelta(days=14)).strftime("%V")

    results = []
    for event in events:
      start = event['start'].get('dateTime', event['start'].get('date'))
      end = event['end'].get('dateTime', event['end'].get('date'))
      summ = event['summary']
      when = "today"
      skip_this = False


      if len(start) == 10: #events that are 'whole day'-events
        startdate = datetime.datetime.strptime(start,"%Y-%m-%d")
        enddate = datetime.datetime.strptime(end,"%Y-%m-%d")
        time = ''
      if len(start) == 25: #events that start at specific time
        startdate = datetime.datetime.strptime(start,"%Y-%m-%dT%H:%M:%S%z")
        enddate = datetime.datetime.strptime(end,"%Y-%m-%dT%H:%M:%S%z")
        time = startdate.strftime("(%-I:%M %p)")
      startdate_date = startdate.date()
      if startdate_date < date.today(): # multi-day events that started before today
        startdate = date.today()
        startdate_date = date.today()
      day = startdate.strftime("%a %-d %b")
      week = startdate.strftime("%V")

      if startdate_date == date.today():
        when = "today"

      elif startdate_date == date.today() + timedelta(days=1):
        when = "tomorrow"

      elif startdate_date <= date.today() + timedelta(days=21) and week == thisweek:
        when = "this week"

      elif startdate_date <= date.today() + timedelta(days=21) and week == nextweek:
        when = "next week"

      else:
        skip_this = True

      if (skip_this == False):
        results.append({"when":     when,
                        "day":      day,
                        "time":     time,
                        "summary":  event["summary"]})

  except HttpError as error:
    print(f"An error occurred: {error}")

  return(results)


def get_weather():
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

    result = {}

    print("Getting weather")

    # get weather datas
    response = requests.post(url, params=weather_json)
    data = {}
    if response.status_code == 200:
        data = response.json()

        result = {"temp": data['main']['temp'],
                  "conditions": data['weather'][0]['description'],
                  "weather_id": data['weather'][0]['id'],
                  "icon": data['weather'][0]['icon'],
                  "icon_file": icons[data['weather'][0]['icon']],
                  "sunrise": convert_date(data['sys']['sunrise']),
                  "sunset":  convert_date(data['sys']['sunset'])}

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

    print("Getting air quality")

    # get air pollution data
    aqi_response = requests.get(aqi_fullurl)
    aqi_data = {}
    if aqi_response.status_code == 200:
        aqi_data = aqi_response.json()

        result['aqi'] = air_quality[aqi_data['list'][0]['main']['aqi']-1]
        result['pm2.5'] = aqi_data['list'][0]['components']['pm2_5']
        result['o3'] = aqi_data['list'][0]['components']['o3']

    else:
        print("aqi error ", aqi_response.status_code)

    return(result)


def convert_date(ts, format="%-I:%M %p"):

    return datetime.datetime.fromtimestamp(ts).strftime(format)


if __name__ == "__main__":
  main()
