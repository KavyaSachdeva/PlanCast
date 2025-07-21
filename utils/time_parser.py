#!/usr/bin/env python3
"""
Smart Time Parser
Hybrid approach using dateparser for common cases and LLM for complex ones
"""

import dateparser
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
import re


class SmartTimeParser:
    def __init__(self, llm=None):
        """Initialize the smart time parser"""
        self.llm = llm
        self.cache = {}  # Simple cache for LLM results

    def parse_datetime(self, text: str) -> Optional[datetime]:
        """
        Parse datetime from natural language text
        Returns datetime object or None if parsing fails
        """
        # Try dateparser first (fast, reliable for common cases)
        try:
            parsed = dateparser.parse(text)
            if parsed:
                return parsed
        except Exception:
            pass

        # Try common patterns manually
        manual_result = self._parse_manual(text)
        if manual_result:
            return manual_result

        # Fall back to LLM for complex cases
        if self.llm:
            return self._parse_with_llm(text)

        return None

    def parse_date(self, text: str) -> Optional[str]:
        """Parse date and return YYYY-MM-DD format"""
        dt = self.parse_datetime(text)
        if dt:
            return dt.strftime('%Y-%m-%d')
        return None

    def parse_time(self, text: str) -> Optional[str]:
        """Parse time and return HH:MM format"""
        # Try to extract time from text
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2})(am|pm)',
            r'(\d{4})',  # 24-hour format like 1430
        ]

        text_lower = text.lower()

        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if ':' in pattern:
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    period = match.group(3) if len(
                        match.groups()) > 2 else None
                else:
                    if 'am' in pattern or 'pm' in pattern:
                        hour = int(match.group(1))
                        period = match.group(2)
                        minute = 0
                    else:
                        # 24-hour format
                        time_str = match.group(1)
                        hour = int(time_str[:2])
                        minute = int(time_str[2:])
                        period = None

                # Convert to 24-hour format
                if period:
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0

                return f"{hour:02d}:{minute:02d}"

        return None

    def _parse_manual(self, text: str) -> Optional[datetime]:
        """Manual parsing for common patterns"""
        text_lower = text.lower().strip()
        today = datetime.now()
        
        # Common date patterns
        if text_lower == 'today':
            return today
        elif text_lower == 'tomorrow':
            return today + timedelta(days=1)
        elif text_lower == 'yesterday':
            return today - timedelta(days=1)
        elif text_lower in ['next week', 'this week']:
            # Return Monday of next week
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:  # Today is Monday
                days_until_monday = 7
            return today + timedelta(days=days_until_monday)
        
        # Day of week patterns with "next" prefix
        day_mapping = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        
        # Handle "next [day]" pattern
        if text_lower.startswith('next '):
            day_part = text_lower[5:]  # Remove "next "
            for day_name, day_num in day_mapping.items():
                if day_name in day_part:
                    # Find next occurrence of this day
                    days_ahead = (day_num - today.weekday()) % 7
                    if days_ahead == 0:  # Today is this day
                        days_ahead = 7
                    return today + timedelta(days=days_ahead)
        
        # Handle regular day names
        for day_name, day_num in day_mapping.items():
            if day_name in text_lower:
                # Find next occurrence of this day
                days_ahead = (day_num - today.weekday()) % 7
                if days_ahead == 0:  # Today is this day
                    days_ahead = 7
                return today + timedelta(days=days_ahead)
        
        return None

    def _parse_with_llm(self, text: str) -> Optional[datetime]:
        """Use LLM to parse complex datetime expressions"""
        if text in self.cache:
            return self.cache[text]

        if not self.llm:
            return None

        try:
            prompt = f"""
            Parse this datetime expression and return only the date in YYYY-MM-DD format:
            "{text}"
            
            Examples:
            "next Monday" -> 2025-07-21
            "Friday afternoon" -> 2025-07-25
            "tomorrow morning" -> 2025-07-21
            "in 2 hours" -> 2025-07-20
            
            Return only the date in YYYY-MM-DD format, nothing else:
            """

            response = self.llm.invoke(prompt).strip()

            # Try to parse the response
            try:
                parsed_date = datetime.strptime(response, '%Y-%m-%d')
                self.cache[text] = parsed_date
                return parsed_date
            except ValueError:
                return None

        except Exception:
            return None

    def extract_datetime_components(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract date and time components from text
        Returns dict with 'date', 'time', 'timezone' keys
        """
        # Try to parse the full text first
        full_dt = self.parse_datetime(text)
        if full_dt:
            return {
                'date': full_dt.strftime('%Y-%m-%d'),
                'time': full_dt.strftime('%H:%M'),
                'timezone': None
            }

        # Try to extract date and time separately
        date = self.parse_date(text)
        time = self.parse_time(text)

        # Extract timezone if present
        timezone = None
        if 'pst' in text.lower() or 'pdt' in text.lower():
            timezone = 'America/Los_Angeles'
        elif 'est' in text.lower() or 'edt' in text.lower():
            timezone = 'America/New_York'
        elif 'utc' in text.lower():
            timezone = 'UTC'

        return {
            'date': date,
            'time': time,
            'timezone': timezone
        }
