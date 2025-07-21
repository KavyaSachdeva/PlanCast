#!/usr/bin/env python3
"""
LangChain Tools for PlanCast
Tools for calendar and weather operations
"""

from langchain.tools import Tool
from typing import List, Dict
import re
from services.calendar import GoogleCalendarService
from services.weather import WeatherService
from utils.time_parser import SmartTimeParser


class PlanCastTools:
    def __init__(self, llm=None):
        """Initialize PlanCast tools"""
        self.calendar_service = GoogleCalendarService()
        self.weather_service = WeatherService()
        self.time_parser = SmartTimeParser(llm)
        self.tools = self._create_tools()
        self._last_event_creation = None  # Simple cache to prevent duplicates

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
                description="Get calendar events for a specific date or upcoming events. Use this to see what's scheduled. Input: date like 'today', 'tomorrow', 'next Monday', or leave empty for upcoming events. Example: 'today' or 'next Friday'",
                func=self._get_calendar_events
            ),

            Tool(
                name="create_calendar_event",
                description="Create a new calendar event. Use this to schedule meetings, appointments, or events. Input format: 'title|date|time|location|attendees' where time, location, and attendees are optional. Examples: 'Team Meeting|tomorrow|2pm|Conference Room|john@email.com' or 'Lunch|Friday|12pm'",
                func=self._create_calendar_event
            ),

            Tool(
                name="check_calendar_availability",
                description="Check if a specific time slot is available on a date. Use this to see if you're free at a particular time. Input format: 'date|time' where time is optional. Examples: 'tomorrow|2pm' or 'next Thursday|3pm' or 'Friday' (for general availability). For duration requests like '3 hour slot', this will check multiple time slots.",
                func=self._check_calendar_availability
            ),

            # Weather Tools
            Tool(
                name="get_current_weather",
                description="Get current weather conditions for a location. Use this for current weather only. Input: city name like 'San Francisco', 'New York', 'London'. Example: 'San Francisco'",
                func=self._get_current_weather
            ),

            Tool(
                name="get_weather_forecast",
                description="Get weather forecast for a specific date and location. Use this for future weather planning. Input format: 'location|date' where date is optional. Examples: 'San Francisco|tomorrow' or 'New York' (for current weather)",
                func=self._get_weather_forecast
            ),

            Tool(
                name="check_weather_for_event",
                description="Check weather for a specific event date and location. Use this when planning outdoor activities or events. Input format: 'date|location'. Example: 'tomorrow|San Francisco' or 'next Saturday|Central Park'",
                func=self._check_weather_for_event
            )
        ]

        return tools

    def _get_calendar_events(self, date: str = "") -> str:
        """Get calendar events"""
        try:
            # Clean and parse input
            date = self._clean_input(date)
            parsed_date = self.time_parser.parse_date(date)

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
            attendees = parts[4].strip().split(',') if len(parts) > 4 and parts[4].strip() else None

            if not title or not date:
                return "Error: Title and date are required. Format: 'title|date|time|location|attendees'"

            # Parse date and time
            parsed_date = self.time_parser.parse_date(date)
            if not parsed_date:
                return f"Error: Invalid date format '{date}'. Use 'today', 'tomorrow', or YYYY-MM-DD"

            parsed_time = self.time_parser.parse_time(time) if time else None

            # Check cache to prevent rapid duplicates
            current_request = f"{title}|{parsed_date}|{parsed_time}"
            if (self._last_event_creation and 
                self._last_event_creation == current_request):
                return f"⚠️ Event '{title}' was just created. No duplicate created."

            # Check for existing similar events to prevent duplicates
            existing_events = self.calendar_service.get_events(parsed_date)
            for event in existing_events:
                if (event['title'].lower() == title.lower() and 
                    event['start'].startswith(parsed_date)):
                    return f"⚠️ Event '{title}' already exists on {parsed_date}. No duplicate created."

            event = self.calendar_service.create_event(
                title=title,
                date=parsed_date,
                time=parsed_time,
                location=location,
                attendees=attendees
            )

            if event:
                # Update cache
                self._last_event_creation = current_request
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
            parsed_date = self.time_parser.parse_date(date)
            if not parsed_date:
                return f"Error: Invalid date format '{date}'. Use 'today', 'tomorrow', or YYYY-MM-DD"

            # Handle time ranges like "3 hour slot"
            if time_slot and "hour" in time_slot.lower():
                # Extract number of hours
                import re
                hour_match = re.search(r'(\d+)\s*hour', time_slot.lower())
                if hour_match:
                    hours = int(hour_match.group(1))
                    # Check multiple time slots throughout the day
                    return self._check_availability_for_duration(parsed_date, hours)
                else:
                    time_slot = None  # Fall back to general availability

            # Parse time slot
            if time_slot:
                parsed_time = self.time_parser.parse_time(time_slot)
                if parsed_time:
                    time_slot = parsed_time

            availability = self.calendar_service.check_availability(parsed_date, time_slot)

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

    def _check_availability_for_duration(self, date: str, hours: int) -> str:
        """Check availability for a specific duration throughout the day"""
        try:
            # Check availability at different times of day
            time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
            available_slots = []
            
            for time_slot in time_slots:
                availability = self.calendar_service.check_availability(date, time_slot)
                if availability['available']:
                    available_slots.append(time_slot)
            
            if available_slots:
                result = f"✅ {date} has {len(available_slots)} available {hours}-hour slots:\n"
                for slot in available_slots[:5]:  # Show first 5 slots
                    result += f"  • {slot}\n"
                if len(available_slots) > 5:
                    result += f"  ... and {len(available_slots) - 5} more"
            else:
                result = f"❌ {date} has no available {hours}-hour slots"
            
            return result
            
        except Exception as e:
            return f"Error checking availability for duration: {str(e)}"

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
            parsed_date = self.time_parser.parse_date(date) if date else None

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
            parsed_date = self.time_parser.parse_date(date)
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
