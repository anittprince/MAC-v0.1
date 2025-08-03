"""
MAC Assistant - Command Processor Brain
Processes natural language commands and routes them to appropriate handlers.
Enhanced with personalization, memory, and learning capabilities.
"""

import re
import platform
from typing import Dict, Any, Optional
from commands.windows import WindowsCommands
from commands.android import AndroidCommands
from .ai_services import AIServices
from .personalization import UserProfile, PersonalAssi        # Always execute these system commands
        execute_types = ['time', 'weather', 'system_info']
        
        return command_type in execute_types
    
    # ========== ENHANCED PERSONALIZATION METHODS ==========
    
    def _check_custom_commands(self, text: str) -> Optional[Dict[str, Any]]:
        """Check if the text matches any custom commands."""
        # Simple matching for now - could be enhanced with fuzzy matching
        text_lower = text.lower()
        
        # Look for exact name matches first
        for command_name in self.custom_commands.commands:
            if command_name.lower() in text_lower:
                result = self.custom_commands.execute_command(command_name)
                return result
        
        # Look for command aliases or keywords
        # This could be enhanced to search descriptions, tags, etc.
        search_results = self.custom_commands.search_commands(text)
        if search_results:
            # Execute the first match
            command_name = search_results[0]["name"]
            result = self.custom_commands.execute_command(command_name)
            return result
        
        return None
    
    def _handle_ai_primary_enhanced(self, original_text: str, command_type: Optional[str], lower_text: str) -> Dict[str, Any]:
        """Handle AI processing with enhanced personalization and memory."""
        try:
            # Build enhanced context with personalization
            base_context = self._build_system_context(command_type)
            
            # Add user profile context
            user_context = self.user_profile.get_context_for_ai()
            
            # Add conversation memory context
            conversation_context = self.conversation_memory.get_context_for_ai()
            
            # Enhance prompt with learning engine
            enhanced_prompt = self.personalized_response.personalize_response_prompt(
                base_context, original_text
            )
            
            # Combine all contexts
            full_context = f"{enhanced_prompt}\n\nUser Profile:\n{user_context}\n\nConversation Context:\n{conversation_context}"
            
            # Get adaptive suggestions
            suggestions = self.learning_engine.get_adaptive_suggestions(original_text)
            if suggestions:
                full_context += f"\n\nRelevant suggestions to consider offering:\n" + "\n".join(suggestions)
            
            # Use smart response generator for context-aware prompting
            final_prompt = self.smart_response.enhance_ai_prompt(original_text, full_context)
            
            # Get AI response with enhanced context
            result = self.ai_services.ask_ai(final_prompt)
            
            if result['success']:
                ai_source = 'Gemini AI (Enhanced)'
                
                # Check if we should also execute system commands
                if self._should_execute_system_command(result['message'], command_type):
                    system_result = self._execute_command(command_type, lower_text)
                    
                    if system_result and 'message' in system_result:
                        # Combine AI response with system data
                        combined_message = f"{result['message']}\n\n{system_result['message']}"
                        return {
                            'status': 'success',
                            'message': combined_message,
                            'data': {
                                'ai_response': result['message'],
                                'system_result': system_result.get('data'),
                                'source': f'{ai_source} + System',
                                'suggestions': suggestions[:3] if suggestions else []
                            }
                        }
                else:
                    # Pure AI response with suggestions
                    return {
                        'status': 'success',
                        'message': result['message'],
                        'data': {
                            'source': ai_source,
                            'suggestions': suggestions[:3] if suggestions else [],
                            'conversation_summary': self.conversation_memory.get_conversation_summary()
                        }
                    }
            else:
                # AI failed, fallback to traditional processing
                return self._handle_traditional_processing(command_type, lower_text)
                
        except Exception as e:
            # Error with AI, fallback to traditional processing
            return self._handle_traditional_processing(command_type, lower_text)
    
    def _learn_from_interaction(self, user_input: str, ai_response: str, success: bool, user_feedback: str = None):
        """Learn from user interactions."""
        try:
            # Update command usage in user profile
            command_type = self._identify_command_type(user_input.lower())
            if command_type:
                self.user_profile.learn_command_usage(command_type)
            
            # Learn patterns in learning engine
            self.learning_engine.learn_from_interaction(user_input, ai_response, success, user_feedback)
            
        except Exception as e:
            print(f"Error in learning from interaction: {e}")
    
    def _save_conversation(self, user_input: str, ai_response: str, metadata: Dict[str, Any] = None):
        """Save conversation to memory systems."""
        try:
            # Save to user profile conversation history
            self.user_profile.add_conversation(user_input, ai_response, metadata)
            
            # Save to conversation memory for context tracking
            self.conversation_memory.add_exchange(user_input, ai_response, metadata)
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def get_personalization_status(self) -> Dict[str, Any]:
        """Get status of personalization features."""
        try:
            return {
                "user_name": self.user_profile.get_name(),
                "total_interactions": self.interaction_count,
                "conversation_summary": self.conversation_memory.get_conversation_summary(),
                "learning_insights": self.learning_engine.get_learning_insights(),
                "custom_commands_count": len(self.custom_commands.commands),
                "active_reminders": len(self.user_profile.get_active_reminders()),
                "response_style": self.user_profile.get_response_style(),
                "most_used_commands": self.user_profile.get_most_used_commands(5)
            }
        except Exception as e:
            return {"error": f"Error getting personalization status: {e}"}
    
    def handle_user_feedback(self, feedback: str, context: Dict[str, Any] = None):
        """Handle explicit user feedback for learning."""
        try:
            # Extract feedback type
            feedback_lower = feedback.lower()
            
            if any(word in feedback_lower for word in ["too long", "verbose", "brief"]):
                self.learning_engine.adapt_to_user_feedback("too_verbose", context or {})
            elif any(word in feedback_lower for word in ["too short", "more detail"]):
                self.learning_engine.adapt_to_user_feedback("too_brief", context or {})
            elif any(word in feedback_lower for word in ["too formal", "casual"]):
                self.learning_engine.adapt_to_user_feedback("too_formal", context or {})
            elif any(word in feedback_lower for word in ["too casual", "formal"]):
                self.learning_engine.adapt_to_user_feedback("too_casual", context or {})
            
            return {
                "status": "success",
                "message": "Thank you for the feedback! I'll adapt my responses accordingly."
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing feedback: {e}"
            }
    
    def create_custom_command(self, name: str, command_type: str, definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new custom command."""
        try:
            success = self.custom_commands.create_command(name, command_type, definition)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Custom command '{name}' created successfully!",
                    "data": {"command_name": name, "command_type": command_type}
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to create command '{name}'. It may already exist or have invalid definition."
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error creating custom command: {e}"
            }
    
    def get_personalized_suggestions(self, context: str = "") -> List[str]:
        """Get personalized suggestions for the user."""
        try:
            # Get suggestions from learning engine
            suggestions = self.learning_engine.get_adaptive_suggestions(context)
            
            # Add conversation-based suggestions
            follow_up = self.conversation_memory.get_relevant_follow_up()
            if follow_up:
                suggestions.append(follow_up)
            
            # Add reminder suggestions if there are active reminders
            active_reminders = self.user_profile.get_active_reminders()
            if active_reminders:
                suggestions.append(f"You have {len(active_reminders)} pending reminders. Would you like to review them?")
            
            # Add time-based suggestions
            import datetime
            current_hour = datetime.datetime.now().hour
            
            if 6 <= current_hour < 12:
                suggestions.append("Good morning! Would you like me to check today's weather?")
            elif 17 <= current_hour < 22:
                suggestions.append("Would you like me to help you plan tomorrow?")
            
            return suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            return [f"Error getting suggestions: {e}"]
    
    def export_personalization_data(self, filepath: str) -> Dict[str, Any]:
        """Export all personalization data."""
        try:
            # Export custom commands
            commands_result = self.custom_commands.export_commands(f"{filepath}_commands.json")
            
            # Export user profile data (this would need implementation in UserProfile)
            # For now, just return success
            
            return {
                "status": "success",
                "message": f"Personalization data exported successfully",
                "files": [f"{filepath}_commands.json"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error exporting data: {e}"
            }
    
    def clear_session_memory(self):
        """Clear current session memory."""
        try:
            self.conversation_memory.clear_session()
            self.interaction_count = 0
            
            return {
                "status": "success",
                "message": "Session memory cleared. Starting fresh!"
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error clearing session: {e}"
            }t
from .conversation_memory import ConversationMemory, SmartResponseGenerator
from .learning_engine import LearningEngine, PersonalizedResponseGenerator
from .custom_commands import CustomCommandManager


class MACBrain:
    def __init__(self):
        self.platform = platform.system().lower()
        self.commands = self._initialize_commands()
        self.ai_services = AIServices()
        
        # Initialize personalization components
        self.user_profile = UserProfile()
        self.personal_assistant = PersonalAssistant(self.user_profile)
        self.conversation_memory = ConversationMemory()
        self.smart_response = SmartResponseGenerator(self.conversation_memory)
        self.learning_engine = LearningEngine()
        self.personalized_response = PersonalizedResponseGenerator(self.learning_engine)
        self.custom_commands = CustomCommandManager()
        
        # Session tracking
        self.session_active = True
        self.interaction_count = 0
        
        # Common command patterns
        self.command_patterns = {
            'greeting': [
                r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bgood morning\b', r'\bgood afternoon\b', r'\bgood evening\b'
            ],
            'time': [
                r'what.*time', r'current time', r'tell me.*time', r'time now', 
                r'what.*is.*time', r'show time', r'get time', r'check time',
                r'whats.*time', r'time is', r'give.*time'
            ],
            'weather': [
                r'weather', r'temperature', r'forecast'
            ],
            'search': [
                r'search for', r'look up', r'find information', r'google search', r'web search',
                r'search google', r'what is', r'who is', r'where is', r'how to', r'why',
                r'tell me about', r'explain', r'define'
            ],
            'youtube': [
                r'youtube', r'find.*video', r'search.*video', r'video.*about', r'watch.*video',
                r'video.*tutorial', r'youtube.*search', r'look.*video'
            ],
            'ai_question': [
                r'ask ai', r'chatgpt', r'artificial intelligence', r'ai question'
            ],
            'system_info': [
                r'system info', r'computer info', r'device info', r'system status'
            ],
            'file_operations': [
                r'open file', r'create file', r'delete file', r'list files', r'find file'
            ],
            'applications': [
                r'open app', r'close app', r'launch', r'start program', r'run application'
            ],
            'network': [
                r'network status', r'wifi', r'internet connection', r'ip address'
            ],
            'volume': [
                r'volume up', r'volume down', r'mute', r'unmute', r'set volume',
                r'increase volume', r'decrease volume', r'turn up volume', r'turn down volume',
                r'what is the volume', r'current volume', r'volume status', r'sound up', r'sound down',
                r'turn up.*volume', r'turn down.*volume', r'raise.*volume', r'lower.*volume'
            ],
            'shutdown': [
                r'shutdown', r'restart', r'reboot', r'power off', r'sleep'
            ]
        }
    
    def _initialize_commands(self):
        """Initialize platform-specific command handlers."""
        if self.platform == 'windows':
            return WindowsCommands()
        elif self.platform == 'android':
            return AndroidCommands()
        else:
            # Fallback to Windows commands for unknown platforms
            return WindowsCommands()
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process a text command and return appropriate response.
        Enhanced with personalization, memory, and learning capabilities.
        
        Args:
            text (str): The command text to process
            
        Returns:
            Dict[str, Any]: Response containing status, message, and optional data
        """
        if not text or not text.strip():
            return {
                'status': 'error',
                'message': 'No command provided',
                'data': None
            }
        
        original_text = text.strip()
        text = text.lower().strip()
        self.interaction_count += 1
        
        try:
            # First, check for personalized commands
            personal_result = self.personal_assistant.process_personalized_command(original_text)
            if personal_result:
                self._learn_from_interaction(original_text, personal_result['message'], True)
                self._save_conversation(original_text, personal_result['message'])
                return personal_result
            
            # Check for custom commands
            custom_result = self._check_custom_commands(original_text)
            if custom_result:
                self._learn_from_interaction(original_text, custom_result['message'], 
                                           custom_result['status'] == 'success')
                self._save_conversation(original_text, custom_result['message'])
                return custom_result
            
            # Identify command type for traditional processing
            command_type = self._identify_command_type(text)
            
            # Check if this is a critical system command that should bypass AI
            critical_commands = self._get_critical_commands()
            
            if command_type in critical_commands:
                # Handle critical system commands directly
                result = self._handle_system_command(command_type, text)
                self._learn_from_interaction(original_text, result['message'], 
                                           result['status'] == 'success')
                self._save_conversation(original_text, result['message'])
                return result
            
            # For all other commands, try AI with enhanced context
            if self.ai_services.is_ai_available():
                result = self._handle_ai_primary_enhanced(original_text, command_type, text)
                self._learn_from_interaction(original_text, result['message'], 
                                           result['status'] == 'success')
                self._save_conversation(original_text, result['message'])
                return result
            else:
                # Fallback to traditional pattern matching if AI unavailable
                result = self._handle_traditional_processing(command_type, text)
                self._learn_from_interaction(original_text, result['message'], 
                                           result['status'] == 'success')
                self._save_conversation(original_text, result['message'])
                return result
                
        except Exception as e:
            error_result = {
                'status': 'error',
                'message': f"Error processing command: {str(e)}",
                'data': None
            }
            self._learn_from_interaction(original_text, error_result['message'], False)
            return error_result
    
    def _identify_command_type(self, text: str) -> Optional[str]:
        """Identify the type of command based on text patterns."""
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return command_type
        return None
    
    def _execute_command(self, command_type: str, text: str) -> Dict[str, Any]:
        """Execute the identified command."""
        method_name = f"handle_{command_type}"
        
        if hasattr(self.commands, method_name):
            method = getattr(self.commands, method_name)
            return method(text)
        else:
            return {
                'message': f"Command type '{command_type}' not implemented for {self.platform}",
                'data': None
            }
    
    def get_available_commands(self) -> Dict[str, list]:
        """Return available command patterns."""
        return self.command_patterns
    
    def get_platform_info(self) -> Dict[str, str]:
        """Return current platform information."""
        return {
            'platform': self.platform,
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    
    def _handle_ai_command(self, command_type: str, text: str) -> Dict[str, Any]:
        """Handle AI-powered commands like search, YouTube, etc."""
        try:
            if command_type == 'search':
                # Extract search query
                query = self._extract_search_query(text)
                if query:
                    result = self.ai_services.search_google(query)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result['data']
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Please specify what you want to search for.',
                        'data': None
                    }
            
            elif command_type == 'youtube':
                # Extract YouTube search query
                query = self._extract_youtube_query(text)
                if query:
                    result = self.ai_services.search_youtube(query)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result['data']
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Please specify what video you want to find.',
                        'data': None
                    }
            
            elif command_type == 'ai_question':
                # Direct AI question
                result = self.ai_services.ask_chatgpt(text)
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result['data']
                }
            
            else:
                return {
                    'status': 'error',
                    'message': f"AI command type '{command_type}' not implemented",
                    'data': None
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"AI service error: {str(e)}",
                'data': None
            }
    
    def _handle_ai_fallback(self, text: str) -> Dict[str, Any]:
        """Handle unrecognized commands using AI as fallback."""
        try:
            # Check if AI services are available
            if self.ai_services.is_ai_available():
                # Ask AI to handle the question
                context = "You are a voice assistant. The user said something that doesn't match predefined commands."
                result = self.ai_services.ask_ai(text, context)
                
                return {
                    'status': 'success' if result['success'] else 'ai_fallback',
                    'message': result['message'],
                    'data': result['data']
                }
            else:
                # Try web search as fallback
                result = self.ai_services.search_google(text)
                
                if result['success']:
                    return {
                        'status': 'ai_fallback',
                        'message': f"I searched for that and found: {result['message']}",
                        'data': result['data']
                    }
                else:
                    return {
                        'status': 'unknown',
                        'message': f"I don't understand '{text}'. Try asking me a specific question or use commands like 'what time is it' or 'search for [topic]'.",
                        'data': None
                    }
                    
        except Exception as e:
            return {
                'status': 'error',
                'message': f"I couldn't process that request: {str(e)}",
                'data': None
            }
    
    def _extract_search_query(self, text: str) -> Optional[str]:
        """Extract search query from text."""
        # Remove common search prefixes
        patterns = [
            r'search for (.+)',
            r'look up (.+)',
            r'google search (.+)',
            r'web search (.+)',
            r'search google for (.+)',
            r'find information about (.+)',
            r'what is (.+)',
            r'who is (.+)',
            r'where is (.+)',
            r'how to (.+)',
            r'why (.+)',
            r'tell me about (.+)',
            r'explain (.+)',
            r'define (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, return the whole text
        return text.strip()
    
    def _extract_youtube_query(self, text: str) -> Optional[str]:
        """Extract YouTube search query from text."""
        patterns = [
            r'youtube (.+)',
            r'find.*video.*about (.+)',
            r'search.*video (.+)',
            r'video.*about (.+)',
            r'watch.*video (.+)',
            r'find (.+) video',
            r'search for (.+) on youtube',
            r'youtube (.+) tutorial',
            r'(.+) tutorial.*youtube',
            r'video.*tutorial.*(.+)',
            r'(.+) video tutorial'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If text contains "youtube" and other words, extract the non-youtube part
        if 'youtube' in text.lower():
            words = text.lower().split()
            youtube_words = ['youtube', 'video', 'watch', 'find', 'search']
            query_words = [word for word in words if word not in youtube_words]
            if query_words:
                return ' '.join(query_words)
        
        # If no pattern matches, return the whole text
        return text.strip()
    
    def get_ai_status(self) -> Dict[str, bool]:
        """Get the status of AI services."""
        return {
            'gemini_available': self.ai_services.gemini_model is not None,
            'ai_available': self.ai_services.is_ai_available()
        }
    
    def _get_critical_commands(self) -> list:
        """Get list of critical system commands that should bypass AI."""
        return ['volume', 'shutdown', 'system_info']
    
    def _handle_ai_primary(self, original_text: str, command_type: str, lower_text: str) -> Dict[str, Any]:
        """Handle command with AI (Gemini) as primary processor."""
        try:
            # Create context for AI about available system functions
            system_context = self._build_system_context(command_type)
            
            # Ask AI to process the command
            result = self.ai_services.ask_ai(original_text, system_context)
            
            if result['success']:
                # Check if AI indicated this needs system function execution
                response_data = result.get('data', {})
                ai_source = response_data.get('source', 'AI')
                
                # If AI suggests a system command, execute it
                if command_type and self._should_execute_system_command(result['message'], command_type):
                    system_result = self._execute_command(command_type, lower_text)
                    
                    # Combine AI response with system execution
                    combined_message = f"{result['message']}\n\nSystem: {system_result.get('message', 'Command executed')}"
                    
                    return {
                        'status': 'success',
                        'message': combined_message,
                        'data': {
                            'ai_response': result['message'],
                            'system_result': system_result.get('data'),
                            'source': f'{ai_source} + System'
                        }
                    }
                else:
                    # Pure AI response
                    return {
                        'status': 'success',
                        'message': result['message'],
                        'data': {
                            'source': ai_source
                        }
                    }
            else:
                # AI failed, fallback to traditional processing
                return self._handle_traditional_processing(command_type, lower_text)
                
        except Exception as e:
            # Error with AI, fallback to traditional processing
            return self._handle_traditional_processing(command_type, lower_text)
    
    def _build_system_context(self, command_type: str) -> str:
        """Build context for ChatGPT about available system functions."""
        context = """You are MAC, a voice assistant with access to system functions. 
        
Available system functions:
- Time queries: Can get current time and date
- System information: Can check CPU, memory, disk usage
- Volume control: Can adjust system volume
- Weather information: Can get weather data (if configured)
- Web search: Can search for information online
- YouTube search: Can find videos

Respond naturally and conversationally. If the user asks for system information like time, weather, or wants to control volume, mention that you're checking or adjusting it for them.

Keep responses concise (under 100 words) for voice interaction."""
        
        if command_type:
            context += f"\n\nThe user's request seems related to: {command_type}"
        
        return context
    
    def _should_execute_system_command(self, chatgpt_response: str, command_type: str) -> bool:
        """Determine if we should execute a system command based on ChatGPT response and command type."""
        if not command_type:
            return False
            
        # Always execute these system commands
        execute_types = ['time', 'weather', 'system_info']
        
        if command_type in execute_types:
            return True
            
        # Check if ChatGPT response suggests system execution
        execution_keywords = ['let me check', 'checking', 'getting', 'finding', 'searching']
        response_lower = chatgpt_response.lower()
        
        return any(keyword in response_lower for keyword in execution_keywords)
    
    def _handle_system_command(self, command_type: str, text: str) -> Dict[str, Any]:
        """Handle critical system commands directly without ChatGPT."""
        try:
            result = self._execute_command(command_type, text)
            return {
                'status': 'success',
                'message': result.get('message', 'Command executed successfully'),
                'data': result.get('data', None)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"System command error: {str(e)}",
                'data': None
            }
    
    def _handle_traditional_processing(self, command_type: str, text: str) -> Dict[str, Any]:
        """Handle commands using traditional pattern matching (fallback mode)."""
        try:
            if command_type:
                # Handle AI-powered commands
                if command_type in ['search', 'youtube', 'ai_question']:
                    return self._handle_ai_command(command_type, text)
                else:
                    # Handle traditional commands
                    result = self._execute_command(command_type, text)
                    return {
                        'status': 'success',
                        'message': result.get('message', 'Command executed successfully'),
                        'data': result.get('data', None)
                    }
            else:
                # If no pattern matches, try AI fallback
                return self._handle_ai_fallback(text)
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Processing error: {str(e)}",
                'data': None
            }
