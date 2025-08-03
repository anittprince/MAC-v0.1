"""
MAC Assistant - Proactive Intelligence System
Provides proactive suggestions, reminders, and smart notifications.
"""

import datetime
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import threading
import time


class ProactiveAssistant:
    """Provides proactive assistance and smart suggestions."""
    
    def __init__(self, user_profile, learning_engine, conversation_memory):
        self.user_profile = user_profile
        self.learning_engine = learning_engine
        self.conversation_memory = conversation_memory
        
        self.proactive_dir = Path("user_data/proactive")
        self.proactive_dir.mkdir(parents=True, exist_ok=True)
        
        self.suggestions_file = self.proactive_dir / "suggestions.json"
        self.notifications_file = self.proactive_dir / "notifications.json"
        self.patterns_file = self.proactive_dir / "proactive_patterns.json"
        
        # Proactive features state
        self.active_suggestions = []
        self.pending_notifications = []
        self.proactive_patterns = self._load_proactive_patterns()
        
        # Monitoring flags
        self.monitoring_active = False
        self.last_check_time = datetime.datetime.now()
        
        # Initialize background monitoring
        self._start_background_monitoring()
    
    def _load_proactive_patterns(self) -> Dict[str, Any]:
        """Load learned proactive patterns."""
        default_patterns = {
            "time_based_suggestions": {
                "morning": {
                    "time_range": {"start": "06:00", "end": "11:00"},
                    "suggestions": [
                        "Good morning! Would you like me to check today's weather?",
                        "Starting your day! Should I review your schedule?",
                        "Morning! Any reminders you'd like me to set for today?"
                    ]
                },
                "afternoon": {
                    "time_range": {"start": "12:00", "end": "17:00"},
                    "suggestions": [
                        "How's your day going? Need help with any work tasks?",
                        "Afternoon check-in! Any updates or questions?",
                        "Midday break? Would you like me to help organize something?"
                    ]
                },
                "evening": {
                    "time_range": {"start": "18:00", "end": "22:00"},
                    "suggestions": [
                        "Evening! How did your day go?",
                        "Winding down? Should I help you plan tomorrow?",
                        "End of day - any accomplishments to celebrate?"
                    ]
                }
            },
            "usage_based_suggestions": {
                "frequent_commands": {},
                "command_sequences": {},
                "context_triggers": {}
            },
            "situation_based_suggestions": {
                "weather_alerts": True,
                "reminder_notifications": True,
                "productivity_tips": True,
                "learning_suggestions": True
            },
            "smart_interruptions": {
                "max_per_hour": 2,
                "quiet_hours": {"start": "22:00", "end": "08:00"},
                "respect_focus_time": True
            }
        }
        
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)
                    return {**default_patterns, **patterns}
            except Exception:
                return default_patterns
        else:
            self._save_proactive_patterns(default_patterns)
            return default_patterns
    
    def _save_proactive_patterns(self, patterns: Dict[str, Any] = None):
        """Save proactive patterns."""
        patterns_to_save = patterns or self.proactive_patterns
        
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns_to_save, f, indent=2, ensure_ascii=False)
    
    def _start_background_monitoring(self):
        """Start background monitoring for proactive features."""
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self._check_proactive_opportunities()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    print(f"Proactive monitoring error: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
    
    def _check_proactive_opportunities(self):
        """Check for proactive suggestion opportunities."""
        current_time = datetime.datetime.now()
        
        # Skip if in quiet hours
        if self._is_quiet_hours(current_time):
            return
        
        # Check for time-based suggestions
        time_suggestions = self._generate_time_based_suggestions(current_time)
        
        # Check for reminder notifications
        reminder_notifications = self._check_reminder_notifications(current_time)
        
        # Check for usage pattern suggestions
        usage_suggestions = self._generate_usage_based_suggestions()
        
        # Check for situational suggestions
        situational_suggestions = self._generate_situational_suggestions(current_time)
        
        # Combine and prioritize suggestions
        all_suggestions = []
        all_suggestions.extend(time_suggestions)
        all_suggestions.extend(reminder_notifications)
        all_suggestions.extend(usage_suggestions)
        all_suggestions.extend(situational_suggestions)
        
        # Filter and add to active suggestions
        for suggestion in all_suggestions:
            if self._should_add_suggestion(suggestion):
                self.active_suggestions.append(suggestion)
        
        # Limit active suggestions
        if len(self.active_suggestions) > 10:
            self.active_suggestions = self.active_suggestions[-10:]
        
        self.last_check_time = current_time
    
    def _is_quiet_hours(self, current_time: datetime.datetime) -> bool:
        """Check if current time is in quiet hours."""
        quiet_config = self.proactive_patterns["smart_interruptions"]["quiet_hours"]
        
        current_time_str = current_time.strftime("%H:%M")
        start_time = quiet_config["start"]
        end_time = quiet_config["end"]
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start_time > end_time:
            return current_time_str >= start_time or current_time_str <= end_time
        else:
            return start_time <= current_time_str <= end_time
    
    def _generate_time_based_suggestions(self, current_time: datetime.datetime) -> List[Dict[str, Any]]:
        """Generate suggestions based on time of day."""
        suggestions = []
        current_time_str = current_time.strftime("%H:%M")
        
        for period, config in self.proactive_patterns["time_based_suggestions"].items():
            time_range = config["time_range"]
            
            if time_range["start"] <= current_time_str <= time_range["end"]:
                # Check if we haven't suggested for this period today
                if not self._already_suggested_today(f"time_based_{period}"):
                    suggestion = {
                        "type": "time_based",
                        "category": period,
                        "message": self._select_time_suggestion(config["suggestions"]),
                        "priority": "medium",
                        "timestamp": current_time.isoformat(),
                        "id": f"time_based_{period}_{current_time.strftime('%Y%m%d')}"
                    }
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _check_reminder_notifications(self, current_time: datetime.datetime) -> List[Dict[str, Any]]:
        """Check for due reminders."""
        notifications = []
        
        active_reminders = self.user_profile.get_active_reminders()
        
        for reminder in active_reminders:
            reminder_time_str = reminder.get("datetime")
            if reminder_time_str:
                try:
                    reminder_time = datetime.datetime.fromisoformat(reminder_time_str)
                    
                    # Check if reminder is due (within 5 minutes)
                    time_diff = (reminder_time - current_time).total_seconds()
                    
                    if 0 <= time_diff <= 300:  # 0 to 5 minutes
                        notification = {
                            "type": "reminder",
                            "category": "due_reminder",
                            "message": f"⏰ Reminder: {reminder['text']}",
                            "priority": "high",
                            "timestamp": current_time.isoformat(),
                            "id": f"reminder_{reminder['id']}",
                            "data": {"reminder_id": reminder["id"]}
                        }
                        notifications.append(notification)
                        
                except Exception as e:
                    print(f"Error processing reminder time: {e}")
        
        return notifications
    
    def _generate_usage_based_suggestions(self) -> List[Dict[str, Any]]:
        """Generate suggestions based on usage patterns."""
        suggestions = []
        
        # Get most used commands
        most_used = self.user_profile.get_most_used_commands(3)
        
        # Suggest related commands or improvements
        for command, usage_count in most_used:
            if usage_count > 5:  # Only suggest for frequently used commands
                suggestion_message = self._get_usage_suggestion(command, usage_count)
                
                if suggestion_message and not self._already_suggested_today(f"usage_{command}"):
                    suggestion = {
                        "type": "usage_based",
                        "category": "command_optimization",
                        "message": suggestion_message,
                        "priority": "low",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "id": f"usage_{command}_{datetime.datetime.now().strftime('%Y%m%d')}"
                    }
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_situational_suggestions(self, current_time: datetime.datetime) -> List[Dict[str, Any]]:
        """Generate suggestions based on current situation."""
        suggestions = []
        
        # Check conversation context for suggestions
        conversation_summary = self.conversation_memory.get_conversation_summary()
        
        if conversation_summary.get("status") == "active_conversation":
            # Suggest follow-ups based on conversation
            follow_up = self.conversation_memory.get_relevant_follow_up()
            
            if follow_up and not self._already_suggested_today("conversation_followup"):
                suggestion = {
                    "type": "situational",
                    "category": "conversation_followup",
                    "message": follow_up,
                    "priority": "medium",
                    "timestamp": current_time.isoformat(),
                    "id": f"followup_{current_time.strftime('%Y%m%d_%H%M')}"
                }
                suggestions.append(suggestion)
        
        # Productivity suggestions based on time patterns
        if self._is_productivity_time(current_time):
            productivity_suggestions = [
                "Would you like me to help you organize your tasks for maximum productivity?",
                "This seems like a great time to tackle important work. Need any assistance?",
                "Productivity tip: Would you like me to set up some focus reminders?"
            ]
            
            if not self._already_suggested_today("productivity_tip"):
                suggestion = {
                    "type": "situational",
                    "category": "productivity",
                    "message": self._select_random_suggestion(productivity_suggestions),
                    "priority": "low",
                    "timestamp": current_time.isoformat(),
                    "id": f"productivity_{current_time.strftime('%Y%m%d')}"
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _already_suggested_today(self, suggestion_id: str) -> bool:
        """Check if we've already made this suggestion today."""
        today = datetime.datetime.now().strftime('%Y%m%d')
        
        for suggestion in self.active_suggestions:
            if suggestion_id in suggestion.get("id", "") and today in suggestion.get("id", ""):
                return True
        
        return False
    
    def _select_time_suggestion(self, suggestions: List[str]) -> str:
        """Select a time-based suggestion, preferring variety."""
        # Simple rotation - could be enhanced with user preference learning
        import random
        return random.choice(suggestions)
    
    def _get_usage_suggestion(self, command: str, usage_count: int) -> Optional[str]:
        """Get usage-based suggestion for a command."""
        usage_suggestions = {
            "time": f"You check the time often ({usage_count} times)! Would you like me to create a desktop clock widget?",
            "weather": f"You love weather updates! Would you like me to set up automatic weather notifications?",
            "search": f"You search frequently! Would you like me to create some custom search shortcuts?",
            "volume": f"You adjust volume often! Would you like me to teach you voice volume control?",
            "system_info": f"You check system info regularly! Would you like a quick system dashboard?"
        }
        
        return usage_suggestions.get(command)
    
    def _is_productivity_time(self, current_time: datetime.datetime) -> bool:
        """Check if current time is typically productive."""
        hour = current_time.hour
        weekday = current_time.weekday()
        
        # Typical productivity hours on weekdays
        if weekday < 5:  # Monday to Friday
            return 9 <= hour <= 11 or 14 <= hour <= 16
        
        return False
    
    def _select_random_suggestion(self, suggestions: List[str]) -> str:
        """Select a random suggestion from a list."""
        import random
        return random.choice(suggestions)
    
    def _should_add_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        """Determine if a suggestion should be added."""
        # Check rate limiting
        current_hour = datetime.datetime.now().hour
        suggestions_this_hour = [
            s for s in self.active_suggestions
            if datetime.datetime.fromisoformat(s["timestamp"]).hour == current_hour
        ]
        
        max_per_hour = self.proactive_patterns["smart_interruptions"]["max_per_hour"]
        
        if len(suggestions_this_hour) >= max_per_hour:
            return False
        
        # Check if similar suggestion already exists
        for existing in self.active_suggestions:
            if (existing["type"] == suggestion["type"] and 
                existing["category"] == suggestion["category"]):
                return False
        
        return True
    
    def get_current_suggestions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get current proactive suggestions."""
        # Sort by priority and timestamp
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        sorted_suggestions = sorted(
            self.active_suggestions,
            key=lambda x: (
                priority_order.get(x.get("priority", "low"), 1),
                datetime.datetime.fromisoformat(x["timestamp"])
            ),
            reverse=True
        )
        
        return sorted_suggestions[:limit]
    
    def dismiss_suggestion(self, suggestion_id: str) -> bool:
        """Dismiss a proactive suggestion."""
        for i, suggestion in enumerate(self.active_suggestions):
            if suggestion.get("id") == suggestion_id:
                self.active_suggestions.pop(i)
                return True
        return False
    
    def accept_suggestion(self, suggestion_id: str) -> Dict[str, Any]:
        """Accept and act on a proactive suggestion."""
        for suggestion in self.active_suggestions:
            if suggestion.get("id") == suggestion_id:
                # Remove from active suggestions
                self.dismiss_suggestion(suggestion_id)
                
                # Learn from acceptance
                self._learn_from_suggestion_acceptance(suggestion)
                
                # Return action result
                return {
                    "status": "success",
                    "message": f"Acting on suggestion: {suggestion['message']}",
                    "action": self._execute_suggestion_action(suggestion)
                }
        
        return {
            "status": "error",
            "message": "Suggestion not found"
        }
    
    def _learn_from_suggestion_acceptance(self, suggestion: Dict[str, Any]):
        """Learn from user accepting a suggestion."""
        # Track successful suggestion types
        suggestion_type = f"{suggestion['type']}_{suggestion['category']}"
        
        if "successful_suggestions" not in self.proactive_patterns:
            self.proactive_patterns["successful_suggestions"] = {}
        
        if suggestion_type not in self.proactive_patterns["successful_suggestions"]:
            self.proactive_patterns["successful_suggestions"][suggestion_type] = 0
        
        self.proactive_patterns["successful_suggestions"][suggestion_type] += 1
        
        # Save updated patterns
        self._save_proactive_patterns()
    
    def _execute_suggestion_action(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action associated with a suggestion."""
        suggestion_type = suggestion["type"]
        category = suggestion["category"]
        
        if suggestion_type == "reminder" and category == "due_reminder":
            # Mark reminder as completed
            reminder_id = suggestion.get("data", {}).get("reminder_id")
            if reminder_id:
                self.user_profile.complete_reminder(reminder_id)
                return {"action": "reminder_completed", "reminder_id": reminder_id}
        
        elif suggestion_type == "time_based":
            # Execute time-based action
            if "weather" in suggestion["message"].lower():
                return {"action": "check_weather", "message": "Let me check the weather for you!"}
            elif "schedule" in suggestion["message"].lower():
                return {"action": "show_schedule", "message": "Here's your schedule overview!"}
        
        elif suggestion_type == "usage_based":
            # Execute usage optimization
            return {"action": "usage_tip", "message": "Here's how to optimize that command!"}
        
        return {"action": "acknowledged", "message": "Suggestion acknowledged!"}
    
    def configure_proactive_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure proactive assistant settings."""
        try:
            # Update smart interruptions settings
            if "max_suggestions_per_hour" in settings:
                self.proactive_patterns["smart_interruptions"]["max_per_hour"] = settings["max_suggestions_per_hour"]
            
            if "quiet_hours" in settings:
                self.proactive_patterns["smart_interruptions"]["quiet_hours"] = settings["quiet_hours"]
            
            # Update feature toggles
            if "enable_time_suggestions" in settings:
                self.proactive_patterns["situation_based_suggestions"]["productivity_tips"] = settings["enable_time_suggestions"]
            
            if "enable_reminder_notifications" in settings:
                self.proactive_patterns["situation_based_suggestions"]["reminder_notifications"] = settings["enable_reminder_notifications"]
            
            # Save settings
            self._save_proactive_patterns()
            
            return {
                "status": "success",
                "message": "Proactive settings updated successfully!"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error updating settings: {e}"
            }
    
    def get_proactive_stats(self) -> Dict[str, Any]:
        """Get statistics about proactive suggestions."""
        total_suggestions = len(self.active_suggestions)
        successful_suggestions = self.proactive_patterns.get("successful_suggestions", {})
        
        # Calculate acceptance rate
        total_successful = sum(successful_suggestions.values())
        
        # Get suggestion type breakdown
        type_breakdown = {}
        for suggestion in self.active_suggestions:
            suggestion_type = suggestion["type"]
            type_breakdown[suggestion_type] = type_breakdown.get(suggestion_type, 0) + 1
        
        return {
            "total_active_suggestions": total_suggestions,
            "total_successful_suggestions": total_successful,
            "suggestion_types": type_breakdown,
            "most_successful_types": sorted(
                successful_suggestions.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "monitoring_active": self.monitoring_active,
            "last_check": self.last_check_time.isoformat()
        }
    
    def stop_monitoring(self):
        """Stop proactive monitoring."""
        self.monitoring_active = False
    
    def restart_monitoring(self):
        """Restart proactive monitoring."""
        if not self.monitoring_active:
            self._start_background_monitoring()


class SmartNotificationManager:
    """Manages smart notifications and alerts."""
    
    def __init__(self):
        self.notifications = []
        self.notification_history = []
        self.settings = {
            "max_notifications": 10,
            "notification_timeout": 300,  # 5 minutes
            "priority_levels": ["low", "medium", "high", "urgent"],
            "quiet_mode": False
        }
    
    def add_notification(self, title: str, message: str, priority: str = "medium", 
                        actions: List[Dict[str, Any]] = None) -> str:
        """Add a smart notification."""
        notification_id = f"notif_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        notification = {
            "id": notification_id,
            "title": title,
            "message": message,
            "priority": priority,
            "timestamp": datetime.datetime.now().isoformat(),
            "actions": actions or [],
            "status": "active",
            "viewed": False
        }
        
        self.notifications.append(notification)
        
        # Maintain max notifications
        if len(self.notifications) > self.settings["max_notifications"]:
            expired = self.notifications.pop(0)
            self.notification_history.append(expired)
        
        return notification_id
    
    def get_notifications(self, priority_filter: str = None) -> List[Dict[str, Any]]:
        """Get active notifications, optionally filtered by priority."""
        if priority_filter:
            return [n for n in self.notifications if n["priority"] == priority_filter]
        
        # Sort by priority and timestamp
        priority_order = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
        
        return sorted(
            self.notifications,
            key=lambda x: (
                priority_order.get(x["priority"], 1),
                datetime.datetime.fromisoformat(x["timestamp"])
            ),
            reverse=True
        )
    
    def mark_notification_viewed(self, notification_id: str) -> bool:
        """Mark a notification as viewed."""
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["viewed"] = True
                return True
        return False
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss a notification."""
        for i, notification in enumerate(self.notifications):
            if notification["id"] == notification_id:
                dismissed = self.notifications.pop(i)
                dismissed["status"] = "dismissed"
                self.notification_history.append(dismissed)
                return True
        return False
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        active_count = len(self.notifications)
        total_count = active_count + len(self.notification_history)
        
        # Count by priority
        priority_counts = {}
        for notification in self.notifications:
            priority = notification["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "active_notifications": active_count,
            "total_notifications": total_count,
            "priority_breakdown": priority_counts,
            "unviewed_count": len([n for n in self.notifications if not n["viewed"]]),
            "quiet_mode": self.settings["quiet_mode"]
        }
