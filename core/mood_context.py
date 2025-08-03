"""
MAC Assistant - Smart Context & Mood Detection System
Provides emotional intelligence and contextual awareness.
"""

import re
import datetime
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter


class MoodDetector:
    """Detects user mood and emotional state from conversation."""
    
    def __init__(self):
        # Emotion indicators
        self.emotion_patterns = {
            "happy": {
                "keywords": ["happy", "great", "awesome", "wonderful", "amazing", "fantastic", "excellent", "love", "excited", "thrilled", "joy"],
                "indicators": ["!", "😊", "😄", "😃", "🎉", "❤️", "😍"],
                "patterns": [r"i'?m (so |really |very )?happy", r"feel(ing)? (great|amazing|wonderful)", r"love (this|it|that)"]
            },
            "sad": {
                "keywords": ["sad", "depressed", "down", "blue", "miserable", "upset", "disappointed", "heartbroken", "crying"],
                "indicators": ["😢", "😭", "💔", "😞", "😔"],
                "patterns": [r"i'?m (so |really |very )?sad", r"feel(ing)? (down|blue|depressed)", r"makes me (sad|cry)"]
            },
            "angry": {
                "keywords": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "rage", "hate", "pissed"],
                "indicators": ["😠", "😡", "🤬", "💢"],
                "patterns": [r"i'?m (so |really |very )?(angry|mad|furious)", r"hate (this|it|that)", r"makes me (angry|mad)"]
            },
            "anxious": {
                "keywords": ["anxious", "worried", "nervous", "stressed", "panic", "fear", "scared", "concerned"],
                "indicators": ["😰", "😱", "😨", "😧"],
                "patterns": [r"i'?m (so |really |very )?(anxious|worried|nervous)", r"stress(ed|ing)", r"makes me (nervous|anxious)"]
            },
            "excited": {
                "keywords": ["excited", "pumped", "hyped", "enthusiastic", "eager", "thrilled", "psyched"],
                "indicators": ["🎉", "🚀", "⚡", "🔥", "💪"],
                "patterns": [r"i'?m (so |really |very )?excited", r"can'?t wait", r"pumped (for|about)"]
            },
            "confused": {
                "keywords": ["confused", "lost", "unclear", "puzzled", "baffled", "bewildered"],
                "indicators": ["🤔", "😕", "❓", "🤷"],
                "patterns": [r"i'?m (so |really |very )?confused", r"don'?t understand", r"what do you mean"]
            },
            "tired": {
                "keywords": ["tired", "exhausted", "sleepy", "drowsy", "weary", "fatigued", "drained"],
                "indicators": ["😴", "😪", "🥱"],
                "patterns": [r"i'?m (so |really |very )?(tired|exhausted)", r"feel(ing)? sleepy", r"need (sleep|rest)"]
            },
            "grateful": {
                "keywords": ["thank", "thanks", "grateful", "appreciate", "thankful", "blessed"],
                "indicators": ["🙏", "❤️", "💕"],
                "patterns": [r"thank you", r"i appreciate", r"grateful (for|that)", r"thanks (for|so much)"]
            }
        }
        
        # Context indicators
        self.context_patterns = {
            "work": ["work", "job", "office", "meeting", "project", "deadline", "boss", "colleague", "presentation", "client"],
            "family": ["family", "mom", "dad", "parent", "child", "kids", "spouse", "wife", "husband", "sister", "brother"],
            "health": ["health", "doctor", "hospital", "medicine", "sick", "pain", "exercise", "diet", "therapy"],
            "relationship": ["girlfriend", "boyfriend", "partner", "dating", "marriage", "wedding", "breakup", "love"],
            "school": ["school", "study", "exam", "homework", "teacher", "student", "university", "college", "grade"],
            "finance": ["money", "budget", "expensive", "cheap", "buy", "sell", "invest", "bank", "loan", "debt"],
            "travel": ["travel", "trip", "vacation", "flight", "hotel", "destination", "vacation", "holiday"],
            "technology": ["computer", "phone", "app", "software", "internet", "website", "bug", "update", "install"]
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            "very": 1.5,
            "really": 1.4,
            "extremely": 2.0,
            "super": 1.6,
            "incredibly": 1.8,
            "absolutely": 1.7,
            "totally": 1.5,
            "completely": 1.8,
            "so": 1.3,
            "quite": 1.2,
            "rather": 1.1,
            "somewhat": 0.8,
            "slightly": 0.6,
            "a bit": 0.7,
            "a little": 0.7
        }
    
    def detect_mood(self, text: str, conversation_history: List[str] = None) -> Dict[str, Any]:
        """Detect mood from text with confidence scores."""
        text_lower = text.lower()
        detected_emotions = {}
        
        # Analyze each emotion
        for emotion, indicators in self.emotion_patterns.items():
            score = 0.0
            matches = []
            
            # Check keywords
            for keyword in indicators["keywords"]:
                if keyword in text_lower:
                    base_score = 1.0
                    # Apply intensity modifiers
                    for modifier, multiplier in self.intensity_modifiers.items():
                        if modifier in text_lower and keyword in text_lower:
                            base_score *= multiplier
                            break
                    
                    score += base_score
                    matches.append(f"keyword: {keyword}")
            
            # Check indicators (emojis, punctuation)
            for indicator in indicators["indicators"]:
                if indicator in text:
                    score += 0.8
                    matches.append(f"indicator: {indicator}")
            
            # Check patterns
            for pattern in indicators["patterns"]:
                if re.search(pattern, text_lower):
                    score += 1.2
                    matches.append(f"pattern: {pattern}")
            
            if score > 0:
                detected_emotions[emotion] = {
                    "score": score,
                    "confidence": min(score / 3.0, 1.0),  # Normalize to 0-1
                    "matches": matches
                }
        
        # Consider conversation history for context
        if conversation_history:
            historical_context = self._analyze_conversation_trend(conversation_history)
            for emotion in detected_emotions:
                if emotion in historical_context:
                    detected_emotions[emotion]["score"] *= 1.2
                    detected_emotions[emotion]["confidence"] = min(detected_emotions[emotion]["confidence"] * 1.1, 1.0)
        
        # Determine primary emotion
        primary_emotion = None
        primary_score = 0
        
        if detected_emotions:
            primary_emotion = max(detected_emotions.keys(), key=lambda e: detected_emotions[e]["score"])
            primary_score = detected_emotions[primary_emotion]["score"]
        
        return {
            "primary_emotion": primary_emotion,
            "primary_confidence": detected_emotions.get(primary_emotion, {}).get("confidence", 0),
            "all_emotions": detected_emotions,
            "emotion_intensity": self._classify_intensity(primary_score),
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }
    
    def detect_context(self, text: str) -> Dict[str, Any]:
        """Detect conversation context and topics."""
        text_lower = text.lower()
        detected_contexts = {}
        
        for context, keywords in self.context_patterns.items():
            score = 0
            matches = []
            
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
                    matches.append(keyword)
            
            if score > 0:
                detected_contexts[context] = {
                    "score": score,
                    "confidence": min(score / 3.0, 1.0),
                    "keywords": matches
                }
        
        # Determine primary context
        primary_context = None
        if detected_contexts:
            primary_context = max(detected_contexts.keys(), key=lambda c: detected_contexts[c]["score"])
        
        return {
            "primary_context": primary_context,
            "all_contexts": detected_contexts,
            "context_confidence": detected_contexts.get(primary_context, {}).get("confidence", 0),
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }
    
    def _analyze_conversation_trend(self, conversation_history: List[str]) -> Dict[str, float]:
        """Analyze emotional trends in conversation history."""
        emotion_counts = defaultdict(int)
        
        for message in conversation_history[-5:]:  # Last 5 messages
            mood_result = self.detect_mood(message)
            if mood_result["primary_emotion"]:
                emotion_counts[mood_result["primary_emotion"]] += 1
        
        # Convert to normalized scores
        total = sum(emotion_counts.values())
        if total > 0:
            return {emotion: count / total for emotion, count in emotion_counts.items()}
        
        return {}
    
    def _classify_intensity(self, score: float) -> str:
        """Classify emotion intensity based on score."""
        if score >= 3.0:
            return "very_high"
        elif score >= 2.0:
            return "high"
        elif score >= 1.0:
            return "medium"
        elif score >= 0.5:
            return "low"
        else:
            return "very_low"
    
    def suggest_response_approach(self, mood_result: Dict[str, Any], context_result: Dict[str, Any]) -> Dict[str, str]:
        """Suggest how to respond based on detected mood and context."""
        primary_emotion = mood_result.get("primary_emotion")
        primary_context = context_result.get("primary_context")
        intensity = mood_result.get("emotion_intensity", "medium")
        
        approach = {
            "tone": "neutral",
            "length": "medium",
            "style": "supportive",
            "focus": "balanced"
        }
        
        # Adjust based on emotion
        if primary_emotion == "happy":
            approach.update({
                "tone": "enthusiastic",
                "style": "celebratory",
                "focus": "positive_reinforcement"
            })
        elif primary_emotion == "sad":
            approach.update({
                "tone": "gentle",
                "style": "empathetic",
                "focus": "emotional_support"
            })
        elif primary_emotion == "angry":
            approach.update({
                "tone": "calm",
                "style": "understanding",
                "focus": "de_escalation"
            })
        elif primary_emotion == "anxious":
            approach.update({
                "tone": "reassuring",
                "style": "calming",
                "focus": "problem_solving"
            })
        elif primary_emotion == "excited":
            approach.update({
                "tone": "enthusiastic",
                "style": "energetic",
                "focus": "encouragement"
            })
        elif primary_emotion == "confused":
            approach.update({
                "tone": "patient",
                "style": "explanatory",
                "focus": "clarification"
            })
        elif primary_emotion == "tired":
            approach.update({
                "tone": "gentle",
                "length": "short",
                "style": "considerate",
                "focus": "efficiency"
            })
        elif primary_emotion == "grateful":
            approach.update({
                "tone": "warm",
                "style": "humble",
                "focus": "acknowledgment"
            })
        
        # Adjust based on context
        if primary_context == "work":
            approach["style"] = "professional"
            if primary_emotion in ["stressed", "anxious"]:
                approach["focus"] = "stress_management"
        elif primary_context == "family":
            approach["style"] = "personal"
            approach["tone"] = "caring"
        elif primary_context == "health":
            approach["style"] = "concerned"
            approach["focus"] = "supportive_guidance"
        
        # Adjust based on intensity
        if intensity in ["very_high", "high"]:
            approach["length"] = "short"  # Don't overwhelm with long responses
            if primary_emotion in ["angry", "sad", "anxious"]:
                approach["tone"] = "very_gentle"
        
        return approach


