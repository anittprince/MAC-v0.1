# System Architecture

This document provides a comprehensive overview of the MAC Assistant's system architecture, design patterns, and component interactions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAC Assistant System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                 ┌─────────────────────────┐ │
│  │   Android App   │                 │    Windows Backend      │ │
│  │                 │                 │                         │ │
│  │  ┌───────────┐  │    HTTP API     │  ┌─────────────────────┐ │ │
│  │  │    UI     │  │ ◄──────────────► │  │   FastAPI Server   │ │ │
│  │  │ (Compose) │  │   (REST/JSON)   │  │                     │ │ │
│  │  └───────────┘  │                 │  └─────────────────────┘ │ │
│  │                 │                 │           │             │ │
│  │  ┌───────────┐  │                 │  ┌─────────────────────┐ │ │
│  │  │   Voice   │  │                 │  │    Command Brain    │ │ │
│  │  │ Recording │  │                 │  │  (Pattern Matcher)  │ │ │
│  │  └───────────┘  │                 │  └─────────────────────┘ │ │
│  │                 │                 │           │             │ │
│  │  ┌───────────┐  │                 │  ┌─────────────────────┐ │ │
│  │  │  Network  │  │                 │  │  Platform Commands │ │ │
│  │  │   Client  │  │                 │  │    (Windows/etc)    │ │ │
│  │  └───────────┘  │                 │  └─────────────────────┘ │ │
│  └─────────────────┘                 │           │             │ │
│                                      │  ┌─────────────────────┐ │ │
│                                      │  │   Voice I/O Engine  │ │ │
│  ┌─────────────────┐                 │  │  (Vosk + pyttsx3)   │ │ │
│  │  Voice Models   │                 │  └─────────────────────┘ │ │
│  │     (Vosk)      │                 │           │             │ │
│  └─────────────────┘                 │  ┌─────────────────────┐ │ │
│                                      │  │   System APIs      │ │ │
│                                      │  │ (Audio, Process,    │ │ │
│                                      │  │  Network, etc.)     │ │ │
│                                      │  └─────────────────────┘ │ │
│                                      └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Command Brain (`core/brain.py`)

The central intelligence of the system that processes natural language commands.

```python
class MACBrain:
    """
    Central command processor with pattern recognition capabilities.
    
    Responsibilities:
    - Parse natural language input
    - Match commands to appropriate handlers
    - Route commands to platform-specific modules
    - Format and return responses
    """
```

**Key Features:**
- **Pattern Recognition**: Uses regex and keyword matching
- **Command Routing**: Directs commands to appropriate platform modules
- **Response Formatting**: Standardizes response format across platforms
- **Error Handling**: Graceful handling of unrecognized commands

**Command Categories:**
- Greetings and social interactions
- Time and date queries
- System information requests
- Volume and audio control
- Application management
- Network diagnostics
- File operations

### 2. Voice Processing Engine

#### Voice Input (`core/voice_input.py`)
```python
class VoiceInput:
    """
    Handles speech-to-text conversion using Vosk.
    
    Features:
    - Offline speech recognition
    - Real-time audio processing
    - Multiple model support
    - Noise filtering
    """
```

**Technical Details:**
- **Engine**: Vosk (Kaldi-based offline recognition)
- **Audio Format**: 16kHz, 16-bit, mono WAV
- **Model Support**: Multiple languages and sizes
- **Real-time Processing**: Streaming audio recognition

#### Voice Output (`core/voice_output.py`)
```python
class VoiceOutput:
    """
    Text-to-speech synthesis using pyttsx3.
    
    Features:
    - Multiple voice options
    - Configurable speech rate
    - Volume control
    - Platform-specific optimizations
    """
```

### 3. Platform Command Modules

#### Windows Commands (`commands/windows.py`)
```python
class WindowsCommands:
    """
    Windows-specific system operations and controls.
    
    Capabilities:
    - System information retrieval
    - Audio control via Windows APIs
    - Process management
    - Network diagnostics
    - Application launching
    """
```

**Windows API Integration:**
- **Audio Control**: pycaw (Windows Core Audio)
- **System Info**: psutil, WMI
- **Process Management**: Windows Process API
- **File Operations**: Windows File System API

#### Android Commands (`commands/android.py`)
```python
class AndroidCommands:
    """
    Android-specific operations (future expansion).
    
    Planned Capabilities:
    - Device information
    - App management
    - Notification handling
    - Settings control
    """
```

### 4. HTTP API Server (`sync/api.py`)

**FastAPI-based REST API** for cross-platform communication.

```python
@app.post("/command")
async def execute_command(request: CommandRequest) -> CommandResponse:
    """
    Main API endpoint for command execution.
    
    Input: CommandRequest (text, metadata)
    Output: CommandResponse (message, data, status)
    """
```

**API Features:**
- **CORS Support**: Cross-origin resource sharing
- **Error Handling**: Structured error responses
- **Health Checks**: System status monitoring
- **Request Validation**: Pydantic models
- **Async Processing**: Non-blocking request handling

### 5. Android Application

#### Architecture Pattern: MVVM (Model-View-ViewModel)

```kotlin
// View Layer
@Composable
fun MainScreen(viewModel: AssistantViewModel)

// ViewModel Layer
class AssistantViewModel(repository: AssistantRepository)

// Model Layer
data class CommandRequest(val text: String, val timestamp: Long)
data class CommandResponse(val message: String, val data: Any?)
```

**Component Structure:**
- **UI Layer**: Jetpack Compose with Material Design 3
- **ViewModel**: State management and business logic
- **Repository**: Data access and API communication
- **Network Layer**: Retrofit for HTTP communication
- **Voice Manager**: Android MediaRecorder integration

## Data Flow Architecture

### 1. Voice Command Flow (Windows)

