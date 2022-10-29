#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import os.path
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_google_calendarid(calendar_title: str):
    """
    This is a way to get your Google calendar id from a calendar title (summary).

    :param calendar_title: the calendar title/summary name
    """
    # Scopes for read/write access to calendars
    SCOPES = ["https://www.googleapis.com/auth/calendar", 
              "https://www.googleapis.com/auth/calendar.events"]

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
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    page_token = None
    while True:
        service = build("calendar", "v3", credentials=creds)
        calendar_list = service.calendarList().list(pageToken=page_token).execute()

        for calendar_list_entry in calendar_list["items"]:
            if calendar_title in calendar_list_entry["summary"]:
                id_found = calendar_list_entry["id"]
        
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break
    
    return id_found


def list_google_calendars_formatted():
    """
    This is so you can find out the calendar id of all of your calendars. Not falling
    into the common error of getting a 404 when referencing the summary title of a 
    calendar.
    """
    # Scopes for read/write access to calendars
    SCOPES = ["https://www.googleapis.com/auth/calendar", 
              "https://www.googleapis.com/auth/calendar.events"]

    creds = None
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    page_token = None
    while True:
        service = build("calendar", "v3", credentials=creds)
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        
        for calendar_list_entry in calendar_list["items"]:
            print("Calendar Title:", calendar_list_entry["summary"])
            print("Calendar ID:", calendar_list_entry["id"])
            print("-" * 3)
        
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break


def google_event_handler(timetree_data: dict, calendarid: str):
    """
    Handles the conversion between TimeTree calendar data formatting and Google's
    calendar event data formatting.

    :param timetree_data: dict of the parsed timetree data
    :param calendarid: google calendar id
    """
    timezone = 'Europe/London'
    event = {
                'summary': timetree_data.get("title"),
                'location': timetree_data.get("location"),
                'description': '',
                'start': {
                    'dateTime': timetree_data.get("starts"),
                    'timeZone': timezone
                },
                'end': {
                    'dateTime': timetree_data.get("ends"),
                    'timeZone': timezone
                },
                'recurrence': timetree_data.get("recurrence"),
                'attendees': [],
                'reminders': {
                    'useDefault': 'True'
                }
            }

    # Scopes for read/write access to calendar events
    SCOPES = ["https://www.googleapis.com/auth/calendar", 
              "https://www.googleapis.com/auth/calendar.events"]

    creds = None
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        event_send = service.events().insert(calendarId=calendarid, body=event).execute()
        return print(f"Event created: {event.get('htmlLink')}")
    except HttpError as error:
        return print(f"An error occurred: {error}." \
                     "Suggestion: Your calendar id maybe incorrect use list_google_calendars()")


def time_conversion(unix_epoch: int):
    """
    Simple function to convert unix epoch milliseconds into date and timestamps.

    :param unix_epoch: int of unix epoch milliseconds
    """
    converted = time.strftime("%Y-%m-%dT%H:%M:%S-00:00", 
                              time.localtime(unix_epoch / 1000))
    return converted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",
                        type=str,
                        help="input file name",
                        required=True)
    parser.add_argument("-c", "--calendar",
                        type=str,
                        help="what google calendar to write to",
                        required=True)

    args = parser.parse_args() 

    with open(args.input, "r") as f:
        data = json.load(f)
        
        for event in data["events"]:
            timetree_event_dict = {}
            timetree_event_dict["title"] = event["title"]
            timetree_event_dict["all_day"] = event["all_day"]
            timetree_event_dict["description"] = event["note"]
            timetree_event_dict["starts"] = time_conversion(event["start_at"])
            timetree_event_dict["ends"] = time_conversion(event["end_at"])
            timetree_event_dict["recurrence"] = event["recurrences"]
            timetree_event_dict["timezone"] = event["start_timezone"]
            timetree_event_dict["location"] = event["location"]
            google_event_handler(timetree_event_dict, get_google_calendarid(args.calendar))


if __name__ == "__main__":
    main()
