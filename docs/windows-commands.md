# Windows Commands Documentation

This document provides comprehensive documentation for all Windows-specific commands available in the MAC Assistant.

## Overview

The Windows command module (`commands/windows.py`) handles all Windows-specific operations including system control, audio management, process handling, and file operations. Commands are processed through natural language understanding and executed using Windows APIs.

## Command Categories

### 1. Greeting and Social Commands

#### Supported Patterns
- `"hello"`, `"hi"`, `"hey"`
- `"good morning"`, `"good afternoon"`, `"good evening"`
- `"how are you"`, `"what's up"`

#### Example Commands

**Command:** `"Hello MAC"`
```json
{
  "message": "Good afternoon, User! I'm MAC, your voice assistant. How can I help you today?",
  "data": {
    "greeting": "Good afternoon",
    "time": "14:30:15",
    "user": "User"
  }
}
```

**Command:** `"Good morning"`
```json
{
  "message": "Good morning, User! I'm MAC, your voice assistant. How can I help you today?",
  "data": {
    "greeting": "Good morning",
    "time": "09:15:30",
    "user": "User"
  }
}
```

#### Features
- **Time-aware greetings**: Automatically adjusts greeting based on current time
- **User personalization**: Uses system username in response
- **Context awareness**: Maintains conversation context

### 2. Time and Date Commands

#### Supported Patterns
- `"what time is it"`, `"current time"`, `"time"`
- `"what's the date"`, `"today's date"`, `"date"`
- `"what day is it"`, `"day of week"`

#### Example Commands

**Command:** `"What time is it?"`
```json
{
  "message": "The current time is 02:30 PM on Monday, January 15, 2024",
  "data": {
    "time": "02:30 PM",
    "date": "Monday, January 15, 2024",
    "timestamp": 1642248600.0
  }
}
```

#### Features
- **12-hour format**: User-friendly time display
- **Full date information**: Day of week, month, day, year
- **Timestamp data**: Unix timestamp for programmatic use

### 3. System Information Commands

#### Supported Patterns
- `"system info"`, `"system information"`, `"computer status"`
- `"how's my pc"`, `"pc status"`, `"computer info"`
- `"system status"`, `"hardware info"`

#### Example Commands

**Command:** `"System info"`
```json
{
  "message": "System Status: CPU 15%, RAM 68%, Disk 45%",
  "data": {
    "cpu_usage": "15.2%",
    "memory_usage": "68.4%",
    "memory_available": "2.8 GB",
    "disk_usage": "45.2%",
    "disk_free": "125.3 GB",
    "os": "Windows",
    "version": "10.0.19044",
    "hostname": "DESKTOP-ABC123",
    "username": "User",
    "processor": "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
  }
}
```

#### Monitored Metrics
- **CPU Usage**: Real-time processor utilization percentage
- **Memory Usage**: RAM usage percentage and available memory
- **Disk Usage**: C: drive usage percentage and free space
- **System Information**: OS version, hostname, username
- **Hardware Details**: Processor information

#### Technical Implementation
```python
# Uses psutil for system monitoring
cpu_percent = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory()
disk = psutil.disk_usage('C:')
```

### 4. Network Commands

#### Supported Patterns
- `"network status"`, `"network info"`, `"connection status"`
- `"check connection"`, `"internet status"`, `"wifi status"`
- `"show ip"`, `"ip address"`, `"network interfaces"`

#### Example Commands

**Command:** `"Network status"`
```json
{
  "message": "Network Status: Connected. Found 3 active interfaces.",
  "data": {
    "internet_status": "Connected",
    "interfaces": [
      {
        "name": "Wi-Fi",
        "ip": "192.168.1.100",
        "status": "up"
      },
      {
        "name": "Ethernet",
        "ip": "192.168.1.101",
        "status": "up"
      }
    ]
  }
}
```

#### Features
- **Internet Connectivity**: Tests connection to Google DNS (8.8.8.8)
- **Interface Discovery**: Lists all active network interfaces
- **IP Address Information**: Shows IPv4 addresses for each interface
- **Status Monitoring**: Reports up/down status for each interface

### 5. Volume and Audio Control

#### Supported Patterns

**Volume Increase:**
- `"volume up"`, `"turn up volume"`, `"increase volume"`
- `"sound up"`, `"make it louder"`, `"raise volume"`

