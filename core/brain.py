"""
MAC Assistant - Command Processor Brain
Processes natural language commands and routes them to appropriate handlers.
"""

import re
import platform
from typing import Dict, Any, Optional
from commands.windows import WindowsCommands
from commands.android import AndroidCommands


class MACBrain:
    def __init__(self):
        self.platform = platform.system().lower()
        self.commands = self._initialize_commands()
        
        # Common command patterns
        self.command_patterns = {
            'greeting': [
                r'hello', r'hi', r'hey', r'good morning', r'good afternoon', r'good evening'
            ],
            'time': [
                r'what time is it', r'current time', r'tell me the time'
            ],
            'weather': [
                r'weather', r'temperature', r'forecast'
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
                result = self._execute_command(command_type, text)
                return {
                    'status': 'success',
                    'message': result.get('message', 'Command executed successfully'),
                    'data': result.get('data', None)
                }
            else:
                return {
                    'status': 'unknown',
                    'message': f"I don't understand the command: {text}",
                    'data': None
                }
                
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
