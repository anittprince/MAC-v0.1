# Development Guide

This guide provides comprehensive information for developers who want to contribute to, extend, or customize the MAC Assistant project.

## Development Environment Setup

### Prerequisites

**Required Software:**
- **Python 3.8+** with pip
- **Git** for version control
- **Code Editor** (VS Code, PyCharm, etc.)
- **Android Studio** (for Android development)
- **Node.js** (for documentation tools, optional)

**Development Dependencies:**
```bash
pip install pytest black flake8 mypy pre-commit sphinx
```

### Project Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd MAC-v0.1
```

2. **Create Development Environment**
```bash
python -m venv venv-dev
venv-dev\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. **Install Pre-commit Hooks**
```bash
pre-commit install
```

4. **Verify Setup**
```bash
python test_mac.py
pytest tests/
```

## Project Structure Deep Dive

### Core Architecture

```
MAC-v0.1/
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── brain.py            # Command processor and pattern matching
│   ├── voice_input.py      # Speech recognition (Vosk)
│   └── voice_output.py     # Text-to-speech (pyttsx3)
├── commands/                # Platform-specific command implementations
│   ├── __init__.py
│   ├── windows.py          # Windows system operations
│   └── android.py          # Android operations (future)
├── sync/                    # Communication layer
│   ├── __init__.py
│   └── api.py              # FastAPI server for cross-platform communication
├── android/                 # Android application
│   └── MACAssistant/       # Kotlin app with Jetpack Compose
├── models/                  # Voice recognition models
│   └── vosk-model/         # Offline speech recognition models
├── tests/                   # Test suite
│   ├── test_core.py
│   ├── test_commands.py
│   └── test_api.py
├── docs/                    # Documentation
├── main.py                  # Application entry point
└── demo.py                  # Quick demonstration script
```

### Code Organization Principles

**Separation of Concerns:**
- **Core**: Voice processing and command routing
- **Commands**: Platform-specific implementations
- **Sync**: Communication between platforms
- **Android**: Mobile interface

**Design Patterns:**
- **Command Pattern**: For extensible command system
- **Strategy Pattern**: For platform-specific operations
- **Observer Pattern**: For event handling
- **Repository Pattern**: For data access (Android)

## Core Module Development

### Brain Module (`core/brain.py`)

The brain is the central command processor that handles natural language understanding and command routing.

**Key Components:**

```python
class MACBrain:
    def __init__(self):
        self.windows_commands = WindowsCommands()
        self.android_commands = AndroidCommands()
        
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process natural language command and return response.
        
        Args:
            text: Natural language command string
            
        Returns:
            Dict containing message, data, and status
        """
```

**Pattern Matching System:**

```python
# Example pattern matching
def _match_patterns(self, text: str) -> Optional[Callable]:
    text = text.lower().strip()
    
    # Greeting patterns
    if any(word in text for word in ['hello', 'hi', 'hey']):
        return self.windows_commands.handle_greeting
    
    # Time patterns
    elif any(phrase in text for phrase in ['time', 'what time']):
        return self.windows_commands.handle_time
    
    # Volume patterns
    elif any(word in text for word in ['volume', 'sound', 'mute']):
        return self.windows_commands.handle_volume
        
    return None
```

**Adding New Patterns:**

1. **Define Pattern Recognition**
```python
elif 'weather' in text or 'temperature' in text:
    return self.windows_commands.handle_weather
```

2. **Implement Handler**
```python
def handle_weather(self, text: str) -> Dict[str, Any]:
    try:
        # Implementation here
        return {
            'message': "Current weather: 72°F, sunny",
            'data': {'temperature': 72, 'condition': 'sunny'}
        }
    except Exception as e:
        return {
            'message': f"Error getting weather: {str(e)}",
            'data': None
        }
```

### Voice Input Module (`core/voice_input.py`)

Handles speech-to-text conversion using Vosk.

**Key Features:**
- Real-time speech recognition
- Offline processing
- Multiple model support
- Audio preprocessing

**Development Notes:**

