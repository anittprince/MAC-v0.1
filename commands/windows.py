"""
MAC Assistant - Windows Commands Module
Handles Windows-specific commands and system operations.
"""

import os
import subprocess
import platform
import psutil
import datetime
import socket
import ctypes
from ctypes import wintypes
from typing import Dict, Any, List
import winreg


class WindowsCommands:
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        try:
            return {
                'os': platform.system(),
                'version': platform.version(),
                'release': platform.release(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': socket.gethostname(),
                'username': os.getenv('USERNAME', 'Unknown')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def handle_greeting(self, text: str) -> Dict[str, Any]:
        """Handle greeting commands."""
        current_time = datetime.datetime.now()
        hour = current_time.hour
        
        if 5 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 17:
            greeting = "Good afternoon"
        elif 17 <= hour < 22:
            greeting = "Good evening"
        else:
            greeting = "Good night"
        
        username = self.system_info.get('username', 'there')
        message = f"{greeting}, {username}! I'm MAC, your voice assistant. How can I help you today?"
        
        return {
            'message': message,
            'data': {
                'greeting': greeting,
                'time': current_time.strftime("%H:%M:%S"),
                'user': username
            }
        }
    
    def handle_time(self, text: str) -> Dict[str, Any]:
        """Handle time-related commands."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d, %Y")
        
        message = f"The current time is {time_str} on {date_str}"
        
        return {
            'message': message,
            'data': {
                'time': time_str,
                'date': date_str,
                'timestamp': now.timestamp()
            }
        }
    
    def handle_system_info(self, text: str) -> Dict[str, Any]:
        """Handle system information commands."""
        try:
            # Get CPU and memory info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            info = {
                'cpu_usage': f"{cpu_percent}%",
                'memory_usage': f"{memory.percent}%",
                'memory_available': f"{memory.available / (1024**3):.1f} GB",
                'disk_usage': f"{disk.percent}%",
                'disk_free': f"{disk.free / (1024**3):.1f} GB"
            }
            
            message = f"System Status: CPU {info['cpu_usage']}, RAM {info['memory_usage']}, Disk {info['disk_usage']}"
            
            return {
                'message': message,
                'data': {**self.system_info, **info}
            }
        except Exception as e:
            return {
                'message': f"Error getting system information: {str(e)}",
                'data': None
            }
    
    def handle_network(self, text: str) -> Dict[str, Any]:
        """Handle network-related commands."""
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            active_interfaces = []
            for interface, addresses in interfaces.items():
                if interface in stats and stats[interface].isup:
                    for addr in addresses:
                        if addr.family == socket.AF_INET:  # IPv4
                            active_interfaces.append({
                                'name': interface,
                                'ip': addr.address,
                                'status': 'up' if stats[interface].isup else 'down'
                            })
            
            # Get internet connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                internet_status = "Connected"
            except OSError:
                internet_status = "Disconnected"
            
            message = f"Network Status: {internet_status}. Found {len(active_interfaces)} active interfaces."
            
            return {
                'message': message,
                'data': {
                    'internet_status': internet_status,
                    'interfaces': active_interfaces
                }
            }
        except Exception as e:
            return {
                'message': f"Error getting network information: {str(e)}",
                'data': None
            }
    
    def handle_applications(self, text: str) -> Dict[str, Any]:
        """Handle application control commands."""
        try:
            if 'open' in text or 'launch' in text or 'start' in text:
                return self._open_application(text)
            elif 'close' in text or 'quit' in text or 'exit' in text:
                return self._close_application(text)
            else:
                return self._list_running_applications()
        except Exception as e:
            return {
                'message': f"Error handling application command: {str(e)}",
                'data': None
            }
    
    def _open_application(self, text: str) -> Dict[str, Any]:
        """Open an application."""
        # Common application mappings
        app_map = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'browser': 'msedge.exe',
            'edge': 'msedge.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'explorer': 'explorer.exe',
            'file manager': 'explorer.exe',
            'control panel': 'control.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe'
        }
        
        app_name = None
        for key, value in app_map.items():
            if key in text.lower():
                app_name = value
                break
        
        if not app_name:
            return {
                'message': "I couldn't identify which application to open. Try saying 'open notepad' or 'launch calculator'.",
                'data': None
            }
        
        try:
            subprocess.Popen(app_name, shell=True)
            return {
                'message': f"Opening {app_name}",
                'data': {'application': app_name, 'action': 'opened'}
            }
        except Exception as e:
            return {
                'message': f"Failed to open {app_name}: {str(e)}",
                'data': None
            }
    
    def _close_application(self, text: str) -> Dict[str, Any]:
        """Close an application."""
        # This is a simplified version - in practice, you'd want more sophisticated process management
        return {
            'message': "Application closing is not yet implemented for safety reasons.",
            'data': None
        }
    
    def _list_running_applications(self) -> Dict[str, Any]:
        """List running applications."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['name'].endswith('.exe'):
                        processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'cpu': proc.info['cpu_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage and get top 10
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            top_processes = processes[:10]
            
            message = f"Found {len(processes)} running processes. Top processes by CPU usage."
            
            return {
                'message': message,
                'data': {'processes': top_processes, 'total_count': len(processes)}
            }
        except Exception as e:
            return {
                'message': f"Error listing applications: {str(e)}",
                'data': None
            }
    
    def handle_volume(self, text: str) -> Dict[str, Any]:
        """Handle volume control commands."""
        try:
            if any(word in text for word in ['up', 'increase', 'turn up', 'sound up']):
                return self._change_volume(10)
            elif any(word in text for word in ['down', 'decrease', 'turn down', 'sound down']):
                return self._change_volume(-10)
            elif 'mute' in text and 'unmute' not in text:
                return self._mute_volume()
            elif 'unmute' in text:
                return self._unmute_volume()
            else:
                return self._get_volume_info()
        except Exception as e:
            return {
                'message': f"Error controlling volume: {str(e)}",
                'data': None
            }
    
    def _change_volume(self, delta: int) -> Dict[str, Any]:
        """Change system volume by delta percentage."""
        try:
            # Use Windows API to change volume
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            # Get current volume as scalar (0.0 to 1.0)
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, min(1.0, current_volume + (delta / 100.0)))
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            
            percentage = int(new_volume * 100)
            action = "increased" if delta > 0 else "decreased"
            
            return {
                'message': f"Volume {action} to {percentage}%",
                'data': {'volume': percentage, 'action': action}
            }
        except ImportError:
            return {
                'message': "Volume control requires pycaw library. Please install it.",
                'data': None
            }
        except Exception as e:
            return {
                'message': f"Error changing volume: {str(e)}",
                'data': None
            }
    
    def _mute_volume(self) -> Dict[str, Any]:
        """Mute system volume."""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            volume.SetMute(1, None)
            
            return {
                'message': "Volume muted",
                'data': {'action': 'muted'}
            }
        except ImportError:
            return {
                'message': "Volume control requires pycaw library. Please install it.",
                'data': None
            }
        except Exception as e:
            return {
                'message': f"Error muting volume: {str(e)}",
                'data': None
            }
    
    def _unmute_volume(self) -> Dict[str, Any]:
        """Unmute system volume."""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            volume.SetMute(0, None)
            
            return {
                'message': "Volume unmuted",
                'data': {'action': 'unmuted'}
            }
        except ImportError:
            return {
                'message': "Volume control requires pycaw library. Please install it.",
                'data': None
            }
        except Exception as e:
            return {
                'message': f"Error unmuting volume: {str(e)}",
                'data': None
            }
    
    def _get_volume_info(self) -> Dict[str, Any]:
        """Get current volume information."""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            current_volume = volume.GetMasterVolumeLevelScalar()
            is_muted = volume.GetMute()
            
            percentage = int(current_volume * 100)
            status = "muted" if is_muted else "unmuted"
            
            return {
                'message': f"Current volume is {percentage}% ({status})",
                'data': {
                    'volume': percentage,
                    'is_muted': bool(is_muted),
                    'status': status
                }
            }
        except ImportError:
            return {
                'message': "Volume control requires pycaw library. Please install it.",
                'data': None
            }
        except Exception as e:
            return {
                'message': f"Error getting volume information: {str(e)}",
                'data': None
            }
    
    def handle_shutdown(self, text: str) -> Dict[str, Any]:
        """Handle shutdown/restart commands."""
        if 'restart' in text or 'reboot' in text:
            return {
                'message': "I can't restart the system for safety reasons. Please restart manually.",
                'data': None
            }
        elif 'shutdown' in text or 'power off' in text:
            return {
                'message': "I can't shutdown the system for safety reasons. Please shutdown manually.",
                'data': None
            }
        elif 'sleep' in text:
            return {
                'message': "I can't put the system to sleep for safety reasons. Please use the power button.",
                'data': None
            }
        else:
            return {
                'message': "Power management commands are disabled for safety.",
                'data': None
            }
    
    def handle_file_operations(self, text: str) -> Dict[str, Any]:
        """Handle file operation commands."""
        try:
            if 'list files' in text or 'show files' in text:
                return self._list_files()
            else:
                return {
                    'message': "File operations are limited for security. I can only list files in safe directories.",
                    'data': None
                }
        except Exception as e:
            return {
                'message': f"Error with file operations: {str(e)}",
                'data': None
            }
    
    def _list_files(self) -> Dict[str, Any]:
        """List files in safe directories."""
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            
            files = []
            for path in [desktop_path, documents_path]:
                if os.path.exists(path):
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        files.append({
                            'name': item,
                            'path': item_path,
                            'type': 'directory' if os.path.isdir(item_path) else 'file',
                            'location': os.path.basename(path)
                        })
            
            message = f"Found {len(files)} items in Desktop and Documents folders."
            
            return {
                'message': message,
                'data': {'files': files[:20]}  # Limit to first 20 items
            }
        except Exception as e:
            return {
                'message': f"Error listing files: {str(e)}",
                'data': None
            }
    
    def handle_weather(self, text: str) -> Dict[str, Any]:
        """Handle weather commands."""
        return {
            'message': "Weather information requires an API key. This feature is not yet configured.",
            'data': None
        }
