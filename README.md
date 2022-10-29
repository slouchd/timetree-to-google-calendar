About
---
Convert TimeTree calendar JSON to Google Calendar events and publish them into your calendar of choice.

Installation
---
Create a virtualenv if you wish to.
```
python3 -m venv .venv
```

Install the requirements.txt generated from requirements.in (pip-compile).
```
python3 -m pip install -r requirements.txt
```

Usage
---
Pre-requisites: Set-up your access and Google Calendar API authentication and application. This guide will help https://developers.google.com/calendar/api/guides/create-events.

Make sure to have the TimeTree sync JSON calendar data in the [data/](data/) directory. You will be able to get this from the TimeTree web application. When you log into the website, inspect the page and open the network tab, you will see a 'sync' request. This will be from the TimeTree API and will contain the JSON version of your calendar. You can then copy the object out from the page and create a file to input.

You need to specify which file to ingest using the argument parser. Along with what calendar for it end up in. Example:
```
python3 timetree_to_google_calendar.py --input <FILENAME> --calendar <CALENDAR_NAME>
```

For help use:
```
python3 timetree_to_google_calendar.py -h
```

License
---
MIT License