```python
class VoiceInput:
    def __init__(self, model_path: str):
        """
        Initialize voice input with Vosk model.
        
        Args:
            model_path: Path to Vosk model directory
        """
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        
    def listen(self) -> Optional[str]:
        """
        Listen for voice input and return recognized text.
        
        Returns:
            Recognized text or None if no speech detected
        """
```

**Optimization Opportunities:**
- Implement voice activity detection
- Add noise filtering
- Support for multiple audio formats
- Streaming recognition for longer commands

### Voice Output Module (`core/voice_output.py`)

Handles text-to-speech synthesis using pyttsx3.

**Configuration Options:**

```python
class VoiceOutput:
    def __init__(self):
        self.engine = pyttsx3.init()
        self._configure_voice()
        
    def _configure_voice(self):
        """Configure voice settings."""
        # Voice selection
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        
        # Speech rate (words per minute)
        self.engine.setProperty('rate', 200)
        
        # Volume (0.0 to 1.0)
        self.engine.setProperty('volume', 0.8)
```

**Customization:**
- Voice personality selection
- Dynamic speech rate adjustment
- Emotion-based voice modulation
- Multi-language support

## Command Module Development

### Windows Command Module (`commands/windows.py`)

Platform-specific Windows operations and system control.

**Command Handler Structure:**

```python
def handle_command_category(self, text: str) -> Dict[str, Any]:
    """
    Handle specific category of commands.
    
    Args:
        text: Command text for additional parsing
        
    Returns:
        Standardized response dictionary
    """
    try:
        # Implementation
        result = perform_operation(text)
        return {
            'message': "Human-readable response",
            'data': result,
            'status': 'success'
        }
    except Exception as e:
        return {
            'message': f"Error: {str(e)}",
            'data': None,
            'status': 'error'
        }
```

**Windows API Integration:**

```python
# System Information
import psutil, platform, socket

# Audio Control
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Process Management
import subprocess, os

# Registry Access
import winreg
```

**Adding New Windows Commands:**

1. **Define Handler Method**
```python
def handle_new_command(self, text: str) -> Dict[str, Any]:
    """Handle new command category."""
    try:
        # Parse command variations
        if 'variation1' in text:
            result = self._handle_variation1()
        elif 'variation2' in text:
            result = self._handle_variation2()
        else:
            result = self._handle_default()
            
        return {
            'message': f"Command executed: {result}",
            'data': result
        }
    except Exception as e:
        return {
            'message': f"Error executing command: {str(e)}",
            'data': None
        }
```

2. **Register in Brain**
```python
# In core/brain.py
elif 'new_command' in text:
    return self.windows_commands.handle_new_command
```

3. **Add Tests**
```python
def test_new_command():
    wc = WindowsCommands()
    result = wc.handle_new_command("new_command test")
    assert result['status'] == 'success'
```

### Android Command Module (`commands/android.py`)

Future platform for Android-specific operations.

**Planned Features:**
- Device information queries
- App management
- Notification handling
- Settings control

## API Development (`sync/api.py`)

FastAPI-based REST API for cross-platform communication.

**API Structure:**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="MAC Assistant API")

class CommandRequest(BaseModel):
    text: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    status: str
    timestamp: float
    execution_time: float