**Volume Decrease:**
- `"volume down"`, `"turn down volume"`, `"decrease volume"`
- `"sound down"`, `"make it quieter"`, `"lower volume"`

**Mute Controls:**
- `"mute"`, `"mute volume"`, `"silence"`
- `"unmute"`, `"unmute volume"`, `"restore sound"`

**Volume Information:**
- `"current volume"`, `"volume level"`, `"what's the volume"`

#### Example Commands

**Command:** `"Volume up"`
```json
{
  "message": "Volume increased to 75%",
  "data": {
    "volume": 75,
    "action": "increased",
    "is_muted": false
  }
}
```

**Command:** `"Mute"`
```json
{
  "message": "Volume muted",
  "data": {
    "action": "muted",
    "is_muted": true
  }
}
```

**Command:** `"Current volume"`
```json
{
  "message": "Current volume is 65% (unmuted)",
  "data": {
    "volume": 65,
    "is_muted": false,
    "status": "unmuted"
  }
}
```

#### Technical Implementation

Uses the **pycaw** library for Windows Core Audio API access:

```python
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Get default audio endpoint
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Volume operations
current_volume = volume.GetMasterVolumeLevelScalar()  # 0.0 to 1.0
volume.SetMasterVolumeLevelScalar(new_volume, None)   # Set volume
volume.SetMute(1, None)                               # Mute
volume.SetMute(0, None)                               # Unmute
```

#### Volume Control Features
- **Incremental Changes**: Volume adjusted by 10% increments
- **Bounds Checking**: Volume constrained between 0% and 100%
- **Mute State Management**: Independent mute/unmute functionality
- **Real-time Feedback**: Immediate audio level confirmation

### 6. Application Management

#### Supported Patterns

**Opening Applications:**
- `"open [app]"`, `"launch [app]"`, `"start [app]"`
- `"run [app]"`, `"execute [app]"`

**Listing Applications:**
- `"list apps"`, `"running apps"`, `"what's running"`
- `"show processes"`, `"active programs"`

#### Supported Applications

| Voice Command | Executable | Description |
|---------------|------------|-------------|
| `"notepad"` | `notepad.exe` | Windows Notepad |
| `"calculator"` | `calc.exe` | Windows Calculator |
| `"paint"` | `mspaint.exe` | Microsoft Paint |
| `"browser"`, `"edge"` | `msedge.exe` | Microsoft Edge |
| `"chrome"` | `chrome.exe` | Google Chrome |
| `"firefox"` | `firefox.exe` | Mozilla Firefox |
| `"explorer"`, `"file manager"` | `explorer.exe` | Windows Explorer |
| `"control panel"` | `control.exe` | Windows Control Panel |
| `"command prompt"` | `cmd.exe` | Command Prompt |
| `"powershell"` | `powershell.exe` | Windows PowerShell |

#### Example Commands

**Command:** `"Open calculator"`
```json
{
  "message": "Opening calc.exe",
  "data": {
    "application": "calc.exe",
    "action": "opened"
  }
}
```

**Command:** `"List running apps"`
```json
{
  "message": "Found 127 running processes. Top processes by CPU usage.",
  "data": {
    "processes": [
      {
        "name": "chrome.exe",
        "pid": 1234,
        "cpu": 5.2
      },
      {
        "name": "code.exe",
        "pid": 5678,
        "cpu": 3.1
      }
    ],
    "total_count": 127
  }
}
```

#### Security Features
- **Safe Application List**: Only predefined, safe applications can be launched
- **No Process Termination**: Application closing disabled for safety
- **Process Information Only**: Lists processes without modification capabilities

### 7. File Operations

#### Supported Patterns
- `"list files"`, `"show files"`, `"what files"`
- `"show desktop"`, `"desktop files"`
- `"documents folder"`, `"my documents"`

#### Example Commands

**Command:** `"List files"`
```json
{
  "message": "Found 15 items in Desktop and Documents folders.",
  "data": {
    "files": [
      {
        "name": "presentation.pptx",
        "path": "C:\\Users\\User\\Desktop\\presentation.pptx",
        "type": "file",
        "location": "Desktop"
      },
      {
        "name": "Projects",
        "path": "C:\\Users\\User\\Documents\\Projects",
        "type": "directory",
        "location": "Documents"
      }
    ]
  }
}
```

