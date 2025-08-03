"""
MAC Assistant - Command Processor Brain
Processes natural language commands and routes them to appropriate handlers.
"""

import re
import platform
from typing import Dict, Any, Optional
from commands.windows import WindowsCommands
from commands.android import AndroidCommands
from .ai_services import AIServices


class MACBrain:
    def __init__(self):
        self.platform = platform.system().lower()
        self.commands = self._initialize_commands()
        self.ai_services = AIServices()
        
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
        ChatGPT is now the primary brain with system commands as fallbacks.
        
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
        
        try:
            # First, check if this is a critical system command that should bypass ChatGPT
            critical_commands = self._get_critical_commands()
            command_type = self._identify_command_type(text)
            
            if command_type in critical_commands:
                # Handle critical system commands directly (volume, shutdown, etc.)
                return self._handle_system_command(command_type, text)
            
            # For all other commands, try AI first
            if self.ai_services.is_ai_available():
                return self._handle_ai_primary(original_text, command_type, text)
            else:
                # Fallback to traditional pattern matching if AI unavailable
                return self._handle_traditional_processing(command_type, text)
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error processing command: {str(e)}",
                'data': None
            }
    
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
