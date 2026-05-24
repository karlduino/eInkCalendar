## eInk Calendar

Following the instructions at
<https://www.instructables.com/E-paper-Calendar-Raspberry-Pi-With-E-ink-Screen-an/>

The Google API part follows <https://developers.google.com/workspace/calendar/api/quickstart/python>

- Using Google Cloud with my google account, the project is called
  "Google Calendar API"

- Need to use pip to install google-api-python-client
  google-auth-httplib2 google-auth-oauthlib

- Needed to do

  ```bash
  python3 -m venv cal_venv

  cal_venv/bin/pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
  ```

- Needed to add email as a test user. In Google Cloud, find the
  project, click Audience and then under Test Users, click Add.

- Then `cal_venv/bin/python quickstart.py`

  It will ask for credentials. But I couldn't get this to work on the
  raspberry pi zero 2w, because of not having enough RAM for either
  browser.

  And I couldn't get it to work on my laptop with Firefox; I seemed to need to
  use Chrome.

- copied over token.json to the pi, and it worked there.

### Weather data

Also looking at [this
instructable](https://www.instructables.com/Raspberry-Pi-Desktop-Weather-Display-Using-OpenWea/)
to include weather information using the OpenWeatherMap API.
See the [API
docs](https://openweathermap.org/api/current?collection=current_forecast).
