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
                r'what is the volume', r'current volume', r'volume status', r'sound up', r'sound down'
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
        
        text = text.lower().strip()
        
        try:
            # Match command to pattern
            command_type = self._identify_command_type(text)
            
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
            services = self.ai_services.is_available()
            
            if services['chatgpt']:
                # Ask ChatGPT to handle the question
                context = "You are a voice assistant. The user said something that doesn't match predefined commands."
                result = self.ai_services.ask_chatgpt(text, context)
                
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
        return self.ai_services.is_available()