```

**Adding New Endpoints:**

```python
@app.post("/new-endpoint")
async def new_endpoint(request: CustomRequest) -> CustomResponse:
    """New API endpoint."""
    try:
        # Process request
        result = await process_request(request)
        return CustomResponse(
            message="Success",
            data=result,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**API Testing:**

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_new_endpoint():
    response = client.post("/new-endpoint", json={
        "field": "value"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

## Android Development

### Project Structure

```
android/MACAssistant/
├── app/
│   ├── src/main/
│   │   ├── java/com/mac/assistant/
│   │   │   ├── MainActivity.kt
│   │   │   ├── viewmodel/
│   │   │   │   └── AssistantViewModel.kt
│   │   │   ├── model/
│   │   │   │   └── ApiModels.kt
│   │   │   ├── network/
│   │   │   │   └── ApiService.kt
│   │   │   ├── repository/
│   │   │   │   └── AssistantRepository.kt
│   │   │   ├── service/
│   │   │   │   └── VoiceManager.kt
│   │   │   └── ui/screens/
│   │   │       └── MainScreen.kt
│   │   └── res/
│   └── build.gradle.kts
├── build.gradle
└── settings.gradle.kts
```

### Android Architecture (MVVM)

**ViewModel:**
```kotlin
class AssistantViewModel(
    private val repository: AssistantRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(AssistantUiState())
    val uiState: StateFlow<AssistantUiState> = _uiState.asStateFlow()
    
    fun executeCommand(text: String) {
        viewModelScope.launch {
            try {
                _uiState.value = _uiState.value.copy(isLoading = true)
                val response = repository.executeCommand(text)
                _uiState.value = _uiState.value.copy(
                    response = response,
                    isLoading = false
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = e.message,
                    isLoading = false
                )
            }
        }
    }
}
```

**Repository:**
```kotlin
class AssistantRepository(
    private val apiService: ApiService
) {
    suspend fun executeCommand(text: String): CommandResponse {
        val request = CommandRequest(
            text = text,
            timestamp = System.currentTimeMillis() / 1000.0
        )
        return apiService.executeCommand(request)
    }
}
```

**UI with Jetpack Compose:**
```kotlin
@Composable
fun MainScreen(viewModel: AssistantViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp)
    ) {
        // Voice input button
        FloatingActionButton(
            onClick = { /* Start voice recording */ }
        ) {
            Icon(Icons.Default.Mic, contentDescription = "Voice Input")
        }
        
        // Response display
        if (uiState.response != null) {
            Text(text = uiState.response.message)
        }
        
        // Loading indicator
        if (uiState.isLoading) {
            CircularProgressIndicator()
        }
    }
}
```

## Testing Strategy

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_brain.py
│   ├── test_voice_input.py
│   ├── test_voice_output.py
│   └── test_commands.py
├── integration/            # Integration tests
│   ├── test_api_integration.py
│   └── test_voice_pipeline.py
├── e2e/                   # End-to-end tests
│   └── test_full_workflow.py
└── fixtures/              # Test data and mocks
    └── sample_audio.wav
```

### Unit Testing Examples

**Testing Brain Module:**
```python
import pytest
from core.brain import MACBrain

class TestMACBrain:
    def setup_method(self):
        self.brain = MACBrain()
    
    def test_greeting_command(self):
        result = self.brain.process_command("hello MAC")
        assert result['status'] == 'success'
        assert 'hello' in result['message'].lower()
    
    def test_time_command(self):
        result = self.brain.process_command("what time is it")
        assert result['status'] == 'success'
        assert 'time' in result['message'].lower()
    
    def test_unknown_command(self):
        result = self.brain.process_command("unknown command")
        assert 'understand' in result['message'].lower()
```

**Testing Windows Commands:**
```python
from commands.windows import WindowsCommands

class TestWindowsCommands:
    def setup_method(self):
        self.commands = WindowsCommands()
    
    def test_system_info(self):
        result = self.commands.handle_system_info("system info")
        assert result['status'] == 'success'
        assert 'cpu_usage' in result['data']
    
    @pytest.mark.skipif(not has_audio_device(), reason="No audio device")
    def test_volume_control(self):
        result = self.commands.handle_volume("volume up")
        assert result['status'] == 'success'
```

**Testing API Endpoints:**
```python
from fastapi.testclient import TestClient
from sync.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert "MAC Assistant API" in response.json()["message"]

def test_command_execution():
    response = client.post("/command", json={
        "text": "what time is it"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### Integration Testing

**Voice Pipeline Test:**
```python
def test_voice_pipeline():
    # Test complete voice processing pipeline
    voice_input = VoiceInput("models/vosk-model")
    brain = MACBrain()
    voice_output = VoiceOutput()
    
    # Simulate voice input
    test_audio = load_test_audio("fixtures/hello_mac.wav")
    recognized_text = voice_input.process_audio(test_audio)
    
    # Process command
    response = brain.process_command(recognized_text)
    
    # Generate voice output
    voice_output.speak(response['message'])
    
    assert recognized_text == "hello mac"
    assert response['status'] == 'success'
```

### Performance Testing

```python
import time
import psutil

def test_performance_benchmarks():
    brain = MACBrain()
    
    # Measure response time
    start_time = time.time()
    result = brain.process_command("system info")
    response_time = time.time() - start_time
    
    # Assert performance requirements
    assert response_time < 1.0  # Response under 1 second
    assert psutil.cpu_percent() < 50  # CPU usage under 50%
```

## Code Quality and Standards

### Code Style

**Python (PEP 8):**
```python
# Use black for formatting
black .

# Use flake8 for linting
flake8 .

# Use mypy for type checking
mypy .
```

**Kotlin (Android):**
```bash
# Use ktlint for formatting
./gradlew ktlintFormat

# Use detekt for static analysis
./gradlew detekt
```

### Type Hints

**Python Type Annotations:**
```python
from typing import Dict, Any, Optional, List

def process_command(self, text: str) -> Dict[str, Any]:
    """Process command with proper type hints."""
    pass

class CommandResponse:
    def __init__(
        self, 
        message: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.data = data
```

### Documentation Standards

**Docstring Format:**
```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of function purpose.
    
    Longer description if needed, explaining the function's
    behavior, side effects, and usage patterns.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Dictionary containing the result with 'status' and 'data' keys
        
    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When system operation fails
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['status'])
        'success'
    """
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        
    - name: Run tests
      run: |
        pytest tests/ --cov=core --cov=commands
        
    - name: Code quality checks
      run: |
        black --check .
        flake8 .
        mypy .
```

## Release Management

### Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

### Release Process

1. **Update Version Numbers**
```python
# In __init__.py
__version__ = "1.2.3"
```

2. **Update Changelog**
```markdown
## [1.2.3] - 2024-01-15
### Added
- New weather command feature
### Fixed
- Volume control stability improvements
### Changed
- Improved voice recognition accuracy
```

3. **Create Release Branch**
```bash
git checkout -b release/1.2.3
git push origin release/1.2.3
```

4. **Build and Test**
```bash
python -m build
pytest tests/
```

5. **Tag Release**
```bash
git tag v1.2.3
git push origin v1.2.3
```

## Performance Optimization

### Profiling

**Python Profiling:**
```python
import cProfile
import pstats

def profile_command_processing():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run commands
    brain = MACBrain()
    for _ in range(100):
        brain.process_command("system info")
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

**Memory Profiling:**
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function to profile
    pass
```

### Optimization Strategies

**Caching:**
```python
from functools import lru_cache
import time

class WindowsCommands:
    @lru_cache(maxsize=1)
    def _get_system_info_cached(self) -> Dict[str, Any]:
        """Cache system info for 30 seconds."""
        return self._get_system_info()
    
    def handle_system_info(self, text: str) -> Dict[str, Any]:
        # Use cached version for better performance
        if time.time() - self._last_update < 30:
            return self._get_system_info_cached()
        return self._get_system_info()
```

**Lazy Loading:**
```python
class VoiceInput:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self._model = None
        self._recognizer = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = vosk.Model(self.model_path)
        return self._model
```

## Security Considerations

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class CommandRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    
    @validator('text')
    def validate_text(cls, v):
        # Remove potentially dangerous characters
        v = re.sub(r'[<>"\']', '', v)
        return v.strip()
```

### Safe Command Execution

```python
def execute_safe_command(command: str) -> Dict[str, Any]:
    # Whitelist of allowed commands
    allowed_commands = {
        'notepad.exe', 'calc.exe', 'mspaint.exe'
    }
    
    if command not in allowed_commands:
        return {
            'message': 'Command not allowed for security reasons',
            'status': 'error'
        }
    
    # Execute safely
    subprocess.Popen(command, shell=False)
```

This development guide provides the foundation for contributing to and extending the MAC Assistant project. Follow these guidelines to maintain code quality, security, and performance standards.
