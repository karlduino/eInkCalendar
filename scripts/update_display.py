#!cal_venv/bin/python

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_epd.uc8179 import Adafruit_UC8179

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

    # First define some color constants
    WHITE = (0xFF, 0xFF, 0xFF)
    BLACK = (0x00, 0x00, 0x00)
    RED = (0xFF, 0x00, 0x00)

    # create the spi device and pins we will need
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    ecs = digitalio.DigitalInOut(board.CE0)
    dc = digitalio.DigitalInOut(board.D22)
    srcs = None
    rst = digitalio.DigitalInOut(board.D27)
    busy = digitalio.DigitalInOut(board.D17)

    display = Adafruit_UC8179(800, 480,         # 7.5" tricolor 800x480 display
        spi,
        cs_pin=ecs,
        dc_pin=dc,
        sramcs_pin=srcs,
        rst_pin=rst,
        busy_pin=busy,
        tri_color = True
    )

    display.rotation = 0

    width = display.width
    height = display.height
    print("display height=", width, " width=", height)

    today = date.today()
    weekday = today.strftime("%A")   # or %A spelled out
    month = today.strftime("%B")     # or %B spelled out
    day = today.strftime("%-d")

    events = get_calendar()
    weather = get_weather()

    font14 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    font16 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    font18 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    font24 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    font32 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    font56 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 56)

    padding = 10
  
    print("load image file")
    image = Image.open(os.path.join("WeatherIcons", "BMPfull", 
                                    weather['icon_file'] + ".bmp"))

    # drawing object to draw on image
    draw = ImageDraw.Draw(image)
  	
    print("Add day, month, weekday")
    x=padding
    y=padding
    draw.text((x,y), day, font=font56, fill=RED)
    x += 80
    y -= 2
    draw.text((x,y), month, font=font24, fill=BLACK)
    y += 28+4
    draw.text((x,y), weekday, font=font24, fill=BLACK)

    print("add temp, sunrise, sunset")
    temp = "%.0f" % weather['temp'] + '\N{DEGREE SIGN}' + 'F'
    draw.text((315, 15), temp, font=font24, fill=BLACK)
    draw.text((425, 15), weather['conditions'], font=font24, fill=BLACK)
    draw.text((343, 50), weather['sunrise'].lower(), font=font18, fill=BLACK)
    draw.text((433, 50), weather['sunset'].lower(), font=font18, fill=BLACK)

    print("add AQI, PM2.5, O3")
    aqi = "AQI: " + weather['aqi']
    draw.text((600, 15), aqi, font=font24, fill=BLACK)
    pm25 = "pm2.5: " + "%.1f" % weather['pm2.5']
    draw.text((600, 50), pm25, font=font18, fill=BLACK)
    o3 = "o" + '\u00b3' + ": " + "%.0f" % weather['o3']
    draw.text((720, 50), o3, font=font18, fill=BLACK)
  
    lineskip = 4

    print("today/tomorrow/this week...")
    x = [6, 6, 270, 534]
    y = [80, 280, 80, 80]
    draw.text((x[0],y[0]), "Today", font=font18, fill=RED) 
    y[0] += 18+lineskip
    draw.text((x[1],y[1]), "Tomorrow", font=font18, fill=RED) 
    y[1] += 18+lineskip
    draw.text((x[2],y[2]), "This Week", font=font18, fill=RED) 
    y[2] += 18+lineskip
    draw.text((x[3],y[3]), "Next Week", font=font18, fill=RED) 
    y[3] += 18+lineskip

    last_day = ""
    sections = ["today", "tomorrow", "this week", "next week"]
    seen = [False, False, False, False]
    for event in events:
        if event["when"] in sections:
            index = sections.index(event["when"])

            if index > 1 and event["day"] != last_day:
                if seen[index]:
                    y[index] += lineskip
                last_day = event["day"]
                draw.text((x[index], y[index]), event["day"], font=font16, fill=RED)
                y[index] += 16+lineskip

            if event["time"] != "":
                output = truncate_string(event["time"].lower() + " " + event["summary"])
            else:
                output = truncate_string(event["summary"])
            draw.text((x[index], y[index]), output, font=font16, fill=BLACK)
            y[index] += 16+lineskip
            seen[index] = True

    print("display image")
    # display image
    display.image(image)
    display.display()





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
        time = startdate.strftime("%-I:%M%p")
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


def convert_date(ts, format="%-I:%M%p"):

    return datetime.datetime.fromtimestamp(ts).strftime(format)


def truncate_string(x, max_length=26):

    if len(x) > max_length:
        x = x[0:max_length]

    return(x)


if __name__ == "__main__":
  main()

