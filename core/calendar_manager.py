"""
MAC Assistant - Calendar and Time Management System
Advanced scheduling, event management, and time-based automation.
"""

import json
import os
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re

@dataclass
class Event:
    """Represents a calendar event."""
    id: str
    title: str
    description: str = ""
    start_time: datetime.datetime = None
    end_time: datetime.datetime = None
    location: str = ""
    attendees: List[str] = None
    reminders: List[int] = None  # Minutes before event
    recurrence: str = ""  # daily, weekly, monthly, yearly
    category: str = "general"
    priority: str = "medium"  # low, medium, high, urgent
    created_at: datetime.datetime = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.reminders is None:
            self.reminders = [15]  # Default 15 minutes
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

class CalendarManager:
    """Advanced calendar and scheduling manager."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize calendar manager."""
        self.data_dir = data_dir
        self.events_file = os.path.join(data_dir, "calendar_events.json")
        self.templates_file = os.path.join(data_dir, "event_templates.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load data
        self.events = self._load_events()
        self.event_templates = self._load_templates()
        
        # Time parsing patterns
        self.time_patterns = {
            'time': r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            'date': r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            'relative_day': r'(today|tomorrow|yesterday)',
            'day_name': r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            'duration': r'(\d+)\s*(minutes?|hours?|days?)'
        }
    
    def _load_events(self) -> List[Event]:
        """Load events from storage."""
        if not os.path.exists(self.events_file):
            return []
        
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            events = []
            for event_dict in events_data:
                # Convert datetime strings back to datetime objects
                if event_dict.get('start_time'):
                    event_dict['start_time'] = datetime.datetime.fromisoformat(event_dict['start_time'])
                if event_dict.get('end_time'):
                    event_dict['end_time'] = datetime.datetime.fromisoformat(event_dict['end_time'])
                if event_dict.get('created_at'):
                    event_dict['created_at'] = datetime.datetime.fromisoformat(event_dict['created_at'])
                
                events.append(Event(**event_dict))
            
            return events
        except Exception as e:
            print(f"Error loading events: {e}")
            return []
    
    def _save_events(self):
        """Save events to storage."""
        try:
            events_data = []
            for event in self.events:
                event_dict = {
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start_time': event.start_time.isoformat() if event.start_time else None,
                    'end_time': event.end_time.isoformat() if event.end_time else None,
                    'location': event.location,
                    'attendees': event.attendees,
                    'reminders': event.reminders,
                    'recurrence': event.recurrence,
                    'category': event.category,
                    'priority': event.priority,
                    'created_at': event.created_at.isoformat() if event.created_at else None
                }
                events_data.append(event_dict)
            
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving events: {e}")
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Load event templates."""
        if not os.path.exists(self.templates_file):
            # Create default templates
            default_templates = {
                "meeting": {
                    "duration": 60,
                    "reminders": [15, 5],
                    "category": "work",
                    "priority": "medium"
                },
                "call": {
                    "duration": 30,
                    "reminders": [10],
                    "category": "communication",
                    "priority": "medium"
                },
                "appointment": {
                    "duration": 60,
                    "reminders": [30, 15],
                    "category": "personal",
                    "priority": "high"
                },
                "workout": {
                    "duration": 90,
                    "reminders": [30],
                    "category": "health",
                    "priority": "medium"
                }
            }
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(default_templates, f, indent=2)
            
            return default_templates
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {}
    
    def parse_natural_time(self, text: str) -> Dict[str, Any]:
        """Parse natural language time expressions."""
        text = text.lower().strip()
        result = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'date_found': False,
            'time_found': False
        }
        
        now = datetime.datetime.now()
        
        # Parse relative days
        if 'today' in text:
            base_date = now.date()
            result['date_found'] = True
        elif 'tomorrow' in text:
            base_date = (now + datetime.timedelta(days=1)).date()
            result['date_found'] = True
        elif 'yesterday' in text:
            base_date = (now - datetime.timedelta(days=1)).date()
            result['date_found'] = True
        else:
            base_date = now.date()
        
        # Parse day names
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(days):
            if day in text:
                days_ahead = i - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                base_date = (now + datetime.timedelta(days=days_ahead)).date()
                result['date_found'] = True
                break
        
        # Parse specific time
        time_match = re.search(self.time_patterns['time'], text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            am_pm = time_match.group(3)
            
            if am_pm:
                if am_pm.lower() == 'pm' and hour != 12:
                    hour += 12
                elif am_pm.lower() == 'am' and hour == 12:
                    hour = 0
            
            result['start_time'] = datetime.datetime.combine(base_date, datetime.time(hour, minute))
            result['time_found'] = True
        
        # Parse duration
        duration_match = re.search(self.time_patterns['duration'], text)
        if duration_match:
            amount = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            
            if 'minute' in unit:
                result['duration'] = datetime.timedelta(minutes=amount)
            elif 'hour' in unit:
                result['duration'] = datetime.timedelta(hours=amount)
            elif 'day' in unit:
                result['duration'] = datetime.timedelta(days=amount)
        
        # Calculate end time if we have start time and duration
        if result['start_time'] and result['duration']:
            result['end_time'] = result['start_time'] + result['duration']
        
        return result
    
    def create_event(self, command: str) -> Dict[str, Any]:
        """Create a calendar event from natural language."""
        try:
            # Generate unique ID
            event_id = f"event_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Parse the command
            parsed_time = self.parse_natural_time(command)
            
            # Extract event title (simple approach)
            title = self._extract_event_title(command)
            
            # Determine event type and apply template
            event_type = self._determine_event_type(command)
            template = self.event_templates.get(event_type, {})
            
            # Create event
            event = Event(
                id=event_id,
                title=title,
                start_time=parsed_time.get('start_time'),
                end_time=parsed_time.get('end_time'),
                reminders=template.get('reminders', [15]),
                category=template.get('category', 'general'),
                priority=template.get('priority', 'medium')
            )
            
            # Set default duration if not specified
            if event.start_time and not event.end_time:
                default_duration = template.get('duration', 60)  # minutes
                event.end_time = event.start_time + datetime.timedelta(minutes=default_duration)
            
            # Add to events list
            self.events.append(event)
            self._save_events()
            
            return {
                'success': True,
                'message': f"✅ Event '{title}' created successfully!",
                'event': event,
                'details': {
                    'time': event.start_time.strftime('%Y-%m-%d %H:%M') if event.start_time else 'No specific time',
                    'duration': str(event.end_time - event.start_time) if event.start_time and event.end_time else 'Unknown',
                    'category': event.category,
                    'reminders': f"{len(event.reminders)} reminders set"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error creating event: {str(e)}",
                'error': str(e)
            }
    
    def _extract_event_title(self, command: str) -> str:
        """Extract event title from command."""
        # Remove common scheduling words
        cleaned = re.sub(r'\b(schedule|create|add|set|meeting|appointment|call|event)\b', '', command, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(for|at|on|tomorrow|today|next|this)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(self.time_patterns['time'], '', cleaned)
        cleaned = re.sub(self.time_patterns['duration'], '', cleaned)
        
        # Clean up and return
        title = ' '.join(cleaned.split()).strip()
        return title if title else "New Event"
    
    def _determine_event_type(self, command: str) -> str:
        """Determine event type from command."""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['meeting', 'meet with', 'conference']):
            return 'meeting'
        elif any(word in command_lower for word in ['call', 'phone', 'contact']):
            return 'call'
        elif any(word in command_lower for word in ['doctor', 'dentist', 'appointment']):
            return 'appointment'
        elif any(word in command_lower for word in ['gym', 'workout', 'exercise']):
            return 'workout'
        else:
            return 'general'
    
    def get_upcoming_events(self, days: int = 7) -> List[Event]:
        """Get upcoming events within specified days."""
        now = datetime.datetime.now()
        end_date = now + datetime.timedelta(days=days)
        
        upcoming = []
        for event in self.events:
            if event.start_time and now <= event.start_time <= end_date:
                upcoming.append(event)
        
        # Sort by start time
        upcoming.sort(key=lambda e: e.start_time or datetime.datetime.max)
        return upcoming
    
    def get_todays_schedule(self) -> List[Event]:
        """Get today's events."""
        today = datetime.date.today()
        todays_events = []
        
        for event in self.events:
            if event.start_time and event.start_time.date() == today:
                todays_events.append(event)
        
        # Sort by start time
        todays_events.sort(key=lambda e: e.start_time or datetime.datetime.max)
        return todays_events
    
    def check_conflicts(self, new_event: Event) -> List[Event]:
        """Check for scheduling conflicts."""
        if not new_event.start_time or not new_event.end_time:
            return []
        
        conflicts = []
        for event in self.events:
            if event.id == new_event.id:
                continue
            
            if not event.start_time or not event.end_time:
                continue
            
            # Check for overlap
            if (new_event.start_time < event.end_time and 
                new_event.end_time > event.start_time):
                conflicts.append(event)
        
        return conflicts
    
    def get_calendar_summary(self) -> Dict[str, Any]:
        """Get calendar summary and statistics."""
        now = datetime.datetime.now()
        today = now.date()
        
        # Count events by category
        categories = {}
        total_events = len(self.events)
        upcoming_count = 0
        today_count = 0
        
        for event in self.events:
            # Count by category
            categories[event.category] = categories.get(event.category, 0) + 1
            
            # Count upcoming and today's events
            if event.start_time:
                if event.start_time.date() == today:
                    today_count += 1
                elif event.start_time > now:
                    upcoming_count += 1
        
        return {
            'total_events': total_events,
            'today_events': today_count,
            'upcoming_events': upcoming_count,
            'categories': categories,
            'busiest_category': max(categories.items(), key=lambda x: x[1])[0] if categories else None
        }
    
    def suggest_meeting_times(self, duration_minutes: int = 60, days_ahead: int = 7) -> List[Dict]:
        """Suggest available meeting times."""
        suggestions = []
        now = datetime.datetime.now()
        
        # Business hours: 9 AM to 6 PM, weekdays only
        for day_offset in range(days_ahead):
            check_date = now + datetime.timedelta(days=day_offset)
            
            # Skip weekends
            if check_date.weekday() >= 5:
                continue
            
            # Check each hour from 9 AM to 6 PM
            for hour in range(9, 18):
                start_time = datetime.datetime.combine(
                    check_date.date(), 
                    datetime.time(hour, 0)
                )
                end_time = start_time + datetime.timedelta(minutes=duration_minutes)
                
                # Create temporary event to check conflicts
                temp_event = Event(
                    id="temp",
                    title="temp",
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Check if this time slot is free
                if not self.check_conflicts(temp_event):
                    suggestions.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'day': start_time.strftime('%A'),
                        'date': start_time.strftime('%Y-%m-%d'),
                        'time': start_time.strftime('%I:%M %p')
                    })
                
                # Limit suggestions
                if len(suggestions) >= 10:
                    break
            
            if len(suggestions) >= 10:
                break
        
        return suggestions
