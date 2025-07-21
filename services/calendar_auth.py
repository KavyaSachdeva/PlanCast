#!/usr/bin/env python3
"""
Alternative Google Calendar Authentication
More robust authentication with better error handling
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


def authenticate_google_calendar():
    """Authenticate with Google Calendar API with better error handling"""

    creds = None

    # Check if token file exists
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print("✅ Found existing token")
        except Exception as e:
            print(f"❌ Error loading existing token: {e}")
            # Remove invalid token
            os.remove('token.json')
            creds = None

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ Refreshed existing token")
            except Exception as e:
                print(f"❌ Error refreshing token: {e}")
                # Remove invalid token
                os.remove('token.json')
                creds = None

        if not creds:
            # Check if credentials file exists
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json not found!")
                print("Please:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a project and enable Google Calendar API")
                print("3. Create OAuth 2.0 credentials (Desktop application)")
                print("4. Download and rename to 'credentials.json'")
                print(
                    "5. Make sure to add http://localhost:8080/ to authorized redirect URIs")
                return None

            try:
                print("🔐 Starting OAuth flow...")
                print("This will open your browser for Google authentication")

                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(
                    port=8080,
                    redirect_uri_trailing_slash=False,
                    authorization_prompt_message="Please authorize PlanCast to access your Google Calendar",
                    success_message="Authentication successful! You can close this window."
                )

                print("✅ Authentication successful!")

                # Save credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("✅ Credentials saved to token.json")

            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                print("Common issues:")
                print("1. Make sure credentials.json is in the project root")
                print(
                    "2. Check that http://localhost:8080/ is in authorized redirect URIs")
                print("3. Try deleting token.json and running again")
                return None

    try:
        # Build the service
        service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar service initialized")
        return service
    except Exception as e:
        print(f"❌ Error building service: {e}")
        return None


def test_calendar_connection():
    """Test the calendar connection"""
    service = authenticate_google_calendar()

    if not service:
        return False

    try:
        # Test a simple API call
        calendar_list = service.calendarList().list().execute()
        print(
            f"✅ Connected to {len(calendar_list.get('items', []))} calendars")
        return True
    except HttpError as error:
        print(f"❌ Calendar API error: {error}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Google Calendar Authentication")
    print("=" * 50)

    if test_calendar_connection():
        print("\n🎉 Calendar authentication successful!")
    else:
        print("\n❌ Calendar authentication failed")
