"""
MAC Assistant - Smart Learning & Adaptation System
Learns from user interactions, adapts behavior, and improves over time.
"""

import json
import datetime
import statistics
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re
from collections import defaultdict, Counter


class LearningEngine:
    """Learns from user interactions and adapts assistant behavior."""
    
    def __init__(self, learning_dir: str = "user_data"):
        self.learning_dir = Path(learning_dir)
        self.learning_dir.mkdir(exist_ok=True)
        
        self.patterns_file = self.learning_dir / "learned_patterns.json"
        self.preferences_file = self.learning_dir / "adaptive_preferences.json"
        self.corrections_file = self.learning_dir / "user_corrections.json"
        self.usage_stats_file = self.learning_dir / "usage_statistics.json"
        
        self.learned_patterns = self._load_learned_patterns()
        self.adaptive_preferences = self._load_adaptive_preferences()
        self.corrections = self._load_corrections()
        self.usage_stats = self._load_usage_stats()
        
        # Learning thresholds
        self.min_pattern_occurrences = 3
        self.confidence_threshold = 0.7
        self.adaptation_rate = 0.1
    
    def _load_learned_patterns(self) -> Dict[str, Any]:
        """Load learned interaction patterns."""
        default_patterns = {
            "command_sequences": {},      # Common command sequences
            "time_patterns": {},          # When user typically uses certain commands
            "context_triggers": {},       # What context leads to what commands
            "response_preferences": {},   # Preferred response styles for different situations
            "error_patterns": {},         # Common errors and their corrections
            "success_patterns": {},       # What works well for this user
            "custom_workflows": {}        # User-specific workflows
        }
        
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)
                    return {**default_patterns, **patterns}
            except Exception:
                return default_patterns
        return default_patterns
    
    def _load_adaptive_preferences(self) -> Dict[str, Any]:
        """Load adaptively learned preferences."""
        default_prefs = {
            "response_length": {"short": 0, "medium": 0, "long": 0},
            "response_style": {"formal": 0, "casual": 0, "friendly": 0, "humorous": 0},
            "interaction_time": {"morning": 0, "afternoon": 0, "evening": 0, "night": 0},
            "command_frequency": {},
            "topic_interests": {},
            "correction_frequency": {},
            "successful_suggestions": {},
            "ignored_suggestions": {}
        }
        
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    return {**default_prefs, **prefs}
            except Exception:
                return default_prefs
        return default_prefs
    
    def _load_corrections(self) -> List[Dict[str, Any]]:
        """Load user corrections and feedback."""
        if self.corrections_file.exists():
            try:
                with open(self.corrections_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _load_usage_stats(self) -> Dict[str, Any]:
        """Load usage statistics."""
        default_stats = {
            "daily_usage": {},            # Usage by day
            "hourly_patterns": {},        # Usage by hour
            "session_lengths": [],        # How long user interacts
            "command_success_rates": {},  # Success rate for each command
            "response_ratings": [],       # Implicit ratings based on follow-ups
            "feature_adoption": {},       # How quickly user adopts new features
            "error_rates": {}            # Error rates for different operations
        }
        
        if self.usage_stats_file.exists():
            try:
                with open(self.usage_stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    return {**default_stats, **stats}
            except Exception:
                return default_stats
        return default_stats
    
    def _save_data(self):
        """Save all learning data."""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.learned_patterns, f, indent=2, ensure_ascii=False)
        
        with open(self.preferences_file, 'w', encoding='utf-8') as f:
            json.dump(self.adaptive_preferences, f, indent=2, ensure_ascii=False)
        
        with open(self.corrections_file, 'w', encoding='utf-8') as f:
            json.dump(self.corrections, f, indent=2, ensure_ascii=False)
        
        with open(self.usage_stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage_stats, f, indent=2, ensure_ascii=False)
    
    def learn_from_interaction(self, user_input: str, ai_response: str, 
                             success: bool = True, user_feedback: str = None):
        """Learn from a user interaction."""
        timestamp = datetime.datetime.now()
        
        # Learn command patterns
        self._learn_command_patterns(user_input, timestamp)
        
        # Learn response preferences
        self._learn_response_preferences(user_input, ai_response, success)
        
        # Learn timing patterns
        self._learn_timing_patterns(user_input, timestamp)
        
        # Learn from feedback
        if user_feedback:
            self._learn_from_feedback(user_input, ai_response, user_feedback)
        
        # Update usage statistics
        self._update_usage_stats(user_input, success, timestamp)
        
        # Save learned data
        self._save_data()
    
    def _learn_command_patterns(self, user_input: str, timestamp: datetime.datetime):
        """Learn patterns in command usage."""
        command_type = self._classify_command(user_input)
        
        # Track command sequences
        if hasattr(self, 'last_command') and self.last_command:
            sequence = f"{self.last_command} -> {command_type}"
            if sequence not in self.learned_patterns["command_sequences"]:
                self.learned_patterns["command_sequences"][sequence] = 0
            self.learned_patterns["command_sequences"][sequence] += 1
        
        self.last_command = command_type
        
        # Learn context triggers
        context_words = self._extract_context_words(user_input)
        for word in context_words:
            if word not in self.learned_patterns["context_triggers"]:
                self.learned_patterns["context_triggers"][word] = defaultdict(int)
            self.learned_patterns["context_triggers"][word][command_type] += 1
    
    def _learn_response_preferences(self, user_input: str, ai_response: str, success: bool):
        """Learn user's response preferences."""
        response_length = self._classify_response_length(ai_response)
        response_style = self._classify_response_style(ai_response)
        
        # Update preference scores based on success
        weight = 1 if success else -0.5
        
        self.adaptive_preferences["response_length"][response_length] += weight
        self.adaptive_preferences["response_style"][response_style] += weight
        
        # Learn successful patterns
        if success:
            pattern_key = f"{self._classify_command(user_input)}_{response_style}_{response_length}"
            if pattern_key not in self.learned_patterns["success_patterns"]:
                self.learned_patterns["success_patterns"][pattern_key] = 0
            self.learned_patterns["success_patterns"][pattern_key] += 1
    
    def _learn_timing_patterns(self, user_input: str, timestamp: datetime.datetime):
        """Learn when user typically uses certain commands."""
        hour = timestamp.hour
        command_type = self._classify_command(user_input)
        
        # Map hour to time period
        if 5 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"
        elif 17 <= hour < 22:
            period = "evening"
        else:
            period = "night"
        
        self.adaptive_preferences["interaction_time"][period] += 1
        
        # Track command timing
        if command_type not in self.learned_patterns["time_patterns"]:
            self.learned_patterns["time_patterns"][command_type] = defaultdict(int)
        self.learned_patterns["time_patterns"][command_type][period] += 1
    
    def _learn_from_feedback(self, user_input: str, ai_response: str, feedback: str):
        """Learn from explicit user feedback."""
        correction_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "user_feedback": feedback,
            "feedback_type": self._classify_feedback(feedback)
        }
        
        self.corrections.append(correction_entry)
        
        # Keep only recent corrections
        if len(self.corrections) > 100:
            self.corrections = self.corrections[-100:]
        
        # Learn from correction patterns
        feedback_type = correction_entry["feedback_type"]
        command_type = self._classify_command(user_input)
        
        if command_type not in self.adaptive_preferences["correction_frequency"]:
            self.adaptive_preferences["correction_frequency"][command_type] = {}
        
        if feedback_type not in self.adaptive_preferences["correction_frequency"][command_type]:
            self.adaptive_preferences["correction_frequency"][command_type][feedback_type] = 0
        
        self.adaptive_preferences["correction_frequency"][command_type][feedback_type] += 1
    
    def _update_usage_stats(self, user_input: str, success: bool, timestamp: datetime.datetime):
        """Update usage statistics."""
        date_str = timestamp.date().isoformat()
        hour_str = str(timestamp.hour)
        command_type = self._classify_command(user_input)
        
        # Daily usage
        if date_str not in self.usage_stats["daily_usage"]:
            self.usage_stats["daily_usage"][date_str] = 0
        self.usage_stats["daily_usage"][date_str] += 1
        
        # Hourly patterns
        if hour_str not in self.usage_stats["hourly_patterns"]:
            self.usage_stats["hourly_patterns"][hour_str] = 0
        self.usage_stats["hourly_patterns"][hour_str] += 1
        
        # Command success rates
        if command_type not in self.usage_stats["command_success_rates"]:
            self.usage_stats["command_success_rates"][command_type] = {"success": 0, "total": 0}
        
        self.usage_stats["command_success_rates"][command_type]["total"] += 1
        if success:
            self.usage_stats["command_success_rates"][command_type]["success"] += 1
    
    def _classify_command(self, user_input: str) -> str:
        """Classify the type of command."""
        text = user_input.lower()
        
        if any(word in text for word in ["time", "clock", "hour"]):
            return "time_query"
        elif any(word in text for word in ["weather", "temperature", "forecast"]):
            return "weather_query"
        elif any(word in text for word in ["search", "find", "look"]):
            return "search"
        elif any(word in text for word in ["play", "music", "youtube"]):
            return "media"
        elif any(word in text for word in ["remind", "reminder", "schedule"]):
            return "reminder"
        elif any(word in text for word in ["open", "launch", "start"]):
            return "application"
        elif any(word in text for word in ["volume", "sound", "audio"]):
            return "system_control"
        elif any(word in text for word in ["remember", "save", "note"]):
            return "memory"
        elif "?" in text or any(word in text for word in ["what", "how", "why", "when", "where"]):
            return "question"
        else:
            return "general"
    
    def _classify_response_length(self, response: str) -> str:
        """Classify response length."""
        word_count = len(response.split())
        
        if word_count < 20:
            return "short"
        elif word_count < 100:
            return "medium"
        else:
            return "long"
    
    def _classify_response_style(self, response: str) -> str:
        """Classify response style."""
        text = response.lower()
        
        formal_indicators = ["however", "therefore", "furthermore", "consequently"]
        casual_indicators = ["yeah", "sure", "cool", "awesome", "hey"]
        friendly_indicators = ["happy to", "glad to", "love to", "excited to"]
        humorous_indicators = ["haha", "lol", "funny", "joke"]
        
        scores = {
            "formal": sum(1 for word in formal_indicators if word in text),
            "casual": sum(1 for word in casual_indicators if word in text),
            "friendly": sum(1 for word in friendly_indicators if word in text),
            "humorous": sum(1 for word in humorous_indicators if word in text)
        }
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "neutral"
    
    def _classify_feedback(self, feedback: str) -> str:
        """Classify user feedback type."""
        feedback_lower = feedback.lower()
        
        if any(word in feedback_lower for word in ["wrong", "incorrect", "not right", "error"]):
            return "correction"
        elif any(word in feedback_lower for word in ["good", "great", "perfect", "right", "correct"]):
            return "positive"
        elif any(word in feedback_lower for word in ["too long", "too short", "verbose", "brief"]):
            return "length_preference"
        elif any(word in feedback_lower for word in ["formal", "casual", "friendly", "professional"]):
            return "style_preference"
        else:
            return "general"
    
    def _extract_context_words(self, text: str) -> List[str]:
        """Extract context words that might trigger certain commands."""
        # Remove common stop words and extract meaningful context
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [word.lower() for word in text.split() if word.lower() not in stop_words and len(word) > 2]
        
        # Return unique words that might be contextual triggers
        return list(set(words))
    
    def get_adaptive_suggestions(self, user_input: str, context: Dict[str, Any] = None) -> List[str]:
        """Get suggestions based on learned patterns."""
        suggestions = []
        command_type = self._classify_command(user_input)
        
        # Suggest based on command sequences
        most_common_sequences = self._get_most_common_sequences(command_type)
        for next_command in most_common_sequences[:2]:
            suggestions.append(f"Would you like to {next_command.replace('_', ' ')}?")
        
        # Suggest based on time patterns
        current_time = datetime.datetime.now()
        time_suggestions = self._get_time_based_suggestions(current_time)
        suggestions.extend(time_suggestions[:2])
        
        # Suggest based on context
        context_suggestions = self._get_context_based_suggestions(user_input)
        suggestions.extend(context_suggestions[:2])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _get_most_common_sequences(self, current_command: str) -> List[str]:
        """Get most common commands that follow the current command."""
        sequences = self.learned_patterns["command_sequences"]
        relevant_sequences = [(seq, count) for seq, count in sequences.items() 
                            if seq.startswith(current_command + " ->")]
        
        # Sort by frequency and extract next commands
        relevant_sequences.sort(key=lambda x: x[1], reverse=True)
        next_commands = [seq[0].split(" -> ")[1] for seq in relevant_sequences[:3]]
        
        return next_commands
    
    def _get_time_based_suggestions(self, current_time: datetime.datetime) -> List[str]:
        """Get suggestions based on time patterns."""
        suggestions = []
        hour = current_time.hour
        
        # Morning suggestions
        if 6 <= hour < 12:
            suggestions.append("Would you like to check today's weather?")
            suggestions.append("Should I help you plan your day?")
        
        # Afternoon suggestions
        elif 12 <= hour < 17:
            suggestions.append("Would you like me to check your reminders?")
            suggestions.append("Need help with any work tasks?")
        
        # Evening suggestions
        elif 17 <= hour < 22:
            suggestions.append("Would you like to review today's accomplishments?")
            suggestions.append("Should I help you plan tomorrow?")
        
        # Night suggestions
        else:
            suggestions.append("Would you like me to set any reminders for tomorrow?")
            suggestions.append("Should I help you wind down for the night?")
        
        return suggestions
    
    def _get_context_based_suggestions(self, user_input: str) -> List[str]:
        """Get suggestions based on context triggers."""
        suggestions = []
        context_words = self._extract_context_words(user_input)
        
        # Find common commands triggered by these context words
        for word in context_words:
            if word in self.learned_patterns["context_triggers"]:
                triggers = self.learned_patterns["context_triggers"][word]
                most_common = max(triggers, key=triggers.get) if triggers else None
                
                if most_common and triggers[most_common] >= self.min_pattern_occurrences:
                    suggestion = self._command_to_suggestion(most_common)
                    if suggestion and suggestion not in suggestions:
                        suggestions.append(suggestion)
        
        return suggestions[:3]
    
    def _command_to_suggestion(self, command_type: str) -> str:
        """Convert command type to user-friendly suggestion."""
        suggestion_map = {
            "time_query": "Would you like to know the current time?",
            "weather_query": "Should I check the weather for you?",
            "search": "Would you like me to search for something?",
            "media": "Should I play some music or videos?",
            "reminder": "Would you like to set a reminder?",
            "application": "Should I open an application for you?",
            "system_control": "Need help with system controls?",
            "memory": "Would you like me to remember something?",
            "question": "Do you have any questions I can help with?"
        }
        
        return suggestion_map.get(command_type)
    
    def get_preferred_response_style(self) -> str:
        """Get the user's preferred response style based on learning."""
        style_prefs = self.adaptive_preferences["response_style"]
        
        # Find the style with highest positive score
        if max(style_prefs.values()) > 0:
            return max(style_prefs, key=style_prefs.get)
        else:
            return "friendly"  # Default
    
    def get_preferred_response_length(self) -> str:
        """Get the user's preferred response length."""
        length_prefs = self.adaptive_preferences["response_length"]
        
        if max(length_prefs.values()) > 0:
            return max(length_prefs, key=length_prefs.get)
        else:
            return "medium"  # Default
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about what the system has learned."""
        insights = {}
        
        # Most used commands
        command_usage = defaultdict(int)
        for seq, count in self.learned_patterns["command_sequences"].items():
            commands = seq.split(" -> ")
            for cmd in commands:
                command_usage[cmd] += count
        
        most_used = sorted(command_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        insights["most_used_commands"] = most_used
        
        # Preferred response style
        insights["preferred_style"] = self.get_preferred_response_style()
        insights["preferred_length"] = self.get_preferred_response_length()
        
        # Usage patterns
        time_prefs = self.adaptive_preferences["interaction_time"]
        most_active_time = max(time_prefs, key=time_prefs.get) if time_prefs else "unknown"
        insights["most_active_time"] = most_active_time
        
        # Success rates
        success_rates = {}
        for cmd, stats in self.usage_stats["command_success_rates"].items():
            if stats["total"] > 0:
                success_rates[cmd] = stats["success"] / stats["total"]
        
        insights["command_success_rates"] = success_rates
        
        # Learning progress
        total_interactions = sum(self.adaptive_preferences["interaction_time"].values())
        insights["total_interactions"] = total_interactions
        insights["corrections_count"] = len(self.corrections)
        insights["patterns_learned"] = len(self.learned_patterns["command_sequences"])
        
        return insights
    
    def adapt_to_user_feedback(self, feedback_type: str, context: Dict[str, Any]):
        """Adapt behavior based on user feedback."""
        adaptation_weight = self.adaptation_rate
        
        if feedback_type == "too_verbose":
            self.adaptive_preferences["response_length"]["long"] -= adaptation_weight
            self.adaptive_preferences["response_length"]["short"] += adaptation_weight
        
        elif feedback_type == "too_brief":
            self.adaptive_preferences["response_length"]["short"] -= adaptation_weight
            self.adaptive_preferences["response_length"]["long"] += adaptation_weight
        
        elif feedback_type == "too_formal":
            self.adaptive_preferences["response_style"]["formal"] -= adaptation_weight
            self.adaptive_preferences["response_style"]["casual"] += adaptation_weight
        
        elif feedback_type == "too_casual":
            self.adaptive_preferences["response_style"]["casual"] -= adaptation_weight
            self.adaptive_preferences["response_style"]["formal"] += adaptation_weight
        
        # Save adaptations
        self._save_data()


class PersonalizedResponseGenerator:
    """Generates responses personalized to user preferences."""
    
    def __init__(self, learning_engine: LearningEngine):
        self.learning_engine = learning_engine
    
    def personalize_response_prompt(self, base_prompt: str, user_input: str) -> str:
        """Personalize AI prompt based on learned preferences."""
        personalized_prompt = [base_prompt]
        
        # Add style preferences
        preferred_style = self.learning_engine.get_preferred_response_style()
        preferred_length = self.learning_engine.get_preferred_response_length()
        
        personalized_prompt.append(f"Response style preference: {preferred_style}")
        personalized_prompt.append(f"Response length preference: {preferred_length}")
        
        # Add learned patterns
        suggestions = self.learning_engine.get_adaptive_suggestions(user_input)
        if suggestions:
            personalized_prompt.append("Consider offering these relevant suggestions:")
            personalized_prompt.extend(suggestions)
        
        # Add context from successful patterns
        command_type = self.learning_engine._classify_command(user_input)
        success_patterns = self.learning_engine.learned_patterns["success_patterns"]
        
        relevant_patterns = [pattern for pattern in success_patterns.keys() 
                           if pattern.startswith(command_type)]
        
        if relevant_patterns:
            best_pattern = max(relevant_patterns, key=lambda p: success_patterns[p])
            parts = best_pattern.split("_")
            if len(parts) >= 3:
                personalized_prompt.append(f"This user typically responds well to {parts[1]} style, {parts[2]} length responses for {command_type} commands.")
        
        return "\n".join(personalized_prompt)