```
User Speech Input
       ↓
[Microphone Capture]
       ↓
[PyAudio Processing]
       ↓
[Vosk Speech Recognition]
       ↓
[Command Text]
       ↓
[MACBrain Pattern Matching]
       ↓
[Windows Command Module]
       ↓
[System API Execution]
       ↓
[Response Generation]
       ↓
[pyttsx3 Text-to-Speech]
       ↓
[Audio Output to User]
```

### 2. Android-to-Windows Flow

```
Android App Voice Input
       ↓
[Android MediaRecorder]
       ↓
[Local Speech Processing]
       ↓
[HTTP POST to Windows API]
       ↓
[FastAPI Request Handler]
       ↓
[MACBrain Command Processing]
       ↓
[Windows Command Execution]
       ↓
[JSON Response to Android]
       ↓
[Android UI Update]
       ↓
[Visual/Audio Feedback]
```

### 3. Command Processing Pipeline

```python
def process_command(text: str) -> Dict[str, Any]:
    """
    1. Input Normalization
       - Convert to lowercase
       - Remove punctuation
       - Trim whitespace
    
    2. Pattern Matching
       - Check greeting patterns
       - Match time/date patterns
       - Identify system commands
       - Detect volume controls
    
    3. Command Routing
       - Route to appropriate handler
       - Pass context and parameters
       - Handle error conditions
    
    4. Response Generation
       - Format success responses
       - Generate error messages
       - Include relevant data
    
    5. Output Formatting
       - Structure for voice output
       - Prepare for API responses
       - Log for debugging
    """
```

## Design Patterns and Principles

### 1. Modular Architecture

**Separation of Concerns:**
- **Core**: Fundamental voice and brain functionality
- **Commands**: Platform-specific implementations
- **Sync**: Communication and API layer
- **Android**: Mobile application layer

**Benefits:**
- Easy testing and maintenance
- Platform-specific optimizations
- Independent component development
- Clear responsibility boundaries

### 2. Plugin-Style Command System

```python
class CommandInterface:
    """
    Abstract base for command modules.
    """
    def handle_greeting(self, text: str) -> Dict[str, Any]: pass
    def handle_time(self, text: str) -> Dict[str, Any]: pass
    def handle_system_info(self, text: str) -> Dict[str, Any]: pass
    # ... other command methods
```

**Extensibility:**
- New platforms can implement the interface
- Commands can be added without core changes
- Runtime command registration possible

### 3. Error Handling Strategy

**Graceful Degradation:**
```python
try:
    result = execute_platform_command(command)
except ImportError:
    return {"message": "Feature requires additional libraries"}
except PermissionError:
    return {"message": "Operation requires elevated permissions"}
except Exception as e:
    return {"message": f"Unexpected error: {str(e)}"}
```

### 4. Configuration Management

**Environment-Based Configuration:**
```python
class Config:
    VOSK_MODEL_PATH = os.getenv('VOSK_MODEL_PATH', 'models/vosk-model')
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    VOICE_RATE = int(os.getenv('VOICE_RATE', '200'))
```

## Security Architecture

### 1. Network Security

**Local Network Only:**
- API server binds to local network interfaces
- No external internet dependencies for core functionality
- CORS configured for known origins only

**Input Validation:**
```python
class CommandRequest(BaseModel):
    text: str = Field(..., max_length=1000, min_length=1)
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
```

### 2. Permission Model

**Restricted Operations:**
- System shutdown/restart commands disabled
- File operations limited to safe directories
- Network access limited to diagnostics
- Application closing requires confirmation

**Safe Defaults:**
```python
def handle_shutdown(self, text: str) -> Dict[str, Any]:
    return {
        'message': "System power commands are disabled for safety.",
        'data': None
    }
```

## Performance Considerations

### 1. Speech Recognition Optimization

**Model Selection:**
- Small models (40MB) for basic commands
- Large models (1.8GB) for accuracy
- GPU acceleration when available

**Audio Processing:**
- Real-time streaming recognition
- Background noise suppression
- Voice activity detection

### 2. API Response Times

**Caching Strategy:**
- System information cached for 30 seconds
- Network status cached for 10 seconds
- Application list cached for 60 seconds

**Async Processing:**
```python
@app.post("/command")
async def execute_command(request: CommandRequest):
    # Non-blocking command execution
    result = await asyncio.get_event_loop().run_in_executor(
        None, brain.process_command, request.text
    )
    return result
```

### 3. Memory Management

**Resource Cleanup:**
- Audio streams properly closed
- Model memory released when unused
- HTTP connections pooled and reused

## Scalability and Extensibility

### 1. Adding New Platforms

```python
# Example: Linux command module
class LinuxCommands:
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def handle_volume(self, text: str) -> Dict[str, Any]:
        # Linux-specific volume control using ALSA/PulseAudio
        pass
```

### 2. Command Extension Framework

```python
# Register new command categories
def register_command_handler(pattern: str, handler: Callable):
    """
    Dynamically register new command patterns.
    """
    brain.command_patterns[pattern] = handler
```

### 3. Multi-Language Support

**Vosk Model Integration:**
- Download language-specific models
- Configure recognition language
- Adjust command patterns for language

**Localization Framework:**
```python
class LocalizedCommands:
    def __init__(self, language: str = 'en'):
        self.language = language
        self.patterns = load_language_patterns(language)
```

## Deployment Architecture

### 1. Development Environment
- Local Python environment
- Android Studio for mobile development
- Testing on local network

### 2. Production Deployment
- Windows service installation
- Android APK distribution
- Network configuration automation

### 3. Monitoring and Logging
- Structured logging with Python logging module
- Performance metrics collection
- Error tracking and reporting

This architecture provides a solid foundation for cross-platform voice assistance while maintaining modularity, security, and performance.
