import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import settings

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    def __init__(self):
        self.service = None
        self.credentials = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None

        # Check if token file exists
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Create credentials file if it doesn't exist
                if not os.path.exists('credentials.json'):
                    raise Exception(
                        "Please create credentials.json from Google Cloud Console")

                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(
                    port=8080,
                    redirect_uri_trailing_slash=False
                )

            # Save credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.credentials = creds
        self.service = build('calendar', 'v3', credentials=creds)

    def get_events(self, date: str = None, max_results: int = 10) -> List[Dict]:
        """Get calendar events for a specific date or upcoming events"""
        try:
            if date:
                # Convert date string to datetime
                if date.lower() == 'today':
                    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                elif date.lower() == 'tomorrow':
                    start_date = datetime.now().replace(hour=0, minute=0, second=0,
                                                        microsecond=0) + timedelta(days=1)
                else:
                    # Try to parse date string
                    start_date = datetime.strptime(date, '%Y-%m-%d')

                end_date = start_date + timedelta(days=1)

                events_result = self.service.events().list(
                    calendarId='primary',
                    timeMin=start_date.isoformat() + 'Z',
                    timeMax=end_date.isoformat() + 'Z',
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
            else:
                # Get upcoming events
                now = datetime.utcnow().isoformat() + 'Z'
                events_result = self.service.events().list(
                    calendarId='primary',
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

            events = events_result.get('items', [])
            return self._format_events(events)

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def create_event(self, title: str, date: str, time: str = None,
                     location: str = None, attendees: List[str] = None) -> Dict:
        """Create a new calendar event"""
        try:
            # Parse date and time
            if time:
                # Handle timezone conversion for PST/PDT
                if 'pst' in time.lower() or 'pdt' in time.lower():
                    # Convert PST to local time (PST is UTC-8, PDT is UTC-7)
                    # For simplicity, assume PST (UTC-8) for now
                    time_clean = time.lower().replace('pst', '').replace('pdt', '').strip()
                    start_datetime = datetime.strptime(
                        f"{date} {time_clean}", "%Y-%m-%d %H:%M")
                    # Add 8 hours to convert from PST to UTC
                    start_datetime = start_datetime + timedelta(hours=8)
                else:
                    start_datetime = datetime.strptime(
                        f"{date} {time}", "%Y-%m-%d %H:%M")
            else:
                start_datetime = datetime.strptime(date, "%Y-%m-%d")
                start_datetime = start_datetime.replace(
                    hour=9, minute=0)  # Default to 9 AM

            end_datetime = start_datetime + \
                timedelta(hours=1)  # Default 1 hour duration

            event = {
                'summary': title,
                'location': location,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/Los_Angeles',  # Use Pacific timezone
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/Los_Angeles',  # Use Pacific timezone
                },
            }

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return self._format_event(event)

        except HttpError as error:
            print(f'An error occurred: {error}')
            return {}

    def check_availability(self, date: str, time_slot: str = None) -> Dict:
        """Check availability for a specific date and time"""
        events = self.get_events(date)

        if not time_slot:
            return {
                'date': date,
                'available': len(events) == 0,
                'events_count': len(events),
                'events': events
            }

        # Parse time slot (e.g., "14:00-15:00" or "2pm")
        if '-' in time_slot:
            start_time, end_time = time_slot.split('-')
        else:
            # Handle single time like "2pm"
            start_time = time_slot
            # Assume 1 hour duration
            start_dt = datetime.strptime(
                f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(hours=1)
            end_time = end_dt.strftime("%H:%M")

        try:
            check_start = datetime.strptime(
                f"{date} {start_time}", "%Y-%m-%d %H:%M")
            check_end = datetime.strptime(
                f"{date} {end_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            # Try to parse with different time formats
            try:
                # Handle "2pm" format
                import re

                # Convert "2pm" to "14:00"
                time_match = re.match(r'(\d{1,2})(am|pm)', start_time.lower())
                if time_match:
                    hour = int(time_match.group(1))
                    period = time_match.group(2)
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                    start_time = f"{hour:02d}:00"

                time_match = re.match(r'(\d{1,2})(am|pm)', end_time.lower())
                if time_match:
                    hour = int(time_match.group(1))
                    period = time_match.group(2)
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                    end_time = f"{hour:02d}:00"

                check_start = datetime.strptime(
                    f"{date} {start_time}", "%Y-%m-%d %H:%M")
                check_end = datetime.strptime(
                    f"{date} {end_time}", "%Y-%m-%d %H:%M")
            except ValueError:
                return {
                    'date': date,
                    'time_slot': time_slot,
                    'available': False,
                    'error': f'Invalid time format: {time_slot}'
                }

        # Check for conflicts
        conflicts = []
        for event in events:
            # Handle timezone-aware datetime parsing
            event_start_str = event['start']
            event_end_str = event['end']

            # Remove timezone info for comparison (simplified approach)
            if 'T' in event_start_str:
                event_start = datetime.fromisoformat(event_start_str.split(
                    'T')[0] + 'T' + event_start_str.split('T')[1].split('-')[0].split('+')[0])
                event_end = datetime.fromisoformat(event_end_str.split(
                    'T')[0] + 'T' + event_end_str.split('T')[1].split('-')[0].split('+')[0])
            else:
                # Handle date-only events
                event_start = datetime.strptime(event_start_str, '%Y-%m-%d')
                event_end = event_start + timedelta(days=1)

            if (check_start < event_end and check_end > event_start):
                conflicts.append(event)

        return {
            'date': date,
            'time_slot': time_slot,
            'available': len(conflicts) == 0,
            'conflicts': conflicts
        }

    def _format_events(self, events: List[Dict]) -> List[Dict]:
        """Format events for better readability"""
        formatted_events = []
        for event in events:
            formatted_events.append(self._format_event(event))
        return formatted_events

    def _format_event(self, event: Dict) -> Dict:
        """Format a single event"""
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        return {
            'id': event['id'],
            'title': event['summary'],
            'start': start,
            'end': end,
            'location': event.get('location', ''),
            'attendees': [attendee['email'] for attendee in event.get('attendees', [])],
            'description': event.get('description', '')
        }
