"""
MAC Assistant - Smart Conversation Memory & Context Management
Provides intelligent conversation continuity and context awareness.
"""

import json
import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re


class ConversationMemory:
    """Manages conversation context and continuity."""
    
    def __init__(self, memory_dir: str = "user_data"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        self.session_file = self.memory_dir / "current_session.json"
        self.context_file = self.memory_dir / "conversation_context.json"
        
        self.current_session = self._load_current_session()
        self.conversation_context = self._load_conversation_context()
        
        # Track conversation state
        self.last_topic = None
        self.active_follow_ups = []
        self.waiting_for_response = False
        self.conversation_depth = 0
    
    def _load_current_session(self) -> List[Dict[str, Any]]:
        """Load current conversation session."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _load_conversation_context(self) -> Dict[str, Any]:
        """Load conversation context data."""
        default_context = {
            "topics": {},           # Topic tracking
            "entities": {},         # Named entities mentioned
            "tasks": [],           # Ongoing tasks/requests
            "follow_ups": [],      # Pending follow-up questions
            "mood": "neutral",     # Conversation mood
            "complexity": "medium", # Conversation complexity level
            "last_activity": None  # Last interaction timestamp
        }
        
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    context = json.load(f)
                    return {**default_context, **context}
            except Exception:
                return default_context
        return default_context
    
    def _save_session(self):
        """Save current session."""
        # Keep only last 20 exchanges to avoid memory bloat
        if len(self.current_session) > 40:  # 20 exchanges = 40 messages
            self.current_session = self.current_session[-40:]
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_session, f, indent=2, ensure_ascii=False)
    
    def _save_context(self):
        """Save conversation context."""
        self.conversation_context["last_activity"] = datetime.datetime.now().isoformat()
        
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_context, f, indent=2, ensure_ascii=False)
    
    def add_exchange(self, user_input: str, ai_response: str, metadata: Dict[str, Any] = None):
        """Add a conversation exchange."""
        timestamp = datetime.datetime.now().isoformat()
        
        # Add user message
        self.current_session.append({
            "type": "user",
            "content": user_input,
            "timestamp": timestamp,
            "metadata": metadata or {}
        })
        
        # Add AI response
        self.current_session.append({
            "type": "assistant",
            "content": ai_response,
            "timestamp": timestamp,
            "metadata": {}
        })
        
        # Update context
        self._update_context(user_input, ai_response)
        
        # Save data
        self._save_session()
        self._save_context()
    
    def _update_context(self, user_input: str, ai_response: str):
        """Update conversation context based on new exchange."""
        # Extract entities (simple implementation)
        entities = self._extract_entities(user_input)
        for entity_type, entity_value in entities:
            if entity_type not in self.conversation_context["entities"]:
                self.conversation_context["entities"][entity_type] = []
            if entity_value not in self.conversation_context["entities"][entity_type]:
                self.conversation_context["entities"][entity_type].append(entity_value)
        
        # Detect topics
        topics = self._detect_topics(user_input)
        for topic in topics:
            if topic not in self.conversation_context["topics"]:
                self.conversation_context["topics"][topic] = 0
            self.conversation_context["topics"][topic] += 1
        
        # Update mood (simple sentiment analysis)
        mood = self._detect_mood(user_input)
        if mood != "neutral":
            self.conversation_context["mood"] = mood
        
        # Detect ongoing tasks
        if any(word in user_input.lower() for word in ["remind", "schedule", "plan", "help me", "work on"]):
            task = {
                "description": user_input,
                "created": datetime.datetime.now().isoformat(),
                "status": "active"
            }
            self.conversation_context["tasks"].append(task)
        
        # Generate follow-ups
        follow_ups = self._generate_follow_ups(user_input, ai_response)
        self.conversation_context["follow_ups"].extend(follow_ups)
        
        # Keep only recent follow-ups
        if len(self.conversation_context["follow_ups"]) > 10:
            self.conversation_context["follow_ups"] = self.conversation_context["follow_ups"][-10:]
    
    def _extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract named entities from text."""
        entities = []
        
        # Simple regex-based entity extraction
        # Names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for name in names:
            if len(name.split()) <= 3:  # Limit to reasonable name length
                entities.append(("person", name))
        
        # Dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            for date in dates:
                entities.append(("date", date))
        
        # Times
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b',
            r'\b(?:morning|afternoon|evening|night)\b'
        ]
        for pattern in time_patterns:
            times = re.findall(pattern, text, re.IGNORECASE)
            for time in times:
                entities.append(("time", time))
        
        # Locations (simple implementation)
        location_keywords = ["at", "in", "to", "from", "near"]
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in location_keywords and i + 1 < len(words):
                next_word = words[i + 1]
                if next_word[0].isupper() and len(next_word) > 2:
                    entities.append(("location", next_word))
        
        return entities
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect conversation topics."""
        topics = []
        text_lower = text.lower()
        
        # Topic keywords mapping
        topic_map = {
            "work": ["work", "job", "office", "meeting", "project", "deadline", "colleague", "boss"],
            "family": ["family", "mom", "dad", "mother", "father", "sister", "brother", "spouse", "child"],
            "health": ["health", "doctor", "medicine", "exercise", "diet", "hospital", "sick", "pain"],
            "technology": ["computer", "software", "app", "website", "code", "programming", "tech"],
            "entertainment": ["movie", "music", "game", "show", "book", "hobby", "fun"],
            "travel": ["travel", "trip", "vacation", "flight", "hotel", "visit", "destination"],
            "food": ["food", "restaurant", "cook", "recipe", "eat", "meal", "dinner", "lunch"],
            "shopping": ["buy", "shop", "store", "purchase", "order", "delivery", "price"],
            "education": ["learn", "study", "school", "university", "course", "teacher", "student"],
            "finance": ["money", "bank", "budget", "invest", "savings", "expense", "cost", "pay"]
        }
        
        for topic, keywords in topic_map.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _detect_mood(self, text: str) -> str:
        """Detect conversation mood."""
        text_lower = text.lower()
        
        positive_words = ["happy", "great", "awesome", "good", "excited", "wonderful", "amazing", "love"]
        negative_words = ["sad", "bad", "terrible", "awful", "hate", "angry", "frustrated", "disappointed"]
        question_words = ["how", "what", "when", "where", "why", "which", "who"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        has_question = any(word in text_lower for word in question_words)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        elif has_question:
            return "curious"
        else:
            return "neutral"
    
    def _generate_follow_ups(self, user_input: str, ai_response: str) -> List[str]:
        """Generate potential follow-up questions."""
        follow_ups = []
        user_lower = user_input.lower()
        
        # Based on user input patterns
        if "how" in user_lower and "work" in user_lower:
            follow_ups.append("Would you like me to help you with any work-related tasks?")
        
        if any(word in user_lower for word in ["problem", "issue", "trouble"]):
            follow_ups.append("Is there anything specific I can help you solve?")
        
        if any(word in user_lower for word in ["plan", "planning", "schedule"]):
            follow_ups.append("Would you like me to help organize your plans?")
        
        if "learn" in user_lower or "how to" in user_lower:
            follow_ups.append("Would you like me to find some learning resources for you?")
        
        # Based on detected entities
        if self._has_date_entity(user_input):
            follow_ups.append("Should I set a reminder for that date?")
        
        if self._has_person_entity(user_input):
            follow_ups.append("Would you like me to remember information about this person?")
        
        return follow_ups[:3]  # Limit to 3 follow-ups
    
    def _has_date_entity(self, text: str) -> bool:
        """Check if text contains date entities."""
        entities = self._extract_entities(text)
        return any(entity_type == "date" for entity_type, _ in entities)
    
    def _has_person_entity(self, text: str) -> bool:
        """Check if text contains person entities."""
        entities = self._extract_entities(text)
        return any(entity_type == "person" for entity_type, _ in entities)
    
    def get_context_for_ai(self) -> str:
        """Get conversation context for AI processing."""
        context_parts = []
        
        # Recent conversation history
        if self.current_session:
            context_parts.append("Recent conversation:")
            recent_messages = self.current_session[-6:]  # Last 3 exchanges
            for msg in recent_messages:
                role = "User" if msg["type"] == "user" else "Assistant"
                content = msg["content"][:150]  # Truncate long messages
                context_parts.append(f"{role}: {content}")
        
        # Current topics
        if self.conversation_context["topics"]:
            top_topics = sorted(self.conversation_context["topics"].items(), 
                              key=lambda x: x[1], reverse=True)[:3]
            topics_str = ", ".join([topic for topic, _ in top_topics])
            context_parts.append(f"Current topics: {topics_str}")
        
        # Conversation mood
        mood = self.conversation_context.get("mood", "neutral")
        if mood != "neutral":
            context_parts.append(f"Conversation mood: {mood}")
        
        # Active tasks
        active_tasks = [task for task in self.conversation_context["tasks"] 
                       if task.get("status") == "active"]
        if active_tasks:
            context_parts.append(f"Active tasks: {len(active_tasks)} ongoing")
        
        # Pending follow-ups
        if self.conversation_context["follow_ups"]:
            latest_follow_up = self.conversation_context["follow_ups"][-1]
            context_parts.append(f"Suggested follow-up: {latest_follow_up}")
        
        return "\n".join(context_parts)
    
    def get_short_context(self) -> str:
        """Get minimal context for quick responses."""
        if not self.current_session:
            return ""
        
        # Just the last exchange
        recent = self.current_session[-2:]  # Last user message and AI response
        if len(recent) >= 2:
            user_msg = recent[0]["content"][:100]
            ai_msg = recent[1]["content"][:100]
            return f"Last exchange - User: {user_msg} | Assistant: {ai_msg}"
        
        return ""
    
    def clear_session(self):
        """Clear current session (new conversation)."""
        self.current_session = []
        self.conversation_context["follow_ups"] = []
        self.conversation_context["mood"] = "neutral"
        self._save_session()
        self._save_context()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        if not self.current_session:
            return {"status": "no_conversation", "message": "No active conversation."}
        
        total_exchanges = len(self.current_session) // 2
        start_time = self.current_session[0]["timestamp"] if self.current_session else None
        
        # Get top topics
        top_topics = sorted(self.conversation_context["topics"].items(), 
                          key=lambda x: x[1], reverse=True)[:3]
        
        # Count entities
        entity_count = sum(len(entities) for entities in self.conversation_context["entities"].values())
        
        return {
            "status": "active_conversation",
            "total_exchanges": total_exchanges,
            "start_time": start_time,
            "mood": self.conversation_context["mood"],
            "top_topics": [topic for topic, _ in top_topics],
            "entities_mentioned": entity_count,
            "active_tasks": len([t for t in self.conversation_context["tasks"] if t.get("status") == "active"]),
            "pending_follow_ups": len(self.conversation_context["follow_ups"])
        }
    
    def suggest_response_style(self) -> str:
        """Suggest response style based on conversation context."""
        mood = self.conversation_context.get("mood", "neutral")
        
        if mood == "positive":
            return "enthusiastic"
        elif mood == "negative":
            return "supportive"
        elif mood == "curious":
            return "informative"
        else:
            return "balanced"
    
    def get_relevant_follow_up(self) -> Optional[str]:
        """Get the most relevant follow-up question."""
        if not self.conversation_context["follow_ups"]:
            return None
        
        # Return the most recent follow-up
        return self.conversation_context["follow_ups"][-1]


class SmartResponseGenerator:
    """Generates contextually aware responses."""
    
    def __init__(self, conversation_memory: ConversationMemory):
        self.memory = conversation_memory
    
    def enhance_ai_prompt(self, user_input: str, base_context: str = "") -> str:
        """Enhance AI prompt with conversation context."""
        enhanced_prompt = []
        
        # Add base context
        if base_context:
            enhanced_prompt.append(base_context)
        
        # Add conversation context
        conv_context = self.memory.get_context_for_ai()
        if conv_context:
            enhanced_prompt.append("Conversation context:")
            enhanced_prompt.append(conv_context)
        
        # Add response style guidance
        style = self.memory.suggest_response_style()
        enhanced_prompt.append(f"Response style: {style}")
        
        # Add the user's actual input
        enhanced_prompt.append(f"User input: {user_input}")
        
        # Add guidance for contextual responses
        enhanced_prompt.append(
            "Please provide a response that:\n"
            "- References relevant conversation history when appropriate\n"
            "- Maintains conversational continuity\n"
            "- Suggests helpful follow-ups when relevant\n"
            "- Adapts to the user's mood and communication style"
        )
        
        return "\n\n".join(enhanced_prompt)
    
    def should_reference_history(self, user_input: str) -> bool:
        """Determine if response should reference conversation history."""
        user_lower = user_input.lower()
        
        # Reference words that suggest continuation
        reference_words = [
            "that", "it", "this", "what we talked about", "before", "earlier",
            "you said", "you mentioned", "continue", "more about", "also"
        ]
        
        return any(word in user_lower for word in reference_words)
    
    def extract_continuation_context(self, user_input: str) -> Optional[str]:
        """Extract specific context the user is referring to."""
        if not self.should_reference_history(user_input):
            return None
        
        # Look for specific references in recent conversation
        recent_context = self.memory.get_short_context()
        return recent_context if recent_context else None
