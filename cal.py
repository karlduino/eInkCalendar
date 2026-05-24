#Waveshare part
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in5_V2
import logging
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

#Calendar API part
import datetime
from datetime import date, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


try:
    #Calendar API part
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=30, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    #E-paper part
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.Clear()

    font14 = ImageFont.truetype("Font.ttc", 14)
    font15 = ImageFont.truetype("Font.ttc", 15)
    font18 = ImageFont.truetype("Font.ttc", 18)
    font24 = ImageFont.truetype("Font.ttc", 24)
    font56 = ImageFont.truetype("Font.ttc", 56)

    Himage = Image.new('1', (epd.width, epd.height), 255)           
    draw = ImageDraw.Draw(Himage)                                   

    #TODAY
    draw.text((20, 20), date.today().strftime("%d"), font = font56, fill = 0)
    draw.text((90, 24), date.today().strftime("%B"), font = font24, fill = 0)
    draw.text((90, 50), date.today().strftime("%A"), font = font24, fill = 0)
    
    draw.text((20, 120), 'TODAY', font = font18, fill = 0)
    
    
    #Loop trough calendar events and draw them to buffer
    x = 20        #start position on x-axis of events on e-ink screen
    y = 140       #start position on y-axis of events on e-ink screen
    curweek = ''  #variable for week of event
    curday = ''   #variable for day of event
    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        summ = event['summary'] 
        
        if len(start) == 10: #events that are 'whole day'-events
               startdate = datetime.datetime.strptime(start,"%Y-%m-%d")
               enddate = datetime.datetime.strptime(end,"%Y-%m-%d")
               time = ''
        if len(start) == 25: #events that start at specific time
               startdate = datetime.datetime.strptime(start,"%Y-%m-%dT%H:%M:%S%z")
               enddate = datetime.datetime.strptime(end,"%Y-%m-%dT%H:%M:%S%z")
               time = startdate.strftime(" (%H:%M)")
        startdate_date = startdate.date()  
        if startdate_date < date.today(): #meerdaagse evenementen startdag op huide dag
            startdate = date.today()
            startdate_date = date.today()
        day = startdate.strftime("%a %m-%d")
        week = startdate.strftime("%V")
        

        
        if curweek != week and startdate_date != date.today():          
            if (week == date.today().strftime("%V")):          
                x = 280
                y = 25
                draw.text((x, y), 'LATER THIS WEEK', font = font18, fill = 0)
            elif (int(week) == int(date.today().strftime("%V"))+1):
                x = 530
                y = 25
                draw.text((x, y), 'NEXT WEEK', font = font18, fill = 0)             
            else:
                break
            curweek = week
            y = y + 25

        if curday != day and startdate_date != date.today():
            draw.text((x, y+4), day.upper(), font = font18, fill = 0)
            curday = day
            y = y + 20
       
        draw.text((x, y),' ' + event['summary'] + time, font = font15, fill = 0)  
        y = y + 20
    
    
    #REFRESH TIME
    now = datetime.datetime.now()
    draw.text((700, 465), 'Update: ' + now.strftime('%H:%M'), font = font14, fill = 0)
       
    #Display buffer on the screen
    epd.display(epd.getbuffer(Himage))    

    
except IOError as e:
    logging.info(e)
