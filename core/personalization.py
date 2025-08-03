"""
MAC Assistant - User Profile & Memory System
Handles user personalization, preferences, and conversation memory.
"""

import json
import os
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class UserProfile:
    def __init__(self, profile_dir: str = "user_data"):
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(exist_ok=True)
        
        self.profile_file = self.profile_dir / "profile.json"
        self.memory_file = self.profile_dir / "memory.json"
        self.conversations_file = self.profile_dir / "conversations.json"
        self.custom_commands_file = self.profile_dir / "custom_commands.json"
        
        self.profile = self._load_profile()
        self.memory = self._load_memory()
        self.conversations = self._load_conversations()
        self.custom_commands = self._load_custom_commands()
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load user profile or create default."""
        default_profile = {
            "name": "User",
            "preferred_name": "User",
            "voice_settings": {
                "wake_words": ["MAC", "Hey MAC", "Computer"],
                "response_style": "friendly",  # friendly, formal, casual, humorous
                "response_length": "medium",   # short, medium, long
                "voice_speed": 200,
                "voice_volume": 0.9
            },
            "preferences": {
                "units": "metric",  # metric, imperial
                "time_format": "12h",  # 12h, 24h
                "language": "en",
                "timezone": "UTC",
                "default_location": "",
                "favorite_topics": [],
                "work_hours": {"start": "09:00", "end": "17:00"},
                "personal_info": {}
            },
            "learning": {
                "command_usage": {},
                "correction_history": [],
                "habits": {},
                "frequent_requests": []
            },
            "created_date": datetime.datetime.now().isoformat(),
            "last_interaction": datetime.datetime.now().isoformat()
        }
        
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    # Merge with defaults to add new fields
                    return {**default_profile, **profile}
            except Exception as e:
                print(f"Error loading profile: {e}")
                return default_profile
        else:
            self._save_profile(default_profile)
            return default_profile
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load long-term memory."""
        default_memory = {
            "facts": {},           # User-provided facts
            "notes": [],          # User notes
            "reminders": [],      # Active reminders
            "important_dates": {}, # Birthdays, anniversaries, etc.
            "favorite_things": {},  # Restaurants, movies, books, etc.
            "relationships": {},   # People in user's life
            "work_projects": {},   # Current projects
            "goals": [],          # User goals
            "achievements": []     # Completed goals/milestones
        }
        
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                    return {**default_memory, **memory}
            except Exception:
                return default_memory
        return default_memory
    
    def _load_conversations(self) -> List[Dict[str, Any]]:
        """Load conversation history."""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _load_custom_commands(self) -> Dict[str, Any]:
        """Load custom user-defined commands."""
        default_commands = {
            "shortcuts": {},       # Custom command shortcuts
            "workflows": {},       # Multi-step workflows
            "aliases": {},        # Command aliases
            "macros": {}          # Recorded command sequences
        }
        
        if self.custom_commands_file.exists():
            try:
                with open(self.custom_commands_file, 'r', encoding='utf-8') as f:
                    commands = json.load(f)
                    return {**default_commands, **commands}
            except Exception:
                return default_commands
        return default_commands
    
    def _save_profile(self, profile: Dict[str, Any] = None):
        """Save user profile."""
        profile_to_save = profile or self.profile
        profile_to_save["last_interaction"] = datetime.datetime.now().isoformat()
        
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_to_save, f, indent=2, ensure_ascii=False)
    
    def _save_memory(self):
        """Save memory data."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def _save_conversations(self):
        """Save conversation history."""
        # Keep only last 100 conversations to avoid huge files
        if len(self.conversations) > 100:
            self.conversations = self.conversations[-100:]
        
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)
    
    def _save_custom_commands(self):
        """Save custom commands."""
        with open(self.custom_commands_file, 'w', encoding='utf-8') as f:
            json.dump(self.custom_commands, f, indent=2, ensure_ascii=False)
    
    # Public methods for profile management
    def get_name(self) -> str:
        """Get user's preferred name."""
        return self.profile.get("preferred_name", "User")
    
    def set_name(self, name: str, preferred_name: str = None):
        """Set user's name."""
        self.profile["name"] = name
        self.profile["preferred_name"] = preferred_name or name
        self._save_profile()
    
    def get_preference(self, key: str, default=None):
        """Get a user preference."""
        return self.profile.get("preferences", {}).get(key, default)
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference."""
        if "preferences" not in self.profile:
            self.profile["preferences"] = {}
        self.profile["preferences"][key] = value
        self._save_profile()
    
    def add_conversation(self, user_input: str, ai_response: str, context: Dict[str, Any] = None):
        """Add conversation to history."""
        conversation = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "context": context or {}
        }
        self.conversations.append(conversation)
        self._save_conversations()
    
    def remember_fact(self, category: str, key: str, value: str):
        """Remember a user-provided fact."""
        if category not in self.memory["facts"]:
            self.memory["facts"][category] = {}
        self.memory["facts"][category][key] = {
            "value": value,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self._save_memory()
    
    def recall_fact(self, category: str, key: str = None):
        """Recall a remembered fact."""
        if key:
            return self.memory["facts"].get(category, {}).get(key, {}).get("value")
        else:
            return self.memory["facts"].get(category, {})
    
    def add_reminder(self, text: str, datetime_str: str = None, priority: str = "normal"):
        """Add a reminder."""
        reminder = {
            "id": len(self.memory["reminders"]) + 1,
            "text": text,
            "datetime": datetime_str or datetime.datetime.now().isoformat(),
            "priority": priority,
            "completed": False,
            "created": datetime.datetime.now().isoformat()
        }
        self.memory["reminders"].append(reminder)
        self._save_memory()
        return reminder["id"]
    
    def get_active_reminders(self) -> List[Dict[str, Any]]:
        """Get all active (incomplete) reminders."""
        return [r for r in self.memory["reminders"] if not r.get("completed", False)]
    
    def complete_reminder(self, reminder_id: int):
        """Mark a reminder as completed."""
        for reminder in self.memory["reminders"]:
            if reminder["id"] == reminder_id:
                reminder["completed"] = True
                self._save_memory()
                return True
        return False
    
    def learn_command_usage(self, command: str):
        """Learn from command usage patterns."""
        if "command_usage" not in self.profile["learning"]:
            self.profile["learning"]["command_usage"] = {}
        
        usage = self.profile["learning"]["command_usage"]
        usage[command] = usage.get(command, 0) + 1
        self._save_profile()
    
    def get_most_used_commands(self, limit: int = 5) -> List[tuple]:
        """Get most frequently used commands."""
        usage = self.profile["learning"].get("command_usage", {})
        return sorted(usage.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def add_custom_command(self, name: str, command_type: str, definition: Dict[str, Any]):
        """Add a custom command or workflow."""
        if command_type not in self.custom_commands:
            self.custom_commands[command_type] = {}
        
        self.custom_commands[command_type][name] = {
            **definition,
            "created": datetime.datetime.now().isoformat(),
            "usage_count": 0
        }
        self._save_custom_commands()
    
    def get_custom_command(self, name: str, command_type: str = None):
        """Get a custom command definition."""
        if command_type:
            return self.custom_commands.get(command_type, {}).get(name)
        else:
            # Search all types
            for cmd_type, commands in self.custom_commands.items():
                if name in commands:
                    return commands[name]
        return None
    
    def get_response_style(self) -> str:
        """Get user's preferred response style."""
        return self.profile.get("voice_settings", {}).get("response_style", "friendly")
    
    def get_wake_words(self) -> List[str]:
        """Get user's custom wake words."""
        return self.profile.get("voice_settings", {}).get("wake_words", ["MAC"])
    
    def add_note(self, text: str, category: str = "general"):
        """Add a personal note."""
        note = {
            "id": len(self.memory["notes"]) + 1,
            "text": text,
            "category": category,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.memory["notes"].append(note)
        self._save_memory()
        return note["id"]
    
    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search through user's notes."""
        query_lower = query.lower()
        return [note for note in self.memory["notes"] 
                if query_lower in note["text"].lower()]
    
    def get_context_for_ai(self) -> str:
        """Get relevant context to pass to AI."""
        context_parts = []
        
        # User name and preferences
        name = self.get_name()
        context_parts.append(f"User's name: {name}")
        
        # Response style
        style = self.get_response_style()
        context_parts.append(f"Response style: {style}")
        
        # Recent conversations (last 3)
        if self.conversations:
            recent = self.conversations[-3:]
            context_parts.append("Recent conversation context:")
            for conv in recent:
                context_parts.append(f"User: {conv['user_input'][:100]}")
                context_parts.append(f"Assistant: {conv['ai_response'][:100]}")
        
        # Active reminders
        reminders = self.get_active_reminders()
        if reminders:
            context_parts.append(f"Active reminders: {len(reminders)} pending")
        
        # Important preferences
        prefs = self.profile.get("preferences", {})
        if prefs.get("units"):
            context_parts.append(f"Preferred units: {prefs['units']}")
        if prefs.get("time_format"):
            context_parts.append(f"Time format: {prefs['time_format']}")
        
        return "\n".join(context_parts)


class PersonalAssistant:
    """Enhanced personal assistant with memory and learning capabilities."""
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.current_session = []
    
    def process_personalized_command(self, command: str) -> Dict[str, Any]:
        """Process commands with personalization."""
        command_lower = command.lower()
        
        # Personal information commands
        if any(phrase in command_lower for phrase in ["remember that", "remember:", "save this"]):
            return self._handle_remember_command(command)
        
        elif any(phrase in command_lower for phrase in ["what do you know about", "tell me about", "recall"]):
            return self._handle_recall_command(command)
        
        elif "remind me" in command_lower:
            return self._handle_reminder_command(command)
        
        elif "my reminders" in command_lower or "what reminders" in command_lower:
            return self._handle_list_reminders()
        
        elif "add note" in command_lower or "save note" in command_lower:
            return self._handle_add_note(command)
        
        elif "search notes" in command_lower or "find note" in command_lower:
            return self._handle_search_notes(command)
        
        elif "my preferences" in command_lower:
            return self._handle_show_preferences()
        
        elif "set preference" in command_lower or "change setting" in command_lower:
            return self._handle_set_preference(command)
        
        elif "my name is" in command_lower or "call me" in command_lower:
            return self._handle_set_name(command)
        
        elif "create command" in command_lower or "add shortcut" in command_lower:
            return self._handle_create_custom_command(command)
        
        elif "my stats" in command_lower or "usage stats" in command_lower:
            return self._handle_show_stats()
        
        return None  # Command not handled, pass to regular processing
    
    def _handle_remember_command(self, command: str) -> Dict[str, Any]:
        """Handle remember commands."""
        # Extract what to remember
        text = command.lower()
        if "remember that" in text:
            info = command.split("remember that", 1)[1].strip()
        elif "remember:" in text:
            info = command.split("remember:", 1)[1].strip()
        elif "save this" in text:
            info = command.split("save this", 1)[1].strip()
        else:
            return {"status": "error", "message": "I didn't understand what to remember."}
        
        # Try to categorize the information
        info_lower = info.lower()
        if any(word in info_lower for word in ["birthday", "born", "anniversary"]):
            category = "important_dates"
        elif any(word in info_lower for word in ["favorite", "like", "love", "prefer"]):
            category = "favorite_things"
        elif any(word in info_lower for word in ["work", "job", "project", "colleague"]):
            category = "work_projects"
        elif any(word in info_lower for word in ["family", "friend", "spouse", "partner"]):
            category = "relationships"
        else:
            category = "general"
        
        # Generate a key from the information
        key = info.split()[0:3]  # Use first 3 words as key
        key = "_".join(key).lower()
        
        self.user_profile.remember_fact(category, key, info)
        
        return {
            "status": "success",
            "message": f"I'll remember that: {info}",
            "data": {"category": category, "key": key}
        }
    
    def _handle_recall_command(self, command: str) -> Dict[str, Any]:
        """Handle recall commands."""
        # Extract what to recall
        text = command.lower()
        query_words = []
        
        if "what do you know about" in text:
            query = command.split("what do you know about", 1)[1].strip()
            query_words = query.split()
        elif "tell me about" in text:
            query = command.split("tell me about", 1)[1].strip()
            query_words = query.split()
        elif "recall" in text:
            query = command.split("recall", 1)[1].strip()
            query_words = query.split()
        
        if not query_words:
            return {"status": "error", "message": "What would you like me to recall?"}
        
        # Search through facts
        found_facts = []
        for category, facts in self.user_profile.memory["facts"].items():
            for key, fact_data in facts.items():
                if any(word.lower() in fact_data["value"].lower() for word in query_words):
                    found_facts.append(f"• {fact_data['value']}")
        
        if found_facts:
            response = f"Here's what I remember about {' '.join(query_words)}:\n" + "\n".join(found_facts)
        else:
            response = f"I don't have any information about {' '.join(query_words)} yet."
        
        return {"status": "success", "message": response}
    
    def _handle_reminder_command(self, command: str) -> Dict[str, Any]:
        """Handle reminder commands."""
        # Extract reminder text
        text = command.lower()
        if "remind me to" in text:
            reminder_text = command.split("remind me to", 1)[1].strip()
        elif "remind me" in text:
            reminder_text = command.split("remind me", 1)[1].strip()
        else:
            return {"status": "error", "message": "What would you like me to remind you about?"}
        
        # For now, just add the reminder (could be enhanced with time parsing)
        reminder_id = self.user_profile.add_reminder(reminder_text)
        
        return {
            "status": "success",
            "message": f"I'll remind you to {reminder_text}. Reminder ID: {reminder_id}",
            "data": {"reminder_id": reminder_id}
        }
    
    def _handle_list_reminders(self) -> Dict[str, Any]:
        """Handle listing reminders."""
        reminders = self.user_profile.get_active_reminders()
        
        if not reminders:
            return {"status": "success", "message": "You have no active reminders."}
        
        response = f"You have {len(reminders)} active reminders:\n"
        for reminder in reminders[:5]:  # Show up to 5
            response += f"• {reminder['text']} (ID: {reminder['id']})\n"
        
        return {"status": "success", "message": response}
    
    def _handle_add_note(self, command: str) -> Dict[str, Any]:
        """Handle adding notes."""
        text = command.lower()
        if "add note" in text:
            note_text = command.split("add note", 1)[1].strip()
        elif "save note" in text:
            note_text = command.split("save note", 1)[1].strip()
        else:
            return {"status": "error", "message": "What note would you like to add?"}
        
        note_id = self.user_profile.add_note(note_text)
        
        return {
            "status": "success",
            "message": f"Note saved! (ID: {note_id})",
            "data": {"note_id": note_id}
        }
    
    def _handle_search_notes(self, command: str) -> Dict[str, Any]:
        """Handle searching notes."""
        text = command.lower()
        if "search notes" in text:
            query = command.split("search notes", 1)[1].strip()
        elif "find note" in text:
            query = command.split("find note", 1)[1].strip()
        else:
            return {"status": "error", "message": "What would you like to search for?"}
        
        notes = self.user_profile.search_notes(query)
        
        if not notes:
            return {"status": "success", "message": f"No notes found matching '{query}'."}
        
        response = f"Found {len(notes)} notes matching '{query}':\n"
        for note in notes[:3]:  # Show up to 3
            response += f"• {note['text'][:100]}...\n"
        
        return {"status": "success", "message": response}
    
    def _handle_show_preferences(self) -> Dict[str, Any]:
        """Show user preferences."""
        prefs = self.user_profile.profile.get("preferences", {})
        name = self.user_profile.get_name()
        
        response = f"Your preferences, {name}:\n"
        response += f"• Units: {prefs.get('units', 'not set')}\n"
        response += f"• Time format: {prefs.get('time_format', 'not set')}\n"
        response += f"• Language: {prefs.get('language', 'not set')}\n"
        response += f"• Response style: {self.user_profile.get_response_style()}\n"
        
        return {"status": "success", "message": response}
    
    def _handle_set_preference(self, command: str) -> Dict[str, Any]:
        """Handle setting preferences."""
        text = command.lower()
        
        # Parse common preference patterns
        if "units to metric" in text or "use metric" in text:
            self.user_profile.set_preference("units", "metric")
            return {"status": "success", "message": "Units set to metric system."}
        elif "units to imperial" in text or "use imperial" in text:
            self.user_profile.set_preference("units", "imperial")
            return {"status": "success", "message": "Units set to imperial system."}
        elif "time format to 24" in text or "24 hour" in text:
            self.user_profile.set_preference("time_format", "24h")
            return {"status": "success", "message": "Time format set to 24-hour."}
        elif "time format to 12" in text or "12 hour" in text:
            self.user_profile.set_preference("time_format", "12h")
            return {"status": "success", "message": "Time format set to 12-hour."}
        elif "response style" in text:
            if "formal" in text:
                self.user_profile.profile["voice_settings"]["response_style"] = "formal"
                self.user_profile._save_profile()
                return {"status": "success", "message": "Response style set to formal."}
            elif "casual" in text:
                self.user_profile.profile["voice_settings"]["response_style"] = "casual"
                self.user_profile._save_profile()
                return {"status": "success", "message": "Response style set to casual."}
            elif "friendly" in text:
                self.user_profile.profile["voice_settings"]["response_style"] = "friendly"
                self.user_profile._save_profile()
                return {"status": "success", "message": "Response style set to friendly."}
        
        return {
            "status": "info", 
            "message": "Try: 'set units to metric', 'set time format to 24 hour', 'set response style to friendly'"
        }
    
    def _handle_set_name(self, command: str) -> Dict[str, Any]:
        """Handle setting user name."""
        text = command.lower()
        if "my name is" in text:
            name = command.split("my name is", 1)[1].strip()
        elif "call me" in text:
            name = command.split("call me", 1)[1].strip()
        else:
            return {"status": "error", "message": "I didn't catch your name."}
        
        self.user_profile.set_name(name, name)
        
        return {
            "status": "success",
            "message": f"Nice to meet you, {name}! I'll remember that.",
            "data": {"name": name}
        }
    
    def _handle_create_custom_command(self, command: str) -> Dict[str, Any]:
        """Handle creating custom commands."""
        return {
            "status": "success",
            "message": "Custom command creation is not fully implemented yet. This feature is coming soon!"
        }
    
    def _handle_show_stats(self) -> Dict[str, Any]:
        """Show usage statistics."""
        most_used = self.user_profile.get_most_used_commands(5)
        total_conversations = len(self.user_profile.conversations)
        active_reminders = len(self.user_profile.get_active_reminders())
        total_notes = len(self.user_profile.memory["notes"])
        
        response = f"Your MAC Assistant Statistics:\n"
        response += f"• Total conversations: {total_conversations}\n"
        response += f"• Active reminders: {active_reminders}\n"
        response += f"• Saved notes: {total_notes}\n"
        
        if most_used:
            response += f"\nMost used commands:\n"
            for cmd, count in most_used:
                response += f"• {cmd}: {count} times\n"
        
        return {"status": "success", "message": response}
