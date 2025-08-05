"""
MAC Assistant - Enhanced Command Processor Brain
Processes natural language commands with personalization, memory, and learning.
"""

import re
import platform
from typing import Dict, Any, Optional, List
from commands.windows import WindowsCommands
from commands.android import AndroidCommands
# Clean module imports for JARVIS-level capabilities
from .ai_services import AIServices
from .personalization import UserProfile, PersonalAssistant
from .conversation_memory import ConversationMemory, SmartResponseGenerator
from .learning_engine import LearningEngine, PersonalizedResponseGenerator
from .custom_commands import CustomCommandManager
from .calendar_manager import CalendarManager
from .web_services import WebServicesManager
from .automation_engine import AutomationEngine
from .advanced_ai import AdvancedAIModule
from .enterprise_integration import EnterpriseIntegration
from .smart_environment import SmartEnvironmentManager
from .mobile_companion import MobileCompanionManager
from .vision_ai import VisionAIManager
from .multi_language import MultiLanguageManager
from .financial_advisor import FinancialAdvisorAgent
from .web_dashboard import WebDashboardManager


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
        
        # Initialize new advanced features
        self.calendar_manager = CalendarManager()
        self.web_services = WebServicesManager()
        self.automation_engine = AutomationEngine()
        
        # Initialize next-generation advanced features
        self.advanced_ai = AdvancedAIModule()
        self.enterprise_integration = EnterpriseIntegration()
        self.smart_environment = SmartEnvironmentManager()
        self.mobile_companion = MobileCompanionManager()
        self.vision_ai = VisionAIManager()
        self.multi_language = MultiLanguageManager()
        self.financial_advisor = FinancialAdvisorAgent()
        
        # Web dashboard - temporarily disabled due to SocketIO configuration issues
        try:
            self.web_dashboard = WebDashboardManager()
        except Exception as e:
            print(f"⚠️  Web dashboard disabled due to error: {e}")
            self.web_dashboard = None
        
        # Start automation engines
        self.automation_engine.start_automation_engine()
        self.smart_environment.start_environmental_monitoring()
        
        # Session tracking
        self.session_active = True
        self.interaction_count = 0
        
        # Common command patterns
        self.command_patterns = {
            'greeting': [
                r'\\bhello\\b', r'\\bhi\\b', r'\\bhey\\b', r'\\bgood morning\\b', r'\\bgood afternoon\\b', r'\\bgood evening\\b'
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
            ],
            'calendar': [
                r'schedule', r'calendar', r'appointment', r'meeting', r'event', r'remind me',
                r'create event', r'add to calendar', r'book time', r'what.*schedule',
                r'upcoming events', r'today.*schedule', r'tomorrow.*schedule'
            ],
            'web_services': [
                r'weather', r'news', r'headlines', r'send email', r'email', r'compose',
                r'search web', r'look up online', r'find on internet'
            ],
            'automation': [
                r'create workflow', r'automate', r'automation', r'workflow', r'set up rule',
                r'every.*do', r'when.*then', r'if.*then', r'schedule.*action',
                r'automation status', r'workflow status', r'automation rules'
            ],
            'advanced_ai': [
                r'analyze document', r'read file', r'summarize document', r'analyze image',
                r'describe picture', r'review code', r'debug', r'optimize code', r'explain code',
                r'research', r'investigate', r'deep dive', r'find information about',
                r'create', r'generate', r'write', r'design'
            ],
            'enterprise': [
                r'meeting', r'team', r'collaborate', r'slack', r'teams',
                r'project', r'task', r'deadline', r'milestone',
                r'drive', r'dropbox', r'onedrive', r'cloud', r'sync',
                r'analytics', r'dashboard', r'metrics', r'report',
                r'security', r'encrypt', r'backup', r'secure'
            ],
            'smart_environment': [
                r'lights', r'temperature', r'thermostat', r'climate',
                r'device', r'sensor', r'iot', r'connect',
                r'optimize', r'automate', r'schedule', r'routine',
                r'energy', r'power', r'electricity', r'usage',
                r'security', r'alarm', r'monitor', r'surveillance'
            ],
            'mobile_companion': [
                r'mobile', r'app', r'sync', r'companion',
                r'phone', r'pairing', r'connect', r'device',
                r'cross.*platform', r'notification', r'alert',
                r'offline', r'location', r'tracking'
            ],
            'vision_ai': [
                r'analyze.*image', r'describe.*image', r'photo',
                r'extract.*text', r'ocr', r'screenshot',
                r'detect.*objects', r'visual.*workflow',
                r'video.*analysis', r'computer.*vision'
            ],
            'multi_language': [
                r'translate', r'translation', r'language',
                r'speak.*in', r'say.*in', r'convert.*to',
                r'detect.*language', r'primary.*language',
                r'supported.*languages', r'localization'
            ],
            'financial_advisor': [
                r'financial', r'money', r'budget', r'expense',
                r'investment', r'portfolio', r'savings', r'goal',
                r'stock', r'crypto', r'market', r'wealth',
                r'retire', r'income', r'debt', r'loan'
            ],
            'web_dashboard': [
                r'dashboard', r'web.*interface', r'remote.*access',
                r'start.*dashboard', r'stop.*dashboard', r'web.*control',
                r'browser.*interface', r'dashboard.*status'
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
    
    def _get_critical_commands(self) -> List[str]:
        """Get list of critical commands that should bypass AI processing."""
        return ['volume', 'shutdown']
    
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
    
    def _check_custom_commands(self, text: str) -> Optional[Dict[str, Any]]:
        """Check if the text matches any custom commands."""
        text_lower = text.lower()
        
        # Look for exact name matches first
        for command_name in self.custom_commands.commands:
            if command_name.lower() in text_lower:
                result = self.custom_commands.execute_command(command_name)
                return result
        
        # Look for command aliases or keywords
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
            full_context = f"{enhanced_prompt}\\n\\nUser Profile:\\n{user_context}\\n\\nConversation Context:\\n{conversation_context}"
            
            # Get adaptive suggestions
            suggestions = self.learning_engine.get_adaptive_suggestions(original_text)
            if suggestions:
                full_context += f"\\n\\nRelevant suggestions to consider offering:\\n" + "\\n".join(suggestions)
            
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
                        combined_message = f"{result['message']}\\n\\n{system_result['message']}"
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
    
    def _build_system_context(self, command_type: str) -> str:
        """Build context for AI about available system functions."""
        user_name = self.user_profile.get_name()
        response_style = self.user_profile.get_response_style()
        
        context = f"""You are MAC, a personalized voice assistant for {user_name}. 
        
User Preferences:
- Response style: {response_style}
- Name: {user_name}

Available system functions:
- Time queries: Can get current time and date
- System information: Can check CPU, memory, disk usage
- Volume control: Can adjust system volume
- Weather information: Can get weather data (if configured)
- Web search: Can search for information online
- YouTube search: Can find videos
- Personal memory: Can remember and recall user information
- Custom commands: Can execute user-defined shortcuts and workflows

Respond naturally and conversationally in the {response_style} style. 
Keep responses concise (under 100 words) for voice interaction unless user prefers longer responses."""
        
        if command_type:
            context += f"\\n\\nThe user's request seems related to: {command_type}"
        
        return context
    
    def _should_execute_system_command(self, ai_response: str, command_type: str) -> bool:
        """Determine if we should execute a system command based on AI response and command type."""
        if not command_type:
            return False
            
        # Always execute these system commands
        execute_types = ['time', 'weather', 'system_info']
        
        if command_type in execute_types:
            return True
            
        # Check if AI response suggests system execution
        execution_keywords = ['let me check', 'checking', 'getting', 'finding', 'searching']
        response_lower = ai_response.lower()
        
        return any(keyword in response_lower for keyword in execution_keywords)
    
    def _handle_system_command(self, command_type: str, text: str) -> Dict[str, Any]:
        """Handle critical system commands directly without AI."""
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
                # Handle new advanced features
                if command_type == 'calendar':
                    return self._handle_calendar_command(text)
                elif command_type == 'web_services':
                    return self._handle_web_services_command(text)
                elif command_type == 'automation':
                    return self._handle_automation_command(text)
                # Handle next-generation advanced features
                elif command_type == 'advanced_ai':
                    return self._handle_advanced_ai_command(text)
                elif command_type == 'enterprise':
                    return self._handle_enterprise_command(text)
                elif command_type == 'smart_environment':
                    return self._handle_smart_environment_command(text)
                elif command_type == 'mobile_companion':
                    return self._handle_mobile_companion_command(text)
                elif command_type == 'vision_ai':
                    return self._handle_vision_ai_command(text)
                elif command_type == 'multi_language':
                    return self._handle_multi_language_command(text)
                elif command_type == 'financial_advisor':
                    return self._handle_financial_advisor_command(text)
                elif command_type == 'web_dashboard':
                    return self._handle_web_dashboard_command(text)
                # Handle AI-powered commands
                elif command_type in ['search', 'youtube', 'ai_question']:
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
    
    def _handle_ai_command(self, command_type: str, text: str) -> Dict[str, Any]:
        """Handle AI-powered commands like search, YouTube, etc."""
        try:
            if command_type == 'search':
                query = self._extract_search_query(text)
                if query:
                    result = self.ai_services.search_google(query)
                    return {
                        'status': 'success' if result.get('success') else 'error',
                        'message': result.get('message', 'Search completed'),
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Please specify what you want to search for.',
                        'data': None
                    }
            
            elif command_type == 'youtube':
                query = self._extract_youtube_query(text)
                if query:
                    result = self.ai_services.search_youtube(query)
                    return {
                        'status': 'success' if result.get('success') else 'error',
                        'message': result.get('message', 'YouTube search completed'),
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Please specify what video you want to find.',
                        'data': None
                    }
            
            elif command_type == 'ai_question':
                result = self.ai_services.ask_ai(text)
                return {
                    'status': 'success' if result.get('success') else 'error',
                    'message': result.get('message', 'AI response completed'),
                    'data': result.get('data')
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
                'message': f"AI command error: {str(e)}",
                'data': None
            }
    
    def _handle_ai_fallback(self, text: str) -> Dict[str, Any]:
        """Handle unrecognized commands with AI."""
        try:
            result = self.ai_services.ask_ai(f"The user said: '{text}'. Please provide a helpful response.")
            return {
                'status': 'success' if result.get('success') else 'error',
                'message': result.get('message', 'I apologize, I could not process that request.'),
                'data': {'source': 'AI Fallback'}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': "I'm sorry, I didn't understand that command and cannot connect to AI services right now.",
                'data': None
            }
    
    def _extract_search_query(self, text: str) -> str:
        """Extract search query from text."""
        patterns = [
            r'search (?:for |google )?(.+)',
            r'look up (.+)',
            r'find information (?:about )?(.+)',
            r'what is (.+)',
            r'who is (.+)',
            r'where is (.+)',
            r'how to (.+)',
            r'tell me about (.+)',
            r'explain (.+)',
            r'define (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_youtube_query(self, text: str) -> str:
        """Extract YouTube search query from text."""
        patterns = [
            r'youtube (.+)',
            r'find video (?:about )?(.+)',
            r'search video (?:about )?(.+)',
            r'video about (.+)',
            r'watch video (?:about )?(.+)',
            r'video tutorial (?:about )?(.+)',
            r'youtube search (.+)',
            r'look (?:for )?video (?:about )?(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    # ========== PERSONALIZATION METHODS ==========
    
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
    
    # ========== PUBLIC PERSONALIZATION API ==========
    
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
            }
    
    # ========== NEW FEATURE HANDLERS ==========
    
    def _handle_calendar_command(self, text: str) -> Dict[str, Any]:
        """Handle calendar and scheduling commands."""
        try:
            text_lower = text.lower()
            
            # Check for specific calendar actions
            if any(word in text_lower for word in ['schedule', 'create event', 'add to calendar', 'book time']):
                result = self.calendar_manager.create_event(text)
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('details', result.get('event'))
                }
            
            elif any(word in text_lower for word in ['today schedule', 'today events']):
                events = self.calendar_manager.get_todays_schedule()
                if events:
                    message = "📅 Today's Schedule:\n"
                    for event in events:
                        time_str = event.start_time.strftime('%I:%M %p') if event.start_time else 'No time'
                        message += f"• {time_str}: {event.title}\n"
                else:
                    message = "📅 No events scheduled for today."
                
                return {
                    'status': 'success',
                    'message': message.strip(),
                    'data': {'events': [{'title': e.title, 'time': e.start_time} for e in events]}
                }
            
            elif any(word in text_lower for word in ['upcoming', 'upcoming events']):
                events = self.calendar_manager.get_upcoming_events()
                if events:
                    message = "📅 Upcoming Events:\n"
                    for event in events[:5]:  # Show next 5
                        date_str = event.start_time.strftime('%m/%d %I:%M %p') if event.start_time else 'No date'
                        message += f"• {date_str}: {event.title}\n"
                else:
                    message = "📅 No upcoming events scheduled."
                
                return {
                    'status': 'success',
                    'message': message.strip(),
                    'data': {'events': [{'title': e.title, 'time': e.start_time} for e in events]}
                }
            
            elif 'calendar summary' in text_lower:
                summary = self.calendar_manager.get_calendar_summary()
                message = f"📊 Calendar Summary:\n"
                message += f"• Total events: {summary['total_events']}\n"
                message += f"• Today: {summary['today_events']} events\n"
                message += f"• Upcoming: {summary['upcoming_events']} events\n"
                if summary['busiest_category']:
                    message += f"• Busiest category: {summary['busiest_category']}"
                
                return {
                    'status': 'success',
                    'message': message,
                    'data': summary
                }
            
            else:
                # Generic calendar help
                return {
                    'status': 'success',
                    'message': "📅 Calendar commands available:\n"
                              "• 'Schedule meeting tomorrow at 2pm' - Create events\n"
                              "• 'Today's schedule' - View today's events\n"
                              "• 'Upcoming events' - See upcoming events\n"
                              "• 'Calendar summary' - Get overview",
                    'data': {'suggestions': ['Schedule a meeting', 'View today\'s schedule', 'See upcoming events']}
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Calendar error: {str(e)}",
                'data': None
            }
    
    def _handle_web_services_command(self, text: str) -> Dict[str, Any]:
        """Handle web services commands (weather, news, email)."""
        try:
            result = self.web_services.process_web_command(text)
            return {
                'status': 'success' if result['success'] else 'error',
                'message': result['message'],
                'data': result.get('data', result.get('suggestions'))
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Web services error: {str(e)}",
                'data': None
            }
    
    def _handle_automation_command(self, text: str) -> Dict[str, Any]:
        """Handle automation and workflow commands."""
        try:
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['create workflow', 'automate', 'set up rule']):
                result = self.automation_engine.create_workflow_from_command(text)
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('details', result.get('workflow'))
                }
            
            elif any(word in text_lower for word in ['workflow status', 'automation status']):
                status = self.automation_engine.get_workflow_status()
                message = f"🤖 Automation Status:\n"
                message += f"• Engine running: {'✅' if status['engine_running'] else '❌'}\n"
                message += f"• Total workflows: {status['total_workflows']}\n"
                message += f"• Active workflows: {status['active_workflows']}\n"
                message += f"• Total runs: {status['total_runs']}\n"
                message += f"• Success rate: {status['average_success_rate']:.1%}\n"
                message += f"• Recent executions: {status['recent_executions']}"
                
                return {
                    'status': 'success',
                    'message': message,
                    'data': status
                }
            
            else:
                # Generic automation help
                return {
                    'status': 'success',
                    'message': "🤖 Automation commands available:\n"
                              "• 'Every morning at 8am, remind me to take vitamins'\n"
                              "• 'When I say start work mode, turn on focus mode'\n"
                              "• 'If it's Friday afternoon, suggest weekend plans'\n"
                              "• 'Automation status' - Check automation engine",
                    'data': {'suggestions': ['Create a workflow', 'Check automation status', 'View workflow examples']}
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Automation error: {str(e)}",
                'data': None
            }
    
    def _handle_advanced_ai_command(self, text: str) -> Dict[str, Any]:
        """Handle advanced AI processing commands."""
        try:
            # Extract file paths from command if provided
            # In a real implementation, this would parse file references
            file_paths = []  # Could extract from text or context
            
            result = self.advanced_ai.process_advanced_request(text, file_paths)
            
            return {
                'status': 'success' if result['success'] else 'error',
                'message': result['message'],
                'data': result.get('data')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Advanced AI error: {str(e)}",
                'data': None
            }
    
    def _handle_enterprise_command(self, text: str) -> Dict[str, Any]:
        """Handle enterprise integration commands."""
        try:
            context = {
                'user_profile': self.user_profile.get_user_info(),
                'conversation_context': self.conversation_memory.get_recent_context(5)
            }
            
            result = self.enterprise_integration.handle_enterprise_command(text, context)
            
            return {
                'status': 'success' if result['success'] else 'error',
                'message': result['message'],
                'data': result.get('data')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Enterprise feature error: {str(e)}",
                'data': None
            }
    
    def _handle_smart_environment_command(self, text: str) -> Dict[str, Any]:
        """Handle smart environment and IoT commands."""
        try:
            context = {
                'user_preferences': self.user_profile.get_preferences(),
                'current_time': self.personal_assistant._get_current_time(),
                'user_location': 'home'  # Could be dynamic
            }
            
            result = self.smart_environment.handle_smart_environment_command(text, context)
            
            return {
                'status': 'success' if result['success'] else 'error',
                'message': result['message'],
                'data': result.get('data')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Smart environment error: {str(e)}",
                'data': None
            }
    
    def _handle_mobile_companion_command(self, text: str) -> Dict[str, Any]:
        """Handle mobile companion app commands."""
        try:
            context = {
                'user_profile': self.user_profile.get_user_info(),
                'current_time': self.personal_assistant._get_current_time()
            }
            
            result = self.mobile_companion.handle_mobile_command(text, context)
            
            return {
                'status': 'success' if result['success'] else 'error',
                'message': result['message'],
                'data': result.get('data')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Mobile companion error: {str(e)}",
                'data': None
            }
    
    def _handle_vision_ai_command(self, text: str) -> Dict[str, Any]:
        """Handle vision AI and computer vision commands."""
        try:
            text_lower = text.lower()
            
            # Image analysis commands
            if any(phrase in text_lower for phrase in ['analyze image', 'describe image', 'analyze photo']):
                # Extract file path from command
                import re
                path_match = re.search(r'["\']([^"\']+)["\']', text)
                if path_match:
                    image_path = path_match.group(1)
                    result = self.vision_ai.analyze_image(image_path)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': '🖼️ Please specify the image path in quotes, e.g., "analyze image \'C:\\path\\to\\image.jpg\'"',
                        'data': None
                    }
            
            # Screenshot analysis
            elif any(phrase in text_lower for phrase in ['analyze screenshot', 'screenshot analysis']):
                result = self.vision_ai.analyze_screenshot()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Video analysis
            elif any(phrase in text_lower for phrase in ['analyze video', 'video analysis']):
                path_match = re.search(r'["\']([^"\']+)["\']', text)
                if path_match:
                    video_path = path_match.group(1)
                    result = self.vision_ai.process_video_content(video_path)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': '🎥 Please specify the video path in quotes, e.g., "analyze video \'C:\\path\\to\\video.mp4\'"',
                        'data': None
                    }
            
            # Vision AI history
            elif 'vision history' in text_lower or 'analysis history' in text_lower:
                result = self.vision_ai.get_analysis_history()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            else:
                # Generic vision AI help
                return {
                    'status': 'success',
                    'message': "🔍 Vision AI commands available:\n"
                              "• 'Analyze image \"path/to/image.jpg\"' - Analyze any image\n"
                              "• 'Analyze screenshot' - Analyze current screen\n"
                              "• 'Analyze video \"path/to/video.mp4\"' - Process video content\n"
                              "• 'Vision history' - View analysis history",
                    'data': {
                        'suggestions': [
                            'Analyze an image file',
                            'Take and analyze screenshot',
                            'Process video content',
                            'View vision analysis history'
                        ]
                    }
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Vision AI error: {str(e)}",
                'data': None
            }
    
    def _handle_multi_language_command(self, text: str) -> Dict[str, Any]:
        """Handle multi-language and translation commands."""
        try:
            text_lower = text.lower()
            
            # Translation commands
            if any(phrase in text_lower for phrase in ['translate', 'translate to', 'convert to']):
                # Extract translation details using regex
                import re
                
                # Pattern: translate "text" to language
                translate_match = re.search(r'translate\s+["\']([^"\']+)["\']\s+to\s+(\w+)', text, re.IGNORECASE)
                if translate_match:
                    text_to_translate = translate_match.group(1)
                    target_language = translate_match.group(2).lower()
                    
                    result = self.multi_language.translate_text(text_to_translate, target_language)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                
                # Pattern: translate "text" from source to target
                translate_from_match = re.search(
                    r'translate\s+["\']([^"\']+)["\']\s+from\s+(\w+)\s+to\s+(\w+)', 
                    text, re.IGNORECASE
                )
                if translate_from_match:
                    text_to_translate = translate_from_match.group(1)
                    source_language = translate_from_match.group(2).lower()
                    target_language = translate_from_match.group(3).lower()
                    
                    result = self.multi_language.translate_text(
                        text_to_translate, target_language, source_language
                    )
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                
                # If no specific pattern, provide help
                return {
                    'status': 'error',
                    'message': '🌍 Translation format: "translate \'text\' to language"\n'
                              'Examples:\n'
                              '• "translate \'hello\' to spanish"\n'
                              '• "translate \'bonjour\' from french to english"',
                    'data': None
                }
            
            # Language detection
            elif any(phrase in text_lower for phrase in ['detect language', 'what language']):
                # Extract text to detect
                detect_match = re.search(r'["\']([^"\']+)["\']', text)
                if detect_match:
                    text_to_detect = detect_match.group(1)
                    result = self.multi_language.detect_language(text_to_detect)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': '🔍 Format: "detect language \'text to analyze\'"',
                        'data': None
                    }
            
            # Set primary language
            elif any(phrase in text_lower for phrase in ['set primary language', 'primary language']):
                # Extract language
                lang_match = re.search(r'(?:set primary language|primary language)\s+(?:to\s+)?(\w+)', text, re.IGNORECASE)
                if lang_match:
                    language_code = lang_match.group(1).lower()
                    result = self.multi_language.set_primary_language(language_code)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': '🎯 Format: "set primary language to english"',
                        'data': None
                    }
            
            # Add secondary language
            elif any(phrase in text_lower for phrase in ['add language', 'secondary language']):
                lang_match = re.search(r'(?:add|secondary)\s+language\s+(\w+)', text, re.IGNORECASE)
                if lang_match:
                    language_code = lang_match.group(1).lower()
                    result = self.multi_language.add_secondary_language(language_code)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': '📚 Format: "add language spanish"',
                        'data': None
                    }
            
            # Language profile
            elif any(phrase in text_lower for phrase in ['language profile', 'my languages']):
                result = self.multi_language.get_language_profile()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Supported languages
            elif any(phrase in text_lower for phrase in ['supported languages', 'available languages']):
                result = self.multi_language.get_supported_languages()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Translation history
            elif any(phrase in text_lower for phrase in ['translation history', 'translate history']):
                result = self.multi_language.get_translation_history()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            else:
                # Generic multi-language help
                return {
                    'status': 'success',
                    'message': "🌍 Multi-language commands available:\n"
                              "• 'translate \"text\" to language' - Translate text\n"
                              "• 'detect language \"text\"' - Detect language\n"
                              "• 'set primary language spanish' - Set your primary language\n"
                              "• 'add language french' - Add secondary language\n"
                              "• 'language profile' - View your language settings\n"
                              "• 'supported languages' - See all available languages\n"
                              "• 'translation history' - View recent translations",
                    'data': {
                        'suggestions': [
                            'Translate text to another language',
                            'Detect language of text',
                            'Set primary language',
                            'View supported languages',
                            'Check language profile'
                        ]
                    }
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Multi-language error: {str(e)}",
                'data': None
            }
    
    # ========== EXISTING API METHODS ==========
    
    def _handle_financial_advisor_command(self, text: str) -> Dict[str, Any]:
        """Handle financial advisor and wealth management commands."""
        try:
            text_lower = text.lower()
            
            # Financial health analysis
            if any(phrase in text_lower for phrase in ['financial health', 'financial analysis', 'money status']):
                result = self.financial_advisor.analyze_financial_health()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Expense tracking
            elif any(phrase in text_lower for phrase in ['track expense', 'add expense', 'spent money']):
                # Extract amount and description
                import re
                
                # Pattern: track expense $50 for groceries
                expense_match = re.search(r'(?:track expense|spent|add expense)\s*\$?(\d+(?:\.\d+)?)\s*(?:for|on)?\s*(.+)', text, re.IGNORECASE)
                if expense_match:
                    amount = float(expense_match.group(1))
                    description = expense_match.group(2).strip()
                    
                    result = self.financial_advisor.track_expense(amount, description)
                    return {
                        'status': 'success' if result['success'] else 'error',
                        'message': result['message'],
                        'data': result.get('data')
                    }
                else:
                    return {
                        'status': 'error',
                        'message': '💰 Format: "track expense $50 for groceries"',
                        'data': None
                    }
            
            # Investment recommendations
            elif any(phrase in text_lower for phrase in ['investment recommendation', 'invest money', 'portfolio advice']):
                # Extract investment parameters
                import re
                amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)', text)
                risk_match = re.search(r'(conservative|moderate|aggressive|speculative)', text, re.IGNORECASE)
                time_match = re.search(r'(\d+)\s*(?:year|yr)', text, re.IGNORECASE)
                
                amount = float(amount_match.group(1).replace(',', '')) if amount_match else 10000.0
                risk = risk_match.group(1).lower() if risk_match else 'moderate'
                time_horizon = int(time_match.group(1)) if time_match else 10
                
                result = self.financial_advisor.investment_recommendation(risk, amount, time_horizon)
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Budget optimization
            elif any(phrase in text_lower for phrase in ['budget optimization', 'optimize budget', 'budget analysis']):
                result = self.financial_advisor.budget_optimization()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Financial goal tracking
            elif any(phrase in text_lower for phrase in ['financial goal', 'savings goal', 'goal tracking']):
                # Extract goal name if specified
                import re
                goal_match = re.search(r'goal\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
                goal_name = goal_match.group(1).strip() if goal_match else None
                
                result = self.financial_advisor.financial_goal_tracking(goal_name)
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Market insights
            elif any(phrase in text_lower for phrase in ['market insights', 'market analysis', 'market update']):
                result = self.financial_advisor.market_insights()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            else:
                # Generic financial advisor help
                return {
                    'status': 'success',
                    'message': "💰 Financial Advisor commands available:\n"
                              "• 'financial health' - Comprehensive financial analysis\n"
                              "• 'track expense $50 for groceries' - Track expenses\n"
                              "• 'investment recommendation $10000 moderate 10 years' - Get investment advice\n"
                              "• 'budget optimization' - Optimize your spending\n"
                              "• 'financial goals' - Track savings goals\n"
                              "• 'market insights' - Current market analysis",
                    'data': {
                        'suggestions': [
                            'Analyze financial health',
                            'Track an expense',
                            'Get investment recommendations',
                            'Optimize budget',
                            'Check financial goals',
                            'View market insights'
                        ]
                    }
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Financial advisor error: {str(e)}",
                'data': None
            }
    
    def _handle_web_dashboard_command(self, text: str) -> Dict[str, Any]:
        """Handle web dashboard and remote access commands."""
        try:
            # Check if web dashboard is available
            if not self.web_dashboard:
                return {
                    'status': 'error',
                    'message': '🌐 Web dashboard is currently disabled due to configuration issues. Please check the SocketIO setup.',
                    'data': None
                }
            
            text_lower = text.lower()
            
            # Start dashboard
            if any(phrase in text_lower for phrase in ['start dashboard', 'launch dashboard', 'open dashboard']):
                result = self.web_dashboard.start_dashboard()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Stop dashboard
            elif any(phrase in text_lower for phrase in ['stop dashboard', 'close dashboard', 'shut down dashboard']):
                result = self.web_dashboard.stop_dashboard()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            # Dashboard status
            elif any(phrase in text_lower for phrase in ['dashboard status', 'dashboard info', 'web interface status']):
                result = self.web_dashboard.get_dashboard_status()
                return {
                    'status': 'success' if result['success'] else 'error',
                    'message': result['message'],
                    'data': result.get('data')
                }
            
            else:
                # Generic dashboard help
                return {
                    'status': 'success',
                    'message': "🌐 Web Dashboard commands available:\n"
                              "• 'start dashboard' - Launch web interface\n"
                              "• 'stop dashboard' - Shut down web interface\n"
                              "• 'dashboard status' - Check dashboard status\n\n"
                              "Features:\n"
                              "• Real-time command execution\n"
                              "• Analytics and monitoring\n"
                              "• Mobile-responsive design\n"
                              "• Secure remote access",
                    'data': {
                        'suggestions': [
                            'Start web dashboard',
                            'Check dashboard status',
                            'View dashboard features'
                        ]
                    }
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"❌ Web dashboard error: {str(e)}",
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