#### Security Restrictions
- **Limited Scope**: Only Desktop and Documents folders accessible
- **Read-Only Access**: No file modification or deletion capabilities
- **Safe Directories**: No access to system or sensitive folders
- **Item Limit**: Maximum 20 items returned per request

### 8. Power Management

#### Supported Patterns
- `"shutdown"`, `"power off"`, `"turn off"`
- `"restart"`, `"reboot"`, `"reset"`
- `"sleep"`, `"hibernate"`, `"suspend"`

#### Security Response

All power management commands are **disabled for safety**:

```json
{
  "message": "Power management commands are disabled for safety.",
  "data": null
}
```

#### Safety Features
- **No System Control**: Cannot shutdown, restart, or sleep system
- **Manual Override Required**: User must perform power operations manually
- **Safety Message**: Clear explanation of safety restrictions

### 9. Weather Information

#### Supported Patterns
- `"weather"`, `"what's the weather"`, `"weather today"`
- `"temperature"`, `"forecast"`, `"weather report"`

#### Current Status

Weather functionality requires API configuration:

```json
{
  "message": "Weather information requires an API key. This feature is not yet configured.",
  "data": null
}
```

#### Future Implementation
- Integration with weather APIs (OpenWeatherMap, etc.)
- Location-based weather reports
- Extended forecasts
- Weather alerts and notifications

## Command Processing Flow

### 1. Input Normalization
```python
def process_command(text: str) -> Dict[str, Any]:
    # Convert to lowercase for pattern matching
    text = text.lower().strip()
    
    # Remove punctuation for better matching
    text = re.sub(r'[^\w\s]', '', text)
```

### 2. Pattern Matching
```python
# Greeting patterns
if any(word in text for word in ['hello', 'hi', 'hey', 'good morning']):
    return self.windows_commands.handle_greeting(text)

# Time patterns
elif any(phrase in text for phrase in ['time', 'what time', 'current time']):
    return self.windows_commands.handle_time(text)

# Volume patterns
elif any(word in text for word in ['volume', 'sound', 'audio', 'mute']):
    return self.windows_commands.handle_volume(text)
```

### 3. Command Execution
```python
try:
    result = command_handler(text)
    return {
        'message': result['message'],
        'data': result['data'],
        'status': 'success'
    }
except Exception as e:
    return {
        'message': f"Error: {str(e)}",
        'data': None,
        'status': 'error'
    }
```

## Error Handling

### Common Error Scenarios

#### Missing Dependencies
```json
{
  "message": "Volume control requires pycaw library. Please install it.",
  "data": null,
  "status": "error"
}
```

#### Permission Errors
```json
{
  "message": "Error getting system information: Access denied",
  "data": null,
  "status": "error"
}
```

#### Invalid Commands
```json
{
  "message": "I couldn't identify which application to open. Try saying 'open notepad' or 'launch calculator'.",
  "data": null,
  "status": "error"
}
```

### Error Recovery
- Graceful degradation when services unavailable
- Helpful error messages with suggestions
- Fallback responses for unrecognized commands

## Performance Considerations

### Caching Strategy
- **System Information**: Cached for 30 seconds
- **Network Status**: Cached for 10 seconds
- **Process List**: Cached for 60 seconds

### Optimization Techniques
- Lazy loading of system APIs
- Background process monitoring
- Efficient pattern matching algorithms

## Extension Guidelines

### Adding New Commands

1. **Define Patterns**: Add recognition patterns to `MACBrain`
2. **Implement Handler**: Create method in `WindowsCommands`
3. **Error Handling**: Include proper exception handling
4. **Documentation**: Update this documentation

### Example: Adding Weather Command

```python
def handle_weather(self, text: str) -> Dict[str, Any]:
    """Handle weather commands."""
    try:
        # Implementation here
        return {
            'message': "Current weather: 72°F, partly cloudy",
            'data': {
                'temperature': 72,
                'condition': 'partly cloudy',
                'humidity': 65
            }
        }
    except Exception as e:
        return {
            'message': f"Error getting weather: {str(e)}",
            'data': None
        }
```

This comprehensive documentation covers all current Windows commands and provides guidance for future development and troubleshooting.
