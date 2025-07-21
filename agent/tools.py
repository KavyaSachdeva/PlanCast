#!/usr/bin/env python3
"""
LangChain Tools for PlanCast
Tools for calendar and weather operations
"""

from langchain.tools import Tool
from typing import List, Dict
from datetime import datetime, timedelta
import re
from services.calendar import GoogleCalendarService
from services.weather import WeatherService


class PlanCastTools:
    def __init__(self):
        """Initialize PlanCast tools"""
        self.calendar_service = GoogleCalendarService()
        self.weather_service = WeatherService()
        self.tools = self._create_tools()

    def _parse_date(self, date_str: str) -> str:
        """Parse natural language dates to YYYY-MM-DD format"""
        if not date_str:
            return None

        date_str = date_str.strip().lower()

        today = datetime.now()

        if date_str == 'today':
            return today.strftime('%Y-%m-%d')
        elif date_str == 'tomorrow':
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_str == 'yesterday':
            return (today - timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_str in ['upcoming', 'this week', 'next week']:
            return None  # Let the service handle upcoming events
        elif date_str in ['monday', 'mon']:
            # Find next Monday
            days_ahead = (0 - today.weekday()) % 7
            if days_ahead == 0:  # Today is Monday
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        elif date_str in ['tuesday', 'tue']:
            # Find next Tuesday
            days_ahead = (1 - today.weekday()) % 7
            if days_ahead == 0:  # Today is Tuesday
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        elif date_str in ['wednesday', 'wed']:
            # Find next Wednesday
            days_ahead = (2 - today.weekday()) % 7
            if days_ahead == 0:  # Today is Wednesday
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        elif date_str in ['thursday', 'thu']:
            # Find next Thursday
            days_ahead = (3 - today.weekday()) % 7
            if days_ahead == 0:  # Today is Thursday
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        elif date_str in ['friday', 'fri']:
            # Find next Friday
            days_ahead = (4 - today.weekday()) % 7
            if days_ahead == 0:  # Today is Friday
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        elif date_str in ['saturday', 'sat']:
            # Find next Saturday
            days_ahead = (5 - today.weekday()) % 7
            if days_ahead == 0:  # Today is Saturday
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        elif date_str in ['sunday', 'sun']:
            # Find next Sunday
            days_ahead = (6 - today.weekday()) % 7
            if days_ahead == 0:  # Today is Sunday
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        else:
            # Try to parse as YYYY-MM-DD
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                # Try other common formats
                try:
                    # MM/DD/YYYY
                    dt = datetime.strptime(date_str, '%m/%d/%Y')
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        # MM-DD-YYYY
                        dt = datetime.strptime(date_str, '%m-%d-%Y')
                        return dt.strftime('%Y-%m-%d')
                    except ValueError:
                        return None

    def _parse_time(self, time_str: str) -> str:
        """Parse time strings to HH:MM format"""
        if not time_str:
            return None

        time_str = time_str.strip().lower()

        # Handle "2pm", "3:30pm" format
        time_match = re.match(r'(\d{1,2})(?::(\d{2}))?(am|pm)', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)

            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0

            return f"{hour:02d}:{minute:02d}"

        # Handle "14:00" format
        time_match = re.match(r'(\d{1,2}):(\d{2})', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            return f"{hour:02d}:{minute:02d}"

        # Handle "1400" format
        time_match = re.match(r'(\d{2})(\d{2})', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            return f"{hour:02d}:{minute:02d}"

        # Handle PST/PDT timezone specifications
        if 'pst' in time_str or 'pdt' in time_str:
            # Keep the timezone info for the calendar service to handle
            return time_str

        return None

    def _clean_input(self, input_str: str) -> str:
        """Clean input string by removing quotes and extra text"""
        if not input_str:
            return ""

        # Remove surrounding quotes
        input_str = input_str.strip()
        if input_str.startswith("'") and input_str.endswith("'"):
            input_str = input_str[1:-1]
        elif input_str.startswith('"') and input_str.endswith('"'):
            input_str = input_str[1:-1]

        # Remove extra text in parentheses
        input_str = re.sub(r'\s*\([^)]*\)', '', input_str)

        return input_str.strip()

    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools"""
        tools = [
            # Calendar Tools
            Tool(
                name="get_calendar_events",
                description="Get calendar events for a specific date or upcoming events. Use this once to get events, then respond to the user. Input should be a date like 'today', 'tomorrow', '2024-01-15', or leave empty for upcoming events.",
                func=self._get_calendar_events
            ),

            Tool(
                name="create_calendar_event",
                description="Create a new calendar event. Input should be in format: 'title|date|time|location|attendees' where time, location, and attendees are optional. Example: 'Team Meeting|today|3pm|Conference Room|john@email.com,jane@email.com'",
                func=self._create_calendar_event
            ),

            Tool(
                name="check_calendar_availability",
                description="Check if a time slot is available on a specific date. Use this once to check availability, then respond to the user. Input should be in format: 'date|time_slot' where time_slot is optional. Example: 'tomorrow|2pm' or just 'tomorrow'",
                func=self._check_calendar_availability
            ),

            # Weather Tools
            Tool(
                name="get_current_weather",
                description="Get current weather for a location. Input should be a city name like 'New York', 'London', etc.",
                func=self._get_current_weather
            ),

            Tool(
                name="get_weather_forecast",
                description="Get weather forecast for a specific date and location. Use this once to get forecast, then respond to the user. Input should be in format: 'location|date' where date is optional. Example: 'New York|tomorrow' or just 'New York' for current weather.",
                func=self._get_weather_forecast
            ),

            Tool(
                name="check_weather_for_event",
                description="Check weather for a specific event date and location. Input should be in format: 'date|location'. Example: 'tomorrow|New York'",
                func=self._check_weather_for_event
            )
        ]

        return tools

    def _get_calendar_events(self, date: str = "") -> str:
        """Get calendar events"""
        try:
            # Clean and parse input
            date = self._clean_input(date)
            parsed_date = self._parse_date(date)

            events = self.calendar_service.get_events(parsed_date)

            if not events:
                date_desc = date if date else "upcoming time"
                return f"No events found for {date_desc}."

            result = f"Found {len(events)} events"
            if date:
                result += f" for {date}"
            result += ":\n"

            for event in events:
                result += f"- {event['title']} at {event['start']}"
                if event['location']:
                    result += f" ({event['location']})"
                result += "\n"

            return result

        except Exception as e:
            return f"Error getting calendar events: {str(e)}"

    def _create_calendar_event(self, input_str: str) -> str:
        """Create a calendar event"""
        try:
            # Clean input
            input_str = self._clean_input(input_str)

            # Parse input: title|date|time|location|attendees
            parts = input_str.split('|')
            title = parts[0].strip()
            date = parts[1].strip() if len(parts) > 1 else None
            time = parts[2].strip() if len(parts) > 2 else None
            location = parts[3].strip() if len(parts) > 3 else None
            attendees = parts[4].strip().split(',') if len(
                parts) > 4 and parts[4].strip() else None

            if not title or not date:
                return "Error: Title and date are required. Format: 'title|date|time|location|attendees'"

            # Parse date and time
            parsed_date = self._parse_date(date)
            if not parsed_date:
                return f"Error: Invalid date format '{date}'. Use 'today', 'tomorrow', or YYYY-MM-DD"

            parsed_time = self._parse_time(time) if time else None

            event = self.calendar_service.create_event(
                title=title,
                date=parsed_date,
                time=parsed_time,
                location=location,
                attendees=attendees
            )

            if event:
                return f"✅ Event created: {event['title']} on {event['start']}"
            else:
                return "❌ Failed to create event"

        except Exception as e:
            return f"Error creating calendar event: {str(e)}"

    def _check_calendar_availability(self, input_str: str) -> str:
        """Check calendar availability"""
        try:
            # Clean input
            input_str = self._clean_input(input_str)

            # Parse input: date|time_slot
            parts = input_str.split('|')
            date = parts[0].strip()
            time_slot = parts[1].strip() if len(parts) > 1 else None

            # Parse date
            parsed_date = self._parse_date(date)
            if not parsed_date:
                return f"Error: Invalid date format '{date}'. Use 'today', 'tomorrow', or YYYY-MM-DD"

            # Parse time slot
            if time_slot:
                parsed_time = self._parse_time(time_slot)
                if parsed_time:
                    time_slot = parsed_time

            availability = self.calendar_service.check_availability(
                parsed_date, time_slot)

            if availability['available']:
                result = f"✅ {date} is available"
                if time_slot:
                    result += f" for {time_slot}"
            else:
                result = f"❌ {date} is not available"
                if time_slot:
                    result += f" for {time_slot}"
                if availability.get('conflicts'):
                    result += f" (conflicts with {len(availability['conflicts'])} events)"

            return result

        except Exception as e:
            return f"Error checking availability: {str(e)}"

    def _get_current_weather(self, location: str) -> str:
        """Get current weather"""
        try:
            location = self._clean_input(location)
            weather = self.weather_service.get_current_weather(location)

            if not weather:
                return f"Weather information unavailable for {location}"

            return f"Current weather in {location}: {weather['temperature']}°C, {weather['description']}, Humidity: {weather['humidity']}%, Wind: {weather['wind_speed']} km/h"

        except Exception as e:
            return f"Error getting weather: {str(e)}"

    def _get_weather_forecast(self, input_str: str) -> str:
        """Get weather forecast"""
        try:
            # Clean input
            input_str = self._clean_input(input_str)

            # Parse input: location|date
            parts = input_str.split('|')
            location = parts[0].strip()
            date = parts[1].strip() if len(parts) > 1 else None

            # Parse date
            parsed_date = self._parse_date(date) if date else None

            forecast = self.weather_service.get_weather_forecast(
                location, parsed_date)

            if not forecast or 'error' in forecast:
                return f"Weather forecast unavailable for {location}"

            result = f"Weather forecast for {location}"
            if date:
                result += f" on {date}"
            result += f": {forecast['temperature']}°C, {forecast['description']}"

            if 'precipitation_chance' in forecast:
                result += f", {forecast['precipitation_chance']}% chance of rain"

            return result

        except Exception as e:
            return f"Error getting weather forecast: {str(e)}"

    def _check_weather_for_event(self, input_str: str) -> str:
        """Check weather for event"""
        try:
            # Clean input
            input_str = self._clean_input(input_str)

            # Parse input: date|location
            parts = input_str.split('|')
            date = parts[0].strip()
            location = parts[1].strip() if len(parts) > 1 else "New York"

            # Parse date
            parsed_date = self._parse_date(date)
            if not parsed_date:
                return f"Error: Invalid date format '{date}'. Use 'today', 'tomorrow', or YYYY-MM-DD"

            weather_data = self.weather_service.check_weather_for_event(
                parsed_date, location)

            if not weather_data.get('weather_available'):
                return f"Weather information unavailable for {date} in {location}"

            result = f"Weather for {date} in {location}: {weather_data['temperature']}°C, {weather_data['description']}"
            result += f", {weather_data['precipitation_chance']}% chance of rain"
            result += f", Humidity: {weather_data['humidity']}%"

            return result

        except Exception as e:
            return f"Error checking weather for event: {str(e)}"

    def get_tools(self) -> List[Tool]:
        """Get all tools"""
        return self.tools