class ContextualResponseGenerator:
    """Generates contextually and emotionally appropriate responses."""
    
    def __init__(self, mood_detector: MoodDetector):
        self.mood_detector = mood_detector
        
        # Response templates for different moods
        self.response_templates = {
            "happy": {
                "acknowledgment": [
                    "I'm so glad to hear you're feeling great!",
                    "That's wonderful! Your happiness is contagious!",
                    "I love hearing such positive energy!",
                    "That's fantastic! Keep that amazing spirit up!"
                ],
                "continuation": [
                    "What's making you so happy today?",
                    "I'd love to help you keep this momentum going!",
                    "How can I help make your day even better?"
                ]
            },
            "sad": {
                "acknowledgment": [
                    "I'm sorry you're feeling down. I'm here for you.",
                    "It sounds like you're going through a tough time.",
                    "I understand that things feel difficult right now.",
                    "Thank you for sharing how you're feeling with me."
                ],
                "continuation": [
                    "Would you like to talk about what's bothering you?",
                    "Is there anything I can do to help brighten your day?",
                    "Sometimes it helps to focus on small positive things. Shall we try that?"
                ]
            },
            "angry": {
                "acknowledgment": [
                    "I can hear that you're really frustrated.",
                    "It sounds like something has really upset you.",
                    "I understand you're angry about this situation.",
                    "Your feelings are completely valid."
                ],
                "continuation": [
                    "Would it help to talk through what happened?",
                    "Let's see if we can find a way to address this issue.",
                    "Take a deep breath. I'm here to help however I can."
                ]
            },
            "anxious": {
                "acknowledgment": [
                    "I can sense you're feeling worried about this.",
                    "It's completely normal to feel anxious sometimes.",
                    "I understand this situation is causing you stress.",
                    "Your concerns are important and valid."
                ],
                "continuation": [
                    "Let's break this down into manageable pieces.",
                    "Would some practical steps help ease your worry?",
                    "Remember, we can tackle this one step at a time."
                ]
            },
            "excited": {
                "acknowledgment": [
                    "Your excitement is absolutely infectious!",
                    "I love how enthusiastic you are about this!",
                    "This energy is amazing! I'm excited too!",
                    "What an incredible thing to be excited about!"
                ],
                "continuation": [
                    "Tell me more about what has you so pumped!",
                    "How can I help you with this exciting venture?",
                    "I'd love to help you make the most of this opportunity!"
                ]
            },
            "confused": {
                "acknowledgment": [
                    "I can see this is confusing for you.",
                    "Let's clear this up together.",
                    "No worries, confusion is totally normal with complex topics.",
                    "I'm here to help make sense of this."
                ],
                "continuation": [
                    "Let me explain this in a different way.",
                    "What specific part would you like me to clarify?",
                    "We'll go through this step by step until it clicks."
                ]
            },
            "tired": {
                "acknowledgment": [
                    "You sound exhausted. Rest is so important.",
                    "I can tell you're really tired.",
                    "It sounds like you need some self-care time.",
                    "Fatigue can be really challenging."
                ],
                "continuation": [
                    "Would you like some quick help so you can rest sooner?",
                    "Let me keep this brief and efficient for you.",
                    "Maybe we should tackle this when you're more rested?"
                ]
            },
            "grateful": {
                "acknowledgment": [
                    "It's my pleasure to help you!",
                    "Your gratitude means the world to me!",
                    "I'm so glad I could be helpful!",
                    "Thank you for being so kind and appreciative!"
                ],
                "continuation": [
                    "Is there anything else I can assist you with?",
                    "I'm always here whenever you need help!",
                    "Your positivity makes helping you a joy!"
                ]
            }
        }
    
    def generate_contextual_response(self, user_input: str, base_response: str, 
                                   conversation_history: List[str] = None) -> str:
        """Generate a contextually and emotionally appropriate response."""
        
        # Detect mood and context
        mood_result = self.mood_detector.detect_mood(user_input, conversation_history)
        context_result = self.mood_detector.detect_context(user_input)
        
        # Get response approach
        approach = self.mood_detector.suggest_response_approach(mood_result, context_result)
        
        # Generate emotional acknowledgment if needed
        emotional_intro = self._generate_emotional_intro(mood_result, approach)
        
        # Modify base response tone
        modified_response = self._adjust_response_tone(base_response, approach)
        
        # Add contextual elements
        contextual_addition = self._add_contextual_elements(context_result, approach)
        
        # Combine elements
        final_response_parts = []
        
        if emotional_intro:
            final_response_parts.append(emotional_intro)
        
        final_response_parts.append(modified_response)
        
        if contextual_addition:
            final_response_parts.append(contextual_addition)
        
        final_response = " ".join(final_response_parts)
        
        # Apply length adjustment
        if approach["length"] == "short":
            final_response = self._shorten_response(final_response)
        elif approach["length"] == "long":
            final_response = self._expand_response(final_response, mood_result, context_result)
        
        return final_response
    
    def _generate_emotional_intro(self, mood_result: Dict[str, Any], approach: Dict[str, str]) -> str:
        """Generate an emotional acknowledgment intro."""
        primary_emotion = mood_result.get("primary_emotion")
        confidence = mood_result.get("primary_confidence", 0)
        
        # Only add emotional intro if confidence is high enough
        if confidence < 0.6 or not primary_emotion:
            return ""
        
        if primary_emotion in self.response_templates:
            templates = self.response_templates[primary_emotion]["acknowledgment"]
            # Choose template based on approach tone
            if approach["tone"] == "gentle":
                return templates[0]  # Usually the most gentle option
            elif approach["tone"] == "enthusiastic":
                return templates[-1]  # Usually the most energetic option
            else:
                return templates[1]  # Middle ground
        
        return ""
    
    def _adjust_response_tone(self, response: str, approach: Dict[str, str]) -> str:
        """Adjust the tone of the base response."""
        tone = approach["tone"]
        style = approach["style"]
        
        # Simple tone adjustments (in a real implementation, you'd use more sophisticated NLP)
        if tone == "gentle":
            # Add softening words
            response = re.sub(r'^([A-Z])', r'Gently, \\1', response)
            response = response.replace("You should", "You might want to")
            response = response.replace("You need to", "It might help to")
        
        elif tone == "enthusiastic":
            # Add energy
            if not response.endswith('!'):
                response += "!"
            response = response.replace("good", "great")
            response = response.replace("okay", "fantastic")
        
        elif tone == "calm":
            # Remove exclamation marks, add calming language
            response = response.replace("!", ".")
            response = "Let's take this step by step. " + response
        
        elif tone == "reassuring":
            # Add reassuring phrases
            response = "Don't worry, " + response.lower()
            response = response.replace(".", ". Everything will be okay.")
        
        return response
    
    def _add_contextual_elements(self, context_result: Dict[str, Any], approach: Dict[str, str]) -> str:
        """Add context-specific elements to the response."""
        primary_context = context_result.get("primary_context")
        focus = approach["focus"]
        
        contextual_additions = {
            "work": {
                "stress_management": "Remember to take breaks and prioritize your well-being at work.",
                "problem_solving": "Let's think about this professionally and systematically.",
                "supportive": "Work challenges are opportunities to grow and learn."
            },
            "family": {
                "emotional_support": "Family relationships can be complex, but they're so important.",
                "problem_solving": "Family matters often require patience and understanding.",
                "supportive": "Your family is lucky to have someone who cares so much."
            },
            "health": {
                "supportive_guidance": "Your health is the most important priority.",
                "emotional_support": "Health concerns can be really stressful, but you're taking the right steps.",
                "problem_solving": "Let's approach this health matter thoughtfully and carefully."
            }
        }
        
        if primary_context and primary_context in contextual_additions:
            if focus in contextual_additions[primary_context]:
                return contextual_additions[primary_context][focus]
        
        return ""
    
    def _shorten_response(self, response: str) -> str:
        """Shorten a response while keeping key information."""
        sentences = response.split('. ')
        if len(sentences) > 2:
            # Keep first and last sentence
            return f"{sentences[0]}. {sentences[-1]}"
        return response
    
    def _expand_response(self, response: str, mood_result: Dict[str, Any], context_result: Dict[str, Any]) -> str:
        """Expand a response with additional supportive content."""
        primary_emotion = mood_result.get("primary_emotion")
        
        if primary_emotion and primary_emotion in self.response_templates:
            continuation_options = self.response_templates[primary_emotion]["continuation"]
            continuation = continuation_options[0]  # Choose first option
            return f"{response} {continuation}"
        
        return response
    
    def get_mood_summary(self, conversation_history: List[str]) -> Dict[str, Any]:
        """Get a summary of mood patterns in conversation history."""
        mood_timeline = []
        emotion_counts = Counter()
        
        for i, message in enumerate(conversation_history):
            mood_result = self.mood_detector.detect_mood(message)
            if mood_result["primary_emotion"]:
                mood_timeline.append({
                    "message_index": i,
                    "emotion": mood_result["primary_emotion"],
                    "confidence": mood_result["primary_confidence"],
                    "intensity": mood_result["emotion_intensity"]
                })
                emotion_counts[mood_result["primary_emotion"]] += 1
        
        # Calculate mood stability
        mood_changes = 0
        for i in range(1, len(mood_timeline)):
            if mood_timeline[i]["emotion"] != mood_timeline[i-1]["emotion"]:
                mood_changes += 1
        
        stability = "stable" if mood_changes <= len(mood_timeline) * 0.3 else "variable"
        
        return {
            "mood_timeline": mood_timeline,
            "dominant_emotions": emotion_counts.most_common(3),
            "mood_stability": stability,
            "total_messages_analyzed": len(conversation_history),
            "emotional_messages": len(mood_timeline)
        }
