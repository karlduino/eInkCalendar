#!cal_venv/bin/python

import datetime
from datetime import date, timedelta
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():
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
        time = startdate.strftime("(%I:%M %p)")
      startdate_date = startdate.date()
      if startdate_date < date.today(): # multi-day events that started before today
        startdate = date.today()
        startdate_date = date.today()
      day = startdate.strftime("%a %m-%d")
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
        to_print = "%-17s %-9s %-10s %-s" % (when, day, time, event["summary"])
        print(to_print)

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
